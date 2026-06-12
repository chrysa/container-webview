# container-webview — Design

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
