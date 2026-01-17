#!/usr/bin/env bash
set -euo pipefail

echo "[deploy-dev]"
bash /srv/app/infra/scripts/deploy.sh dev

bash /srv/app/infra/scripts/healthcheck.sh
