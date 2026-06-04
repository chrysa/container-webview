import { test, expect } from "../fixtures/app";
import { mockBackend } from "../fixtures/mocks";

test.describe("Metrics page", () => {
  test("renders the charts and summary table", async ({ mockedPage }) => {
    await mockedPage.goto("/projects/webapp/metrics", {
      waitUntil: "networkidle",
    });
    await expect(
      mockedPage.getByRole("heading", { name: /métriques/i }),
    ).toBeVisible();
    await expect(mockedPage.getByText("CPU (%)")).toBeVisible({
      timeout: 10000,
    });
    await expect(mockedPage.getByText(/mémoire/i)).toBeVisible();
    await expect(mockedPage.getByText("Résumé")).toBeVisible();
    // Summary table rows reflect the mocked services.
    await expect(mockedPage.getByRole("cell", { name: "api" })).toBeVisible();
    await expect(mockedPage.getByRole("cell", { name: "db" })).toBeVisible();
  });

  test("shows the no-data state when metrics are empty", async ({
    mockedPage,
  }) => {
    await mockBackend(mockedPage, { metrics: [] });
    await mockedPage.goto("/projects/webapp/metrics", {
      waitUntil: "networkidle",
    });
    await expect(mockedPage.getByText(/aucune donnée disponible/i)).toBeVisible(
      { timeout: 10000 },
    );
  });

  test("shows the error state when the metrics API fails", async ({
    mockedPage,
  }) => {
    await mockBackend(mockedPage, { errors: { metrics: 503 } });
    await mockedPage.goto("/projects/webapp/metrics", {
      waitUntil: "networkidle",
    });
    await expect(
      mockedPage.getByText(/erreur lors du chargement des métriques/i),
    ).toBeVisible({ timeout: 10000 });
  });
});
