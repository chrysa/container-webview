# container-webview — Design contract

Baseline contract for the human-facing surface documented in this repository. This change documents requirements; it does not redesign or certify the implementation.

## Scope and priority journeys

Product UI: organise navigation around user tasks and domain objects rather than
copying a generic dashboard layout.

1. Locate a Compose project and its services.
2. Inspect topology, metrics and alerts.
3. Review a lifecycle action before applying it.

## Sources and implementation evidence

- [README.md](README.md)
- [code/index.html](code/index.html)
- [code/public/index.html](code/public/index.html)
- [code/src/App.tsx](code/src/App.tsx)
- [code/src/components/alerts/AlertsPanel.tsx](code/src/components/alerts/AlertsPanel.tsx)
- [code/src/components/forms/LoginForm.tsx](code/src/components/forms/LoginForm.tsx)
- [code/src/components/layouts/AppHeader.tsx](code/src/components/layouts/AppHeader.tsx)
- [code/src/index.css](code/src/index.css)

These are repository evidence, not proof that every desired journey is implemented.
Where source code and product intent differ, record the gap explicitly.

## Visual language and components

Existing style/token sources: [code/src/index.css](code/src/index.css).
Use the existing semantic variables and component conventions. Record inconsistencies
as design debt; do not invent a replacement palette during an unrelated feature.

Use a legible body face and reserve monospace for code, identifiers and numeric data.
Prefer clear hierarchy, predictable spacing and restrained, functional transitions.
Keep dense operational data scannable; progressively disclose advanced controls.
Reuse components and document default, focus, active, disabled and error states.
Do not introduce a light/dark switch or new brand persona without a product decision.

## UX acceptance and verification

- Make the primary task visible; preserve navigation, filters, input and focus across updates.
- Define loading, empty, validation error, unavailable dependency, stale data and recovery
  states where relevant. Never display a failed operation as successful.
- Use text or icons with labels as well as colour for status. Keep keyboard focus visible,
  navigation predictable and motion optional; respect reduced-motion preferences.
- For web content, target WCAG 2.2 AA; use at least 4.5:1 contrast for ordinary text
  (3:1 for qualifying large text), and aim for 44 CSS px touch controls. Verify the
  complete applicable standard, not only these examples. Apply equivalent native
  accessibility APIs to desktop controls; do not claim web certification for a native UI.
- Test the primary journey, empty data, a failed operation and recovery at representative
  viewport/window sizes. Verify keyboard use, long labels and realistic data volumes.
  Keep screenshots or other reproducible evidence with the UI change; document checks
  that could not run. Static lint is not evidence of usability or accessibility compliance.
- Maintain provenance and licence records for fonts, icons, artwork and generated assets;
  serve assets locally where feasible. Do not copy a reference brand's logos or identity.
- Keep detailed journeys/acceptance evidence in existing project documentation. Update
  this contract alongside UI changes; preserve existing component and token ownership.

## Agent and lint integration

Consult this file before UI work and keep it aligned with the implementation. The
filename alone does not load it into Claude Code or other agents. Use an explicit
on-demand reference from the repository's instruction files. Prism validates the
instruction document's size, imports and dead local references; it does not choose
an aesthetic, enforce this product's UX or certify the resulting interface.
