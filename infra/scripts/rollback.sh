#!/usr/bin/env bash
set -euo pipefail

ENV="$1"                 # dev | prod
APP_DIR="/srv/app-$ENV"

echo "[rollback] start"

cd "$APP_DIR"
git reset --hard HEAD~1

echo "[rollback] done"
