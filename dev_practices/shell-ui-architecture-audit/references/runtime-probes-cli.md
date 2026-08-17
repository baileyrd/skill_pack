# Runtime Probes — CLI / TUI Shell

Probes for terminal-rendered shells: Textual / Rich / prompt_toolkit
(Python), Ink (Node), Ratatui / Crossterm (Rust), Bubble Tea (Go), and
plain CLIs.

A TUI is a "shell" in the same sense as a desktop or web app: it has
regions (header, body, footer, status), navigation (key bindings, focus
between widgets), state (loading / error / empty), theming (color palette,
density), and persistence (last-used view, panel sizes). The probes
differ — there's no DOM to query — but the dimensions are the same.

---

## Probe Index

| Probe                  | Used by phase                            |
|------------------------|------------------------------------------|
| `tuiFrameworkDetect`   | 02 runtime-bootstrap                     |
| `terminalCapability`   | 02 runtime-bootstrap, 09 cross-platform  |
| `widgetTreeDump`       | 03 layout                                |
| `keyBindingMap`        | 04 navigation, 05 accessibility          |
| `paletteAndContrast`   | 08 theming, 05 accessibility             |
| `screenStateCapture`   | 03, 06, 07                               |
| `streamTeeProbe`       | 11 observability                         |
| `configFileAudit`      | 13 persistence                           |
| `pluginRegistryProbe`  | 10 extensibility                         |

---

## tuiFrameworkDetect

Static — read the manifest:

| Manifest entry                       | Framework         |
|--------------------------------------|-------------------|
| `textual` in `pyproject.toml`        | Textual (Python)  |
| `rich` only                          | Rich (Python)     |
| `prompt_toolkit`                     | prompt_toolkit    |
| `ink` in `package.json`              | Ink (React in TTY)|
| `blessed` / `neo-blessed`            | blessed (Node)    |
| `ratatui` / `tui` in `Cargo.toml`    | Ratatui (Rust)    |
| `bubbletea` in `go.mod`              | Bubble Tea (Go)   |

Runtime — most TUIs expose introspection only via in-app dev tooling:

- Textual: run with `textual run --dev <module>` and use
  `textual console` to attach a remote dev console. The dev console gives
  you the widget tree, log stream, and CSS info.
- Ink: instrument with `DEBUG=ink:*`.
- Ratatui: most apps don't expose runtime introspection — rely on log
  files (`tracing` crate) and screen capture.

---

## terminalCapability

Capture the terminal environment the shell runs in:

```bash
echo "TERM=$TERM"
echo "COLORTERM=$COLORTERM"
echo "TERM_PROGRAM=$TERM_PROGRAM"
echo "LANG=$LANG"
tput colors 2>/dev/null
tput cols && tput lines
```

| Env var         | Common values & meaning                                      |
|-----------------|--------------------------------------------------------------|
| `TERM`          | `xterm-256color` (256), `xterm-kitty` (truecolor + kitty graphics), `screen` (limited) |
| `COLORTERM`     | `truecolor` or `24bit` → 24-bit color supported               |
| `TERM_PROGRAM`  | `iTerm.app`, `vscode`, `WezTerm`, `Alacritty`, etc.           |

**Cross-platform parity matrix** — what the shell must degrade gracefully
across:

| Capability        | Modern (kitty/wezterm/iterm) | Standard (xterm-256) | Limited (screen, tmux+old) | Windows console |
|-------------------|------------------------------|----------------------|----------------------------|-----------------|
| 24-bit color      | ✓                            | dithered             | none                       | recent only     |
| Bold + dim        | ✓                            | ✓                    | sometimes                  | ✓               |
| Box-drawing       | ✓                            | ✓                    | ASCII fallback             | ✓               |
| Mouse             | ✓                            | ✓                    | ✓                          | ✓               |
| Hyperlinks (OSC8) | ✓                            | partial              | none                       | partial         |
| Synchronized output| ✓                           | partial              | none                       | rare            |
| Sixel / Kitty img | varies                       | none                 | none                       | none            |

A shell that hard-codes truecolor escape sequences without checking
`COLORTERM` is a High finding for any user with a limited terminal.

---

## widgetTreeDump

**Textual** — attach to a running app:

```bash
# Terminal A: run the app
textual run --dev your.module:YourApp

# Terminal B: console with widget tree
textual console -v
```

In the console, `tree` prints the live widget hierarchy. Save it to
`findings/textual-tree.txt`.

**Ink** — Ink doesn't have a built-in tree dumper, but `INK_DEBUG=1` plus a
custom render hook can dump the React tree at intervals.

**Ratatui** — instrument a debug key (e.g., `F12`) that calls
`tracing::debug!("{:#?}", frame.area())` for every widget the app draws.

