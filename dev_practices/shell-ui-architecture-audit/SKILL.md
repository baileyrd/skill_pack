---
name: shell-ui-architecture-audit
description: >
  Perform a detailed multi-dimensional audit of the SHELL of a user interface
  — the outer chrome, layout regions, navigation, command surfaces, theming,
  persistence, and extensibility scaffolding around feature pages. Adapts to
  desktop (Tauri/Electron), web (React/Vue/Svelte/hypermedia), and terminal
  (Textual/Rich/Ink/Ratatui/Bubble Tea) shells. Combines static code analysis
  with runtime introspection, scores each dimension Pass/Warn/Fail with
  evidence, and emits a prioritized backlog ranked by CVSS-style severity.
  Use whenever the user asks to audit, review, deconstruct, or harden the
  shell, chrome, outer UI, app frame, navigation skeleton, or layout system
  of an application — even when they just say 'review my app shell', 'audit
  the command palette', 'check multi-window behavior', or 'evaluate the
  theming system'. Trigger even if the user doesn't say 'shell' — 'chrome
  around the pages' or 'parts of the app that aren't feature screens'
  qualify.
version: 1.1.0
---

# Shell UI Architecture Audit

You are a methodical UI shell auditor. The "shell" is everything around the
feature pages: window chrome, regions and slots, top / side / bottom bars,
navigation, routing skeleton, command palettes, theming, persisted layout
state, error boundaries, and the extensibility scaffolding the rest of the
app plugs into. This audit deconstructs that shell layer by layer, scores each
dimension, and produces a prioritized remediation backlog.

## Philosophy

- **Read on demand.** This SKILL.md is the orchestrator only. Each phase has
  its own file in `phases/`. Open a phase when you start it; do not pre-load
  all phases — that wastes context before you reach the expensive runtime
  probes. The microkernel-architecture-audit skill failed at runtime when its
  monolithic instructions consumed context before screenshots and DOM walks
  could finish; this skill avoids that failure mode by design.
- **Adaptive shell type.** Desktop, web, and CLI shells share most concepts
  (regions, navigation, persistence) but evaluate against different probes.
  Phase 00 detects the shell type once and writes it to `findings.json`;
  every later phase loads the right probe pack from `references/`.
- **Static + runtime, both.** Static evidence (file structure, framework
  signals, design tokens in source) is fast and cheap. Runtime evidence (live
  DOM, computed styles, network behavior, Tauri command surface, terminal
  rendering) is what reveals actual behavior. Use both. Disagreement between
  static and runtime is itself a finding.
- **Verdicts need evidence.** Every Pass / Warn / Fail must cite a concrete
  artifact: a file path, a code snippet, a probe result, a screenshot, or a
  measured number. Verdicts without evidence are inadmissible.
- **Backlog is the deliverable.** The narrative report is for humans reading
  top-down; the prioritized backlog is for engineers planning sprints and
  agents acting on findings. Both ship together.

## Trigger Conditions

Use this skill when the user says any of:

- "audit my app shell / outer UI / chrome / layout system"
- "review the navigation skeleton / window structure / app frame"
- "is my command palette / theming / multi-window behavior sound"
- "deconstruct the parts of the app around the feature pages"
- "evaluate my Tauri / Electron / desktop app shell"
- "check my TUI / terminal app architecture"
- Hands over a UI codebase or running app and asks for an architecture review
  of the non-feature layer

## Inputs

The audit can run from any combination of:

- **A codebase** — local path or repo (static evidence)
- **A running app** — desktop window, browser tab, or terminal session
  (runtime evidence)
- **Design or architecture docs** — ADRs, design system docs, layout specs

Strongly prefer having both code and a runnable instance. If only one is
available, complete what you can and explicitly mark dimensions as
"static-only" or "runtime-only" in the report.

## Workflow

```
00 preparation         ← detect shell type, gather inputs, scope confirmation
01 static-scan         ← repo structure, framework signals, build tooling
02 runtime-bootstrap   ← spin up live introspection (DOM, devtools, headless, TTY tee)
─────────────────────  dimension audits (read on demand) ─────────────────────
03 layout
04 navigation
05 accessibility
06 state
07 performance
08 theming
09 cross-platform
10 extensibility
11 observability
12 multi-window        ← desktop-only; skip for web / CLI
13 persistence
─────────────────────  synthesis  ────────────────────────────────────────────
14 synthesis           ← report + prioritized backlog
```

Each phase reads its own file from `phases/` when entered, runs its probes,
appends findings to `findings.json`, and returns a checkpoint summary to the
user. Do **not** read the phase file until you are about to execute that
phase.

## Execution

### Step 1 — Phase 00: Preparation

Read `phases/00-preparation.md`. It will:
- confirm scope (codebase / running app / both)
- detect shell type (desktop / web / cli) using `references/shell-type-signals.md`
- create `findings.json` from `assets/findings-schema.json`
- decide whether Phase 12 (multi-window) is in scope

### Step 2 — Phase 01: Static scan

Read `phases/01-static-scan.md`. Inventory of directories, frameworks,
build tools, and design system artifacts. Writes a `staticInventory` block
to `findings.json` that later phases reference.

### Step 3 — Phase 02: Runtime bootstrap

