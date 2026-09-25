# SECURITY — container-webview

> Generated 2026-09-25 by a documentation pass (no code changes). Findings are for the owner to
> triage; nothing here was fixed. No live secret was copied. Severity uses HIGH/MEDIUM/LOW/INFO.

## Secret scan
- FACT — No live secrets found in tracked files. `.env.example` ships only placeholders
  (`SECRET_KEY=change-me-in-production`, empty LDAP fields, empty `ADMIN_PASSWORD_HASH`).
- FACT — `.secrets.baseline` (detect-secrets) and `.gitleaks.toml` are present; the gitleaks config
  allowlists only the baseline files (which store hashed fingerprints, not live secrets).
- INFO — Real `.env` is git-ignored; hooks block env edits (`.claude/hooks/check-no-env-files.cjs`,
  `hookify.block-env-edits`).

## Positive controls observed (FACT)
- Production secure-config guard in `api/app/config.py`: rejects the default/empty `SECRET_KEY` and
  refuses plaintext `ADMIN_PASSWORD` in production unless LDAP is configured (bcrypt hash required).
- `api/app/security.py`: bcrypt password verification, constant-time comparison
  (`hmac.compare_digest`) for username and secret, JWT validation with `sub` claim check, LDAP errors
  logged at debug (no credential leakage in the seen excerpts).
- Docker socket and projects directory mounted read-only (`:ro`) in `docker-compose.yml`.
- Security scanning wired into pre-commit + CI (`.pre-commit-config.yaml`, gitleaks, detect-secrets).

## Findings for owner review (NOT fixed)

### S1 — Docker socket exposure — MEDIUM
- Evidence: `docker-compose.yml` mounts `/var/run/docker.sock:ro` into the API container.
- Note: `:ro` prevents writing the socket file but does NOT restrict Engine command scope — an
  actor with API access to that container can control the Docker daemon (start/stop/inspect any
  container, and socket access is a well-known host-takeover vector). This is inherent to the
  product's purpose; document the trust boundary and ensure the API is never exposed unauthenticated.
- Recommendation (owner): keep the API behind auth + reverse proxy; consider a socket-proxy
  (least-privilege API filtering) for any non-local deployment.

### S2 — Default/dev credentials shipped as defaults — LOW (dev), guarded in prod
- Evidence: README states default credentials `admin`/`admin` if unconfigured; `.env.example`
  plaintext `ADMIN_PASSWORD` fallback.
- Note: production guard (config.py) blocks these; risk is limited to misconfigured non-prod
  deployments run with `ENVIRONMENT=development` on an exposed host.

### S3 — CORS dev origins hardcoded as defaults — LOW / INFO
- Evidence: `config.py` default `cors_origins` includes `http://localhost:3000` and `:5173`
  (annotated, overridable via `CORS_ORIGINS`).
- Note: acceptable as dev defaults; confirm they are overridden in production.

### S4 — `VITE_API_URL` baked at build time — INFO
- Evidence: `.env.example`, `README.md`. Rebuild required to change API URL; ensure production images
  are built with the correct value or fronted by a proxy.

## Not assessed
- Dynamic testing (DAST), dependency CVE audit, and auth flow runtime testing were out of scope for
  this documentation pass. `dependabot.yml` is present for dependency updates.
