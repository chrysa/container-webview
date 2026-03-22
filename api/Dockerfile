# syntax=docker/dockerfile:1.4
# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — system dependencies + pip install
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

# Build-time deps for python-ldap
RUN apt-get update && apt-get install -y --no-install-recommends \
    libldap2-dev libsasl2-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — development (uvicorn --reload)
# ─────────────────────────────────────────────────────────────────────────────
FROM base AS dev

COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ─────────────────────────────────────────────────────────────────────────────
# Stage 3 — test (run pytest with coverage)
# ─────────────────────────────────────────────────────────────────────────────
FROM base AS test

RUN pip install --no-cache-dir ".[dev]"
COPY . .
CMD ["python", "-m", "pytest", "--cov=app", "--cov-report=term-missing", "--cov-report=xml"]

# ─────────────────────────────────────────────────────────────────────────────
# Stage 4 — production (no reload, no dev tools)
# ─────────────────────────────────────────────────────────────────────────────
FROM base AS production

COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
