# syntax=docker/dockerfile:1.4

FROM node:lts-slim AS package



COPY ./code/package.json /app/package.json
COPY ./code/package-lock.json /app/package-lock.json

WORKDIR /app

RUN npm ci

COPY ./code /app



FROM package AS build

ENV PATH=$PATH:/app/node_modules

RUN npm run build




FROM node:lts-slim as production

ENV PORT=80 NODE_ENV=production PATH=$PATH:/app/node_modules/:/app/node_modules/.bin

COPY --from=build /app/build /app/build
COPY --from=build /app/package*.json /app/

RUN set -ex \
    && set -ex pipefail \
    && apt-get update \
    && apt-get install -qq -o=Dpkg::Use-Pty=0 --no-install-recommends -y xsel \
    && apt-get purge -y --auto-remove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN set -ex \
  && npm install -g serve --silent

CMD [ "serve", "-s", "/app/build" ]

VOLUME ["/configs"]
