# syntax=docker/dockerfile:1.7

# Frontend (React + Vite) — multi-stage: base -> builder -> production -> dev
# The app source lives in ./code; the build context is the repo root.
# Stage 1: OS base (shared parent) — pinned Node

FROM node:22-slim AS base

ENV NODE_ENV=production

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser \
    && useradd -r -u 10001 -g appuser appuser

# Stage 2: builder — install deps and compile the static bundle

FROM base AS builder

ENV NODE_ENV=development

COPY code/package.json code/package-lock.json ./

RUN npm ci --legacy-peer-deps

COPY code/ ./

ARG VITE_API_URL=

ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Stage 3: production — minimal static server, non-root

FROM base AS production

RUN npm install -g serve@14.2.4

COPY --from=builder /app/dist ./dist

USER 10001

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["curl", "-f", "http://localhost:3000/"]

CMD ["serve", "-s", "dist", "-l", "3000"]

# Stage 4: dev — Vite dev server with hot reload (extends builder)

FROM builder AS dev

ENV NODE_ENV=development

EXPOSE 3000

CMD ["npm", "run", "dev"]
