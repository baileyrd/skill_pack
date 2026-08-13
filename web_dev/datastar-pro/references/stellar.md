# Datastar Pro — Stellar CSS Reference

Stellar CSS is the first-party CSS framework for the Datastar ecosystem. It provides a
configurable design system via CSS custom properties (variables) with **no build step** —
it runs entirely in the browser.

> **Status:** Work-in-progress. Actively used on the [data-star.dev](https://data-star.dev)
> site but not yet released as a downloadable Pro feature. The API below reflects what is
> publicly known; expect changes before the stable release.

## What Stellar CSS Is

- A lightweight, browser-only CSS framework based on CSS custom properties
- Positioned between [OpenProps](https://open-props.style/) and [UnoCSS](https://unocss.dev/) —
  configurable like OpenProps, utility-aware like UnoCSS, but smaller and faster than either
- Zero build step — no PostCSS, no Tailwind config, no purging
- Designed to complement Datastar's inline `data-style` and `data-class` attributes
- Replaces the need for Tailwind CSS, which tends to bloat markup with utility classes

## Why Use Stellar CSS with Datastar

Datastar's built-in styling (`data-style`, `data-class`, `data-animate`) is powerful for
reactive, signal-driven appearance changes. Stellar CSS complements this by providing:

1. **Design tokens** — consistent spacing, colors, typography, and sizing via CSS variables
2. **Base styles** — sensible defaults for HTML elements without adding classes
3. **Theming** — swap design tokens to retheme an entire app without touching markup
4. **No class bloat** — unlike Tailwind, Stellar keeps your HTML clean

The two systems work together:
- **Stellar CSS** handles the static design system (tokens, base styles, theme)
- **Datastar attributes** handle dynamic, signal-driven style changes at runtime

## Current Usage Pattern

Since Stellar CSS is not yet publicly released, the recommended approach is:

### For Production Apps Today
Use Datastar's built-in styling attributes with CSS custom properties in a `<style>` block:

```html
<style>
  :root {
    /* Define your own design tokens */
    --color-primary: #4CAF50;
    --color-surface: #ffffff;
    --color-text: #333333;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 2rem;
    --radius-md: 8px;
    --font-sans: system-ui, -apple-system, sans-serif;
  }

  @media (prefers-color-scheme: dark) {
    :root {
      --color-primary: #66BB6A;
      --color-surface: #1a1a2e;
      --color-text: #e0e0e0;
    }
  }
</style>
```

Then reference tokens in `data-style` expressions:

```html
<div data-style='{"padding": "var(--spacing-md)", "backgroundColor": "var(--color-surface)", "color": "var(--color-text)", "borderRadius": "var(--radius-md)"}'>
  Content using design tokens
</div>
```

### When Stellar CSS Ships
Stellar will provide these tokens (and many more) out of the box, replacing the manual
`<style>` block above with a single script/link include. Generated code that uses CSS
custom properties today will be forward-compatible with Stellar CSS.

## Design Token Categories (Expected)

Based on the data-star.dev site's usage, Stellar CSS is expected to provide tokens for:

| Category | Example Variables | Purpose |
|----------|------------------|---------|
| Colors | `--color-primary`, `--color-surface`, `--color-text` | Semantic color palette |
| Spacing | `--spacing-xs` through `--spacing-xl` | Consistent whitespace |
| Typography | `--font-sans`, `--font-mono`, `--font-size-*` | Font families and sizes |
| Borders | `--radius-sm`, `--radius-md`, `--radius-lg` | Border radius tokens |
| Shadows | `--shadow-sm`, `--shadow-md`, `--shadow-lg` | Elevation system |
| Transitions | `--transition-fast`, `--transition-normal` | Duration presets |

## Integration with Datastar Attributes

### data-style + Stellar tokens
```html
<button data-style='{"padding": "var(--spacing-sm) var(--spacing-md)", "backgroundColor": "var(--color-primary)", "borderRadius": "var(--radius-md)", "color": "white"}'>
  Styled Button
</button>
```

### data-class + Stellar (when available)
```html
<!-- Stellar will likely provide utility classes that can be toggled reactively -->
<div data-class:dark-theme="$isDark">
  Theme-aware content
</div>
```

### Signal-driven theming with tokens
```html
<div data-signals:theme="'light'">
  <div data-style:backgroundColor="$theme === 'dark' ? 'var(--color-surface-dark)' : 'var(--color-surface-light)'"
       data-style:color="$theme === 'dark' ? 'var(--color-text-dark)' : 'var(--color-text-light)'">
    <button data-on:click="$theme = $theme === 'dark' ? 'light' : 'dark'">
      Toggle Theme
    </button>
  </div>
</div>
```

## When to Recommend Stellar CSS

| Scenario | Recommendation |
|----------|---------------|
| User asks for styled Datastar app | Use `data-style`/`data-class` with CSS custom property tokens (forward-compatible with Stellar) |
| User asks specifically for Stellar CSS | Explain WIP status, generate token-based approach that will be compatible |
| User asks for Tailwind + Datastar | Suggest CSS custom properties approach instead — cleaner markup, no build step, Stellar-compatible |
| User needs complex design system | Generate a `<style>` block with design tokens, note that Stellar will replace this |
| Simple demo or prototype | Inline styles via `data-style` are sufficient — no tokens needed |

## Key Points

1. Stellar CSS is a **first-party** companion to Datastar — not a generic third-party framework
2. It is **not yet released** — do not generate `<link>` or `<script>` tags for Stellar
3. Code using CSS custom properties today is **forward-compatible** with Stellar
4. Stellar does **not replace** `data-style`/`data-class` — it complements them with tokens
5. Unlike Tailwind, Stellar avoids class bloat — it uses CSS variables, not utility classes

## Sources

- [Datastar Pro page](https://data-star.dev/datastar_pro)
- [V1 and Beyond essay](https://data-star.dev/essays/v1_and_beyond)
