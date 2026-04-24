# syntax=docker/dockerfile:1.4

# ── base: system deps + production requirements ──────────────────────────────
FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    libldap2-dev libsasl2-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

# ── deps: install dev/test extras on top of base ─────────────────────────────
FROM base AS deps

RUN pip install --no-cache-dir -e ".[dev]"

# ── test: run the test suite ─────────────────────────────────────────────────
FROM deps AS test

COPY . .

CMD ["python", "-m", "pytest", "--tb=short", "-q"]

# ── production ────────────────────────────────────────────────────────────────
FROM base AS production

COPY . .

RUN addgroup --system app && adduser --system --ingroup app app \
    && chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/api || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
