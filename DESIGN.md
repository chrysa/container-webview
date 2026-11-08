# container-webview — Design contract

> Product design contract for the Docker Overview web UI (`code/`). Read it before any
> interface, component, style, navigation, interaction or asset work, and update it in the same
> change. The fleet rule, method and acceptance criteria live in shared-standards
> (`standards/rules/design.md`, `shared-standards/docs/DESIGN-CONTRACT.md`); they are not repeated here.
>
> Status of every statement: **[implemented]** links the code · **[decided]** cites the decision
> · **[proposed]** is not agreed yet. This file documents the current UI; it does not redesign
> it.

## 1. Surface and status

- **Surface:** web app — React 18 / Vite SPA styled with stock Bootstrap 5, in front of the
  FastAPI backend in `api/`. **[implemented]** ([code/src/App.tsx](code/src/App.tsx),
  [code/src/main.tsx](code/src/main.tsx))
- **Lifecycle:** prototype (shared-standards `repos.yml`: `status: dev`). The UI covers
  login, project list and project detail. Topology, lifecycle actions and logs exist in the API
  and in API clients but have **no screen** yet (see §11).
- **Detailed specs:** none. The [README.md](README.md) feature list and roadmap describe intent.

## 2. Users, devices and priority tasks

| User | Context and device | Priority tasks |
| ---- | ------------------ | -------------- |
| Self-hosting operator of a Docker host | Desktop browser on the LAN, occasional checks | 1. see which Compose projects exist and whether any container is in trouble · 2. read a project's services and live metrics · 3. act on a service (start/stop/restart) — not available in the UI yet |

Primary action per view: **Dashboard** — open a project ("Voir le détail"); **Project detail**
— read the services and metrics; **Login** — sign in.

## 3. Journeys and navigation

- **J1 — Sign in:** `/login` → username + password → dashboard. Failure: inline message
  "Identifiants invalides", input kept. **[implemented]**
  ([LoginForm.tsx](code/src/components/forms/LoginForm.tsx),
  [LoginPage.tsx](code/src/pages/LoginPage.tsx))
- **J2 — Check the host:** dashboard lists Compose projects as cards with an alerts panel
  above → open a project → services table, metrics table (refreshed every 10 s), project
  alerts (every 30 s) → "← Retour". **[implemented]**
  ([DashboardPage.tsx](code/src/pages/DashboardPage.tsx),
  [ProjectDetailPage.tsx](code/src/pages/ProjectDetailPage.tsx))
- **J3 — Act on a service:** start / stop / restart / pause from the UI. **[proposed]** — the
  client exists ([lifecycleService.ts](code/src/api/docker/lifecycleService.ts)), no control
  calls it.
- **Information architecture:** three routes in [routes.ts](code/src/constants/routes.ts)
  (`/`, `/projects/:id`, `/login`), guarded by `ProtectedRoute`/`PublicRoute`; a dark top bar
  with brand, user name and logout ([AppHeader.tsx](code/src/components/layouts/AppHeader.tsx)).
- **Density:** comfortable cards on the dashboard, compact `table-sm` tables on the detail
  page.

## 4. Identity

- No brand brief. The look is stock Bootstrap (light background, dark navbar, blue primary)
  with a whale emoji as the mark. **[implemented]**
- **[proposed]** Write a short brand brief before any visual work: a neutral operational tool
  identity is likely enough for a LAN admin UI.
- **References:** Bootstrap defaults; no third-party identity copied.

## 5. Tokens and components (owned elsewhere)

| Concern | Source of truth | Rules of use |
| ------- | --------------- | ------------ |
| Colour roles and themes | Bootstrap 5 defaults (imported in [main.tsx](code/src/main.tsx)) | contextual classes (`bg-primary`, `alert-danger`, …); light theme only |
| Typography | system stack in [index.css](code/src/index.css) | Bootstrap heading utilities (`h4`, `h6`) |
| Spacing, grid, breakpoints | Bootstrap grid and spacing utilities | `row-cols-1 / md-2 / xl-3` on the dashboard |
| Motion | none beyond Bootstrap spinners | |
| Components | [code/src/components/](code/src/components/), [code/src/features/](code/src/features/) | `LoadingSpinner`, `ErrorAlert`, `AlertsPanel`, `MetricsTable`, `ProjectCard` |

