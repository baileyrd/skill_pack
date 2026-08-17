# Phase 09 — Cross-Platform Parity

Audit how consistently the shell behaves across the platforms it ships
to. For desktop apps: macOS / Windows / Linux. For web apps: browsers
and viewport classes (mobile / tablet / desktop). For TUIs: terminals
and color profiles.

The goal is not pixel-perfect parity — it's *intentional* behavior at
each platform's expectations. A shell that ignores macOS conventions on
macOS is failing parity even if it looks identical to the Windows build.

---

## What we evaluate

| Concern              | Question                                          |
|----------------------|---------------------------------------------------|
| Platforms targeted   | Which OSes / browsers / terminals are shipped to? |
| Platform conventions | Does the shell honor each platform's expectations? |
| Native chrome        | Window controls, menu bar, scrollbars, focus rings|
| Input idioms         | Right-click menus, drag-drop, keyboard chords     |
| File system access   | Path conventions, native dialogs, permissions     |
| Notifications        | Native notification surface, badge / dock         |
| Auto-update          | Per-platform update mechanism (sparkle, squirrel) |
| Accessibility APIs   | macOS VoiceOver, Win Narrator, Linux AT-SPI       |
| Browser parity (web) | Chromium / Firefox / WebKit feature alignment     |
| Mobile / tablet (web)| Touch targets, viewport, on-screen keyboards      |
| Terminal degradation | TUI behaves on limited / mixed terminals          |

---

## Static probes

### Desktop

```bash
# Tauri targets
cat src-tauri/tauri.conf.json | grep -E 'targets|bundle|identifier'

# Electron platform-specific code
rg -n 'process\.platform\s*===\s*[\'"](darwin|win32|linux)[\'"]' --type ts --type js
rg -n 'os\.platform\(\)|os\.type\(\)' --type ts --type js

# Tauri platform-specific
rg -n 'cfg\(target_os' src-tauri/src/

# Per-platform asset selection
rg -n 'icon\.(icns|ico|png)' src-tauri/ assets/ build/
```

### Web

```bash
# Browser-specific feature detection
rg -n 'navigator\.userAgent|isChrome|isFirefox|isSafari|isMobile|isTouch' --type ts --type tsx

# Touch / pointer events
rg -n 'onTouchStart|onPointerDown|@touch|@click|@pointer' --type tsx --type vue --type svelte

# Viewport / meta
rg -n 'viewport.*width=device-width|maximum-scale|user-scalable' --type html --type tsx

# Polyfills
cat package.json | grep -E 'core-js|polyfill|@babel/preset-env'
```

### CLI / TUI

```bash
# Terminal capability checks
rg -n 'TERM|COLORTERM|terminfo|tcgetattr|isatty' --type rust --type py --type go --type ts

# Windows-specific TUI handling
rg -n 'winapi|windows-rs|os\.name\s*==\s*[\'"]nt[\'"]' --type rust --type py
```

---

## Runtime probes

### Desktop

This phase requires testing on each shipped OS, ideally. If only one OS
is available, mark the others `confidence: low` and document what was
verified.

For each OS the app ships to:

1. Native window controls — close / minimize / maximize buttons in the
   right place and behaving as expected.
2. Menu bar — present per-window on Win/Linux, in the global bar on
   macOS, with the right standard items.
3. Right-click context menus — system-native or in-app? Consistent?
4. Drag and drop — files into the shell? Items between regions?
5. Keyboard chords — Cmd vs Ctrl, Option vs Alt; OS-specific shortcuts
   (Cmd+Q, Cmd+W, Cmd+, on macOS) wired up?
6. File dialogs — using the OS-native picker?
7. Notifications — fired through the native API?
8. Dock / taskbar — badge, jump list, custom items?
9. Dark mode — follows OS appearance setting?
10. Accessibility API — try VoiceOver / Narrator briefly on the shell.

### Web

For each browser × viewport class:

