# Phase 12 — Multi-Window / Multi-Instance

**This phase runs only when `findings.shellType === "desktop"`.** For
web and CLI shells, Phase 00 should have pre-filled this dimension as
`Skipped` and the orchestrator skips this file.

Audit the shell's behavior with multiple windows / instances: window
spawn, state sync, focus routing, close-last-window semantics per OS,
and recovery from crashes that affect a subset of windows.

---

## What we evaluate

| Concern               | Question                                          |
|-----------------------|---------------------------------------------------|
| Multi-window support  | Can the user open more than one window? How?      |
| Window relationships  | Independent? Linked (parent/child)? Shared state? |
| State sync            | Theme / persisted layout / auth flow across windows |
| Focus routing         | Keyboard shortcuts route to focused window only?  |
| Close-last-window     | Quits app? Stays alive in tray? Per-OS conventions? |
| Multi-instance        | Two app launches → second instance, or focus first?|
| File-handle conflicts | Two windows opening the same file → conflict?     |
| Per-window crash      | One window crash → others survive?                |
| Window roles          | Distinct kinds (main, settings, palette popup)?   |

---

## Static probes

### Tauri

```bash
# Static window declarations
cat src-tauri/tauri.conf.json | grep -A 30 '"windows"'

# Runtime window creation
rg -n 'WindowBuilder::new|tauri::WindowBuilder|window\.create' src-tauri/src/

# Window event listeners
rg -n 'window\.on_window_event|listen_global' src-tauri/src/

# Single-instance plugin
rg -n 'tauri-plugin-single-instance|single_instance' src-tauri/Cargo.toml src-tauri/src/

# IPC across windows
rg -n 'emit_to|emit_all|emit\b' src-tauri/src/
```

### Electron

```bash
# BrowserWindow creation sites
rg -n 'new BrowserWindow' --type ts --type js

# Single-instance lock
rg -n 'app\.requestSingleInstanceLock|second-instance' --type ts --type js

# Window-all-closed handler
rg -n 'window-all-closed|app\.quit|app\.dock\.show' --type ts --type js

# IPC routing across windows
rg -n 'webContents\.send|BrowserWindow\.fromWebContents' --type ts --type js
```

### Wails

```bash
rg -n 'WindowSetTitle|WindowReload|WindowExecJS' --type go --type ts
```

---

## Runtime probes

For each open window, capture:

```javascript
// Inside each window's WebView
(() => {
  return {
    label: window.__TAURI__?.window?.getCurrent?.()?.label || 'unknown',
    url: location.href,
    size: { w: window.innerWidth, h: window.innerHeight },
    isFocused: document.hasFocus(),
    isVisible: !document.hidden
  };
})()
```

Then run these scenarios:

### 1. Spawn a second window

- Trigger via the user-facing path (File → New Window, Cmd/Ctrl+N).
- Confirm a second window opens with its own state.
- Confirm both windows are listed in OS window switcher / dock / taskbar.

### 2. State sync

- Switch the theme in window A. Does window B reflect the change
  immediately, on focus, or only after relaunch?
- Resize / move panels in window A. Does the persisted layout apply to
  newly-spawned windows? Does it apply to existing windows?
- Authenticate / log out in window A. Does window B follow?

Record the sync model: **broadcast** (instant), **lazy** (on focus /
poll), **boot-only** (read on window create), or **independent** (no
sync, each window has own state).

### 3. Focus routing

- Open both windows. Bring window A to front.
- Trigger a global shortcut (registered via `globalShortcut` /
  `tauri::GlobalShortcut`). Which window receives it?
- Trigger a window-scoped shortcut. Confirm only the focused window acts.

### 4. Close-last-window behavior

This is one of the highest-impact divergence points across OSes.

- macOS convention: closing the last window does **not** quit. The app
  stays in the dock; clicking it re-spawns a window.
- Windows / Linux convention: closing the last window **does** quit
  (tray apps are an exception).

For each OS the app ships to:
- Close all windows.
- Confirm the app behaves per the OS's convention (or has a deliberate
  override that's documented).
- Confirm reopen-from-dock / tray spawns a new window in the right state.

### 5. Multi-instance / second launch

