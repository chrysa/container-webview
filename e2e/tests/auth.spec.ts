import { test, expect } from "../fixtures/app";
import { mockBackend } from "../fixtures/mocks";

test.describe("Authentication", () => {
  test("login page is accessible", async ({ loginPage, page }) => {
    await loginPage.goto();
    await expect(page).toHaveURL(/login/);
    await expect(
      page.getByRole("button", { name: /login|connexion|connecter/i }),
    ).toBeVisible();
  });

  test("successful login redirects to projects", async ({
    loginPage,
    page,
  }) => {
    await loginPage.goto();
    await loginPage.loginAsAdmin();
    await expect(page).toHaveURL(/projects|dashboard/);
  });

  test("failed login shows error message", async ({ loginPage, page }) => {
    // Override the default (success) mock so /auth/login returns 401.
    await mockBackend(page, { loginFails: true });
    await loginPage.goto();
    await loginPage.login("wrong", "credentials");
    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page).toHaveURL(/login/);
  });

  test("login button shows pending state while submitting", async ({
    loginPage,
    page,
  }) => {
    // Delay the auth response so the pending label is observable.
    await page.route("**/api/auth/login", async (route) => {
      await new Promise((r) => setTimeout(r, 600));
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "tok",
          token_type: "bearer",
          username: "admin",
        }),
      });
    });
    await loginPage.goto();
    await page.getByLabel(/username|utilisateur/i).fill("admin");
    await page.getByLabel(/password|mot de passe/i).fill("admin");
    const submit = page.getByRole("button", {
      name: /login|connexion|connecter/i,
    });
    await submit.click();
    // Button is disabled and shows the "Connexion…" label while pending.
    await expect(submit).toBeDisabled();
    await expect(page).toHaveURL(/projects/);
  });

  test("expired/invalid token on a protected query redirects to login", async ({
    page,
  }) => {
    // Seed a token so RequireAuth passes, then make the API reject with 401.
    await page.addInitScript(() => {
      window.localStorage.setItem("token", "expired-token");
      window.localStorage.setItem("username", "admin");
    });
    await page.route("**/api/projects", (route) =>
      route.fulfill({ status: 401, body: "{}" }),
    );
    await page.goto("/projects");
    // The Axios 401 interceptor clears the session and hard-redirects to /login.
    await expect(page).toHaveURL(/login/, { timeout: 10000 });
  });

  test("session persists across reload", async ({ mockedPage }) => {
    await mockedPage.goto("/projects", { waitUntil: "networkidle" });
    await expect(mockedPage).toHaveURL(/projects/);
    await mockedPage.reload({ waitUntil: "networkidle" });
    // Still authenticated — not bounced to /login.
    await expect(mockedPage).toHaveURL(/projects/);
    await expect(
      mockedPage.getByRole("heading", { name: /projets|projects/i }),
    ).toBeVisible();
  });

  test("unauthenticated access to /projects redirects to login", async ({
    page,
  }) => {
    await page.goto("/projects");
    await expect(page).toHaveURL(/login/);
  });

  test("logout clears session and redirects to login", async ({
    authenticatedPage,
  }) => {
    await expect(authenticatedPage).toHaveURL(/projects/, { timeout: 5000 });
    const logoutButton = authenticatedPage.locator(
      'button[aria-label="Se déconnecter"]',
    );
    await expect(logoutButton).toBeVisible({ timeout: 10000 });
    await logoutButton.click();
    await expect(authenticatedPage).toHaveURL(/login/);
  });
});
