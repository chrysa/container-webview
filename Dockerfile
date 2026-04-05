# syntax=docker/dockerfile:1.4

# ─────────────── Stage 1 : dépendances ───────────────
FROM node:22-slim AS deps

WORKDIR /app
COPY code/package.json ./
RUN npm install --legacy-peer-deps

# ─────────────── Stage 2 : build Vite ───────────────
FROM deps AS build

# URL de l'API (baked at build-time via docker-compose build.args)
ARG VITE_API_URL=
ENV VITE_API_URL=${VITE_API_URL}

COPY code/ .
RUN npm run build

# ─────────────── Stage 3 : production (serve) ───────
FROM node:22-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g serve@14 \
    && groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=build /app/dist /app/dist

WORKDIR /app
USER appuser
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1
CMD ["serve", "-s", "dist", "-l", "3000"]
