import { test, expect } from "../fixtures/app";
import { mockBackend } from "../fixtures/mocks";

test.describe("Services page", () => {
  test("renders a table row per service", async ({ mockedPage }) => {
    await mockedPage.goto("/projects/webapp/services", {
      waitUntil: "networkidle",
    });
    await expect(
      mockedPage.getByRole("heading", { name: /services/i }),
    ).toBeVisible();
    await expect(mockedPage.getByText("api", { exact: true })).toBeVisible();
    await expect(mockedPage.getByText("db", { exact: true })).toBeVisible();
    await expect(mockedPage.getByText("myorg/api:1.2.3")).toBeVisible();
  });

  test("expanding a row reveals volumes, env and dependencies", async ({
    mockedPage,
  }) => {
    await mockedPage.goto("/projects/webapp/services", {
      waitUntil: "networkidle",
    });
    const apiRow = mockedPage.locator("tr").filter({ hasText: "myorg/api" });
    // The expand toggle is the last button in the row.
    await apiRow.getByRole("button").last().click();
    await expect(mockedPage.getByText(/volumes/i)).toBeVisible();
    await expect(mockedPage.getByText(/dépend de/i)).toBeVisible();
    await expect(
      mockedPage.getByText(/variables d'environnement/i),
    ).toBeVisible();
  });

  test("sensitive env values are masked by default and reveal on toggle", async ({
    mockedPage,
  }) => {
    await mockedPage.goto("/projects/webapp/services", {
      waitUntil: "networkidle",
    });
    const apiRow = mockedPage.locator("tr").filter({ hasText: "myorg/api" });
    await apiRow.getByRole("button").last().click();

    const envBlock = mockedPage.locator("pre").first();
    // Masked: secret value hidden behind bullets, non-sensitive value visible.
    await expect(envBlock).toContainText("••••••••");
    await expect(envBlock).not.toContainText("fake-masked-pw");
    await expect(envBlock).toContainText("NODE_ENV=production");

    // Reveal toggle (eye button next to the env header).
    await mockedPage
      .getByRole("button", { name: /afficher les valeurs sensibles/i })
      .click();
    await expect(envBlock).toContainText("fake-masked-pw");
    await expect(envBlock).toContainText("fake-masked-tok");
  });

  test("a lifecycle action shows a success toast", async ({ mockedPage }) => {
    await mockedPage.goto("/projects/webapp/services", {
      waitUntil: "networkidle",
    });
    const apiRow = mockedPage.locator("tr").filter({ hasText: "myorg/api" });
    // "Démarrer" exactly — avoids matching "Redémarrer".
    await apiRow.getByRole("button", { name: "Démarrer", exact: true }).click();
    await expect(mockedPage.getByText(/start de api effectué/i)).toBeVisible({
      timeout: 10000,
    });
  });

  test("a failing lifecycle action shows an error toast", async ({
    mockedPage,
  }) => {
    await mockBackend(mockedPage, { actionFails: true });
    await mockedPage.goto("/projects/webapp/services", {
      waitUntil: "networkidle",
    });
    const apiRow = mockedPage.locator("tr").filter({ hasText: "myorg/api" });
    await apiRow.getByRole("button", { name: /arrêter/i }).click();
    await expect(mockedPage.getByText(/échec stop de api/i)).toBeVisible({
      timeout: 10000,
    });
  });

  test("shows error state when the project API fails", async ({
    mockedPage,
  }) => {
    await mockBackend(mockedPage, { errors: { project: 500 } });
    await mockedPage.goto("/projects/webapp/services", {
      waitUntil: "networkidle",
    });
    await expect(
      mockedPage.getByText(/erreur lors du chargement des services/i),
    ).toBeVisible({ timeout: 10000 });
  });
});
