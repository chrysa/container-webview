import { test, expect } from "../fixtures/app";
import { mockBackend, PROJECT_EMPTY_SERVICES } from "../fixtures/mocks";

test.describe("Projects page", () => {
  test("displays projects list after login", async ({ mockedPage }) => {
    await mockedPage.goto("/projects", { waitUntil: "networkidle" });
    await expect(mockedPage).toHaveURL(/projects/);
    await expect(
      mockedPage.getByRole("heading", { name: /projects|projets/i }),
    ).toBeVisible({ timeout: 10000 });
  });

  test("renders one card per configured project with service counts", async ({
    mockedPage,
  }) => {
    await mockedPage.goto("/projects", { waitUntil: "networkidle" });
    const cards = mockedPage.locator('[data-testid="project-card"]');
    await expect(cards).toHaveCount(2);
    await expect(cards.filter({ hasText: "webapp" })).toBeVisible();
    await expect(cards.filter({ hasText: "monitoring" })).toBeVisible();
    // The webapp card lists its two services.
    const webapp = cards.filter({ hasText: "webapp" });
    await expect(webapp.getByText("2 services")).toBeVisible();
  });

  test("shows empty state when no projects configured", async ({
    mockedPage,
  }) => {
    await mockBackend(mockedPage, { projects: [] });
    await mockedPage.goto("/projects", { waitUntil: "networkidle" });
    await expect(mockedPage.locator('[data-testid="empty-state"]')).toBeVisible(
      { timeout: 10000 },
    );
    await expect(mockedPage.getByText(/aucun projet détecté/i)).toBeVisible();
  });

  test("shows error state when the projects API fails", async ({
    mockedPage,
  }) => {
    await mockBackend(mockedPage, { errors: { projects: 500 } });
    await mockedPage.goto("/projects", { waitUntil: "networkidle" });
    await expect(
      mockedPage.getByText(/impossible de charger les projets/i),
    ).toBeVisible({ timeout: 10000 });
  });

  test("navigates to project topology on link click", async ({
    mockedPage,
  }) => {
    await mockedPage.goto("/projects", { waitUntil: "networkidle" });
    const webapp = mockedPage
      .locator('[data-testid="project-card"]')
      .filter({ hasText: "webapp" });
    await webapp.getByRole("link", { name: /topologie/i }).click();
    await expect(mockedPage).toHaveURL(/projects\/webapp\/topology/);
  });
});

test.describe("404 page", () => {
  test("shows not-found page for unknown routes", async ({ mockedPage }) => {
    await mockedPage.goto("/this-route-does-not-exist", {
      waitUntil: "networkidle",
    });
    await expect(
      mockedPage.getByText(/not found|404|introuvable/i).first(),
    ).toBeVisible();
  });

  test("404 page links back to projects", async ({ mockedPage }) => {
    await mockedPage.goto("/nope", { waitUntil: "networkidle" });
    await mockedPage.getByRole("link", { name: /projets|projects/i }).click();
    await expect(mockedPage).toHaveURL(/projects/);
  });
});

test.describe("Project with no services", () => {
  test("topology shows the no-service empty state", async ({ mockedPage }) => {
    await mockBackend(mockedPage, {
      project: PROJECT_EMPTY_SERVICES,
      topology: { nodes: [], edges: [] },
    });
    await mockedPage.goto("/projects/stub/topology", {
      waitUntil: "networkidle",
    });
    await expect(mockedPage.getByText(/aucun service détecté/i)).toBeVisible({
      timeout: 10000,
    });
  });
});
