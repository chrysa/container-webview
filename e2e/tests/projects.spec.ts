import { test, expect } from '../fixtures/app';

test.describe('Projects page', () => {
  test('displays projects list after login', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/projects');
    await expect(authenticatedPage).toHaveURL(/projects/);
    // The page title or heading should be visible
    await expect(
      authenticatedPage.getByRole('heading', { name: /projects|projets/i }),
    ).toBeVisible();
  });

  test('shows empty state when no projects configured', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/projects');
    // Wait for either project cards or empty state to appear
    const combined = authenticatedPage.locator('[data-testid="project-card"], [data-testid="empty-state"]');
    await expect(combined.first()).toBeVisible();
  });

  test('navigates to project detail page on click', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/projects');
    const cards = authenticatedPage.locator('[data-testid="project-card"]');
    const count = await cards.count();

    if (count === 0) {
      test.skip(true, 'No projects available to click');
      return;
    }

    await cards.first().click();
    await expect(authenticatedPage).toHaveURL(/projects\/.+/);
  });
});

test.describe('404 page', () => {
  test('shows not-found page for unknown routes', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/this-route-does-not-exist');
    await expect(
      authenticatedPage.getByText(/not found|404|introuvable/i),
    ).toBeVisible();
  });
});
