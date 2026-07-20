# ERP System — Boilerplate (Phase 0 / Cimientos)

Modular ERP boilerplate built with **FastAPI + SvelteKit 5 + PostgreSQL 16**.
This repository currently contains **Phase 0** only: the production-grade
foundation (monorepo, Docker, async DB layer, migrations, security headers,
health endpoints, no-FOUC theme switch, test harness, docs scaffolding).

Modules with real functionality (Auth, Users, Employees, RBAC, Audit log,
Dashboard, Sidebar, Dark/Light) are introduced in **Phases 1–6**. See
`docs/architecture.md` and the master prompt's phase plan.

---

## Stack

| Layer       | Technology |
|-------------|------------|
| Backend     | Python 3.12, FastAPI (async), SQLAlchemy 2.0 async, Alembic, Pydantic v2, asyncpg, structlog, Argon2, PyJWT |
| Frontend    | SvelteKit (Svelte 5 runes), TypeScript strict, TailwindCSS, Vitest |
| Database    | PostgreSQL 16 |
| Infra       | Docker, Docker Compose v2, Nginx (prod profile), Redis (optional profile) |
| Tooling     | `uv` (backend deps), `pnpm` (frontend deps), `make` |

---

## One-command setup

Requirements: **Docker** (with Compose v2) and **Git**. Nothing else.

```bash
git clone <repo-url> erp-system && cd erp-system
make setup          # or: ./scripts/setup.sh
```

This will:

1. Copy `.env.example` → `.env` (with a warning to review secrets).
2. Build and start `db`, `backend`, `frontend` containers with healthchecks.
3. Wait for Postgres to be healthy.
4. Run Alembic migrations automatically (backend startup hook).
5. Print the final URLs and credentials.

When it finishes you should have:

| Service           | URL |
|-------------------|-----|
| Frontend (Svelte) | http://localhost:5173 |
| Backend (FastAPI) | http://localhost:8000 |
| Swagger docs      | http://localhost:8000/docs |
| ReDoc docs        | http://localhost:8000/redoc |
| Postgres          | localhost:5432 |

### Seed credentials (Phase 1)

After `make seed`, a SUPER_ADMIN user is created with:

| Field | Value |
|-------|-------|
| Username | `superadmin` |
| Email | `superadmin@erp-system.dev` |
| Password | `Cambio!Seguro2026` |

> **Rotate this password immediately in any non-local environment.**
> 25 additional demo users are seeded with password `Demo!Usuario2026`
> for pagination/search testing.

Login at http://localhost:5173/login — the frontend redirects there
automatically when no session is present.

---

## Common commands

```bash
make up              # start dev stack
make down            # stop dev stack
make logs            # tail logs
make ps              # container status
make test            # all tests (backend + frontend)
make test-backend    # backend tests with coverage
make test-frontend   # frontend vitest
make reset-db        # destructive: drop & migrate the DB
make clean           # remove containers + volumes + images
make prod-up         # build & start the hardened prod profile (with nginx)
```

---

## Project structure

```
erp-system/
├── compose.yaml              # dev stack
├── compose.prod.yaml         # hardened prod overlay (+ nginx)
├── Makefile
├── .env.example
├── scripts/                  # setup.sh, seed.sh, reset-db.sh, run-tests.sh
├── docs/                     # architecture, db schema, rbac, api, design-system
├── backend/                  # FastAPI (Clean / Hexagonal)
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic/              # versioned migrations (async)
│   ├── app/
│   │   ├── main.py
│   │   ├── core/             # config, security, logging, exceptions, deps
│   │   ├── domain/           # entities + ports (no framework deps)
│   │   ├── application/      # use cases
│   │   ├── infrastructure/   # db engine/session, ORM models, repositories
│   │   ├── api/v1/           # routers + Pydantic DTOs
│   │   └── middlewares/      # security headers, (audit, rate limit: phase 1+)
│   ├── seed/                 # seed scripts
│   └── tests/                # unit / integration / e2e
└── frontend/                 # SvelteKit 5 (feature-sliced)
    ├── Dockerfile
    ├── package.json
    ├── src/
    │   ├── app.html          # no-FOUC theme script
    │   ├── routes/           # thin route files only
    │   └── lib/              # api, components/ui, features, stores, types, utils
    └── tests/
```

Full layering rules in `docs/architecture.md`.

---

## Security posture (Phase 0)

Already in place:

- Argon2id-ready password hashing interface (wired in Phase 1).
- Security headers middleware: `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Strict-Transport-Security` (prod), a conservative CSP.
- CORS restricted to explicit origins (never `*` with credentials).
- Debug mode off in prod profile; generic error responses to clients.
- `.env`-based secrets; no hardcoded credentials in source.
- Health endpoints separated: `/health/live` (process) and `/health/ready`
  (DB reachable), useful for orchestrators.

Coming in **Phase 1+**: JWT (access + rotating refresh), rate limiting,
progressive lockout, refresh-token reuse detection, RBAC engine, audit log.

See `docs/architecture.md` for the OWASP mapping planned per phase.

---

## Testing

- **Backend**: `pytest` + `pytest-asyncio` + `httpx.AsyncClient` + `pytest-cov`.
  Unit (in-memory fakes), integration (real Postgres via `test` profile),
  e2e (full FastAPI app). Target coverage ≥ 80% on `domain/` and `application/`.
- **Frontend**: `Vitest` + `@testing-library/svelte` (Phase 0: harness +
  smoke tests). Playwright arrives with Phase 5/6.

Run everything:

```bash
make test
```

---

## Roadmap (master prompt phases)

| Phase | Scope | Status |
|-------|-------|--------|
| 0 | Cimientos (this repo) | done |
| 1a | Auth core (login/JWT/refresh rotation/logout/me + seed + frontend login) | done |
| 1b | Users CRUD (list/create/update/deactivate/force-reset/unlock + business rules) | done |
| 2 | RBAC (roles/permissions engine) | next |
| 3 | Employees + departments | pending |
| 4 | Audit log (append-only) + UI | pending |
| 5 | App shell (sidebar, dashboard, theme polish) | pending |
| 6 | Hardening (OWASP sweep, perf, a11y, coverage, docs) | pending |

---

## License

Proprietary — boilerplate for internal use.