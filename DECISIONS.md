# DECISIONS — container-webview

> Repository-local ADRs (Architectural Decision Records). Numbering: D-XXXX.
> Any deviation from [CODE_MANIFEST.md](../../CODE_MANIFEST.md) must be documented here.
> No active deviation → this project follows all chrysa global standards.

---

## D-0001 — Adherence to chrysa global standards

**Date**: 2026-04-29
**Status**: accepted

This project follows all conventions defined in `CODE_MANIFEST.md` (chrysa portfolio standards).
No active deviation is in effect. Any future deviation must be added as a new ADR entry below.

---

## D-0002 — Frontend visual identity: chrysa "Neon Brutalist" (cyan)

**Date**: 2026-06-10
**Status**: accepted

The web UI adopts the ecosystem Neon Brutalist design system
(`shared-standards/docs/DESIGN-SYSTEM.md`): radius 0, 2px FG-colored borders,
hard offset shadows (`4px 4px 0`, no blur), flat fills, mono-forward (JetBrains
Mono + Space Grotesk display), one acid accent — **cyan `#00e5ff`**.

The re-skin is driven through the existing SCSS token layer
(`src/styles/_theme.scss`, `_variables.scss`, `_globals.scss`, `_mixins.scss`):
the CSS custom-property names (`--bg`, `--primary`, `--border`, `--status-*`…)
and the `html.dark` switch are preserved, so every `*.module.scss` inherits the
look. A handful of modules that hardcoded radius/blur-shadow/hex (topology
nodes, banners, toast, alerts) were migrated onto the same tokens. No component
logic, route, or `data-testid` changed.

**Documented deviation — dense surfaces.** A muted `--grid` token backs inner
separators of dense lists/log views, while structural surfaces (cards, sidebar,
header, topology nodes, inputs, buttons) carry the loud 2px FG border. The
terminal-style `LogsPanel` keeps its fixed dark scheme by design.