For each region in the widget tree, record:
- Name / type (Header, Body, Sidebar, Footer, StatusBar)
- Size (rows × cols)
- Whether it's resizable or fixed
- Visible at startup yes/no

---

## keyBindingMap

**Textual** — `App.BINDINGS` and per-screen `BINDINGS` lists:

```bash
rg -n '\bBINDINGS\b' --type py
rg -n 'Binding\s*\(' --type py
```

**Ink** — `useInput` hooks:

```bash
rg -n 'useInput\b' --type ts --type tsx
```

**Ratatui** — match arms in event loops:

```bash
rg -n 'KeyCode::|KeyEvent\s*\{' --type rust
```

For each binding, record: combo, action, scope (global / screen / widget),
and whether it's discoverable (in a help screen, footer hint, or palette).

**Findings:**
- No global help screen / footer hint → Medium.
- Bindings collide between scopes silently → High.
- Common action without keyboard binding → Medium per action.
- Mouse-only paths (no keyboard equivalent) → High (a11y).

---

## paletteAndContrast

Inventory the color palette:

**Textual** — `App.CSS` and `*.tcss` files:

```bash
rg -n 'color|background' app.tcss styles/*.tcss
```

**Rich** — search for `Style(...)` and `Color(...)` constructors:

```bash
rg -n 'rich\.style|Style\s*\(|Color\s*\(' --type py
```

For each color, compute the WCAG contrast ratio against the surrounding
background. Use 4.5:1 (AA normal text) and 3:1 (AA large text / UI
components) as thresholds.

**Findings:**
- Any text below 4.5:1 contrast → High a11y finding.
- Theme switch loses contrast on a subset of widgets → High.
- Truecolor escapes used without a 256-color fallback → Medium (degrade).

---

## screenStateCapture

Capture the rendered screen at key moments. Two methods:

**asciinema** — record an interactive session:

```bash
asciinema rec /tmp/audit-session.cast
# perform interaction, then exit
asciinema cat /tmp/audit-session.cast > /tmp/audit-session.txt
```

The `.cast` file is JSON with timestamped output frames; use it to extract
specific frames for the report.

**`script(1)`** — log everything to a typescript:

```bash
script -q /tmp/audit-session.log
# interact
exit
```

Strip ANSI escapes for the report:

```bash
sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' /tmp/audit-session.log > /tmp/audit-clean.txt
```

States to capture:
- Startup splash → first useful frame
- Main view → resting state
- Navigation between top-level views
- Loading / fetching state
- Error state (force one, e.g., disconnect network)
- Empty state
- Theme switch (if supported)
- Smallest supported size (e.g., 80×24)
- Largest reasonable size (e.g., 200×60)

---

## streamTeeProbe

Many TUIs hide their own logs behind the screen. Tee them to disk for
analysis:

```bash
# Run the app with stderr captured
your-tui-binary 2> /tmp/audit-stderr.log

# Or with structured logging
RUST_LOG=debug your-tui-binary 2> /tmp/audit-tracing.log

# Python apps using stdlib logging
python -m your.tui --log-file /tmp/audit-app.log
```

**Findings to extract:**
- Are errors logged at all?
- Are user-facing errors (shown in the TUI) also written to logs?
- Is there a debug overlay / log viewer accessible from inside the TUI?
- Does the app keep a rolling log file in `~/.local/share/<app>/logs/`?

---

## configFileAudit

TUI shells typically persist user prefs to disk. Common locations:

| Platform | Path                                                      |
|----------|-----------------------------------------------------------|
| Linux    | `$XDG_CONFIG_HOME/<app>/` (default `~/.config/<app>/`)    |
| macOS    | `~/Library/Application Support/<app>/` or `~/.config/<app>/` |
| Windows  | `%APPDATA%/<app>/`                                        |

Capture before/after state:

```bash
# Snapshot before
cp -r ~/.config/your-app /tmp/before-config

# Use the app, change settings
your-app

# Diff
diff -u /tmp/before-config ~/.config/your-app
```

**Findings:**
- Config not written → Medium.
- Config written but not read on next launch → High.
- Config corruption locks user out → Critical.
- Config holds secrets in plaintext → High security finding.

---

## pluginRegistryProbe

If the TUI supports plugins / extensions:

**Static**:
```bash
rg -n 'register_plugin|load_plugin|plugins\b|extensions\b' --type py --type rust --type ts
```

**Runtime** — most TUIs expose plugin lists via a command:
```bash
your-tui --list-plugins
your-tui plugin list
```

Record:
- Discovery mechanism (entry points, directory scan, manifest file)
- Isolation (separate process, sandbox, in-process — in-process is the
  norm for TUIs and is acceptable; record it as informational)
- Failure mode (one plugin crash → shell crash, or recovered?)
- Hot reload support
