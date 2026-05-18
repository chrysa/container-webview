import { test as base, Page } from "@playwright/test";

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
};

export const test = base.extend<AppFixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  projectsPage: async ({ page }, use) => {
    await use(new ProjectsPage(page));
  },
  authenticatedPage: async ({ page }, use) => {
    // Perform real login to get a valid token from the API
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
});

export { expect } from "@playwright/test";
