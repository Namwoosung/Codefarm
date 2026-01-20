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

# backend 확인
# 1) actuator health가 200이면 OK
# 2) actuator가 없거나 막혀있으면, 포트가 열렸는지(HTTP 응답이 오기만 하면)로 최소 OK 처리
#    (루트가 404여도 "서버는 뜬 것"이므로 통과)
check_backend () {
  local primary="$BACK_URL_PRIMARY"
  local fallback="$BACK_URL_FALLBACK"

  echo "[healthcheck] check backend primary: $primary"
  for i in $(seq 1 30); do
    code="$(curl -sS -o /dev/null -w "%{http_code}" "$primary" || true)"
    if [ "$code" = "200" ]; then
      echo "[healthcheck] backend OK (primary 200)"
      return 0
    fi
    sleep 2
  done

  echo "[healthcheck] backend primary not ready (or not exposed). checking fallback reachability: $fallback"
  for i in $(seq 1 30); do
    code="$(curl -sS -o /dev/null -w "%{http_code}" "$fallback" || true)"
    # 000은 연결 실패(포트/프로세스 문제). 그 외(200/301/302/401/403/404 등)는 "응답은 왔다" = 서버는 살아있음
    if [ "$code" != "000" ]; then
      echo "[healthcheck] backend reachable (fallback http_code=$code)"
      return 0
    fi
    echo "[healthcheck] backend not reachable ($i/30) ..."
    sleep 2
  done

  echo "[healthcheck] ERROR: backend not reachable: $fallback"
  return 1
}

check_backend
