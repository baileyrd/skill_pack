# Phase 11 — Observability

Audit the shell's observability: telemetry sinks, error boundaries,
structured logging, debug affordances, and in-app debug overlays. The
shell sits above feature pages, so shell-level observability is what
catches the cross-cutting bugs nobody else sees.

---

## What we evaluate

| Concern              | Question                                          |
|----------------------|---------------------------------------------------|
| Telemetry sinks      | Where do events go? Crash reports, analytics, RUM |
| Error boundaries     | Present at right places? What do they capture?    |
| Structured logging   | One format? Levels respected? Correlation IDs?    |
| User-visible errors  | Distinct from logs; recoverable; not raw stacks   |
| Debug overlay        | Dev-only or production-gated? What does it expose? |
| Performance traces   | Captured for the shell layer (route changes, etc.)|
| Privacy boundary     | PII scrubbed? Consent honored?                    |
| Sampling             | Volume managed without losing important signals   |
| Source maps          | Shipped (production)? Symbolicated stacks?        |

---

## Static probes

### Web

```bash
# Telemetry SDKs
rg -l '@sentry|sentry-browser|datadog-rum|@datadog/browser-rum|bugsnag|posthog|@amplitude|segment-analytics' \
   package.json

# Error boundaries
rg -n 'class .* extends.*Component[\s\S]*?componentDidCatch|<ErrorBoundary' --type tsx --type ts

# Structured logger
rg -n 'pino\b|winston\b|loglevel\b|debug\(' --type ts --type tsx

# Console.log presence (smell)
rg -n 'console\.(log|warn|error)\(' --type ts --type tsx | wc -l

# Debug overlays / dev tools
rg -n 'DebugPanel|DebugOverlay|__DEV__|process\.env\.NODE_ENV' --type tsx --type ts

# PII scrubbing
rg -n 'beforeSend|scrubFn|redact|maskInputs' --type ts --type tsx
```

### Desktop

```bash
# Native crash reporting
rg -n 'crashReporter|sentry-tauri|sentry-electron' --type ts --type js --type rust

# Tauri tracing
rg -n 'tracing::|log::|env_logger|fern\b' src-tauri/

# Electron logging
rg -n 'electron-log|app\.getPath\([\'"]logs[\'"]' --type ts --type js
```

### CLI / TUI

```bash
# Structured logging
rg -n 'tracing|slog|zap\.|logging\.|loguru' --type rust --type go --type py

# Crash reporting in Rust binaries
rg -n 'panic_hook|set_hook|color_eyre|miette|anyhow' --type rust

# Log file paths
rg -n 'XDG_STATE_HOME|app_log_dir|log_dir|logs/' --type rust --type py --type go
```

---

## Runtime probes

### Web

From `references/runtime-probes-web.md`:

1. `telemetrySinks` — confirm which SDKs are alive at runtime.
2. `errorBoundary` — count error-boundary indicators in the DOM.
3. **Trigger an error**: e.g., navigate to a route with a forced
   `throw new Error('audit-test')` (in dev) or pin a known broken
   feature. Capture:
   - User-visible behavior (boundary message vs blank page vs raw
     stack vs full crash).
   - Network: was an event sent to Sentry / Datadog / etc.?
   - Console: is a structured error logged with stack and breadcrumbs?
4. **Network panel walk**: open DevTools → Network → filter by
   `analytics`, `events`, `sentry`. Navigate through the shell. Confirm:
   - Page-view events fire.
   - Route-transition events fire (or are recoverable from RUM).
   - Errors are sent without raw PII (scan payloads).
5. **Source maps**: in DevTools → Sources, confirm production source
   maps are reachable (or that they're privately uploaded to Sentry,
   not shipped publicly).
6. **Debug overlay**: if a debug panel is shipped (often gated by a key
   chord like `Cmd+Shift+D`), confirm it works in dev and is properly
   gated in production.

### Desktop

In addition to the renderer-side probes:

1. Confirm a native crash reporter is installed (Sentry-Tauri,
   electron-log + Sentry, etc.). Force a renderer crash via
   `process.crash()` (Electron) or a Rust panic in a command, and
   verify the crash is captured.
