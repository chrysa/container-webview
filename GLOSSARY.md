# GLOSSARY — container-webview

> Generated 2026-09-25. Terms as used in this repository.

- **Project** — a directory containing a `docker-compose` definition, discovered under the mounted
  `/projects` path. Source: `services/project_manager.py`, `.env.example`.
- **Service** — a service declared in a project's Compose file; the unit acted on by lifecycle actions.
- **Topology** — the graph of a project's services and networks. Source: `services/topology_service.py`.
- **Lifecycle action** — start / stop / restart / pause / unpause issued against a service.
  Source: `routers/lifecycle.py`.
- **Metrics** — live CPU / memory / network stats per container. Source: `services/metrics_service.py`.
- **Alert** — an automatically detected anomalous container state (exited, restarting, unhealthy).
  Source: `services/alerts_service.py`.
- **HATEOAS** — hypermedia response models embedding links; `api/app/models/hateoas.py`.
- **Local admin fallback** — dev-only username/password auth when LDAP is not configured;
  bcrypt hash preferred. Source: `security.py`, `.env.example`.
- **Managed standards block** — the `chrysa:standards` region in `CLAUDE.md`, inlined by
  `distribute-standards.sh`; do not hand-edit.
- **Generated context files** — `handover.md`, `ai-instructions.md`, `context-map.json`,
  `llms-full.txt`, produced by `scripts/gen_context_files.py` (ADR D-0012); regenerate, don't edit.
- **Canon** — the chrysa transverse standards under `standards/`; source of truth over any per-tool view.
- **Profile / DDD level** — chrysa repo-classification metadata; here `profiles` is empty in
  `context-map.json` and "(not available)" in `handover.md` (UNKNOWN).
