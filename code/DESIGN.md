# container-webview — Design

## Information Architecture (Phase-4 IA pass)

### Job-to-be-done

An operator answers "is this project healthy and what's wrong?" in a single
screen — without hopping across four separate routes. The homelab/chrysa-fleet
audience needs triage latency under 5 s, not feature breadth.

### Primary object

A **Compose project as a live fleet of services**. The project is the root
entity; each service is a member with observable health and driveable
lifecycle.

### Primary action

**Lifecycle-from-health** — the operator sees the health state of a service
and can act on it (restart / start) from the same row, without navigating
away. Stop and pause are demoted to secondary to reduce accidental destructive
actions.

### Master/detail project workspace (`/projects/:id`)

The headline screen uses a **master/detail** metaphor (console genre):

- **LEFT MASTER (280 px)** — service fleet list. Each row: derived health
  badge + service name + image. Keyboard-navigable (`role="option"`,
  `aria-selected`). Auto-selects first service on load.
- **RIGHT DETAIL (flex-1)** — selected service panel, scrollable:
    - Config section (ports / networks / volumes / depends_on / env vars with
    reveal toggle, `aria-expanded`)
    - Live metrics sparkline (recharts AreaChart; rolling 20-sample window
    accumulated client-side — no backend change)
    - Inline alerts filtered to this service (`aria-live="polite"`)
    - Inline lifecycle actions (primary = Restart/Start; secondary = Stop/Pause)
    - Log link (deep-link to `/projects/:id/logs`)

### Health derivation (client-side)

`deriveServiceHealth(name, metrics, alerts)` in `domain/health/deriveHealth.ts`:

1. **Metrics path (preferred)** — `ServiceMetrics.status` is the raw Docker
   status string already exposed by the existing `/projects/:id/metrics`
   endpoint. Maps `running` → running, `exited` → exited, `restarting` →
   restarting, `paused` → paused, `*unhealthy*` → unhealthy.
2. **Alert-derived fallback** — if no metrics entry: a `critical` alert for
   the service → `unhealthy`; a `warning` alert → `exited`.
3. **Unknown** — no data from either source (service never polled yet).

`deriveProjectHealth` aggregates across all services; worst status wins.

### Per-page IA

| Route | Screen | Role |
|---|---|---|
| `/projects` | Projects landing | Cards grid; each card now shows project-level health badge + per-service health dots |
| `/projects/:id` | **Project Workspace (NEW)** | Master/detail; primary entry from project card |
| `/projects/:id/topology` | Topology graph | Deep-link; unchanged |
| `/projects/:id/services` | Services table | Deep-link; health badge added to each row; key bug fixed |
| `/projects/:id/logs` | Log stream | Deep-link; unchanged |
| `/projects/:id/metrics` | Metrics charts | Deep-link; unchanged |
| `/alerts` | Alerts roll-up | Global view; unchanged |
| `/login` | Auth | Unchanged |

### Deferred items

- **i18n** — strings are hardcoded French (app has no i18n infra). All new
  strings are centralised in a `STRINGS` const at the top of each component
  so a later i18n pass (FR + EN) is mechanical. i18next is out-of-scope here.
- **Backend status field** — a first-class `service.status` on the Project
  type would remove the dependency on the metrics query for the health badge.
  Tracked as `// FOLLOW-UP` comments in `deriveHealth.ts` and
  `ProjectWorkspace.tsx`.

---

Visual identity for the docker-overview web UI. Implements the chrysa design
system, **Console persona** (`shared-standards/docs/DESIGN-SYSTEM.md` §1 +
[ADR 0002](https://github.com/chrysa/shared-standards/blob/main/docs/adr/0002-design-personas.md)).
A dense container/topology monitoring dashboard — the Console genre.

## Persona

- **Subtle rounding** — `--radius-sm/md/lg = 3/4/6px` (`--radius-full` kept for
  genuine circles: status dots, spinner).
- **1px hairline borders** — `--border-width: 1px`, `--border` a subtle neutral
  (`#2e2e33` dark / `#d4d4d8` light), not foreground-loud.
- **Soft restrained shadows** — `--shadow-sm/md = 0 1px 2px / 0 2px 8px` (no hard
  offset).
- **Readable sans body** — Inter (`--font-sans`) in normal case; **mono reserved
  for data** (JetBrains Mono); Space Grotesk for display headings.
- **One accent:** **cyan** — `#00e5ff` (dark), `#0891b2` (light) — used as a block
  with `--accent-ink` text on top (WCAG AA), never thin acid text.

## Tokens

Single source of truth: `src/styles/_theme.scss` (palette; `:root` is the light
default and `html.dark` is canonical) plus `_variables.scss`
(radius/shadow/border-width/font/spacing). Every `*.module.scss` and the
`@mixin card` consume these vars (24 `var(--radius-*)` + 5 `var(--border-width)`
references), so the persona migration was a near-pure token revalue — no
per-component rewrites beyond one literal border holdout. The `html.dark` toggle
is unchanged.

| role | dark | light |
|---|---|---|
| `--bg` | `#0e0e10` | `#fafafa` |
| `--bg-secondary` | `#18181b` | `#ffffff` |
| `--border` (hairline) | `#2e2e33` | `#d4d4d8` |
| `--grid` (dense line) | `#2e2e33` | `#e4e4e7` |
| `--primary` (cyan) | `#00e5ff` | `#0891b2` |
| `--accent-ink` | `#0e0e10` | `#ffffff` |

## Topology (React Flow)

`ServiceNode` / `NetworkNode` are surface boxes with a subtle radius + hairline
border + soft shadow (all via tokens). Status keeps the semantic `--status-*`
palette.

## Constraints kept

- No framework migration (SCSS + CSS modules retained).
- All `data-testid` selectors and the `html.dark` switch preserved — no component
  logic or test changed.
- `prefers-reduced-motion` respected; focus outline kept in the accent. Deviation
  recorded as **D-0002** in `DECISIONS.md`.
