# syntax=docker/dockerfile:1.4

FROM mcr.microsoft.com/playwright:v1.43.0-jammy AS e2e

WORKDIR /app

COPY code/package*.json ./
RUN npm install --legacy-peer-deps

COPY playwright.config.ts ./
COPY e2e/ ./e2e/
COPY code/src/ ./src/

CMD ["npx", "playwright", "test", "--config=playwright.config.ts"]
