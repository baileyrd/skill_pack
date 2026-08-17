# Phase 02 — Runtime Bootstrap

Confirm the live target is reachable and probes execute correctly. Load
the right probe pack based on the shell type detected in Phase 00. This
phase doesn't score anything — it's a dry run that catches setup
problems before the dimension audits begin.

If the audit is static-only, skip this phase and write
`runtimeBootstrap: { available: false }` to `findings.json`.

---

## Step 1 — Load the probe pack

Open the right reference based on `findings.shellType`:

| Shell type | Probe pack                                  |
|------------|---------------------------------------------|
| desktop    | `references/runtime-probes-desktop.md` (and the web pack for the embedded WebView) |
| web        | `references/runtime-probes-web.md`          |
| cli        | `references/runtime-probes-cli.md`          |

Read the probe index at the top of the pack so you know which probes
each later phase will need.

---

## Step 2 — Reachability check

### Web shell

```
1. Confirm a browser tab is open at the target URL.
2. Run `frameworkFingerprint` from runtime-probes-web.md.
3. Verify the result is a non-empty object.
```

If the framework fingerprint comes back empty: the page either failed to
load, is gated behind auth, or uses a framework none of the heuristics
catch. Ask the user to check the tab and retry; or note "no
fingerprintable framework detected" as informational and continue.

### Desktop shell

```
1. Confirm the desktop app is running.
2. If a DevTools / WebView introspection path exists, attach to it.
3. Run `desktopRuntimeDetect` from runtime-probes-desktop.md.
4. For Tauri: `window.__TAURI__` should be present.
   For Electron: `window.electronAPI` or `process.versions.electron`.
   For Wails: `window.runtime`.
```

If the WebView is locked (CSP blocks `eval`, no DevTools port), record
that as a constraint and proceed with what static evidence and
screenshots provide.

### CLI / TUI shell

```
1. Identify the runtime mode the user can offer:
   - `textual run --dev` + `textual console`  (Textual)
   - `INK_DEBUG=1`                            (Ink)
   - `RUST_LOG=debug` + log file              (Ratatui / generic Rust)
   - `script(1)` or `asciinema rec`           (any TUI for screen capture)
2. Confirm at least one channel is producing output.
3. Capture `terminalCapability` from runtime-probes-cli.md
   (TERM, COLORTERM, TERM_PROGRAM, dimensions).
```

For a plain non-interactive CLI, `terminalCapability` plus subprocess
stdout/stderr capture is enough.

---

## Step 3 — Auth state check (web/desktop only)

If the target requires authentication and the dimension audits need
authenticated views (most do — settings, command palette, user-specific
state), confirm the live session is logged in:

```javascript
// Web / desktop WebView
(() => ({
  cookies: document.cookie ? document.cookie.split(';').length : 0,
  authStorageHints: ['token','auth','session','jwt']
    .filter(k => Object.keys(localStorage).some(lk => lk.toLowerCase().includes(k)))
}))()
```

Don't capture token values — only the *presence* of auth artifacts.
If the session isn't authenticated and the audit needs to be, ask the
user to log in (in the user-visible browser/window) before continuing.

**Never type passwords yourself.** The user must log in.

---

## Step 4 — Take baseline artifacts

Capture a baseline so later phases can compare against it.

### Web

- Screenshot of the resting state at the default route.
- `regionInventory` probe output → `findings.runtimeBootstrap.regions`
- Viewport size + DPR

### Desktop

- Screenshot of the main window at default size.
- `windowChromeAudit` (static + runtime parts) →
  `findings.runtimeBootstrap.windowChrome`
- All currently-open windows: capture each one's label + size if multi-
  window is in scope.

### CLI / TUI

- `script` or `asciinema` recording of: launch → main view → quit.
- Capture the rendered first frame as a text snapshot (after stripping
  ANSI) for the report.
- `terminalCapability` output.

Save artifacts under `/tmp/shell-audit/baseline/` (or the working dir
agreed in Phase 00).

---

## Step 5 — Write to findings.json

```json
"runtimeBootstrap": {
  "available": true,
  "probePackLoaded": "web",
  "reachable": true,
  "frameworkFingerprint": { "react": true, "nextjs": true, "tailwind": true },
  "baselineArtifacts": [
    "/tmp/shell-audit/baseline/screenshot-default.png",
    "/tmp/shell-audit/baseline/regionInventory.json"
  ],
  "constraints": [
    "DevTools accessible; CSP allows javascript_tool.",
    "Authenticated session confirmed (auth_token in localStorage)."
  ],
  "notes": "All web probes available."
}
```

Update `phasesCompleted: [..., "02-runtime-bootstrap"]`.

---

## Step 6 — Checkpoint

Print a short status:

```
Runtime probe bootstrap complete:

  Probe pack:    web
  Framework:     Next.js 15 + Tailwind
  Auth:          authenticated session detected
  Baseline:      screenshot + regionInventory captured
  Constraints:   none

Ready to begin dimension audits. Proceed with Phase 03 (Layout)?
```

Wait for confirmation. The user may want to point out specific routes /
windows / TUI screens to focus on before dimension probes start running.

---

## Output of this phase

- `runtimeBootstrap` block populated in `findings.json`.
- Baseline artifacts saved.
- Probe pack confirmed working.

Move on to Phase 03 (`phases/03-layout.md`).
