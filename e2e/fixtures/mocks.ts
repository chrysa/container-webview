import type { Page, Route } from "@playwright/test";

/**
 * Deterministic backend mocks driven entirely by Playwright route interception.
 *
 * Why mocks: the nominal specs used to require a *live* API + frontend stack
 * (real JWT login, a real /projects mount, the Docker socket). That makes
 * error / empty / degraded journeys impossible to exercise reliably. By
 * intercepting every `**​/api/**` call we get a hermetic, deterministic suite
 * that covers ALL user journeys (CODE_MANIFEST §6.4 / ADR D-0002) without any
 * backend running.
 *
 * The frontend is built with VITE_API_URL pointing at the API origin, so calls
 * go to `<origin>/api/...`. The `**​/api/...` glob below matches both the
 * absolute (dev) and relative (K8s) URL shapes.
 */

export const FAKE_TOKEN = "e2e.fake.jwt-token";

export interface ProjectFixture {
  id: string;
  name: string;
  path: string;
  compose_file: string;
  services: ServiceFixture[];
  networks: string[];
}

export interface ServiceFixture {
  name: string;
  image: string;
  ports: string[];
  depends_on: string[];
  networks: string[];
  volumes: string[];
  environment: Record<string, string>;
  healthcheck: Record<string, unknown> | null;
}

export const PROJECT_WEB: ProjectFixture = {
  id: "webapp",
  name: "webapp",
  path: "/projects/webapp",
  compose_file: "docker-compose.yml",
  services: [
    {
      name: "api",
      image: "myorg/api:1.2.3",
      ports: ["8000:8000"],
      depends_on: ["db"],
      networks: ["backend"],
      volumes: ["./data:/data"],
      environment: {
        NODE_ENV: "production",
        DB_PASSWORD: "fake-masked-pw",
        API_TOKEN: "fake-masked-tok",
        LOG_LEVEL: "info",
      },
      healthcheck: null,
    },
    {
      name: "db",
      image: "postgres:16",
      ports: ["5432:5432"],
      depends_on: [],
      networks: ["backend"],
      volumes: ["pgdata:/var/lib/postgresql/data"],
      environment: { POSTGRES_PASSWORD: "pg-secret" },
      healthcheck: null,
    },
  ],
  networks: ["backend", "frontend"],
};

export const PROJECT_EMPTY_SERVICES: ProjectFixture = {
  id: "stub",
  name: "stub",
  path: "/projects/stub",
  compose_file: "docker-compose.yml",
  services: [],
  networks: [],
};

export const PROJECTS_LIST: ProjectFixture[] = [
  PROJECT_WEB,
  {
    id: "monitoring",
    name: "monitoring",
    path: "/projects/monitoring",
    compose_file: "compose.yaml",
    services: [
      {
        name: "prometheus",
        image: "prom/prometheus",
        ports: ["9090:9090"],
        depends_on: [],
        networks: ["mon"],
        volumes: [],
        environment: {},
        healthcheck: null,
      },
    ],
    networks: ["mon"],
  },
];

export const TOPOLOGY_WEB = {
  nodes: [
    {
      id: "api",
      type: "service",
      data: { label: "api", image: "myorg/api:1.2.3", status: "running" },
      position: { x: 0, y: 0 },
    },
    {
      id: "db",
      type: "service",
      data: { label: "db", image: "postgres:16", status: "running" },
      position: { x: 240, y: 0 },
    },
    {
      id: "backend",
      type: "network",
      data: { label: "backend" },
      position: { x: 120, y: 160 },
    },
  ],
  edges: [
    {
      id: "e1",
      source: "api",
      target: "db",
      label: "depends_on",
      animated: true,
    },
  ],
};

export const TOPOLOGY_EMPTY = { nodes: [], edges: [] };

export const METRICS_WEB = [
  {
    service: "api",
    container_id: "abc123",
    status: "running",
    cpu_percent: 12.5,
    mem_usage_mb: 128,
    mem_limit_mb: 512,
    mem_percent: 25,
    net_rx_mb: 3.2,
    net_tx_mb: 1.1,
    block_read_mb: 0.5,
    block_write_mb: 0.2,
  },
  {
    service: "db",
    container_id: "def456",
    status: "running",
    cpu_percent: 4.0,
    mem_usage_mb: 256,
    mem_limit_mb: 1024,
    mem_percent: 25,
    net_rx_mb: 0.4,
    net_tx_mb: 0.3,
    block_read_mb: 2.0,
    block_write_mb: 1.5,
  },
];

