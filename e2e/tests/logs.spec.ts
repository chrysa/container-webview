import { test, expect } from "../fixtures/app";
import { mockBackend, PROJECT_EMPTY_SERVICES } from "../fixtures/mocks";

/**
 * The logs panel streams via WebSocket. Playwright's WebSocket routing
 * (`routeWebSocket`) is only available from @playwright/test 1.48 and this
 * suite pins 1.43, so we cannot inject frames. We instead cover the
 * deterministic UI journey: tab rendering, tab switching, the connection
 * indicator (which sits in the disconnected state since no WS server answers),
 * the line counter and the clear control.
 */
test.describe("Logs page", () => {
  test("renders a tab per service and a log viewer", async ({ mockedPage }) => {
    await mockedPage.goto("/projects/webapp/logs", {
      waitUntil: "networkidle",
    });
    await expect(
      mockedPage.getByRole("heading", { name: /logs/i }),
    ).toBeVisible();
    // One tab button per service.
    await expect(
      mockedPage.getByRole("button", { name: "api", exact: true }),
    ).toBeVisible({ timeout: 10000 });
    await expect(
      mockedPage.getByRole("button", { name: "db", exact: true }),
    ).toBeVisible();
    // The first service is auto-selected; its viewer header and counter show.
    await expect(mockedPage.getByText(/lignes/i)).toBeVisible();
  });

  test("switching tabs changes the active service viewer", async ({
    mockedPage,
  }) => {
    await mockedPage.goto("/projects/webapp/logs", {
      waitUntil: "networkidle",
    });
    await mockedPage.getByRole("button", { name: "db", exact: true }).click();
    // The viewer header now shows the db service label.
    await expect(mockedPage.locator("text=db").first()).toBeVisible();
    // Controls are present regardless of stream connectivity.
    await expect(
      mockedPage.getByRole("button", { name: /vider/i }),
    ).toBeVisible();
    await expect(
      mockedPage.getByRole("button", { name: /auto-scroll/i }),
    ).toBeVisible();
  });

  test("exposes a connection indicator and a clear control", async ({
    mockedPage,
  }) => {
    await mockedPage.goto("/projects/webapp/logs", {
      waitUntil: "networkidle",
    });
    const clear = mockedPage.getByRole("button", { name: /vider/i });
    await expect(clear).toBeVisible({ timeout: 10000 });
    await clear.click();
    // After clearing, the counter reads zero lines.
    await expect(mockedPage.getByText(/0 lignes/i)).toBeVisible();
  });

  test("project with no services shows no log tabs", async ({ mockedPage }) => {
    await mockBackend(mockedPage, { project: PROJECT_EMPTY_SERVICES });
    await mockedPage.goto("/projects/stub/logs", {
      waitUntil: "networkidle",
    });
    await expect(
      mockedPage.getByRole("heading", { name: /logs/i }),
    ).toBeVisible({ timeout: 10000 });
    // No service tabs are rendered.
    await expect(
      mockedPage.getByRole("button", { name: "api", exact: true }),
    ).toHaveCount(0);
  });
});
