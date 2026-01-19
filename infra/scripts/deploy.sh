#!/usr/bin/env bash
set -euo pipefail

ENV="${1:?usage: deploy.sh <dev|prod>}"
APP_DIR="/srv/app-$ENV"
REPO_URL="https://lab.ssafy.com/s14-webmobile2-sub1/S14P11B109.git"

echo "[deploy] env=$ENV dir=$APP_DIR"

mkdir -p "$APP_DIR"

if [ ! -d "$APP_DIR/.git" ]; then
  echo "[deploy] first clone"
  git clone "$REPO_URL" "$APP_DIR"
else
  echo "[deploy] git pull"
  cd "$APP_DIR"
  git pull
fi

echo "[deploy] completed"
