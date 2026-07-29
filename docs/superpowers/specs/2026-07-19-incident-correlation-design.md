# Incident Correlation — Design (container-overview V1 intelligence layer)

- **Status:** Proposed
- **Date:** 2026-07-19
- **Repo:** `chrysa/container-webview` (canonical name target: `container-overview`)
- **Layer:** C3 · Observability
- **Author:** brainstorm session, validated with owner

---

## 1. Summary

Add an **intelligence layer** to the existing Docker Overview WebUI: an engine that
fuses **Docker events**, **log error bursts**, and **metric anomalies** into a single,
dated **incident** with a **probable cause** and a fused timeline.

This is the differentiator against Portainer / Dozzle / Prometheus+Grafana: those tools
*show* raw signals; none *correlate* them into "what actually happened on this host, and
why". The dead hypothesis for the project is that the intelligence never surpasses the
living-doc / raw-dashboard stage — this feature is the direct answer to it.

Scope of this spec: **V1 incident correlation, read-only.** Actions (auto-restart),
long-term trend dashboards, and ML are explicitly out.

## 2. Context — current state of the code

The repo is more advanced than the Notion fiches suggest. Verified by codebase map:

- Backend: FastAPI 0.136, docker-py 7.1 via `services/docker_client.py`
  (`docker.from_env()`, containers discovered by Compose labels). Routers: auth,
  config, projects, topology, lifecycle, logs (WS), metrics, alerts.
- Auth: **PyJWT already** (CVE-2024-33664 mitigated — CLAUDE.md is stale on this).
- WebSocket log streaming: **done** (`routers/logs.py`, xterm frontend).
- Metrics: **live snapshots only** — `container.stats(stream=False)` per request,
  nothing persisted.
- **No persistence, no time-series, and `client.events()` is never consumed.** This is
  the foundation gap this feature must fill.
- Only existing "intelligence" = threshold rules in `services/alerts_service.py`.
- Frontend: React 19 + Vite 8 + TS, TanStack Query v5, ReactFlow topology, Recharts,
  SCSS modules. 127 backend tests (pytest, `fail_under=78`), thin Vitest, 8 Playwright specs.

Note: the transverse chrysa standard is Postgres 16 + Redis 7 + SQLAlchemy 2.0 async; the
repo has **not** adopted it. This feature adopts it (see §5) — a deliberate alignment.

## 3. Locked decisions

| Axis | Decision |
| --- | --- |
| First intelligence brick | **Incident correlation** (subsumes anomaly + log analysis as inputs) |
| Cause engine | **Hybrid** — deterministic signal fusion, then optional local-Ollama narrative on top |
| Store | **Postgres 16 + TimescaleDB** (SQLAlchemy 2.0 async + Alembic) |
| Scope | **Host-wide collection, project-filterable UI** |
| Canonical name | `container-overview` (git rename + Notion merge = separate track, not in this spec) |

## 4. Scope & boundaries

**In V1**

- Host-wide collector: Docker events + periodic stats + on-trigger log excerpts.
- Correlation engine producing read-only incidents with probable cause + fused timeline.
- REST + WebSocket API for the incident feed and detail.
- Global `/incidents` UI, filterable by compose project.

**Out of V1 (later bricks)**

- Auto-restart / remediation actions.
- Long-term resource-trend dashboards.
- ML-based anomaly detection — V1 uses EWMA / z-score only.
- Full log NLP — the LLM is used *only* for the narrative summary.

**Separate track (validated per element, not in this spec)**

- Rename GitHub repo `container-webview` → `container-overview`, fleet ref updates.
- Merge the two duplicate Notion fiches ("Docker Overview" concept + "container-webview"
  implementation) under the canonical name.

## 5. Architecture

```
Docker host  (/var/run/docker.sock, read-only)
   │  events stream        stats poll (10s)       logs on-trigger
   ▼
collector/                    ← asyncio tasks in FastAPI lifespan, decoupled module
   event_consumer · stats_poller · log_tailer      (extractable to a worker later)
   ▼
Postgres 16 + TimescaleDB     ← SQLAlchemy 2.0 async + Alembic
   ▼
services/incidents_service.py ← trigger → window gather → group/dedup
                                → deterministic cause → optional Ollama narrative
   ▼
routers/incidents.py          ← REST + WebSocket live push
   ▼
frontend /incidents           ← host-wide feed + project filter + detail timeline
```

### 5.1 Components

**`collector/`** (new module)

- `event_consumer` — consumes `client.events(decode=True)`, filtered to relevant types
  (`die`, `oom`, `kill`, `health_status`, `restart`, `start`, `stop`). Normalizes and
  persists to `docker_events`. Reconnects with backoff on stream loss.
- `stats_poller` — every `COLLECTOR_STATS_INTERVAL_S` (default 10), iterates running
  containers with bounded concurrency, computes CPU%/mem%/net/blkio from
  `container.stats(stream=False)`, writes to the `metric_samples` hypertable.
- `log_tailer` — **on trigger only**, pulls a bounded recent log excerpt for the involved
  containers into `log_excerpts` (keeps storage bounded; no permanent log storage).
- Runs as supervised asyncio tasks started in the FastAPI lifespan. The module is
  self-contained so it can move to a dedicated worker service without API changes.

**`services/incidents_service.py`** (new, DDD sibling of `alerts_service.py`)

- **Trigger** = a primary signal: a Docker event (die/oom/unhealthy/restart-loop), a
  metric anomaly (EWMA baseline + z-score over the sample window), or a log error burst
  (rate spike of ERROR / exception lines).
- **Window** = gather all signals within `±INCIDENT_WINDOW_S` (default 90) for the
  triggering container **and its neighbours**: compose `depends_on`, shared network, same
  host.
