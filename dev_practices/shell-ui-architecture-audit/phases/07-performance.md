# Phase 07 — Performance

Audit the shell's performance characteristics: initial paint, route
transitions, animation smoothness, memory growth, and bundle / binary
size. The shell is loaded on every page; performance regressions here
multiply across the app.

---

## What we evaluate

| Concern              | Question                                          |
|----------------------|---------------------------------------------------|
| Initial paint        | How fast does the shell first show?               |
| Time to interactive  | When can the user act?                            |
| Route transitions    | Smooth or janky? Long-tasks logged?               |
| Animation jank       | Layout / paint events trigger during transitions? |
| Memory growth        | Does memory creep on prolonged session?           |
| Bundle size (web)    | Shell-only JS / CSS sizes; tree-shaking working?  |
| Binary size (desktop)| Tauri / Electron build size; install footprint    |
| Startup time (CLI)   | First-frame time on cold start                    |
| Resize jank          | Window resize triggers full re-layout?            |
| Long tasks           | > 50ms tasks during user interactions             |

---

## Static probes

### Web

```bash
# Bundle size — built artifacts
du -sh dist/ build/ out/ .next/ 2>/dev/null

# Bundle analyzer hooks
rg -n 'webpack-bundle-analyzer|rollup-plugin-visualizer|@next/bundle-analyzer' \
   package.json next.config.* vite.config.* webpack.config.*

# Code-splitting markers
rg -n 'lazy\(|dynamic\(|loadable\(|defineAsyncComponent\(' --type tsx --type ts --type vue
rg -n 'import\(.+\)' --type tsx --type ts --type vue --type svelte | wc -l

# Image / font optimization
rg -n 'next/image|<Image\b|sharp|imagemin' --type ts --type tsx
rg -n 'font-display|preload.*font' --type css --type tsx --type html

# Hot paths likely to be slow
rg -n 'useEffect.*\[\]|onMount\(|created\(' --type tsx --type vue --type svelte | wc -l
```

### Desktop

```bash
# Tauri release build size
du -sh src-tauri/target/release/ 2>/dev/null
ls -lh src-tauri/target/release/bundle/*/  2>/dev/null

# Electron bundle / asar
du -sh dist/*/  out/*/ 2>/dev/null
```

### CLI / TUI

```bash
# Rust binary size
cargo build --release && ls -lh target/release/<app>

# Python TUI startup imports — heavy imports kill cold start
rg -n '^from |^import ' src/<entry>.py
```

---

## Runtime probes

### Web

From `references/runtime-probes-web.md`:

1. `paintTimings` — at the default route on a cold load (DevTools →
   Empty Cache and Hard Reload).
2. `transitionJank` — install the long-task observer, navigate to a
   data-heavy route, then read `window.__longTasks`. Any task > 50ms is
   user-visible jank; > 100ms is bad; > 500ms is severe.
3. **Lighthouse audit** (Performance + Best Practices categories) — run
   in DevTools → Lighthouse, capture the score and key metrics (FCP,
   LCP, TBT, CLS).
4. **Memory walk**: open DevTools → Memory → Heap snapshot. Take baseline.
   Navigate through 10 routes. Take second snapshot. Compare retained
   size; large delta on shell-level objects = leak.
5. **Resize test**: drag the window edge slowly. Watch FPS in
   DevTools → Rendering → FPS meter. Below 30fps = jank; below 15fps =
   severe.
6. **Long Animation Frames API** (if available): use
   `PerformanceObserver` for `'long-animation-frame'` entries during a
   transition.

### Desktop

1. Cold-start time: time the app launch from invocation to first
   interactive frame. (CI script or manual stopwatch — record the method.)
2. Memory at idle vs. after 30 minutes of use.
3. Bundle / install size on disk.
4. Resize jank inside the WebView (same probe as web).

### CLI / TUI

1. Cold-start time: `time <app> --version` (or equivalent no-op flag) for
   import overhead; `time <app>` for full launch to first prompt /
   first-frame.