2. Locate the log file path (`app.getPath('logs')` or the platform-
   appropriate path) and confirm logs accumulate.

### CLI / TUI

1. Trigger a controlled error (corrupt the config, kill a dependency).
   Confirm:
   - User-facing error message is informative (not a raw stack).
   - Full stack written to the log file.
   - Exit code is non-zero where appropriate.
2. Locate the log file (`~/.local/state/<app>/`, `~/Library/Logs/<app>/`,
   `%LOCALAPPDATA%\<app>\Logs\`). Confirm it rotates / has size limits.
3. Run with verbose flag (`-v`, `--debug`, `RUST_LOG=debug`,
   `LOGURU_LEVEL=DEBUG`). Confirm structured output, levels honored.

---

## Verdict rubric

### Pass

- Telemetry covers the shell layer: route changes, errors, key shell
  actions.
- Error boundary at the shell root catches and renders a recoverable
  surface.
- Structured logger in use; no `console.log` debris.
- PII / secrets scrubbed before send.
- Source maps shipped privately.
- Debug overlay gated to dev or behind a flag.
- Crash reporter installed (desktop / CLI).

### Warn

- Telemetry exists but misses meaningful events (e.g., palette opens not
  tracked).
- Error boundary present but renders only a generic "something went
  wrong".
- Logger mixed with `console.log` (some files use one, some the other).
- Debug overlay present in production without a gate.

### Fail

- No error boundary at the shell root; one error blanks the app.
- No telemetry at all (and this isn't a deliberate privacy choice).
- Raw stacks rendered to users on errors.
- PII (emails, tokens, IDs) shipped to telemetry without scrubbing.
- No log file at all (CLI / desktop).

---

## Severity examples

- **Critical**: PII (auth tokens, passwords) sent to a third-party
  analytics endpoint without consent.
- **High**: shell has no error boundary; first feature error blanks the
  whole UI.
- **Medium**: structured logger used inconsistently; `console.log` still
  present.
- **Low**: debug panel ships with a typo on a label.

---

## Findings entry schema

```json
{
  "id": "11-observability",
  "name": "Observability",
  "verdict": "Warn",
  "verdictRationale": "Sentry installed and capturing errors with source maps. No event tracking on shell-level actions (palette open, theme switch) — gaps in product analytics. console.log debris across components.",
  "evidence": [
    { "kind": "probe", "ref": "telemetrySinks", "summary": "{ sentry: true, posthog: true }" },
    { "kind": "probe", "ref": "errorBoundary", "summary": "1 boundary at shell root" },
    { "kind": "log", "ref": "/tmp/shell-audit/11-network-events.har", "summary": "23 page-view events, 0 palette-open events" }
  ],
  "findings": [
    {
      "id": "SH-080",
      "title": "Shell-level user actions not tracked in product analytics",
      "severity": "Medium",
      "description": "Page views and feature events are captured by PostHog. Shell-level actions — opening the command palette, switching themes, opening settings — are not instrumented. Cannot answer 'how often is the palette used' or 'what % of users have set a non-default theme'.",
      "evidence": ["/tmp/shell-audit/11-network-events.har", "src/shell/CommandPalette.tsx"],
      "remediation": "Add a small instrumentation helper and wire it into the shell action dispatch. Aim for a fixed list (palette open, theme set, layout reset, settings open).",
      "scope": "all shell-level actions",
      "confidence": "high"
    }
  ],
  "completedAt": "<ISO datetime>"
}
```

---

## Checkpoint

```
Phase 11 complete — Observability: Warn

Top issues:
  • [Medium] Shell-level actions not instrumented (palette, theme switch, settings)
  • [Medium] 47 console.log calls in shell-layer code (logger inconsistency)
  • [Low]    Debug overlay ships in production but is keyboard-gated

Findings recorded: 4 (0 High, 2 Medium, 2 Low)
Proceed to Phase 12 (Multi-Window) — or skip if not desktop?
```
