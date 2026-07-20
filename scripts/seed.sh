#!/usr/bin/env bash
# Run the backend seed (idempotent). Phase 1 seeds SUPER_ADMIN + demo users.
set -euo pipefail
echo "[seed] Running backend seed (idempotent)..."
docker compose exec -T backend python -m seed.seed_data 2>&1 || \
  echo "[seed] Backend not reachable — is the stack running? Try 'make up' first."