Read `phases/02-runtime-bootstrap.md`. Loads the right runtime probe pack
based on detected shell type:
- desktop → `references/runtime-probes-desktop.md`
- web → `references/runtime-probes-web.md`
- cli → `references/runtime-probes-cli.md`

Verifies the live target is reachable and probe execution works, then exits.

### Step 4 — Dimension phases (03–13)

For each dimension in order:

1. Open the phase file. Each phase has the same shape:
   - **What we evaluate** — scope of the dimension
   - **Static probes** — repo / file checks
   - **Runtime probes** — live introspection
   - **Verdict rubric** — dimension-specific Pass / Warn / Fail criteria
   - **Findings entry schema** — what to write to `findings.json`
2. Run the probes. Static first (cheap), runtime second.
3. Score the verdict against the rubric and `references/verdict-rubric.md`.
4. Append a dimension entry to `findings.json` matching the schema.
5. Print a one-paragraph checkpoint to the user. Wait for them to either
   acknowledge or ask to dig deeper before moving on.

Phase 12 (multi-window) is skipped automatically if the shell type is `web`
or `cli`. The orchestrator records `skipped: "not applicable to shell type"`
in `findings.json` and moves on.

### Step 5 — Phase 14: Synthesis

Read `phases/14-synthesis.md`. Loads the full `findings.json` and
`assets/report-template.md`, then writes:

- `audit-report.md` — narrative report with verdict table, dimension-by-
  dimension findings, and architecture observations
- `audit-backlog.md` — prioritized issue list ordered by CVSS-style severity
  (Critical → High → Medium → Low), each item linked back to the dimension
  and evidence that surfaced it

Both files go to `/mnt/user-data/outputs/` and are presented via
`present_files`.

## Severity Rubric (Backlog Ranking)

Each finding gets one of:

| Level    | Definition                                                                          |
|----------|-------------------------------------------------------------------------------------|
| Critical | Shell is broken, unusable for a class of users, or actively hostile (data loss, lockout, severe a11y blocker). |
| High     | Major functional or architectural defect with clear user impact; blocks a significant workflow or violates a hard invariant of the chosen framework. |
| Medium   | Real defect with limited impact, or architectural drift that will compound over time but isn't yet user-visible. |
| Low      | Polish, consistency, or nice-to-have. Not blocking anything. |

The full rubric — including how to decide between adjacent levels — lives in
`references/verdict-rubric.md`. Read it once before scoring the first
dimension, and again any time you're uncertain.

## Important Reminders

- **Do not pre-load phases.** Open phase files only as you enter them.
- **Adaptive probes only.** Never run a desktop probe against a web target,
  or vice versa. Phase 02 sets the active probe pack; later phases reference
  it.
- **Cite evidence.** Every verdict needs a file path, a code snippet, or a
  probe result attached. No bare verdicts.
- **Disagreement is a finding.** When static evidence and runtime behavior
  disagree, that gap is itself important — record it.
- **Conditional phases.** Phase 12 (multi-window) only runs for desktop
  targets. Phases 09 (cross-platform) and 13 (persistence) are universal but
  their probes vary by shell type — let the phase file tell you what to run.
- **Honest confidence.** If a probe could not run (sandboxed, no source
  maps, restricted access), mark the affected sub-finding as
  `confidence: low` rather than guessing.

## Limitations

- **Runtime phases need a runnable target.** Phase 02 bootstraps a live
  instance, and phases that depend on it degrade to static-only in a sandbox
  with no display, no browser, or no way to launch the app. That's a partial
  audit, not a clean one — say which phases ran degraded rather than reporting
  a score as if all fifteen executed.
- **Fifteen phases is a long run.** Nothing here is cheap: a full pass reads a
  lot of source and drives a live UI. Scope it to the phases the question
  actually needs — the phase files are independent by design, and a focused
  four-phase audit that finishes beats a fifteen-phase one that gets abandoned.
- **Verdicts are qualitative.** The rubric makes them consistent and citable;
  it doesn't make them objective, and two reviewers can reasonably split
  Warn/Fail on the same evidence. The CVSS-style severity ranking is an
  ordering device, not a computed score.
- **Shell only, by construction.** Feature pages, business logic, data layers,
  and API design are all out of scope. A shell that passes every dimension can
  sit around an application that is wrong in every other way.
- **Shell-type detection is signal-based.** `references/shell-type-signals.md`
  infers desktop/web/terminal from what's in the repo. A hybrid or unusual
  stack can be misclassified, which points phase 02 at the wrong probe pack —
  check its verdict before trusting the probes that follow.

## Wrap-up retro

**After the report lands**, run a [`meta/skill-retro`](../../meta/skill-retro)
pass on **this skill**, grounded in what just happened: did phase 02's
shell-type detection call it correctly, or did a phase downstream have to
work around a misclassification it should have caught itself; did any phase
run degraded (no runtime target) without that showing up clearly in the
final report; did the fifteen phases actually stay independent in practice,
or did a later one silently assume state a skipped earlier one would have
established; did a runtime probe in `references/runtime-probes-*.md` not
match what the target actually needed, forcing an improvised one; did the
severity rubric sort these findings or did most of them pile into one band.

Running and reporting the retro is automatic and safe unattended —
`skill-retro` never edits this skill's files on its own. *Applying* anything
it finds is a separate, explicitly-approved follow-up through this repo's
normal PR workflow, never bundled into the run that triggered it.
