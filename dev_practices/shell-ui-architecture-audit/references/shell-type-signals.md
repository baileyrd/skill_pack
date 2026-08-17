# Shell Type Signals

Use this reference to classify the target as `desktop`, `web`, or `cli`. The
correct classification drives which probe pack later phases load. When
multiple signals fire, the strongest evidence wins; record secondary
hypotheses in `findings.json` under `shellTypeSecondary`.

## Desktop Shell Signals

A desktop shell wraps a runtime (Tauri, Electron, Wails, .NET MAUI, native)
in OS-level window chrome. Signals:

| Signal                                      | Strength | Type                |
|---------------------------------------------|----------|---------------------|
| `src-tauri/tauri.conf.json`                 | Decisive | Tauri               |
| `src-tauri/Cargo.toml` with `tauri = ...`   | Decisive | Tauri               |
| `package.json` deps include `electron`      | Decisive | Electron            |
| `electron-builder.yml` / `electron.config.*`| Decisive | Electron            |
| `package.json` deps include `@wails/runtime`| Decisive | Wails               |
| `forge.config.*` / `electron-forge`         | Strong   | Electron            |
| `node_modules/electron`                     | Strong   | Electron            |
| `*.entitlements`, `Info.plist`              | Strong   | macOS native shell  |
| `.csproj` referencing `Microsoft.Maui`      | Decisive | .NET MAUI           |
| Window menu definitions in code (`Menu.setApplicationMenu`, `tauri::Menu`) | Strong | Desktop |
| Tray icon code (`SystemTray`, `Tray::new`)  | Strong   | Desktop             |
| Native dialog / file picker APIs in use     | Strong   | Desktop             |

If a desktop signal is decisive, the shell is `desktop` even if it also
ships a web bundle inside (which most desktop apps do).

## Web Shell Signals

A web shell renders inside a browser tab. Signals:

| Signal                                      | Strength |
|---------------------------------------------|----------|
| `index.html` at repo root with framework script tags | Strong |
| `vite.config.*`, `next.config.*`, `nuxt.config.*`, `svelte.config.*`, `astro.config.*`, `remix.config.*` | Strong |
| `package.json` deps include `react`/`vue`/`svelte`/`solid`/`qwik` and **no** desktop wrapper | Strong |
| `public/` directory with browser assets     | Medium   |
| Service worker (`sw.js`, `service-worker.ts`) | Medium |
| `manifest.webmanifest`                      | Medium   |
| Server-side framework only (Rails, Django, FastAPI + Jinja2, Phoenix LiveView) | Strong (treat as web) |

If both web and desktop signals fire, the desktop signal wins (the app is a
desktop shell that happens to embed web tech).

## CLI / TUI Shell Signals

A CLI / TUI shell renders to a terminal. Signals:

| Signal                                          | Strength | Stack                   |
|-------------------------------------------------|----------|-------------------------|
| `pyproject.toml` deps include `textual`         | Decisive | Textual (Python)        |
| `pyproject.toml` deps include `rich`            | Strong   | Rich (Python)           |
| `pyproject.toml` deps include `prompt_toolkit`  | Strong   | prompt_toolkit (Python) |
| `package.json` deps include `ink`               | Decisive | Ink (Node)              |
| `package.json` deps include `blessed` / `neo-blessed` | Strong | blessed (Node)        |
| `Cargo.toml` deps include `ratatui` / `tui`     | Decisive | Ratatui (Rust)          |
| `Cargo.toml` deps include `crossterm` and binary entrypoint | Strong | Rust TUI         |
| `go.mod` deps include `bubbletea` / `lipgloss`  | Decisive | Bubble Tea (Go)         |
| `package.json` `bin` field present, no UI deps  | Medium   | Plain CLI               |
| Entry point uses `argparse` / `clap` / `commander` / `cobra` | Medium | Plain CLI       |
| ANSI escape constants in source (`\x1b[`, `\033[`) | Medium | Custom TUI             |

For "shell UI" purposes, plain non-interactive CLIs (one-shot commands) are
in scope only for: command surface, persistence, and observability
dimensions. Layout / navigation / theming probes target TUIs specifically.
Phase 00 should ask the user whether to scope a plain CLI as a `cli` shell
or skip the audit entirely.

## Detection Procedure

1. **Read manifests first.** `package.json`, `Cargo.toml`, `pyproject.toml`,
   `go.mod`, `*.csproj`. Manifest evidence is the strongest signal.
2. **Read root config files.** `tauri.conf.json`, `electron-builder.yml`,
   `vite.config.*`, etc.
3. **Look at the entry points.** `main.rs`, `main.ts`, `__main__.py`,
   `cmd/main.go`. Entry imports often confirm classification.
4. **Look at the build outputs.** If `dist/` or `out/` contains a `.app`,
   `.exe`, or `.AppImage` → desktop. If only HTML/JS → web.
5. **Ask the user as a last resort.** If signals conflict or are absent
   (e.g., codebase wasn't shared, only a running app), ask explicitly:
   *"Where does this shell run — desktop window, browser tab, or terminal?"*

## Hybrid Cases

| Situation                                          | Classification         |
|----------------------------------------------------|------------------------|
| Tauri / Electron app with web build also deployed  | `desktop` (primary), record `web` as secondary |
| Web app with PWA installed mode                    | `web` (PWA is a deployment detail) |
| TUI that also has a web mode                       | Run the audit twice, once per surface |
| Server-rendered web with a thick CLI sibling       | `web` (the shell is the page) |

Record the primary classification in `findings.json.shellType` and any
secondary in `findings.json.shellTypeSecondary` (string array).
