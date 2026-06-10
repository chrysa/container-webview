# container-webview — Design

Visual identity for the docker-overview web UI. Implements the chrysa
**Neon Brutalist** design system (`shared-standards/docs/DESIGN-SYSTEM.md`).

## DNA

- **Radius 0** (`--radius-sm/md/lg = 0`; `--radius-full` kept only for genuine
  circles — status dots, spinner).
- **2px FG-colored borders** as structure (`--border-width`, `--border` = FG).
- **Hard offset shadows** (`--shadow-sm/md = 3px/4px 4px 0`, no blur).
- **Flat fills, no gradients/glow.**
- **Mono-forward:** JetBrains Mono (UI/data) + Space Grotesk (display headings),
  loaded via `code/index.html`.
- **One acid accent:** **cyan** — `#00e5ff` (dark), `#0891b2` (light) — used as a
  block with `--accent-ink` text on top (WCAG AA), never thin acid text.

## Tokens

Single source of truth: `src/styles/_theme.scss` (palette; `:root` is the light
default and `html.dark` is canonical) plus `_variables.scss`
(radius/shadow/font/spacing). Every `*.module.scss` and the `@mixin card`
consume these vars, so the re-skin propagates without per-component rewrites.
The `html.dark` toggle is unchanged.

| role | dark | light |
|---|---|---|
| `--bg` | `#0e0e10` | `#fafafa` |
| `--bg-secondary` | `#18181b` | `#ffffff` |
| `--border` (loud) | `#fafafa` | `#0e0e10` |
| `--grid` (dense line) | `#3f3f46` | `#d4d4d8` |
| `--primary` (cyan) | `#00e5ff` | `#0891b2` |
| `--accent-ink` | `#0e0e10` | `#ffffff` |

## Topology (React Flow)

`ServiceNode` / `NetworkNode` are flat brutalist boxes (radius 0, 2px loud
border, hard shadow). Status keeps the semantic `--status-*` palette.

## Constraints kept

- No framework migration (SCSS + CSS modules retained).
- All `data-testid` selectors and the `html.dark` switch preserved — no
  component logic or test changed.
- `prefers-reduced-motion` respected. Deviation recorded as **D-0002** in
  `DECISIONS.md`.
