#!/usr/bin/env bash
# Destructive: drop and recreate the public schema, then re-run migrations.
set -euo pipefail
echo "[reset-db] WARNING: this destroys all data in the 'public' schema."
read -r -p "Type 'yes' to continue: " ans
if [[ "$ans" != "yes" ]]; then
  echo "[reset-db] Aborted."
  exit 0
fi

echo "[reset-db] Dropping public schema..."
docker compose exec -T db psql -U "${POSTGRES_USER:-erp_admin}" -d "${POSTGRES_DB:-erp_db}" \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO ${POSTGRES_USER:-erp_admin}; GRANT ALL ON SCHEMA public TO public;"

echo "[reset-db] Re-running migrations via backend restart..."
docker compose restart backend

echo "[reset-db] Waiting for backend to be healthy..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/health/live >/dev/null 2>&1; then
    echo "[reset-db] Done."
    exit 0
  fi
  sleep 2
done
echo "[reset-db] Backend did not become healthy. Check 'docker compose logs backend'." >&2
exit 1