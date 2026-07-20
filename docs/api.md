# API Reference

> Status: **Phase 0**. Interactive docs available at `/docs` (Swagger) and
> `/redoc` when running in non-production mode.

## 1. Base URL

| Environment | Base URL |
|-------------|----------|
| Local dev (compose) | `http://localhost:8000` |
| Prod (Nginx) | `https://<your-domain>/api` (reverse-proxied) |

## 2. Phase 0 endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/` | App name + status + links | None |
| `GET` | `/health/live` | Liveness probe (no I/O) | None |
| `GET` | `/health/ready` | Readiness probe (checks DB) | None |
| `GET` | `/health` | Full health report | None |
| `GET` | `/openapi.json` | OpenAPI schema (non-prod only) | None |

## 3. Roadmap

| Phase | Endpoint group |
|-------|----------------|
| 1 | `/api/v1/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/password-reset` |
| 1 | `/api/v1/me`, `/me/permissions`, `/me/sessions` |
| 1 | `/api/v1/users` CRUD |
| 2 | `/api/v1/roles` CRUD, `/api/v1/permissions`, role/permission assignment |
| 3 | `/api/v1/employees` CRUD, `/api/v1/departments` |
| 4 | `/api/v1/audit-logs` (read-only, paginated, filtered) |
| 5 | (frontend-only) dashboard, sidebar |

## 4. Conventions

- **Auth**: `Authorization: Bearer <access_token>` for protected endpoints.
  Refresh token is an httpOnly, Secure, SameSite=Strict cookie.
- **Errors**: uniform JSON body `{ "code": "...", "message": "..." }` with the
  appropriate HTTP status. Client messages are generic; details are logged
  server-side only.
- **Pagination**: `?page=1&size=20` for small catalogues; `?cursor=...&size=50`
  for the audit log (keyset over `created_at`).
- **IDs**: all resource IDs are UUIDs.
- **Versioning**: API is under `/api/v1`. Breaking changes bump the version.

## 5. Security headers (Phase 0, already applied)

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Content-Security-Policy`: conservative default; tightened per environment.
- `Strict-Transport-Security` (production only)

## 6. CORS

Allowed origins come from `CORS_ORIGINS` (comma-separated). Credentials are
allowed. `*` is **never** used with credentials.