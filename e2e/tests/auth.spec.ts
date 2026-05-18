import { test, expect } from '../fixtures/app';

const ADMIN_USERNAME = process.env.ADMIN_USERNAME ?? 'admin';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD ?? 'admin';

test.describe('Authentication', () => {
  test('login page is accessible', async ({ loginPage, page }) => {
    await loginPage.goto();
    await expect(page).toHaveURL(/login/);
    await expect(page.getByRole('button', { name: /login|connexion|connecter/i })).toBeVisible();
  });

  test('successful login redirects to projects', async ({ loginPage, page }) => {
    await loginPage.goto();
    await loginPage.loginAsAdmin();
    await expect(page).toHaveURL(/projects|dashboard/);
  });

  test('failed login shows error message', async ({ loginPage, page }) => {
    await loginPage.goto();
    await loginPage.login('wrong', 'credentials');
    await expect(page.getByRole('alert')).toBeVisible();
    await expect(page).toHaveURL(/login/);
  });

  test('unauthenticated access to /projects redirects to login', async ({ page }) => {
    await page.goto('/projects');
    await expect(page).toHaveURL(/login/);
  });

  test('logout clears session and redirects to login', async ({ authenticatedPage }) => {
    await expect(authenticatedPage).toHaveURL(/projects/, { timeout: 5000 });
    const logoutButton = authenticatedPage.locator('button[aria-label="Se déconnecter"]');
    await expect(logoutButton).toBeVisible({ timeout: 10000 });
    await logoutButton.click();
    await expect(authenticatedPage).toHaveURL(/login/);
  });
});
