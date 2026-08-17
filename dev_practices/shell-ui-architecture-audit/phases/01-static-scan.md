# Phase 01 — Static Scan

Inventory the codebase. Build a structural map that later dimension
phases reference: where the shell lives, what framework owns it, how the
build works, what the design system looks like in source.

This phase is read-only static analysis. No runtime, no probes.

---

## What this phase does

1. Walk the repository tree (one level deep, then targeted deeper reads).
2. Identify the framework, build tool, and entry points.
3. Locate the shell layer — the files that define the outer chrome,
   layout, and navigation.
4. Inventory the design system / token source.
5. Write a `staticInventory` object to `findings.json`.

If the audit is runtime-only (no code), skip this phase and write
`staticInventory: { available: false }`.

---

## Step 1 — Top-level walk

```bash
ls -la <repo-root>
cat <repo-root>/{package.json,Cargo.toml,pyproject.toml,go.mod}  2>/dev/null
cat <repo-root>/{tauri.conf.json,electron-builder.yml,vite.config.*,next.config.*}  2>/dev/null
```

Record manifest type, declared dependencies of interest (UI frameworks,
state libraries, design system packages, plugin SDKs), and build tools.

For monorepos: identify the package that owns the shell (look for
`packages/app-shell`, `apps/desktop`, `crates/shell`, or similar). The
audit focuses on that package.

---

## Step 2 — Locate the shell layer

The shell layer is whatever code defines:
- The outermost layout component (regions, slots).
- The router or navigation skeleton.
- The window / app frame setup.
- The provider stack (theme, auth, query client, error boundary).
- The persistent UI furniture (menus, command palette, status bar).

Common locations by stack:

| Stack            | Likely shell paths                                      |
|------------------|---------------------------------------------------------|
| Next.js (App Router) | `app/layout.tsx`, `app/(shell)/**`, `app/providers.tsx` |
| Next.js (Pages)  | `pages/_app.tsx`, `components/Layout/*`                 |
| Vite + React     | `src/App.tsx`, `src/shell/**`, `src/layouts/**`         |
| Vue / Nuxt       | `app.vue`, `layouts/default.vue`                        |
| SvelteKit        | `src/routes/+layout.svelte`, `src/lib/shell/**`         |
| Astro            | `src/layouts/**`                                        |
| Remix            | `app/root.tsx`, `app/routes/_app.tsx`                   |
| Tauri (frontend) | same as web stack above + `src-tauri/src/**` for window setup |
| Electron         | `main.ts` / `main.js` (main process) + renderer's web stack |
| Textual          | `app.py` with `App` subclass + `screens/**` + `*.tcss` files |
| Ratatui          | `src/main.rs`, `src/ui/**`, `src/app.rs`                |
| Bubble Tea       | `cmd/main.go`, `internal/ui/**` with `tea.Model` types  |

Use `rg` / `grep` / `find` to confirm presence:

```bash
# Web — look for top-level layout
rg -l '<html|<body|export default function (Root|Layout|App|Shell)' \
   --type ts --type tsx --type vue --type svelte --type astro

# Tauri — window builders
rg -n 'WindowBuilder::new|tauri::WindowBuilder' src-tauri/

# Electron — BrowserWindow creation
rg -n 'new BrowserWindow' --type ts --type js

# Textual — App + Screen subclasses
rg -n 'class .*\((App|Screen|Container)\)' --type py

# Ratatui — TUI setup
rg -n 'Terminal::new|enable_raw_mode|Frame<' --type rust
```

Record the discovered paths in `staticInventory.shellLayer.paths`.

---

## Step 3 — Inventory the build pipeline

Identify how the shell is built and shipped:

- **Bundler**: Vite, webpack, Turbopack, Rollup, esbuild, Bun, raw tsc?
- **Compiler**: SWC, Babel, tsc?
- **CSS pipeline**: PostCSS, Tailwind JIT, vanilla-extract, CSS Modules,
  styled-components, Emotion, CSS-in-JS, plain CSS, Sass?
- **Asset pipeline**: how are fonts / icons / images served?
- **Production output**: where do built files end up? (`dist/`, `build/`,
  `out/`, `target/release/`, `src-tauri/target/release/`)

This matters for performance (Phase 07) and theming (Phase 08).

---

## Step 4 — Inventory the design system

Look for design tokens in source:

```bash
# Tailwind config
cat tailwind.config.{js,ts,mjs} 2>/dev/null

# CSS variable definitions
rg -n '^\s*--[a-z-]+\s*:' --type css

# CSS-in-JS theme objects
rg -n 'createTheme|defineTheme|themeOptions|colors\s*:' --type ts --type tsx --type js

# Stitches / vanilla-extract token files
fd -t f 'tokens|theme' --extension ts --extension css

# shadcn/ui marker
fd -t f 'components.json'
```

Record:
- Token source location(s)
- Number of named color tokens
- Whether a dark mode variant exists
- Density / spacing scale
- Typography scale

---

## Step 5 — Inventory the provider / context stack

Most modern shells wrap children in a stack of providers. Order matters
(theme outside auth outside query client, etc.). Inventory it:

```bash
# React app — find the provider stack
rg -n '<.*Provider' --type tsx | head -50

# Vue / Nuxt
rg -n 'app\.provide|provide\s*\(' --type vue --type ts

# Svelte stores
rg -n 'writable\(|readable\(|derived\(' --type svelte
```

Record each provider in order, with file path. Findings later phases will
reference: "the theme provider sits below the error boundary, so a theme
crash takes down the whole app" → relevant to 08 theming and 11
observability.

---

## Step 6 — Detect plugin / extension scaffolding

```bash
# Plugin / extension keywords across the shell
rg -n 'registerPlugin|definePlugin|registerExtension|defineExtension|registerCommand|registerAction' --type ts --type tsx --type js --type rust --type py
```

If found, note the registration mechanism, the SDK location, and the
contribution points. This becomes input to Phase 10 (extensibility).

---

## Step 7 — Write to findings.json

Append to `findings.staticInventory`:

```json
{
  "available": true,
  "shellLayer": {
    "paths": ["app/layout.tsx", "app/providers.tsx", "..."],
    "framework": "Next.js 15 App Router",
    "compiler": "SWC",
    "bundler": "Turbopack",
    "cssPipeline": "Tailwind v4 + CSS modules",
    "renderingMode": "RSC + client islands"
  },
  "designSystem": {
    "tokenSource": "tailwind.config.ts + css/tokens.css",
    "colorTokens": 42,
    "darkMode": "class-based",
    "spacingScale": "4px base, 0.5×–96× steps",
    "typeScale": "12/14/16/18/24/32/48"
  },
  "providerStack": [
    { "name": "ErrorBoundary", "path": "app/error-boundary.tsx" },
    { "name": "ThemeProvider", "path": "app/providers.tsx:18" },
    { "name": "QueryClientProvider", "path": "app/providers.tsx:24" },
    { "name": "AuthProvider", "path": "app/providers.tsx:31" }
  ],
  "extensionScaffolding": {
    "present": false,
    "reason": "No registerPlugin / defineExtension calls found."
  }
}
```

Update `phasesCompleted: ["00-preparation", "01-static-scan"]`.

---

## Output of this phase

- A complete `staticInventory` object in `findings.json`.
- A printed checkpoint summary listing: shell paths, framework version,
  build pipeline, design system, provider stack, and extensibility status.

Move on to Phase 02 (`phases/02-runtime-bootstrap.md`).
