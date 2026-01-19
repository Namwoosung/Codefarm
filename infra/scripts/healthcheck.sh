#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/srv/app-dev"

echo "[healthcheck] start"

if [ ! -d "$APP_DIR" ]; then
  echo "[healthcheck] app directory missing"
  exit 1
fi

echo "[healthcheck] OK"
