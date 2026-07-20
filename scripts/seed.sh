#!/usr/bin/env bash
# Phase 0 seed placeholder. Real seed (roles, permissions, super-admin user,
# faker-generated employees/users) is added in phases 1-4.
set -euo pipefail
echo "[seed] Phase 0: no seed data yet. Migrations already create the empty schema."
echo "[seed] (Phase 1+ will seed roles, permissions, super-admin, and demo data here.)"
docker compose exec -T backend python -m seed.seed_data --phase0 2>/dev/null || \
  echo "[seed] Backend not reachable or seed_data not present yet — skipping."