import { test, expect } from "../fixtures/app";
import { mockBackend } from "../fixtures/mocks";

test.describe("Topology page", () => {
  test("renders the service graph with nodes", async ({ mockedPage }) => {
    await mockedPage.goto("/projects/webapp/topology", {
      waitUntil: "networkidle",
    });
    await expect(
      mockedPage.getByRole("heading", { name: /topologie/i }),
    ).toBeVisible();
    // ReactFlow renders a viewport pane; the graph node labels appear in it.
    await expect(mockedPage.locator(".react-flow").first()).toBeVisible({
      timeout: 10000,
    });
    await expect(
      mockedPage.getByText("api", { exact: true }).first(),
    ).toBeVisible();
    await expect(
      mockedPage.getByText("db", { exact: true }).first(),
    ).toBeVisible();
  });

  test("shows the empty state when no nodes are returned", async ({
    mockedPage,
  }) => {
    await mockBackend(mockedPage, { topology: { nodes: [], edges: [] } });
    await mockedPage.goto("/projects/webapp/topology", {
      waitUntil: "networkidle",
    });
    await expect(mockedPage.getByText(/aucun service détecté/i)).toBeVisible({
      timeout: 10000,
    });
  });

  test("shows the error state when the topology API fails", async ({
    mockedPage,
  }) => {
    await mockBackend(mockedPage, { errors: { topology: 500 } });
    await mockedPage.goto("/projects/webapp/topology", {
      waitUntil: "networkidle",
    });
    await expect(
      mockedPage.getByText(/erreur lors du chargement/i),
    ).toBeVisible({ timeout: 10000 });
  });
});
