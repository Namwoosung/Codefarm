#!/usr/bin/env bash
set -euo pipefail

ENV="${1:?usage: rollback.sh <dev|prod>}"

APP_DIR="/srv/app-$ENV"
COMPOSE_FILE="$APP_DIR/infra/docker-compose.$ENV.yml"

echo "[rollback] start env=$ENV dir=$APP_DIR"

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

# CI에서 쓰던 레지스트리 로그인 정보가 서버에 필요.
# 1) 서버에 영구 저장해둔 docker login이 이미 되어있으면 이 단계는 생략 가능
# 2) 아니면 CI에서 rollback 호출할 때 export해서 넘겨주면 됨
if [ -n "${CI_REGISTRY:-}" ] && [ -n "${CI_REGISTRY_USER:-}" ] && [ -n "${CI_REGISTRY_PASSWORD:-}" ]; then
  echo "[rollback] docker login to registry=$CI_REGISTRY"
  echo "$CI_REGISTRY_PASSWORD" | docker login "$CI_REGISTRY" -u "$CI_REGISTRY_USER" --password-stdin
else
  echo "[rollback] WARN: registry env not provided. Assuming docker is already logged in."
fi

export CI_REGISTRY_IMAGE="${CI_REGISTRY_IMAGE:-}"
if [ -z "$CI_REGISTRY_IMAGE" ]; then
  echo "[rollback] ERROR: CI_REGISTRY_IMAGE is missing"
  exit 1
fi

export IMAGE_TAG="$PREV_TAG"

echo "[rollback] pull images tag=$IMAGE_TAG"
docker compose -f "$COMPOSE_FILE" pull

echo "[rollback] up -d (rollback)"
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

# 태그 파일 스왑(현재/이전)
if [ -f "$CURR_TAG_FILE" ]; then
  cp "$CURR_TAG_FILE" "$PREV_TAG_FILE.tmp" || true
  echo "$PREV_TAG" > "$CURR_TAG_FILE"
  mv "$PREV_TAG_FILE.tmp" "$PREV_TAG_FILE" || true
fi

echo "[rollback] done (now running tag=$IMAGE_TAG)"

# 원하면 헬스체크도 같이
bash "$APP_DIR/infra/scripts/healthcheck.sh" "$ENV"