export const ALERTS_LIST = [
  {
    id: "a1",
    level: "critical" as const,
    project: "webapp",
    service: "db",
    message: "Container exited unexpectedly",
    timestamp: "2026-01-01T10:00:00Z",
  },
  {
    id: "a2",
    level: "warning" as const,
    project: "webapp",
    service: "api",
    message: "High memory usage (85%)",
    timestamp: "2026-01-01T10:05:00Z",
  },
  {
    id: "a3",
    level: "info" as const,
    project: "monitoring",
    service: "prometheus",
    message: "Scrape target added",
    timestamp: "2026-01-01T10:06:00Z",
  },
];

function json(route: Route, body: unknown, status = 200) {
  return route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

export interface BackendMockOptions {
  projects?: ProjectFixture[];
  project?: ProjectFixture;
  topology?: unknown;
  metrics?: unknown;
  alerts?: unknown;
  /** Force an HTTP error status on a given collection of endpoints. */
  errors?: Partial<
    Record<"projects" | "project" | "topology" | "metrics" | "alerts", number>
  >;
  /** Reject the lifecycle action POST (e.g. 500) to exercise the error toast. */
  actionFails?: boolean;
  /** Reject /auth/login with 401 to exercise the failed-login journey. */
  loginFails?: boolean;
}

/**
 * Install backend route handlers. Endpoints are matched most-specific-first by
 * Playwright (last registered handler wins), so we register the broad /projects
 * list handler and let the per-resource handlers override sub-paths.
 */
export async function mockBackend(
  page: Page,
  opts: BackendMockOptions = {},
): Promise<void> {
  const {
    projects = PROJECTS_LIST,
    project = PROJECT_WEB,
    topology = TOPOLOGY_WEB,
    metrics = METRICS_WEB,
    alerts = ALERTS_LIST,
    errors = {},
    actionFails = false,
    loginFails = false,
  } = opts;

  // ── Auth ──────────────────────────────────────────────────────────────
  await page.route("**/api/auth/login", (route) => {
    if (loginFails) {
      return json(route, { detail: "Invalid credentials" }, 401);
    }
    return json(route, {
      access_token: FAKE_TOKEN,
      token_type: "bearer",
      username: "admin",
    });
  });

  // ── Lifecycle action (POST .../services/<svc>/<action>) ───────────────
  await page.route(
    /\/api\/projects\/[^/]+\/services\/[^/]+\/(start|stop|restart|pause)$/,
    (route) => {
      if (route.request().method() !== "POST") return route.fallback();
      if (actionFails) {
        return json(route, { detail: "Docker daemon error" }, 500);
      }
      const url = route.request().url();
      const parts = url.split("/");
      const action = parts.at(-1) ?? "start";
      const service = parts.at(-2) ?? "svc";
      return json(route, { service, action, status: "ok" });
    },
  );

  // ── Per-project sub-resources ─────────────────────────────────────────
  await page.route(/\/api\/projects\/[^/]+\/topology$/, (route) =>
    errors.topology
      ? json(route, { detail: "boom" }, errors.topology)
      : json(route, topology),
  );
  await page.route(/\/api\/projects\/[^/]+\/metrics$/, (route) =>
    errors.metrics
      ? json(route, { detail: "boom" }, errors.metrics)
      : json(route, metrics),
  );

  // ── Single project (GET /projects/<id>) ───────────────────────────────
  await page.route(/\/api\/projects\/[^/]+$/, (route) =>
    errors.project
      ? json(route, { detail: "boom" }, errors.project)
      : json(route, project),
  );

  // ── Alerts ────────────────────────────────────────────────────────────
  await page.route("**/api/alerts", (route) =>
    errors.alerts
      ? json(route, { detail: "boom" }, errors.alerts)
      : json(route, alerts),
  );

  // ── Projects list (GET /projects) ─────────────────────────────────────
  await page.route("**/api/projects", (route) =>
    errors.projects
      ? json(route, { detail: "boom" }, errors.projects)
      : json(route, projects),
  );

  // ── Health probe (GET /api) ───────────────────────────────────────────
  await page.route(/\/api\/?$/, (route) => json(route, { status: "ok" }));
}

/** Seed a valid session in localStorage so RequireAuth passes without a UI login. */
export async function seedSession(page: Page): Promise<void> {
  await page.addInitScript(
    ([token]) => {
      window.localStorage.setItem("token", token);
      window.localStorage.setItem("username", "admin");
    },
    [FAKE_TOKEN],
  );
}