- Launch the app twice from the OS launcher.
- Confirm one of:
  - Second launch focuses the existing instance and exits (single-
    instance lock — most common modern default).
  - Second launch spawns a second instance (rare; intentional).
- If single-instance: pass any args from the second launch to the first
  (file open, deep link, etc.).

### 6. Per-window crash

- In one window: trigger a renderer-process panic (DevTools → Crash
  renderer, or use a known broken feature in dev).
- Confirm:
  - Other windows continue to function.
  - The crashed window can be recovered (relaunched) without restarting
    the app.
  - Crash is reported to telemetry (cross-check with Phase 11).

### 7. File-handle / shared-resource

If the app opens documents, projects, or any owned files:

- Open the same file in two windows.
- Modify in window A, save.
- Confirm window B notices (file watcher, refresh prompt) — or
  acknowledges its model is stale.
- Close window A unsaved, then close window B unsaved — confirm save
  prompts route correctly.

---

## Verdict rubric

### Pass

- Multi-window works smoothly. State sync model is documented or
  consistent.
- Close-last-window matches OS convention on every shipped OS.
- Single-instance lock implemented (or single-instance is impossible
  intentionally).
- Per-window crashes don't take the app down.
- Global shortcuts route to focused window.

### Warn

- State sync inconsistent (theme syncs, layout doesn't, or vice versa).
- Close-last-window behavior is the same on all OSes despite shipping
  to multiple (one of them violates conventions).
- Second instance launches a duplicate process when single-instance
  was intended.

### Fail

- Closing the last window quits the app silently with unsaved data on
  any OS.
- Per-window crash kills the entire app process.
- State sync corrupts shared state (e.g., theme tokens partially apply,
  leaving windows mismatched).
- Multi-instance launches conflict on shared persisted state and
  corrupt it.

### Skipped

- The app intentionally supports only one window. Mark
  `verdict: "Skipped"` with `skipReason: "Single-window app by design;
  no contribution surface for additional windows."`. (This is the
  common case for many desktop apps.)

---

## Severity examples

- **Critical**: closing the last window discards unsaved work without
  warning.
- **High**: per-window crash kills the whole app; theme switch corrupts
  one window leaving an unreadable state.
- **Medium**: state sync is boot-only — open windows ignore changes
  until relaunch.
- **Low**: window stacking order on macOS doesn't match expectation
  after spawning a child window.

---

## Findings entry schema

```json
{
  "id": "12-multi-window",
  "name": "Multi-Window / Multi-Instance",
  "verdict": "Fail",
  "verdictRationale": "Single-instance lock works. State sync is boot-only — theme and layout changes don't propagate to existing windows. Per-window crash kills entire app on Tauri (no recovery).",
  "evidence": [
    { "kind": "snippet", "ref": "src-tauri/src/main.rs:88", "summary": "single_instance plugin registered" },
    { "kind": "snippet", "ref": "src/stores/theme.ts:42", "summary": "Theme stored in window-local store, not synced via Tauri events" },
    { "kind": "screenshot", "ref": "/tmp/shell-audit/12-mismatched-theme.png" },
    { "kind": "log", "ref": "/tmp/shell-audit/12-renderer-crash.log" }
  ],
  "findings": [
    {
      "id": "SH-090",
      "title": "Theme switch doesn't propagate to other open windows",
      "severity": "High",
      "description": "Switching themes in window A leaves window B in the previous theme. Each window holds its own theme store and the change isn't broadcast via `emit_all`. Users notice immediately when they have two windows side-by-side.",
      "evidence": ["src/stores/theme.ts:42", "screenshot-12-mismatched-theme.png"],
      "remediation": "Move theme state to a Tauri-managed singleton; emit a `theme-changed` event to all windows on switch; subscribe in each window's bootstrap.",
      "scope": "all multi-window sessions",
      "confidence": "high"
    }
  ],
  "completedAt": "<ISO datetime>"
}
```

---

## Checkpoint

```
Phase 12 complete — Multi-Window: Fail

Top issues:
  • [High] Theme switch doesn't propagate to other open windows
  • [High] Layout persistence is boot-only (existing windows don't update)
  • [Medium] Renderer crash in one window restarts the whole app

Findings recorded: 4 (2 High, 1 Medium, 1 Low)
Proceed to Phase 13 (Persistence)?
```
