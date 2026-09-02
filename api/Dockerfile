# syntax=docker/dockerfile:1.7

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — base : shared OS layer, runtime libs, non-root user
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# curl for HEALTHCHECK; libldap2 + libsasl2-2 are the runtime shared libs
# python-ldap links against (dev headers live in the builder stage only).

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl libldap2 libsasl2-2 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r -g 10001 appuser \
    && useradd -r -u 10001 -g appuser appuser

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — builder : installs runtime dependencies only
# ─────────────────────────────────────────────────────────────────────────────

FROM base AS builder

# Build-time deps for python-ldap (compiled from source)

RUN apt-get update \
    && apt-get install -y --no-install-recommends libldap2-dev libsasl2-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# ─────────────────────────────────────────────────────────────────────────────
# Stage 3 — production : minimal image (no build tools, non-root)
# ─────────────────────────────────────────────────────────────────────────────

FROM base AS production

COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app/ app/

RUN chown -R appuser:appuser /app

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["curl", "-f", "http://localhost:8000/health"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# ─────────────────────────────────────────────────────────────────────────────
# Stage 4 — dev : extends builder, hot-reload server
# ─────────────────────────────────────────────────────────────────────────────

FROM builder AS dev

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ─────────────────────────────────────────────────────────────────────────────
# Stage 5 — test : extends builder, runs pytest with coverage
# ─────────────────────────────────────────────────────────────────────────────

FROM builder AS test

RUN pip install --no-cache-dir ".[dev]"

COPY . .

CMD ["python", "-m", "pytest", "--cov=app", "--cov-report=term-missing", "--cov-report=xml"]
