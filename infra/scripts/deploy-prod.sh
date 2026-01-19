#!/usr/bin/env bash
set -euo pipefail

echo "[deploy-prod]"
bash /srv/app-prod/infra/scripts/deploy.sh prod
bash /srv/app-prod/infra/scripts/healthcheck.sh prod