2. Frame budget: TUIs usually update at 30–60 Hz. Long-running commands
   should not block the render loop.
3. Memory after long-running session (RSS via `ps`, `top`, or
   `tracing` instrumentation).

---

## Reasonable thresholds

These aren't laws, but they're useful defaults. Adjust to the user's
context.

| Metric                   | Pass    | Warn      | Fail     |
|--------------------------|---------|-----------|----------|
| FCP (web, fast 4G)       | < 1.8s  | 1.8–3.0s  | > 3.0s   |
| LCP (web, fast 4G)       | < 2.5s  | 2.5–4.0s  | > 4.0s   |
| TBT (web)                | < 200ms | 200–600ms | > 600ms  |
| CLS                      | < 0.1   | 0.1–0.25  | > 0.25   |
| Route transition jank    | none    | 1 task > 100ms | > 1 task > 500ms |
| Resize FPS               | ≥ 60    | 30–59     | < 30     |
| Desktop cold start       | < 2s    | 2–5s      | > 5s     |
| TUI cold start (Python)  | < 500ms | 0.5–1.5s  | > 1.5s   |
| TUI cold start (Rust/Go) | < 100ms | 100–400ms | > 400ms  |
| Shell-only JS bundle     | < 250KB | 250–500KB | > 500KB  |

---

## Verdict rubric

### Pass

- All paint / interactivity metrics within thresholds.
- No long tasks > 100ms on standard transitions.
- Bundle size reasonable; code-splitting in use for non-shell routes.
- No memory leak observed over a 10-route walk.
- Resize stays at native frame rate.

### Warn

- One metric in the Warn band.
- Bundle larger than expected but not user-visible yet.
- Minor leak (slow heap growth on repeated nav).

### Fail

- Any metric in the Fail band on a primary route.
- Severe jank (> 500ms long task) on a common interaction.
- Confirmed leak that grows past 200MB in 30 minutes of use.

---

## Severity examples

- **Critical**: shell is unusable on slower hardware (10s FCP, frozen on
  resize).
- **High**: every route transition triggers a 500ms+ long task; leak
  causes OOM on day-long sessions.
- **Medium**: bundle 700KB but route-split correctly; resize jank only
  visible on the very largest viewport.
- **Low**: a single image not optimized; a redundant re-render on theme
  switch.

---

## Findings entry schema

```json
{
  "id": "07-performance",
  "name": "Performance",
  "verdict": "Warn",
  "verdictRationale": "FCP and LCP within thresholds. One systemic issue: every route transition logs a 320ms long task from rehydrating React Query cache.",
  "evidence": [
    { "kind": "probe", "ref": "paintTimings", "data": { "fcp": 1420, "lcp": 2300 } },
    { "kind": "probe", "ref": "transitionJank", "summary": "8 long tasks in a 6-route walk; mean 280ms" },
    { "kind": "log", "ref": "/tmp/shell-audit/07-lighthouse.json" }
  ],
  "findings": [
    {
      "id": "SH-040",
      "title": "Route transitions trigger a 320ms long task on every navigation",
      "severity": "High",
      "description": "On every route change, React Query rehydrates from localStorage in a single synchronous block, blocking the main thread for ~320ms. Causes a visible pause before the new page becomes interactive.",
      "evidence": ["transitionJank probe", "src/providers/queryClient.ts:42"],
      "remediation": "Move rehydration off the main thread (web worker or `requestIdleCallback`), or hydrate only the entries the new route needs.",
      "scope": "every route transition",
      "confidence": "high"
    }
  ],
  "completedAt": "<ISO datetime>"
}
```

---

## Checkpoint

```
Phase 07 complete — Performance: Warn

Top issues:
  • [High]   Route transitions trigger 320ms long task (React Query rehydration)
  • [Medium] Shell-only bundle 480KB; one large dep (ChartLib) shipped on every route
  • [Low]    Spinner shows on transitions < 200ms (visual flicker)

Findings recorded: 5 (1 High, 2 Medium, 2 Low)
Proceed to Phase 08 (Theming)?
```
