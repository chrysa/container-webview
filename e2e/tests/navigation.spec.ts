import { test, expect } from "../fixtures/app";

test.describe("Navigation & shell", () => {
  test("sidebar links navigate between top-level areas", async ({
    mockedPage,
  }) => {
    await mockedPage.goto("/projects", { waitUntil: "networkidle" });
    await mockedPage.getByRole("link", { name: /alertes/i }).click();
    await expect(mockedPage).toHaveURL(/alerts/);
    await mockedPage
      .getByRole("link", { name: /projets/i })
      .first()
      .click();
    await expect(mockedPage).toHaveURL(/projects$/);
  });

  test("project-scoped sidebar links appear inside a project", async ({
    mockedPage,
  }) => {
    await mockedPage.goto("/projects/webapp/topology", {
      waitUntil: "networkidle",
    });
    // The "Projet actif" section exposes the per-project nav links.
    await expect(
      mockedPage.getByRole("link", { name: /services/i }),
    ).toBeVisible({ timeout: 10000 });
    await mockedPage.getByRole("link", { name: /métriques/i }).click();
    await expect(mockedPage).toHaveURL(/projects\/webapp\/metrics/);
  });

  test("breadcrumb reflects the current project page", async ({
    mockedPage,
  }) => {
    await mockedPage.goto("/projects/webapp/services", {
      waitUntil: "networkidle",
    });
    const breadcrumb = mockedPage.getByRole("navigation", {
      name: /fil d'ariane/i,
    });
    await expect(breadcrumb).toBeVisible({ timeout: 10000 });
    await expect(
      breadcrumb.getByRole("link", { name: /projets/i }),
    ).toBeVisible();
    // Clicking the Projets crumb returns to the list.
    await breadcrumb.getByRole("link", { name: /projets/i }).click();
    await expect(mockedPage).toHaveURL(/projects$/);
  });

  test("theme toggle switches and persists across reload", async ({
    mockedPage,
  }) => {
    await mockedPage.goto("/projects", { waitUntil: "networkidle" });
    // Theme is applied via the `dark` class on <html> (default: dark).
    const initial = await mockedPage.evaluate(() =>
      document.documentElement.classList.contains("dark"),
    );
    await mockedPage.getByRole("button", { name: /changer le thème/i }).click();
    const toggled = await mockedPage.evaluate(() =>
      document.documentElement.classList.contains("dark"),
    );
    expect(toggled).not.toBe(initial);
    // Persisted to localStorage (key: theme) and survives a reload.
    await mockedPage.reload({ waitUntil: "networkidle" });
    const afterReload = await mockedPage.evaluate(() =>
      document.documentElement.classList.contains("dark"),
    );
    expect(afterReload).toBe(toggled);
  });

  test("sidebar can be collapsed", async ({ mockedPage }) => {
    await mockedPage.goto("/projects", { waitUntil: "networkidle" });
    // While expanded, the "Navigation" logo label is visible.
    await expect(mockedPage.getByText("Navigation")).toBeVisible({
      timeout: 10000,
    });
    // The collapse toggle is the first button in the sidebar's top bar.
    await mockedPage.locator("aside button").first().click();
    await expect(mockedPage.getByText("Navigation")).toHaveCount(0);
  });
});
