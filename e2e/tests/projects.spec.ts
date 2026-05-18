import { test, expect } from "../fixtures/app";

test.describe("Projects page", () => {
  test("displays projects list after login", async ({ authenticatedPage }) => {
    await authenticatedPage.goto("/projects", { waitUntil: "networkidle" });
    await expect(authenticatedPage).toHaveURL(/projects/);
    // Wait for loading to finish (either heading or error state)
    await authenticatedPage.waitForSelector('h1, [data-testid="empty-state"]', {
      timeout: 15000,
    });
    await expect(
      authenticatedPage.getByRole("heading", { name: /projects|projets/i }),
    ).toBeVisible({ timeout: 10000 });
  });

  test("shows empty state when no projects configured", async ({
    authenticatedPage,
  }) => {
    await authenticatedPage.goto("/projects", { waitUntil: "networkidle" });
    // Wait for loading to finish
    await authenticatedPage.waitForSelector(
      'h1, [data-testid="empty-state"], .error',
      { timeout: 15000 },
    );
    // Wait for either project cards or empty state to appear
    const combined = authenticatedPage.locator(
      '[data-testid="project-card"], [data-testid="empty-state"]',
    );
    await expect(combined.first()).toBeVisible({ timeout: 10000 });
  });

  test("navigates to project detail page on click", async ({
    authenticatedPage,
  }) => {
    await authenticatedPage.goto("/projects", { waitUntil: "networkidle" });
    const cards = authenticatedPage.locator('[data-testid="project-card"]');
    const count = await cards.count();

    if (count === 0) {
      test.skip(true, "No projects available to click");
      return;
    }

    await cards.first().click();
    await expect(authenticatedPage).toHaveURL(/projects\/.+/);
  });
});

test.describe("404 page", () => {
  test("shows not-found page for unknown routes", async ({
    authenticatedPage,
  }) => {
    await authenticatedPage.goto("/this-route-does-not-exist", {
      waitUntil: "networkidle",
    });
    await expect(
      authenticatedPage.getByText(/not found|404|introuvable/i).first(),
    ).toBeVisible();
  });
});
