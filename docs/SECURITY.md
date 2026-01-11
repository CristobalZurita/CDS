# Security Checklist & How to prepare environment for production

This document summarizes the immediate security hardening steps applied and how to prepare the environment for production.

## What was changed
- The backend now requires critical secrets to be provided via environment variables when `ENVIRONMENT` is set to `production` (or `prod`). These are: `SECRET_KEY`, `JWT_SECRET` (and optionally `JWT_REFRESH_SECRET`). The application will raise an error on startup if they are missing.
- CORS configuration is now parsed from `ALLOWED_ORIGINS` env var (comma-separated). If not set, development defaults are used.
- HTTPS enforcement (`HTTPSRedirectMiddleware`) and common security headers (HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy) are applied automatically when `ENVIRONMENT=production`.
- A helper script `scripts/generate_webfonts.sh` was added (related to brand assets). See README for running scripts.

## Required environment variables (example `.env`)

```dotenv
# Always fill these before running in production
ENVIRONMENT=production
SECRET_KEY=your-long-random-secret
JWT_SECRET=your-jwt-secret
JWT_REFRESH_SECRET=your-refresh-secret
ALLOWED_ORIGINS=https://cirujanodesintetizadores.cl,https://www.cirujanodesintetizadores.cl
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cirujano_db
```

## How to test locally
1. Copy `.env.example` to `.env` and set your values.
2. Run the app in development: `ENVIRONMENT=development .venv/bin/uvicorn backend.app.main:app --reload --port 8000`.

## Notes & Next steps
- Verify that secrets are stored in your hosting environment securely (cPanel, platform variables, or secrets manager).
- Consider using a secret scanner in CI to prevent accidental commits of secrets.
 - A basic GitHub Action `secret-scan` has been added to fail on obvious matches like `SECRET_KEY` or `JWT_SECRET` in committed files. This is a lightweight check and can be extended with tools like `detect-secrets` or `trufflehog` later.
 - A unit test `backend/tests/test_config.py` was added to assert that the application fails to start in `production` when critical secrets are missing.
- Add rate limiting and file upload validation (next tasks).
 - Implemented a rate limiting plan: the app supports a Redis-backed rate limiter (via `slowapi`). Add `RATE_LIMIT_STORAGE_URI` to your `.env` to enable Redis storage (recommended). A basic uploads validator was added to validate image size and format; endpoints reject invalid files.
 - Files added: `backend/app/core/ratelimit.py`, `backend/app/routers/uploads.py`, `backend/app/utils/uploads.py`. Unit tests added under `backend/tests/test_ratelimit.py` and `backend/tests/test_uploads.py`.
 - Implemented audit logging & structured JSON logs: the app now logs audit events to `audit_logs` table and emits structured JSON logs via `python-json-logger`. File: `backend/app/models/audit.py`, `backend/app/services/logging_service.py`, `backend/app/core/logging_config.py`. Unit test: `backend/tests/test_audit_logging.py`.
 - Use the helper script `scripts/check_env.py` to validate your environment before starting in production: `python scripts/check_env.py --env-file .env --strict`.

If you want, I can prepare a GitHub Action job that fails if `SECRET_KEY` or `JWT_SECRET` are accidentally found in committed files.
