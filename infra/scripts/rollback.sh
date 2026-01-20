#!/usr/bin/env bash
set -euo pipefail

ENV="${1:?usage: rollback.sh <dev|prod>}"

APP_DIR="/srv/app-$ENV"
COMPOSE_DIR="$APP_DIR/infra/compose"

BASE_FILE="$COMPOSE_DIR/docker-compose.base.yml"
ENV_FILE="$COMPOSE_DIR/docker-compose.$ENV.yml"
ENV_VARS_FILE="$COMPOSE_DIR/$ENV.env"

CURRENT_TAG_FILE="$APP_DIR/.current_image_tag"
PREV_TAG_FILE="$APP_DIR/.previous_image_tag"

echo "[rollback] env=$ENV dir=$APP_DIR"
echo "[rollback] base=$BASE_FILE"
echo "[rollback] env_compose=$ENV_FILE"
echo "[rollback] env_vars=$ENV_VARS_FILE"

: "${DOCKERHUB_USERNAME:?missing DOCKERHUB_USERNAME}"
: "${DOCKERHUB_TOKEN:?missing DOCKERHUB_TOKEN}"

for f in "$BASE_FILE" "$ENV_FILE" "$ENV_VARS_FILE"; do
  if [ ! -f "$f" ]; then
    echo "[rollback] ERROR: file not found: $f" >&2
    exit 1
  fi
done

if [ ! -f "$PREV_TAG_FILE" ]; then
  echo "[rollback] ERROR: previous tag not found: $PREV_TAG_FILE" >&2
  echo "[rollback] hint: deploy.sh must run at least twice to create .previous_image_tag" >&2
  exit 1
fi

PREV_TAG="$(cat "$PREV_TAG_FILE")"
if [ -z "$PREV_TAG" ]; then
  echo "[rollback] ERROR: previous tag file is empty: $PREV_TAG_FILE" >&2
  exit 1
fi

echo "[rollback] docker login (Docker Hub)"
echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

echo "[rollback] rolling back to IMAGE_TAG=$PREV_TAG"
export DOCKERHUB_USERNAME IMAGE_TAG="$PREV_TAG"

echo "[rollback] pull images tag=$IMAGE_TAG"
docker compose \
  -f "$BASE_FILE" \
  -f "$ENV_FILE" \
  --env-file "$ENV_VARS_FILE" \
  pull

echo "[rollback] up -d"
docker compose \
  -f "$BASE_FILE" \
  -f "$ENV_FILE" \
  --env-file "$ENV_VARS_FILE" \
  up -d --remove-orphans

# 태그 파일 스왑 (현재<->이전)
if [ -f "$CURRENT_TAG_FILE" ]; then
  TMP_TAG="$(cat "$CURRENT_TAG_FILE")"
  echo "$IMAGE_TAG" > "$CURRENT_TAG_FILE"
  echo "$TMP_TAG" > "$PREV_TAG_FILE"
else
  echo "$IMAGE_TAG" > "$CURRENT_TAG_FILE"
fi

echo "[rollback] completed (current=$IMAGE_TAG)"
