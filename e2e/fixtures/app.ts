import { test as base, Page } from "@playwright/test";
import { mockBackend, seedSession } from "./mocks";

const ADMIN_USERNAME = process.env.ADMIN_USERNAME ?? "admin";
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD ?? "admin";

export class LoginPage {
  constructor(private readonly page: Page) {}

  async goto() {
    await this.page.goto("/login");
  }

  async login(username: string, password: string) {
    await this.page.getByLabel(/username|utilisateur/i).fill(username);
    await this.page.getByLabel(/password|mot de passe/i).fill(password);
    await this.page
      .getByRole("button", { name: /login|connexion|connecter/i })
      .click();
  }

  async loginAsAdmin() {
    await this.login(ADMIN_USERNAME, ADMIN_PASSWORD);
  }
}

export class ProjectsPage {
  constructor(private readonly page: Page) {}

  async goto() {
    await this.page.goto("/projects");
  }

  async getProjectCards() {
    return this.page.locator('[data-testid="project-card"]').all();
  }
}

type AppFixtures = {
  loginPage: LoginPage;
  projectsPage: ProjectsPage;
  authenticatedPage: Page;
  /**
   * A page with the deterministic backend already mocked AND a valid session
   * seeded in localStorage. Use this for every journey that exercises the
   * authenticated area without depending on a live API. Override the mocks
   * per-test with `mockBackend(page, { ... })` *before* navigating.
   */
  mockedPage: Page;
};

export const test = base.extend<AppFixtures>({
  loginPage: async ({ page }, use) => {
    // Mock the backend so the login journey is deterministic and needs no API.
    await mockBackend(page);
    await use(new LoginPage(page));
  },
  projectsPage: async ({ page }, use) => {
    await use(new ProjectsPage(page));
  },
  authenticatedPage: async ({ page }, use) => {
    // Deterministic backend (mocked) + real UI login flow to obtain a token.
    await mockBackend(page);
    const login = new LoginPage(page);
    await login.goto();
    await login.loginAsAdmin();
    // Wait for SPA navigation to authenticated area
    await page.waitForURL(/projects|dashboard/, { timeout: 10000 });
    // Layout (header/sidebar) renders synchronously once RequireAuth passes.
    // The Suspense in Layout only wraps the inner page content, not the shell.
    await page.waitForSelector("header", { state: "visible", timeout: 15000 });
    await use(page);
  },
  mockedPage: async ({ page }, use) => {
    await mockBackend(page);
    await seedSession(page);
    await use(page);
  },
});

export { expect } from "@playwright/test";
