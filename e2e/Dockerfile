# syntax=docker/dockerfile:1.4

# Image tag MUST match the @playwright/test version pinned in code/package-lock.json
# (currently 1.60.0). A drifted tag makes Playwright refuse to launch its browser.
FROM mcr.microsoft.com/playwright:v1.60.0-jammy AS e2e

WORKDIR /app

COPY code/package.json code/package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY playwright.config.ts ./
COPY e2e/ ./e2e/
COPY code/src/ ./src/

CMD ["npx", "playwright", "test", "--config=playwright.config.ts"]