- **Group / dedup** = signals close in time on related containers merge into a single
  incident; restart-loops collapse into one incident (no per-restart spam).
- **Cause** = ordered deterministic rules (§6). First match wins.
- **Narrative** = optional local-Ollama summary written over the deterministic result
  (never changes the category). Feature-flagged off by default; degrades to a
  deterministic template with `narrative_source = template`.
- **Close** = an incident auto-closes when the primary container returns healthy for
  `INCIDENT_RESOLVE_S`.

**`routers/incidents.py`** (new)

- `GET /api/incidents?project=&status=&since=` → paginated list (host-wide).
- `GET /api/incidents/{incident_id}` → detail: fused timeline (signals ordered), involved
  services, probable cause, narrative, bounded log excerpt.
- `WS /api/incidents/stream` → live push of new/updated incidents (token via query param,
  same convention as `logs.py`).
- REST shapes follow the `api-design` skill: plural-noun collections, semantic URLs,
  RFC-7807 errors, `Depends(get_current_user)` on all routes.

**Frontend `/incidents`** (new global page)

- Host-wide feed (severity chip, title, involved services, opened-at), project filter
  reusing the existing project list.
- Detail view: interleaved timeline (event / metric / log signals), a mini ReactFlow graph
  highlighting involved services (reuse topology components), Recharts mini-charts over the
  incident window, and the log excerpt.
- Live badge via the WebSocket; all HTTP through TanStack Query. Dark mode + WCAG 2.1 AA.

### 5.2 Data flow

Docker host → collector persists events + metric samples continuously → a new event or a
detected anomaly/burst triggers the correlation engine → engine gathers the window,
groups signals, infers cause, optionally writes a narrative, persists the incident and its
signal links, pulls a bounded log excerpt → API serves the feed/detail and pushes updates
over WS → frontend renders feed + detail.

## 6. Data model

SQLAlchemy 2.0 async models, Alembic migrations. All thresholds/intervals live in an
external YAML config loaded via Pydantic Settings (no inline literals — chrysa rule).

| Table | Columns (essential) | Notes |
| --- | --- | --- |
| `metric_samples` | `ts`, `container_id`, `cpu_pct`, `mem_pct`, `net_rx`, `net_tx`, `blk_r`, `blk_w` | **Timescale hypertable**, retention policy `METRIC_RETENTION_DAYS` (default 7) |
| `docker_events` | `ts`, `container_id`, `service`, `project`, `type`, `exit_code`, `health` | normalized event |
| `incidents` | `id`, `opened_at`, `closed_at`, `container_id`, `service`, `project`, `status`, `severity`, `cause_category`, `narrative`, `narrative_source` | kept longer than samples |
| `incident_signals` | `incident_id`, `signal_type` (event/metric/log), `ref_id`, `ts`, `summary` | N-N link reconstructing the timeline |
| `log_excerpts` | `incident_id`, `container_id`, `captured_at`, `content` | bounded excerpt, no permanent log store |

### 6.1 Deterministic cause rules (ordered, first match wins)

1. event `OOMKilled` → **memory**
2. exit code ≠ 0 → **crash**
3. healthcheck failing → **readiness**
4. an upstream dependency's incident opened first → **cascade**
5. sustained metric spike → **resource saturation**
6. no rule matched → **undetermined**

The Ollama narrative rewrites the human sentence over the chosen category; it never
overrides the category.

## 7. Error handling

- **docker.sock unavailable** → collector retries with backoff; incident endpoints return
  `503`; health endpoint reports degraded.
- **Ollama absent / timeout** → fall back to deterministic template,
  `narrative_source = template`. Never blocks incident creation.
- **Collector task crash** → a supervising wrapper restarts the lifespan task; worst-case
  loss is a single in-flight sample.
- **TimescaleDB extension missing** → migration guard fails fast at startup with a clear
  message (do not silently run without the hypertable).
- **Backpressure** → bounded stats concurrency; event stream buffered; oldest metric
  samples dropped by the retention policy.
- Follows the chrysa `error-handling` skill (FastAPI errors + Sentry).

## 8. Testing

Coverage target ≥ 85% (fleet floor; repo currently `fail_under=78` — raise it).

- **Unit** — cause rules over signal fixtures (each rule → expected category), anomaly
  math (EWMA / z-score), event normalizer, incident grouping/dedup.
- **Integration** — collector against a Postgres + TimescaleDB testcontainer with
  simulated Docker events; engine end-to-end on seeded samples.
- **Frontend** — Vitest for feed + detail; state and rendering of the timeline.
- **E2E** — Playwright: seed an incident, open `/incidents`, assert the fused timeline and
  probable cause render.

## 9. Config keys (external YAML, typed loader)

`COLLECTOR_STATS_INTERVAL_S` (10) · `INCIDENT_WINDOW_S` (90) · `INCIDENT_RESOLVE_S` ·
`METRIC_RETENTION_DAYS` (7) · `ANOMALY_Z_THRESHOLD` · `LOG_BURST_RATE` ·
`OLLAMA_ENABLED` (false) · `OLLAMA_MODEL` · `OLLAMA_URL`.

## 10. Open questions / deferred

- Collector as lifespan tasks (V1) vs a dedicated worker service (deferred; module kept
  extractable).
- Redis: not required for V1 (WS push is in-process). Add only if a worker split needs a
  pub/sub bus.
- Cross-host correlation: out of scope — single host only.

## 11. Non-goals

Remediation actions, trend dashboards, ML anomaly detection, permanent log storage,
multi-host, and the git-rename / Notion-merge track are **not** part of this spec.
