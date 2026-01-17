#!/usr/bin/env bash
set -euo pipefail

echo "[deploy-prod]"
bash /srv/app/infra/scripts/deploy.sh prod

bash /srv/app/infra/scripts/healthcheck.sh
