#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/srv/app-dev"

echo "[rollback] start"

cd "$APP_DIR"
git reset --hard HEAD~1

echo "[rollback] done"
