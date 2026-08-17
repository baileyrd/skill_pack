# Phase 00 — Preparation

Establish scope, classify the shell type, and initialize `findings.json`.
This phase is fast — no probes, just intake.

---

## What this phase does

1. Confirm what's being audited and how (code, running app, or both).
2. Classify the shell type: `desktop` / `web` / `cli`.
3. Decide whether Phase 12 (multi-window) applies.
4. Create `findings.json` matching `assets/findings-schema.json`.
5. Print a scope summary to the user and pause for confirmation.

---

## Step 1 — Confirm inputs

Ask the user (or infer from the conversation):

- **Code**: do you have a local path / repo to inspect? If yes, where?
- **Running app**: is there a live target — an open desktop window,
  browser tab, or terminal session — that you can introspect?
- **Both / one / neither**: pick one of `code` / `runtime` / `both`.

If only code is available: Phases 02 and the runtime portions of every
dimension will be marked `runtime: unavailable`. The audit can still
produce a useful static report.

If only runtime is available: Phases 01 and the static portions will be
marked `static: unavailable`. The audit can still produce a useful
runtime-only report.

If neither: ask whether the user wants to bail or proceed with a
"description-only" audit (interview-style, no evidence). Default to
bailing.

---

## Step 2 — Classify shell type

Open `references/shell-type-signals.md` and follow its detection
procedure. The decision rule is:

1. Read manifests (`package.json`, `Cargo.toml`, `pyproject.toml`,
   `go.mod`, `*.csproj`).
2. Read root configs (`tauri.conf.json`, `electron-builder.yml`, etc.).
3. Look at entry points and build outputs.
4. If signals conflict, ask the user.

Record:
- `findings.shellType`: `"desktop" | "web" | "cli"`
- `findings.shellTypeSecondary`: any additional surfaces
- One sentence in `findings.staticInventory.shellTypeReasoning`

---

## Step 3 — Multi-window applicability

If `shellType === "desktop"`: Phase 12 is **in scope**.

If `shellType === "web"` or `"cli"`: Phase 12 will be **skipped**. Pre-fill
its dimension entry now:

```json
{
  "id": "12-multi-window",
  "name": "Multi-Window / Multi-Instance",
  "verdict": "Skipped",
  "skipReason": "Not applicable to <shellType> shells.",
  "evidence": [],
  "findings": []
}
```

(For CLI / TUI shells, "multi-window" reduces to multi-instance behavior:
two instances of the same TUI in two terminals — file locking, config
contention. Phase 13 (persistence) covers that case, so Phase 12 stays
skipped.)

---

## Step 4 — Initialize findings.json

Create the file at the agreed working path (default
`/tmp/shell-audit/findings.json`). Seed it from the schema:

```json
{
  "target": {
    "name": "<app name>",
    "codePath": "<path or null>",
    "runtimeUrl": "<url/process or null>",
    "scope": "code | runtime | both"
  },
  "shellType": "<desktop|web|cli>",
  "shellTypeSecondary": [],
  "startedAt": "<ISO datetime>",
  "completedAt": null,
  "phasesCompleted": ["00-preparation"],
  "staticInventory": {
    "shellTypeReasoning": "<one sentence>"
  },
  "runtimeBootstrap": null,
  "dimensions": []
}
```

If Phase 12 is being skipped, also push the pre-filled dimension entry
into `dimensions[]` now.

---

## Step 5 — Scope confirmation checkpoint

Print a short summary to the user:

```
Shell UI Architecture Audit — scope confirmed:

Target:        <app name>
Code path:     <path or "—">
Runtime:       <url/window or "—">
Shell type:    <desktop|web|cli> (<one-sentence reasoning>)
Multi-window:  in scope | skipped (not applicable)

Dimensions to audit:
  03 Layout & Composition
  04 Navigation & Routing
  05 Accessibility
  06 State & Data Flow
  07 Performance
  08 Theming & Design Tokens
  09 Cross-Platform Parity
  10 Extensibility
  11 Observability
  12 Multi-Window               (skipped — not applicable)
  13 Persistence

Estimated runtime: 30–90 minutes depending on app size.
Proceed?
```

Wait for confirmation before continuing. If the user wants to descope or
add anything, update `findings.json` and re-print the summary.

---

## Output of this phase

- `findings.json` created and seeded
- `phasesCompleted: ["00-preparation"]`
- A confirmed scope agreement with the user

Move on to Phase 01 (`phases/01-static-scan.md`).
