import { test, expect } from "../fixtures/app";
import { mockBackend } from "../fixtures/mocks";

test.describe("Alerts page", () => {
  test("renders the alert list with level counters", async ({ mockedPage }) => {
    await mockedPage.goto("/alerts", { waitUntil: "networkidle" });
    await expect(
      mockedPage.getByRole("heading", { name: /alertes/i }),
    ).toBeVisible();
    // One alert of each level in the fixture.
    await expect(
      mockedPage.getByText(/container exited unexpectedly/i),
    ).toBeVisible({
      timeout: 10000,
    });
    await expect(mockedPage.getByText(/high memory usage/i)).toBeVisible();
    await expect(mockedPage.getByText(/scrape target added/i)).toBeVisible();
    // Counter summary reflects 1 critical.
    await expect(mockedPage.getByText(/critique/i).first()).toBeVisible();
  });

  test("shows the empty state when there are no alerts", async ({
    mockedPage,
  }) => {
    await mockBackend(mockedPage, { alerts: [] });
    await mockedPage.goto("/alerts", { waitUntil: "networkidle" });
    await expect(mockedPage.getByText(/aucune alerte active/i)).toBeVisible({
      timeout: 10000,
    });
  });

  test("shows the error state when the alerts API fails", async ({
    mockedPage,
  }) => {
    await mockBackend(mockedPage, { errors: { alerts: 500 } });
    await mockedPage.goto("/alerts", { waitUntil: "networkidle" });
    await expect(
      mockedPage.getByText(/erreur lors du chargement des alertes/i),
    ).toBeVisible({ timeout: 10000 });
  });
});
