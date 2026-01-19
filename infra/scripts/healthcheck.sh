#!/usr/bin/env bash
set -euo pipefail

$ENV="$1"                 # dev | prod
APP_DIR="/srv/app-$ENV"

echo "[healthcheck] start"

if [ ! -d "$APP_DIR" ]; then
  echo "[healthcheck] app directory missing"
  exit 1
fi

echo "[healthcheck] OK"
