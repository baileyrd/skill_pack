# Runtime Probes — Desktop Shell

Reusable probes for desktop shells (Tauri, Electron, Wails, native). These
combine source-code inspection with live introspection from the embedded
WebView (where applicable).

Most desktop shells ship a web frontend inside a window — so the
`runtime-probes-web.md` probes also apply *inside* the WebView. This file
covers the parts that are unique to desktop: window chrome, native menus,
IPC surface, multi-window behavior, and OS integration.

---

## Probe Index

| Probe                    | Used by phase           |
|--------------------------|-------------------------|
| `desktopRuntimeDetect`   | 02 runtime-bootstrap    |
| `windowChromeAudit`      | 03 layout, 12 multi-window |
| `nativeMenuMap`          | 04 navigation           |
| `tauriCommandSurface`    | 10 extensibility        |
| `electronIpcSurface`     | 10 extensibility        |
| `multiWindowState`       | 12 multi-window         |
| `windowStateRestore`     | 13 persistence          |
| `osIntegrationProbe`     | 09 cross-platform       |

---

## desktopRuntimeDetect

Run inside the WebView via DevTools / `javascript_tool`:

```javascript
(() => {
  return {
    tauri: !!window.__TAURI__ ? {
      version: window.__TAURI__.version || null,
      coreApiKeys: Object.keys(window.__TAURI__).slice(0, 30)
    } : null,
    electron: !!(window.electronAPI || window.process?.versions?.electron) ? {
      version: window.process?.versions?.electron || null,
      contextIsolation: !window.require,  // require absent → isolation likely on
      preloadApiKeys: window.electronAPI ? Object.keys(window.electronAPI) : null
    } : null,
    wails: !!window.runtime ? { keys: Object.keys(window.runtime).slice(0, 30) } : null,
    userAgent: navigator.userAgent,
    platform: navigator.platform
  };
})()
```

**Static signals to cross-check (in source):**
- `src-tauri/tauri.conf.json` → `tauri.security.csp`, `tauri.windows[]`
- `src-tauri/Cargo.toml` → `tauri = { features = [...] }`
- `electron-builder.yml` / `package.json#build` → window defaults
- `main.ts` / `main.js` (Electron main process) → `BrowserWindow` constructor calls

---

## windowChromeAudit

Static — read the window config:

**Tauri** (`src-tauri/tauri.conf.json`):
```jsonc
{
  "tauri": {
    "windows": [{
      "title": "...",
      "width": 1200, "height": 800,
      "decorations": true,         // false = custom titlebar
      "transparent": false,
      "resizable": true,
      "minWidth": 800, "minHeight": 600,
      "fullscreen": false,
      "alwaysOnTop": false
    }]
  }
}
```

**Electron** (search `main.ts`/`main.js` for `BrowserWindow`):
```javascript
new BrowserWindow({
  frame: true,                     // false = custom titlebar
  titleBarStyle: 'hiddenInset',
  webPreferences: {
    nodeIntegration: false,        // MUST be false in modern apps
    contextIsolation: true,        // MUST be true
    sandbox: true                  // recommended
  }
})
```

Runtime — inside the WebView:

```javascript
(() => {
  return {
    windowOuterSize: { w: window.outerWidth, h: window.outerHeight },
    windowInnerSize: { w: window.innerWidth, h: window.innerHeight },
    chromeOverhead: {
      vertical: window.outerHeight - window.innerHeight,
      horizontal: window.outerWidth - window.innerWidth
    },
    customTitlebarPresent: !!document.querySelector('[data-tauri-drag-region], .titlebar, [data-titlebar]'),
    minSizeRespected: 'unknown — flag in source review'
  };
})()
```

**Findings to record:**
- `decorations: false` without a custom drag region → titlebar bug.
- `contextIsolation: false` (Electron) → Critical security finding.
- `nodeIntegration: true` (Electron) → Critical security finding.
- `sandbox: false` (Electron, modern) → High security finding.
- No min-size set → Medium UX finding (window can shrink to unusable).

---

## nativeMenuMap

**Tauri** — search `src-tauri/src/` for `Menu::new()`, `MenuBuilder`, or
`tauri::Menu`. Inventory the items, accelerators, and event handlers.

**Electron** — search `main.ts` for `Menu.buildFromTemplate(...)` and
`Menu.setApplicationMenu(...)`. Collect the template tree.

**Static template** to fill in the findings:

