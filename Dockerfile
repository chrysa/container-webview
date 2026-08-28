# syntax=docker/dockerfile:1.4

# ─────────────── Stage 1 : dépendances ───────────────

COPY ./code/package.json /app/package.json
COPY ./code/package-lock.json /app/package-lock.json

WORKDIR /app

COPY code/package.json ./

# The node_modules named volume is seeded from this layer; chown it to the host
# UID (default 1000) so bind-mount dev/test containers running as
# "${UID:-1000}:${GID:-1000}" can write Vite/Vitest caches into node_modules/.
RUN npm install --legacy-peer-deps \
    && chown -R 1000:1000 /app/node_modules

FROM package AS build

ARG VITE_API_URL=

ENV VITE_API_URL=${VITE_API_URL}

COPY code/ .

RUN npm run build

FROM node:lts-slim as production

ENV PORT=80 \
    NODE_ENV=production \
    PATH=$PATH:/app/node_modules/:/app/node_modules/.bin

USER appuser

RUN set -ex \
    && set -ex pipefail \
    && apt-get update \
    && apt-get install -qq -o=Dpkg::Use-Pty=0 --no-install-recommends -y xsel \
    && apt-get purge -y --auto-remove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*set -ex \
    && npm install -g serve@14.2.4 --silent

CMD [ "serve", "-s", "/app/build" ]
VOLUME ["/configs"]
