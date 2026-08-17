# Phase 04 — Navigation & Routing

Audit how users move through the shell: information architecture, routing
mechanism, deep-linking, history behavior, breadcrumbs, command palette,
and native menu (desktop) or key-driven navigation (TUI).

---

## What we evaluate

| Concern              | Question                                                |
|----------------------|---------------------------------------------------------|
| IA & wayfinding      | Can a user state where they are and how they got there? |
| Routing mechanism    | Server / client / hybrid? Match the framework's idiom?  |
| Deep linking         | Does a URL / command-line arg restore full state?       |
| History behavior     | Back / forward work? Browser/native expectations met?   |
| Breadcrumbs          | Present where useful, accurate, navigable?              |
| Command palette      | Reaches every shell-level action? Discoverability?      |
| Native menu (desktop)| Standard items present per OS? Accelerators wired up?   |
| Keyboard nav (TUI)   | Every action reachable; bindings discoverable           |
| Active state         | Current route reflected in nav + breadcrumbs + title    |
| Scroll restoration   | Per-route scroll position restored on back/forward      |

---

## Static probes

### Web

```bash
# Discover the routing mechanism
fd -t f 'router|routes|route\.config' src/ app/

# Next.js: app router or pages router?
ls app/ pages/ 2>/dev/null

# React Router declarations
rg -n '<Route\b|createBrowserRouter|createRoutesFromElements' --type ts --type tsx

# TanStack Router
rg -n 'createRoute|createRootRoute|createFileRoute' --type ts --type tsx

# Vue Router
rg -n 'createRouter\(|defineRouter\(' --type ts --type vue

# SvelteKit page tree
fd -t f '\+page|\+layout' src/routes/

# Hypermedia (HTMX / Datastar)
rg -n 'data-on-click|hx-get|hx-post|data-on-load' --type html --type tsx --type vue
```

### Desktop

```bash
# Tauri menu definitions
rg -n 'Menu::new|MenuBuilder|tauri::Menu' src-tauri/

# Electron menu templates
rg -n 'Menu\.buildFromTemplate|setApplicationMenu' --type ts --type js

# Deep-link / custom scheme registration
rg -n 'deep_link|setAsDefaultProtocolClient|protocol\.handle' --type rust --type ts --type js
```

### CLI / TUI

```bash
# Textual: screens & screen-stacking
rg -n 'class.*\(Screen\)|push_screen|switch_screen|pop_screen' --type py

# Ratatui: tabs / page state machines
rg -n 'enum .*Page|enum .*Tab|enum .*Screen' --type rust

# Bubble Tea: model transitions
rg -n 'tea\.Cmd|case.*KeyMsg' --type go

# Key bindings (covered more in Phase 05)
rg -n '\bBINDINGS\b' --type py
rg -n 'KeyCode::|KeyEvent\s' --type rust
```

### Command palette

```bash
# Common palette libraries
rg -n 'cmdk|kbar|command-palette|@radix-ui/react-dialog.*command' --type ts --type tsx

# Tauri / Electron equivalent: global shortcuts
rg -n 'globalShortcut|register_shortcut' --type ts --type rust
```

---

## Runtime probes

### Web

From `references/runtime-probes-web.md`:

1. `routeMap` — discover declared and link-derived routes.
2. Click through the primary navigation. For each transition, capture:
   - URL after click
   - Title after click
   - Active-state indicator (which nav item is highlighted)
   - Active route reflected in breadcrumbs (if present)