- **Shared contract:** `contract.css` not imported; `@chrysa/ui` not used.
- **Design debt and drift:** duplicate components — `components/alerts`, `components/projects`,
  `components/metrics` and `components/shared` copies differ from the `features/` and
  `components/ui` versions the pages import; inline styles in
  [GlobalLoader.tsx](code/src/components/loaders/GlobalLoader.tsx) and the login card; no
  design tokens of its own.

## 6. Interaction and states

- **Component states:** Bootstrap defaults (hover, focus ring, disabled); the login button is
  disabled with a spinner while submitting. **[implemented]**
- **Data states:**

  | State | Where it appears | Behaviour |
  | ----- | ---------------- | --------- |
  | Loading | route chunks, dashboard, detail | full-screen `GlobalLoader`, then a centred spinner; no skeleton |
  | Empty | dashboard, metrics, alerts | "Aucun projet … trouvé", "Aucune métrique disponible", "Aucune alerte active" |
  | Error | dashboard, detail | `ErrorAlert` (`role="alert"`) with the API message; no retry button |
  | Offline / backend unreachable | — | not handled beyond the error alert |
  | Stale data | alerts | alert timestamps only; metrics show no age |
  | Reconnect | — | React Query retry (1) and polling; no banner |

- **Real-time:** polling, not push — metrics every 10 s, alerts every 30 s
  ([ProjectDetailPage.tsx](code/src/pages/ProjectDetailPage.tsx)). Tables re-render in place.
- **Motion:** none; no entrance effect (FE-053).

## 7. Responsive and support conventions

Bootstrap responsive grid and `table-responsive` wrappers; login card capped at 420 px. No
viewport has been tested. **[implemented]**

## 8. Accessibility

- **Target:** WCAG 2.1 AA (canon floor).
- **Keyboard:** native links, buttons and form controls only; no custom shortcut.
- **Perception:** status badges show the status word as well as a colour; Bootstrap contrast
  not measured here.
- **Assistive technology:** labelled login inputs; spinners with visually hidden text;
  `role="alert"` on errors. The page language is French (`lang="fr"`) but labels are hard-coded,
  with no i18n. No screen-reader pass recorded.

## 9. Assets

| Asset | Source | Licence | Formats | Location |
| ----- | ------ | ------- | ------- | -------- |
| Bootstrap 5.3 CSS | npm `bootstrap` | MIT (package metadata) | CSS | npm dependency |
| `favicon.ico`, `logo192.png`, `logo512.png`, `manifest.json` | Create React App boilerplate (manifest still says "Create React App Sample") | unknown in the repository | ICO, PNG | [code/public/](code/public/) |
| Brand mark | 🐳 emoji, rendered by the system emoji font | platform font licence | text | inline |

[code/public/index.html](code/public/index.html) is a leftover CRA page; Vite serves
[code/index.html](code/index.html).

## 10. Acceptance criteria and evidence

- **Criteria:** the shared-standards observable list, applied to J1–J2: a failing project is
  identifiable on the dashboard; login keeps input after an error; errors offer a way to retry;
  an unreachable API shows a persistent banner; metrics show their age.
- **Existing tests:** none for the UI (`vitest` is configured, no test file exists in `code/`).
- **Evidence log:**

  | Date | Change | Checks run | Result | Not run, and why |
  | ---- | ------ | ---------- | ------ | ---------------- |
  | 2026-11-08 | contract written from the code | source review of `code/src` | gaps listed in §11 | no browser run: documentation-only change |

## 11. Open choices, known gaps and maintenance

- **Known gaps (from the code, 2026-11-08):** the README advertises an interactive topology
  and lifecycle actions "from the UI", but no screen calls
  [topologyService.ts](code/src/api/docker/topologyService.ts) or
  [lifecycleService.ts](code/src/api/docker/lifecycleService.ts); no offline banner, retry or
  stale-data age; polling instead of push (FE-080); no entrance motion (FE-053) and no
  reduced-motion handling; no dark theme; no UI tests; CRA boilerplate assets and manifest;
  duplicated components (§5); hard-coded French strings.
- **Open choices [proposed]:** decide whether the UI stays Bootstrap or adopts the fleet
  `contract.css`/`@chrysa/ui`; build J3 with a confirmation step before destructive actions.
- **Maintenance:** any UI change updates this file in the same PR.
