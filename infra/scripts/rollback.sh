#!/usr/bin/env bash
set -euo pipefail

ENV="${1:?usage: rollback.sh <dev|prod>}"

APP_DIR="/srv/app-$ENV"
COMPOSE_FILE="$APP_DIR/infra/docker-compose.$ENV.yml"

echo "[rollback] start env=$ENV dir=$APP_DIR"
echo "[rollback] compose=$COMPOSE_FILE"

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "[rollback] ERROR: compose file missing: $COMPOSE_FILE"
  exit 1
fi

PREV_TAG_FILE="$APP_DIR/.previous_image_tag"
CURR_TAG_FILE="$APP_DIR/.current_image_tag"

if [ ! -f "$PREV_TAG_FILE" ]; then
  echo "[rollback] ERROR: previous tag file missing: $PREV_TAG_FILE"
  echo "[rollback] (hint) deploy.sh에서 .previous_image_tag 저장하도록 설정해야 함"
  exit 1
fi

PREV_TAG="$(cat "$PREV_TAG_FILE")"
echo "[rollback] previous tag=$PREV_TAG"

: "${DOCKERHUB_USERNAME:?missing DOCKERHUB_USERNAME}"
: "${DOCKERHUB_TOKEN:?missing DOCKERHUB_TOKEN}"

echo "[rollback] docker login (Docker Hub)"
echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

export DOCKERHUB_USERNAME
export IMAGE_TAG="$PREV_TAG"

echo "[rollback] pull images tag=$IMAGE_TAG"
docker compose -f "$COMPOSE_FILE" pull

echo "[rollback] up -d (rollback)"
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

# 태그 파일 스왑(현재/이전)
if [ -f "$CURR_TAG_FILE" ]; then
  CURR_TAG="$(cat "$CURR_TAG_FILE" || true)"
  echo "$PREV_TAG" > "$CURR_TAG_FILE"
  if [ -n "${CURR_TAG:-}" ]; then
    echo "$CURR_TAG" > "$PREV_TAG_FILE"
  fi
else
  # current가 없으면 현재를 prev로 기록만
  echo "$PREV_TAG" > "$CURR_TAG_FILE"
fi

echo "[rollback] done (now running tag=$IMAGE_TAG)"

bash "$APP_DIR/infra/scripts/healthcheck.sh" "$ENV"
