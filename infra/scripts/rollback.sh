#!/usr/bin/env bash
set -euo pipefail

ENV="${1:?usage: healthcheck.sh <dev|prod>}"
APP_DIR="/srv/app-$ENV"

echo "[rollback] start env=$ENV dir=$APP_DIR"

cd "$APP_DIR"
git reset --hard HEAD~1

echo "[rollback] done"