```yaml
nativeMenu:
  topLevel:
    - File
    - Edit
    - View
    - Window
    - Help
  perPlatform:
    macOS: { hasAppMenu: true, hasWindowMenu: true, hasHelpMenu: true }
    windows: { hasAppMenu: false, ... }
  acceleratorCoverage:
    total: 24
    withShortcut: 18
    missing: [ "View → Toggle Sidebar", "File → New Window", ... ]
```

**Runtime** — for Electron, IPC into the main process to dump the active
menu (via a debug command). For Tauri, evaluate `__TAURI__.menu` if
exposed.

---

## tauriCommandSurface

**Static** — list every Tauri command:

```bash
# Find all #[tauri::command] declarations
rg -n '#\[tauri::command\]' src-tauri/src
# Find the invoke_handler registration
rg -n 'invoke_handler|generate_handler' src-tauri/src
```

For each command, record: name, args, return type, ACL, allowlist
membership.

**Runtime** — from inside the WebView:

```javascript
(async () => {
  if (!window.__TAURI__?.invoke) return { error: 'not a Tauri app' };
  // Call a benign known command if you have one; otherwise just record
  // that the bridge is reachable:
  return { invokeAvailable: true, eventsAvailable: !!window.__TAURI__.event };
})()
```

**Tauri 2.x ACL check** — `src-tauri/capabilities/*.json`:
- Each command should appear in a capability with the right window scope.
- Wildcard `"core:*"` capabilities are a High finding.
- Missing capabilities = command rejected at runtime.

---

## electronIpcSurface

**Static** — inventory the IPC contract:

```bash
# Main-side handlers
rg -n 'ipcMain\.(on|handle|once)' --type ts --type js
# Renderer-side senders / preload exposure
rg -n 'ipcRenderer\.(send|invoke)' --type ts --type js
rg -n 'contextBridge\.exposeInMainWorld' --type ts --type js
```

**Critical checks:**
- `ipcRenderer` exposed directly to renderer via `contextBridge` → Critical.
- Channel names use string literals scattered across files → Medium (build
  a typed contract instead).
- `webContents.executeJavaScript` called with renderer-supplied input →
  Critical.
- No origin / sender validation in `ipcMain.handle` → High.

---

## multiWindowState

For desktop apps that support multiple windows (or could):

**Static**:
- Tauri: `tauri.conf.json#tauri.windows[]` length, plus runtime
  `WindowBuilder::new(...)` calls in Rust.
- Electron: count `new BrowserWindow(...)` call sites.

**Runtime** (per window) — capture the same probe in each open window:

```javascript
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

**Behaviors to verify:**
- Closing the last window → does the app quit? (macOS convention: no.
  Windows/Linux convention: yes.)
- Reopening from dock / taskbar with no windows → spawns a new window?
- State sync between windows (theme, persisted layout) → instantaneous,
  delayed, or absent?
- Multi-window keyboard shortcuts → routed to focused window only?

---

## windowStateRestore

**Static** — search for window-state libraries:
- `tauri-plugin-window-state`
- `electron-window-state`
- Custom storage of `bounds`, `display`, `maximized` flags.

**Runtime** — verify the round-trip:
1. Resize, move, and maximize the window. Note the bounds.
2. Quit and relaunch.
3. Confirm the bounds restore exactly.
4. Move the window to a second display, quit, relaunch — does it restore
   to the right display? Falls back gracefully if the display is gone?

**Findings:**
- No persistence → Medium (annoying, not blocking).
- Persistence ignores multi-monitor → High (loses windows off-screen).
- Persistence fails to restore maximized state → Low.
- Persistence corrupts itself on a crash and locks user out → Critical.

---

## osIntegrationProbe

Cross-platform behaviors to verify per OS where the app ships:

| Capability                         | macOS | Windows | Linux |
|------------------------------------|-------|---------|-------|
| Native menu in menubar             | ✓     | per-window | per-window (some DEs) |
| Tray icon                          | ✓     | ✓       | ✓ (varies) |
| Notifications                      | ✓     | ✓       | ✓     |
| Auto-launch at login               | LSUI  | regkey  | desktop file |
| File associations                  | UTI   | reg     | mime  |
| Single-instance lock               | n/a*  | mutex   | dbus / lockfile |
| Deep link / custom URL scheme      | ✓     | ✓       | ✓     |
| Dock badge / taskbar progress      | ✓     | ✓       | partial |
| Dark mode follow OS                | ✓     | ✓       | ✓     |

*macOS handles single-instance via Launch Services automatically for
bundled apps; for unbundled binaries it must be implemented.

For each capability the app claims to support, verify on each target OS
or mark `confidence: low` if untestable in this session.