3. Hit browser back / forward buttons. Confirm:
   - URL restores
   - Scroll position restores (or doesn't, intentionally)
   - In-page state restores (open accordions, selected tabs)
4. Direct-load a deep link (paste URL into a fresh tab). Confirm full
   state restoration without prior navigation.
5. `commandPaletteProbe` — open the palette via known triggers
   (Mod+K, Mod+Shift+P, Mod+/). Type and inventory which actions are
   reachable: navigation only? Settings? Theme switch? Plugin actions?

### Desktop

1. Inventory the native menu via `nativeMenuMap` (desktop probes).
2. Test every accelerator listed; confirm each invokes the right action.
3. Test deep-link / custom URL scheme handling (open the registered
   scheme from another app and confirm correct navigation).
4. Inside the WebView: same web probes (`routeMap`,
   `commandPaletteProbe`).

### CLI / TUI

1. Run the app, trigger every top-level navigation key. Capture screens
   before / after.
2. Confirm a help screen / footer hint exists and lists current bindings.
3. If the app supports launching with a sub-command or argument that
   jumps directly to a view, test it (TUI deep-link equivalent).

---

## Verdict rubric

### Pass criteria

- Routing mechanism is the framework's recommended idiom and used
  consistently.
- Every UI link / nav action has a stable URL or command equivalent.
- Deep links restore full state.
- Back / forward / history work as expected for the platform.
- Active route is consistently reflected in nav indicator + breadcrumbs +
  document/window title.
- Command palette (web/desktop) or footer hint + help screen (TUI)
  reaches every shell-level action.
- Native menu (desktop) covers the platform's expected baseline (App,
  File, Edit, View, Window, Help on macOS; File / Edit / View / Window /
  Help on Win/Linux as appropriate) and accelerators work.

### Common Warn signals

- Some shell actions are reachable only via clicking a specific button
  (no palette / menu / shortcut).
- Active state lags one render behind the URL.
- Scroll restoration on back navigation is inconsistent.
- Native menu missing standard items the OS expects.

### Common Fail signals

- Deep links 404 or fail to restore state.
- Back / forward breaks or causes data loss.
- Command palette can't reach > 30% of shell-level actions.
- Native menu accelerators silently no-op.
- Routing mixes incompatible mechanisms (e.g., Next.js Pages + custom
  client router).

---

## Severity examples

- **Critical**: deep linking is broken everywhere; users lose state on
  every refresh.
- **High**: command palette / menu missing > 30% of shell actions;
  back-button data loss in a workflow.
- **Medium**: scroll restoration inconsistent; active-state highlighter
  bug on one nav item.
- **Low**: tooltip on a nav item shows the wrong shortcut.

---

## Findings entry schema

```json
{
  "id": "04-navigation",
  "name": "Navigation & Routing",
  "verdict": "Pass | Warn | Fail | Unknown",
  "verdictRationale": "...",
  "evidence": [
    { "kind": "probe", "ref": "routeMap", "summary": "12 declared routes, 14 link-derived" },
    { "kind": "probe", "ref": "commandPaletteProbe", "summary": "Palette opens on Mod+K" },
    { "kind": "screenshot", "ref": "/tmp/shell-audit/04-palette-open.png" },
    { "kind": "log", "ref": "/tmp/shell-audit/04-deeplink-trace.txt" }
  ],
  "findings": [
    {
      "id": "SH-014",
      "title": "Deep link to /settings/billing 404s after auth refresh",
      "severity": "High",
      "description": "A direct URL load to /settings/billing during an expired-token state redirects to /login but loses the original target. After login, the user lands on /dashboard, not /settings/billing.",
      "evidence": ["/tmp/shell-audit/04-deeplink-trace.txt:18", "src/auth/redirect.ts:42"],
      "remediation": "Capture the requested path before the auth redirect and append as `?next=` query param; restore on successful login.",
      "scope": "all auth-gated routes when token is expired",
      "confidence": "high"
    }
  ],
  "completedAt": "<ISO datetime>"
}
```

---

## Checkpoint

```
Phase 04 complete — Navigation & Routing: Warn

Top issues:
  • [High]   Deep links to auth-gated routes lose target after login
  • [Medium] Command palette covers ~70% of shell actions; missing theme switch and plugin commands

Findings recorded: 4 (1 High, 2 Medium, 1 Low)
Proceed to Phase 05 (Accessibility)?
```
