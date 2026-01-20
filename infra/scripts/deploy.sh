#!/usr/bin/env bash
set -euo pipefail

ENV="${1:?usage: deploy.sh <dev|prod>}"

APP_DIR="/srv/app-$ENV"
COMPOSE_FILE="$APP_DIR/infra/docker-compose.$ENV.yml"

echo "[deploy] env=$ENV dir=$APP_DIR"
echo "[deploy] compose=$COMPOSE_FILE"

: "${DOCKERHUB_USERNAME:?missing DOCKERHUB_USERNAME}"
: "${DOCKERHUB_TOKEN:?missing DOCKERHUB_TOKEN}"
: "${IMAGE_TAG:?missing IMAGE_TAG}"

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "[deploy] ERROR: compose file not found: $COMPOSE_FILE"
  exit 1
fi

echo "[deploy] docker login (Docker Hub)"
echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

# 이전/현재 태그 기록 (롤백용)
if [ -f "$APP_DIR/.current_image_tag" ]; then
  cp "$APP_DIR/.current_image_tag" "$APP_DIR/.previous_image_tag" || true
fi
echo "$IMAGE_TAG" > "$APP_DIR/.current_image_tag"

export DOCKERHUB_USERNAME IMAGE_TAG

echo "[deploy] pull images tag=$IMAGE_TAG"
docker compose -f "$COMPOSE_FILE" pull

echo "[deploy] up -d"
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

echo "[deploy] completed"
bash "$APP_DIR/infra/scripts/healthcheck.sh" "$ENV"
