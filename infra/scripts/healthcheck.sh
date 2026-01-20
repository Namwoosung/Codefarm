#!/usr/bin/env bash
set -euo pipefail

ENV="${1:?usage: healthcheck.sh <dev|prod>}"

APP_DIR="/srv/app-$ENV"
COMPOSE_FILE="$APP_DIR/infra/docker-compose.$ENV.yml"

echo "[healthcheck] start env=$ENV dir=$APP_DIR"
echo "[healthcheck] compose=$COMPOSE_FILE"

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "[healthcheck] ERROR: compose file missing: $COMPOSE_FILE"
  exit 1
fi

# compose로 정의된 컨테이너가 떠있는지 확인
echo "[healthcheck] containers:"
docker compose -f "$COMPOSE_FILE" ps

# HTTP 헬스체크 (기본값: frontend 80 / backend 8080)
FRONT_URL="${FRONT_URL:-http://127.0.0.1/}"
BACK_URL_PRIMARY="${BACK_URL_PRIMARY:-http://127.0.0.1:8080/actuator/health}"
BACK_URL_FALLBACK="${BACK_URL_FALLBACK:-http://127.0.0.1:8080/}"

# curl 없을 수 있어서 설치 안내 대신, 있으면 사용
if ! command -v curl >/dev/null 2>&1; then
  echo "[healthcheck] WARN: curl not found. Skipping HTTP checks."
  echo "[healthcheck] OK (containers only)"
  exit 0
fi

# 재시도 헬퍼
wait_http () {
  local name="$1"
  local url="$2"
  local retries="${3:-30}"
  local sleep_sec="${4:-2}"

  echo "[healthcheck] check $name: $url"
  for i in $(seq 1 "$retries"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "[healthcheck] $name OK"
      return 0
    fi
    echo "[healthcheck] $name not ready ($i/$retries) ..."
    sleep "$sleep_sec"
  done
  echo "[healthcheck] ERROR: $name failed: $url"
  return 1
}

# frontend 확인
wait_http "frontend" "$FRONT_URL" 30 2

# backend 확인 (actuator 있으면 그걸로, 없으면 /로 한 번 더)
if ! curl -fsS "$BACK_URL_PRIMARY" >/dev/null 2>&1; then
  echo "[healthcheck] backend primary failed, trying fallback..."
  wait_http "backend" "$BACK_URL_FALLBACK" 30 2
else
  echo "[healthcheck] backend OK (primary)"
fi

echo "[healthcheck] ALL OK"
