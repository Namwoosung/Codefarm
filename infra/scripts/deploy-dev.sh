#!/usr/bin/env bash
set -euo pipefail

echo "[deploy-dev]"
bash /srv/app-dev/infra/scripts/deploy.sh dev

bash /srv/app-dev/infra/scripts/healthcheck.sh
