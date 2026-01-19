#!/usr/bin/env bash
set -euo pipefail

ENV="${1:?usage: healthcheck.sh <dev|prod>}"
APP_DIR="/srv/app-$ENV"

echo "[healthcheck] start env=$ENV dir=$APP_DIR"

if [ ! -d "$APP_DIR" ]; then
  echo "[healthcheck] app directory missing: $APP_DIR"
  exit 1
fi

echo "[healthcheck] OK"