1. **Chromium** (Chrome/Edge/Brave/Arc) — desktop & mobile.
2. **Firefox** — desktop & mobile.
3. **WebKit** (Safari/iOS) — desktop & mobile.
4. **Mobile gestures**: swipe, pinch, two-finger scroll all behave?
5. **On-screen keyboard**: don't cover focused inputs?
6. **Viewport meta** correct? No accidental zoom-out?
7. **Touch target size** ≥ 44×44 CSS pixels for mobile interactions?
8. **Print stylesheet** if shell has printable views?

### CLI / TUI

Run the app under a matrix of terminals. At minimum:

| Terminal           | Platform       | Notable      |
|--------------------|----------------|--------------|
| Apple Terminal.app | macOS          | 256-color, no truecolor by default in older versions |
| iTerm2             | macOS          | full feature set |
| WezTerm / Kitty    | cross-platform | truecolor + images |
| Alacritty          | cross-platform | truecolor, no images |
| Windows Terminal   | Windows        | recent versions support truecolor |
| Old `cmd.exe`      | Windows        | very limited; user may still hit it |
| GNOME Terminal     | Linux          | varies by version |
| `tmux` / `screen`  | overlay        | strips capabilities; very common |
| `dumb` (TERM=dumb) | minimal        | no escape codes at all |

For each terminal the user supports, capture: startup, main view, theme
switch, smallest size, any TUI-only features (sixel images, hyperlinks).

---

## Verdict rubric

### Pass

- Every shipped platform / terminal exhibits intentional behavior.
- Per-platform conventions honored where the user notices (menu, chords,
  dialogs, controls).
- Web: browsers & viewport classes pass core flows.
- TUI: degrades cleanly on limited terminals.

### Warn

- One platform has a noticeable inconsistency the team accepts.
- One browser / viewport has minor issues that don't block flows.
- TUI ships features that no-op on `tmux` without surfacing it.

### Fail

- A shipped platform has a broken flow.
- macOS conventions ignored on macOS (e.g., Cmd+W closes the app instead
  of the window) — or vice versa.
- Mobile web shell unusable (touch targets too small, keyboard covers
  inputs).
- TUI fails to render on standard `xterm-256color`.

---

## Severity examples

- **Critical**: Linux build segfaults on Ubuntu LTS during launch.
- **High**: macOS Cmd+, doesn't open Settings; Windows Alt+F4 doesn't
  close the window; mobile shell unusable below 400px viewport.
- **Medium**: scrollbar styling clashes with native on Windows but
  doesn't break flows.
- **Low**: focus ring slightly different shape on Firefox vs Chrome.

---

## Findings entry schema

```json
{
  "id": "09-cross-platform",
  "name": "Cross-Platform Parity",
  "verdict": "Warn",
  "verdictRationale": "macOS, Windows, Linux all functional. macOS conventions partially honored: app menu present, but Cmd+, doesn't open Preferences. Windows scrollbar styling clashes with native theme.",
  "evidence": [
    { "kind": "screenshot", "ref": "/tmp/shell-audit/09-macos-app-menu.png" },
    { "kind": "screenshot", "ref": "/tmp/shell-audit/09-windows-scrollbar.png" },
    { "kind": "snippet", "ref": "src-tauri/src/menu.rs:48", "summary": "macOS Preferences accelerator missing" }
  ],
  "findings": [
    {
      "id": "SH-061",
      "title": "macOS Cmd+, does not open Preferences",
      "severity": "Medium",
      "description": "On macOS users expect Cmd+, to open the app's settings. The accelerator is registered but bound to a no-op handler. Users have to mouse to the menu.",
      "evidence": ["src-tauri/src/menu.rs:48", "screenshot-09-macos-app-menu.png"],
      "remediation": "Wire the Preferences menu item to navigate to /settings or invoke the existing settings command.",
      "scope": "macOS only",
      "confidence": "high"
    }
  ],
  "completedAt": "<ISO datetime>"
}
```

---

## Checkpoint

```
Phase 09 complete — Cross-Platform Parity: Warn

Top issues:
  • [Medium] macOS Cmd+, does not open Preferences (no-op handler)
  • [Medium] Windows scrollbar styling clashes with native theme
  • [Low]    Linux: focus ring drawn 1px wider than other platforms

Findings recorded: 5 (0 High, 3 Medium, 2 Low)
Proceed to Phase 10 (Extensibility)?
```
