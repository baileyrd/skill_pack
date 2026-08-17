# Phase 06 — State & Data Flow

Audit how the shell manages state: provider stack, async data flow,
loading / error / empty states, optimistic updates, cache invalidation,
and the boundary between shell-level state (theme, layout, user) and
feature-level state.

---

## What we evaluate

| Concern              | Question                                          |
|----------------------|---------------------------------------------------|
| Provider stack       | Is it ordered correctly? Single-purpose providers? |
| Shell vs. feature state | Is the boundary clear?                         |
| Async data layer     | Single source of truth, or competing libraries?    |
| Loading state        | Consistent across the shell (spinner, skeleton)?   |
| Error state          | Boundary catches errors? Recoverable surface?      |
| Empty state          | Distinguishable from loading? Actionable?          |
| Optimistic updates   | Used where appropriate? Roll back cleanly?         |
| Cache strategy       | Invalidation rules clear? Stale-while-revalidate?  |
| Subscription cleanup | No leaked listeners on unmount / route change?     |

---

## Static probes

### Web

```bash
# Identify async data libraries
rg -l '@tanstack/react-query|swr\b|@apollo/client|urql|relay-runtime|@trpc/client' --type ts --type tsx

# Identify state libraries
rg -l 'redux|zustand|jotai|recoil|valtio|nanostores' --type ts --type tsx

# Find provider stack location (often providers.tsx or _app.tsx / layout.tsx)
fd -t f 'providers|app-providers'

# Loading state markers
rg -n '<Suspense|<SkeletonLoader|isLoading|isFetching|isPending' --type tsx --type vue --type svelte | wc -l

# Error boundaries
rg -l 'ErrorBoundary|componentDidCatch|<ErrorBoundary|errorElement' --type tsx --type ts

# Empty states
rg -n 'EmptyState|empty-state|<Empty\b|no-results' --type tsx --type vue
```

### Desktop

In addition to web checks (renderer is web), look for IPC-mediated state:

```bash
# Tauri events / listen
rg -n 'invoke\(|listen\(|emit\(' --type ts

# Electron channel sends/handles
rg -n 'ipcRenderer\.(send|invoke|on)|ipcMain\.(handle|on)' --type ts --type js
```

### CLI / TUI

```bash
# Reactive / state primitives
rg -n 'reactive|computed|signal|var\s+\w+\s+\w+' --type py --type rust --type go

# Async / spinner widgets in TUIs
rg -n 'LoadingIndicator|Spinner|spinner|loading_widget' --type py --type rust

# Error widgets
rg -n 'ErrorWidget|alert|notify|toast' --type py --type rust --type go
```

---

## Runtime probes

### Web

1. `stateManager` — confirm which state library is active.
2. `loadingErrorEmpty` — count loading / error / empty markers in the DOM
   at the default route.
3. **Loading state walk**: throttle network to "Slow 3G" (DevTools).
   Navigate to a data-heavy page. Capture the loading state. Compare
   across pages — is it the same pattern (skeletons / spinners /
   suspense fallback) or does it drift?
4. **Error state walk**: stop the API server (or use DevTools network
   blocking on `/api/*`). Trigger a feature that fetches data. Capture
   the error state. Confirm:
   - The error reaches a boundary (the whole shell isn't blanked).
   - The error is recoverable (retry button, navigation away works).
   - The error is logged (telemetry — phase 11 will follow up).
5. **Empty state walk**: navigate to a feature with no data (a brand-new
   project, an empty list). Capture the empty state. Confirm it's
   distinguishable from loading (no spinner) and actionable (CTA
   present).
6. **Optimistic update test**: where the app does optimistic mutations
   (e.g., adding an item to a list), force the API to error and confirm
   the optimistic change rolls back cleanly.

### Desktop

Same as web for the renderer. Plus:

1. Cause an IPC handler to throw on the main side. Confirm the renderer
   handles it gracefully and the shell doesn't crash.
2. Restart only the renderer (Cmd-R / Ctrl-R) and confirm the main
   process state is still intact.

### CLI / TUI

1. Throttle or block the upstream the TUI talks to (`tc qdisc` or stop
   the dependency). Trigger a fetch in the TUI. Confirm:
   - A loading state is visible.
   - Error message is clear (not a stack trace).
   - User can recover (retry binding, go elsewhere).
2. Navigate to an empty data set. Confirm the empty state is informative.

---

## Verdict rubric

### Pass

- One async data library or a clearly delegated split (e.g., React Query
  for server state, Zustand for client UI state).
- Loading / error / empty states are consistent across the shell.
- Top-level error boundary present and tested.
- Optimistic updates roll back cleanly when present.
- No state subscription leaks observed on rapid navigation.
- Provider stack ordered logically (theme outermost typically; auth
  before query client; error boundary outermost or per-route).

### Warn

- Two competing data-fetching libraries in use.
- Loading state inconsistent across regions.
- Error boundary present but doesn't fall through to a useful UI.
- One leaked subscription identified.

### Fail

- No error boundary; one feature's error blanks the whole shell.
- No loading state at all (cold blank during fetches).
- Optimistic updates leave inconsistent state on rollback.
- Multiple providers competing for the same state with race conditions.

---

## Severity examples

- **Critical**: any unhandled error in a feature kills the shell process
  (web: blank page; desktop: renderer crash without recovery).
- **High**: error boundary catches but renders a useless "something went
  wrong" with no recovery path.
- **Medium**: loading state drift; one optimistic mutation that doesn't
  roll back.
- **Low**: spinner timing inconsistent (200ms vs 500ms grace).

---

## Findings entry schema

```json
{
  "id": "06-state",
  "name": "State & Data Flow",
  "verdict": "Warn",
  "verdictRationale": "Top-level error boundary present and recovers cleanly; loading state drifts between sidebar (spinner) and main (skeleton); two data libraries in mixed use.",
  "evidence": [
    { "kind": "probe", "ref": "stateManager", "summary": "React Query + Apollo both detected" },
    { "kind": "screenshot", "ref": "/tmp/shell-audit/06-loading-mixed.png", "summary": "Sidebar spinner vs main skeleton at the same load moment" },
    { "kind": "log", "ref": "/tmp/shell-audit/06-error-trace.log" }
  ],
  "findings": [
    {
      "id": "SH-031",
      "title": "Two server-data libraries in mixed use",
      "severity": "Medium",
      "description": "React Query owns 80% of fetches; Apollo Client owns the GraphQL surface for the billing feature only. Cache invalidation between them is ad-hoc and has caused stale data after subscription updates.",
      "evidence": ["package.json", "src/billing/apolloClient.ts", "src/queries/featureFlags.ts"],
      "remediation": "Pick one. Migrate billing to React Query (REST proxy already exists), or move all server-state to Apollo if GraphQL coverage is expanding.",
      "scope": "billing surface vs rest of app",
      "confidence": "high"
    }
  ],
  "completedAt": "<ISO datetime>"
}
```

---

## Checkpoint

```
Phase 06 complete — State & Data Flow: Warn

Top issues:
  • [Medium] Two server-data libraries in mixed use
  • [Medium] Loading state drift between sidebar and main
  • [Low]    Empty state CTAs missing on two routes

Findings recorded: 4 (0 High, 2 Medium, 2 Low)
Proceed to Phase 07 (Performance)?
```
