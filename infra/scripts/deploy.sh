#!/usr/bin/env bash
set -euo pipefail

ENV="${1:?usage: deploy.sh <dev|prod>}"

APP_DIR="/srv/app-$ENV"
COMPOSE_DIR="$APP_DIR/infra/compose"

BASE_FILE="$COMPOSE_DIR/docker-compose.base.yml"
ENV_FILE="$COMPOSE_DIR/docker-compose.$ENV.yml"
ENV_VARS_FILE="$COMPOSE_DIR/$ENV.env"   # infra/compose/dev.env, infra/compose/prod.env

echo "[deploy] env=$ENV dir=$APP_DIR"
echo "[deploy] base=$BASE_FILE"
echo "[deploy] env_compose=$ENV_FILE"
echo "[deploy] env_vars=$ENV_VARS_FILE"

: "${DOCKERHUB_USERNAME:?missing DOCKERHUB_USERNAME}"
: "${DOCKERHUB_TOKEN:?missing DOCKERHUB_TOKEN}"
: "${IMAGE_TAG:?missing IMAGE_TAG}"

for f in "$BASE_FILE" "$ENV_FILE" "$ENV_VARS_FILE"; do
  if [ ! -f "$f" ]; then
    echo "[deploy] ERROR: file not found: $f" >&2
    exit 1
  fi
done

echo "[deploy] docker login (Docker Hub)"
echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

# 이전/현재 태그 기록 (롤백용)
if [ -f "$APP_DIR/.current_image_tag" ]; then
  cp "$APP_DIR/.current_image_tag" "$APP_DIR/.previous_image_tag" || true
fi
echo "$IMAGE_TAG" > "$APP_DIR/.current_image_tag"

export DOCKERHUB_USERNAME IMAGE_TAG

echo "[deploy] pull images tag=$IMAGE_TAG"
docker compose \
  -f "$BASE_FILE" \
  -f "$ENV_FILE" \
  --env-file "$ENV_VARS_FILE" \
  pull

echo "[deploy] up -d"
docker compose \
  -f "$BASE_FILE" \
  -f "$ENV_FILE" \
  --env-file "$ENV_VARS_FILE" \
  up -d --remove-orphans

echo "[deploy] completed"
bash "$APP_DIR/infra/scripts/healthcheck.sh" "$ENV"