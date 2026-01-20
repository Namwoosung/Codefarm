#!/usr/bin/env bash
set -euo pipefail

ENV="${1:?usage: healthcheck.sh <dev|prod>}"

APP_DIR="/srv/app-$ENV"
COMPOSE_DIR="$APP_DIR/infra/compose"

BASE_FILE="$COMPOSE_DIR/docker-compose.base.yml"
ENV_FILE="$COMPOSE_DIR/docker-compose.$ENV.yml"
ENV_VARS_FILE="$COMPOSE_DIR/$ENV.env"

echo "[healthcheck] start env=$ENV dir=$APP_DIR"
echo "[healthcheck] base=$BASE_FILE"
echo "[healthcheck] env_compose=$ENV_FILE"
echo "[healthcheck] env_vars=$ENV_VARS_FILE"

for f in "$BASE_FILE" "$ENV_FILE" "$ENV_VARS_FILE"; do
  if [ ! -f "$f" ]; then
    echo "[healthcheck] ERROR: file not found: $f" >&2
    exit 1
  fi
done

echo "[healthcheck] containers:"
docker compose \
  -f "$BASE_FILE" \
  -f "$ENV_FILE" \
  --env-file "$ENV_VARS_FILE" \
  ps

# api 헬스 체크 (actuator health 기준)
echo "[healthcheck] waiting for api to be healthy..."
for i in $(seq 1 30); do
  if docker exec api-$ENV sh -lc "wget -qO- http://localhost:8080/actuator/health >/dev/null 2>&1"; then
    echo "[healthcheck] api healthy"
    exit 0
  fi
  sleep 2
done

echo "[healthcheck] ERROR: api did not become healthy in time" >&2
docker logs --tail=200 "api-$ENV" || true
exit 1
