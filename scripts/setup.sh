#!/usr/bin/env bash
# ERP System — single-command setup.
# Idempotent: safe to re-run.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

log()  { printf "${GREEN}[setup]${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}[setup]${NC} %s\n" "$*"; }
info() { printf "${CYAN}[setup]${NC} %s\n" "$*"; }
err()  { printf "${RED}[setup]${NC} %s\n" "$*" >&2; }

# 1) .env
if [[ ! -f .env ]]; then
  log "Copying .env.example -> .env"
  cp .env.example .env
  warn ".env created from template. REVIEW SECRETS BEFORE PRODUCTION USE."
else
  info ".env already exists — leaving it untouched."
fi

# 2) Build & start
log "Building and starting containers (db, backend, frontend)..."
docker compose up -d --build

# 3) Wait for db healthy
log "Waiting for postgres to be healthy..."
for i in $(seq 1 60); do
  status=$(docker inspect --format '{{json .State.Health.Status }}' erp-db 2>/dev/null || \
           docker compose ps -q db | xargs -I{} docker inspect --format '{{json .State.Health.Status }}' {} 2>/dev/null || true)
  if [[ "$status" == *"healthy"* ]]; then
    log "Postgres is healthy."
    break
  fi
  sleep 2
  if [[ $i -eq 60 ]]; then
    err "Postgres did not become healthy in time. Run 'docker compose logs db' to inspect."
    exit 1
  fi
done

# 4) Wait for backend healthy (this also means migrations ran)
log "Waiting for backend to be healthy (runs migrations on startup)..."
for i in $(seq 1 60); do
  if curl -sf http://localhost:8000/health/live >/dev/null 2>&1; then
    log "Backend is live."
    break
  fi
  sleep 2
  if [[ $i -eq 60 ]]; then
    err "Backend did not become healthy in time. Run 'docker compose logs backend' to inspect."
    exit 1
  fi
done

# 5) Wait for frontend
log "Waiting for frontend to be healthy..."
for i in $(seq 1 60); do
  if curl -sf http://localhost:5173/healthz >/dev/null 2>&1; then
    log "Frontend is up."
    break
  fi
  sleep 2
  if [[ $i -eq 60 ]]; then
    warn "Frontend did not become healthy in time. It may still be starting — check 'docker compose logs frontend'."
  fi
done

# 6) Seed (Phase 0: idempotent placeholder that becomes real in later phases)
log "Running seed (phase 0 placeholder)..."
./scripts/seed.sh || warn "Seed script returned non-zero — see message above."

echo
log "================ ERP System is up ================"
info "Frontend (SvelteKit):  http://localhost:5173"
info "Backend (FastAPI):     http://localhost:8000"
info "API docs (Swagger):    http://localhost:8000/docs"
info "API docs (ReDoc):      http://localhost:8000/redoc"
info "Postgres:              localhost:5432 (user/db from .env)"
echo
warn "Phase 0 = foundations only. Auth, RBAC, users CRUD, etc. arrive in later phases."
printf "${GREEN}[done]${NC} All services started.\n"