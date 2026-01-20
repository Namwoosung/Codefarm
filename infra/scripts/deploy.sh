#!/usr/bin/env bash
set -euo pipefail

ENV="${1:?usage: deploy.sh <dev|prod>}"   # dev | prod

APP_DIR="/srv/app-$ENV"
COMPOSE_FILE="$APP_DIR/infra/docker-compose.$ENV.yml"

echo "[deploy] env=$ENV dir=$APP_DIR"
echo "[deploy] compose=$COMPOSE_FILE"

# 필수 환경변수 체크 (CI에서 SSH로 export해서 넘겨줄 것)
: "${CI_REGISTRY:?missing CI_REGISTRY}"
: "${CI_REGISTRY_USER:?missing CI_REGISTRY_USER}"
: "${CI_REGISTRY_PASSWORD:?missing CI_REGISTRY_PASSWORD}"
: "${CI_REGISTRY_IMAGE:?missing CI_REGISTRY_IMAGE}"
: "${IMAGE_TAG:?missing IMAGE_TAG}"

mkdir -p "$APP_DIR"
if [ ! -f "$COMPOSE_FILE" ]; then
  echo "[deploy] ERROR: compose file not found: $COMPOSE_FILE"
  exit 1
fi

echo "[deploy] docker login to registry=$CI_REGISTRY"
echo "$CI_REGISTRY_PASSWORD" | docker login "$CI_REGISTRY" -u "$CI_REGISTRY_USER" --password-stdin

echo "[deploy] pull images tag=$IMAGE_TAG"
export CI_REGISTRY_IMAGE IMAGE_TAG
docker compose -f "$COMPOSE_FILE" pull

echo "[deploy] up -d"
if [ -f "$APP_DIR/.current_image_tag" ]; then
  cp "$APP_DIR/.current_image_tag" "$APP_DIR/.previous_image_tag"
fi
echo "$IMAGE_TAG" > "$APP_DIR/.current_image_tag"
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

echo "[deploy] completed"

# 기존 healthcheck 유지
bash "$APP_DIR/infra/scripts/healthcheck.sh" "$ENV"
