# Phase 08 — Theming & Design Tokens

Audit the shell's design token system: where tokens live, how widely
they're used, dark / density modes, brand customization, and whether the
shell can switch themes cleanly without leaving artifacts.

---

## What we evaluate

| Concern              | Question                                          |
|----------------------|---------------------------------------------------|
| Token source         | Single source of truth? Where?                    |
| Token coverage       | Are colors / spacing / radii / typography all tokenized? |
| Hard-coded values    | How many magic colors / sizes bypass the tokens?  |
| Dark mode            | Implemented? Complete? Triggered correctly?       |
| Density modes        | If supported, complete and consistent?            |
| OS preference        | `prefers-color-scheme` honored? OS appearance follow? |
| Brand / customer themes | If multi-tenant, can a tenant inject brand tokens? |
| Theme switch artifact | Anything not switching, flashing, or locked at boot? |
| Contrast across themes | All tokens still meet contrast in every mode?    |
| TUI-specific         | Color palette degrades on 256-color / 16-color terminals? |

---

## Static probes

### Web

```bash
# Token source candidates
fd -t f 'tokens|theme|design-tokens|tailwind\.config' --extension ts --extension js --extension mjs --extension css --extension json

# CSS variables defined
rg -n '^\s*--[a-z][a-z0-9-]*\s*:' --type css | wc -l

# Tailwind config color extension
rg -n 'extend\s*:\s*\{[\s\S]*?colors' tailwind.config.*

# Hard-coded hex colors in component code (bypass)
rg -n '#[0-9a-fA-F]{3,8}\b' --type tsx --type vue --type svelte | wc -l
rg -n 'rgb\(|rgba\(|hsl\(|hsla\(' --type tsx --type vue --type svelte | wc -l

# Inline style usage (often hard-codes design)
rg -n 'style=\{?\{' --type tsx --type vue | wc -l

# Dark mode markers
rg -n 'dark:|\.dark\b|prefers-color-scheme|theme-dark|data-theme' --type css --type tsx --type vue --type svelte

# Density / size scale markers
rg -n 'density|size-(xs|sm|md|lg|xl)|--space-\d' --type tsx --type css
```

### Desktop

```bash
# Native chrome / accent color tracking
rg -n 'NSAppearance|nativeTheme|useNativeTitleBar' --type ts --type js --type rust

# Tauri theme API
rg -n 'theme\(\)|ThemeChangePayload|set_theme' --type rust --type ts
```

### CLI / TUI

```bash
# Textual CSS files
fd -t f --extension tcss

# Rich console themes
rg -n 'Theme\(|console\.theme|Style\(' --type py

# Ratatui style usage
rg -n 'Style::default|Color::|set_style' --type rust

# Truecolor escape patterns (no fallback)
rg -n '\\x1b\[38;2;|\\033\[38;2;' --type rust --type py --type go
```

---

## Runtime probes

### Web / Desktop renderer

From `references/runtime-probes-web.md`:

1. `tokenAudit` — capture all `--*` custom properties at the document
   root. Record token count and a sample.
2. **Theme switch test**: capture `tokenAudit` snapshot A. Flip the
   theme via the user-facing toggle. Capture snapshot B (`themeSwitch`
   probe handles this two-step). Diff:
   - How many tokens changed?
   - Are there color tokens that *didn't* change but visibly should
     have? (Probably hard-coded values bypassing the system.)
3. **OS preference test**: in DevTools → Rendering → emulate
   `prefers-color-scheme: dark`. Without flipping the user toggle,
   confirm the shell follows.
4. **Brand override test** (multi-tenant only): switch tenant / load a
   themed account. Confirm brand tokens flow through to the shell, not
   just feature pages.
5. **Hard-coded scan in DOM**:
   ```javascript
   (() => [...document.querySelectorAll('[style*="color"], [style*="background"]')]
     .slice(0, 50).map(el => ({ tag: el.tagName, style: el.getAttribute('style') })))()
   ```
   Inline style attributes that hard-code colors are bypass evidence.

### CLI / TUI

1. Run with `COLORTERM=truecolor` and capture the rendered screen.
2. Run with `TERM=xterm-256color` (no `COLORTERM`) and capture again.
3. Run with `TERM=xterm` (16-color) and capture again.
4. Compare: does the app degrade gracefully? Or does it ship the same
   truecolor sequences regardless?
5. If a theme switch exists (light/dark inside the TUI), flip it and
   confirm all widgets respond.

---

## Verdict rubric

### Pass

- Single, named token source the team can point at.
- > 90% of color / spacing values come from tokens (small bypass list,
  documented).
- Dark mode (or OS-following) implemented and complete.
- Theme switch swaps without leaving artifacts.
- TUI degrades from truecolor → 256 → 16 colors gracefully if shipped to
  varied terminals.
- Contrast holds in every shipped theme.

### Warn

- Tokens exist but a meaningful portion of the shell hard-codes values.
- Dark mode mostly works but has 1–3 known bleed-through components.
- Theme switch leaves a brief flash of unstyled / wrong-themed content.
- TUI ships truecolor without explicit fallback (works but degraded
  experience on 256-color terminals).

### Fail

- No token system; ad-hoc colors throughout.
- Dark mode implemented but visibly broken in many places (unreadable
  text, mixed light / dark regions).
- Theme switch leaves the shell in a corrupt state requiring reload.
- A shipped theme has WCAG-failing contrast.

---

## Severity examples

- **Critical**: a shipped theme has body-text contrast < 3:1 (unreadable).
- **High**: dark mode toggle leaves the sidebar in light mode after
  switch.
- **Medium**: 200+ hard-coded colors in components bypass the token
  system.
- **Low**: token spacing scale uses inconsistent steps (4, 8, 14, 16).

---

## Findings entry schema

```json
{
  "id": "08-theming",
  "name": "Theming & Design Tokens",
  "verdict": "Warn",
  "verdictRationale": "Token system exists and is used in the shell layer. Bypass is concentrated in feature-page components, not the shell, so shell-level theming holds. Dark mode complete but flashes on initial load.",
  "evidence": [
    { "kind": "probe", "ref": "tokenAudit", "summary": "82 CSS custom properties at :root" },
    { "kind": "probe", "ref": "themeSwitch", "summary": "57 tokens change on theme flip; 3 expected color tokens unchanged" },
    { "kind": "snippet", "ref": "src/components/StatusDot.tsx:14", "summary": "hard-coded #00B894 instead of --color-success" }
  ],
  "findings": [
    {
      "id": "SH-051",
      "title": "Flash of light theme on initial load when user has dark preference",
      "severity": "Medium",
      "description": "On cold reload, the shell renders light for ~80ms before the theme cookie is read and re-rendered as dark. Visible flash on every reload for dark-mode users.",
      "evidence": ["screenshot-08-flash.png", "app/layout.tsx:22"],
      "remediation": "Move theme detection to a synchronous server-side cookie read (or a blocking inline script that sets `data-theme` on `<html>` before paint).",
      "scope": "every cold reload for dark-theme users",
      "confidence": "high"
    }
  ],
  "completedAt": "<ISO datetime>"
}
```

---

## Checkpoint

```
Phase 08 complete — Theming & Design Tokens: Warn

Top issues:
  • [Medium] Flash of light theme on cold reload for dark-preference users
  • [Medium] 3 status colors hard-coded in components (bypass tokens)
  • [Low]    Spacing token scale has irregular steps

Findings recorded: 4 (0 High, 2 Medium, 2 Low)
Proceed to Phase 09 (Cross-Platform Parity)?
```
