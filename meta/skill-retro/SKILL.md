---
name: skill-retro
description: Runs a post-execution retrospective on a skill (call it B) immediately after B finishes real work, treating what just happened as evidence about B's own instructions rather than about the task B was doing. Re-reads B's current SKILL.md/references/scripts on disk, reconstructs what actually happened in this session against them — every ambiguity resolved by guessing, every question asked that B's instructions should have pre-answered, every step skipped/reordered/improvised, every stale reference or script that errored — and reports each as a finding: what happened, which file/section it traces to, and a concrete proposed edit. Never edits B's files unprompted; applies findings only on explicit approval, then bumps B's version and RELEASE_NOTES.md per this repo's own versioning convention, through the normal PR workflow. Use immediately after finishing a task that leaned on another skill in this repo, when the user asks to retro/review/critique/post-mortem a skill that was just used, wants to close the loop on whether that skill's own instructions were good enough, or references this by name (skill-retro, meta-review).
version: 1.1.0
---

# skill-retro

Turns "was that skill actually well-specified, or did we just muscle through
it" into a structured, evidence-grounded pass: re-read B as it exists on
disk → reconstruct this session's actual walk through it → classify what
didn't go clean → report before touching anything → apply only on approval
→ version-bump and log B's own `RELEASE_NOTES.md`.

This skill reviews **another skill's instructions**, not the work that skill
just produced. If the task itself has a bug, that's a normal bug fix in
whatever repo the task touched — `skill-retro` is specifically about
whether *following B's SKILL.md* went the way B's author intended.

## Run (when invoked)

**0. Identify the target and the evidence**
- `TARGET_SKILL` (B) — which skill's instructions are under review, and
  where its directory lives (this repo's own `my_loops/`/`yt_research_for_cc/`
  and now `meta/`, or a skill loaded from elsewhere if the user points at
  one).
- Evidence source — by default, this session's own conversation: the run of
  B that just finished. This skill has no memory beyond what's actually in
  context. If the user wants a retro against a *different* session or a
  pasted transcript/log, that's fine — but say explicitly what evidence
  this retro is grounded in, and never backfill findings from assumption
  about a run this skill didn't actually see.
- If there's no real evidence available (asked to retro a skill "in
  general" with no specific run to point at), say so and offer the
  alternative: a straight read-through critique of B's SKILL.md against
  this repo's own skill-authoring conventions, clearly labeled as
  *unvalidated* — not the same weight as an incident-grounded finding, and
  not this skill's main mode.

**1. Re-read B as it currently exists on disk** — its full `SKILL.md`, and
anything in its `references/`, `scripts/`, `assets/` that this session's run
actually touched. Read the files themselves, not a memory or summary of
them from earlier in the conversation — they may have changed, and a stale
mental model produces wrong findings.

**2. Reconstruct the actual run against B's steps** — walk B's own
numbered/step structure (if it has one) and note, per step:
- Followed as written, no friction — not a finding.
- **Skipped or reordered** — and whether B's own text allowed that (a
  documented "adapt to your stack" escape hatch is not a finding; silently
  diverging from a step B stated as mandatory is).
- **A question was asked of the user** — check it against B's own stated
  rules for what should be asked vs. decided. A stop-and-ask that B's rules
  explicitly call for (breaking change, new dependency, ambiguous scope
  step 0 says to ask about) is B working correctly, not a finding. A
  question asked because B's instructions simply didn't cover the
  situation is a real gap — that's the one to report.
- **Guessed or inferred beyond what B's text supported** — the instructions
  didn't say what to do, so a judgment call filled the gap. Report what was
  guessed and where B's text ran out.
- **A script, reference, or template misfired** — wrong path, stale sibling
  repo name, a command that errored, a template field that didn't match
  what the situation needed.
- **Ran but added nothing this time** — a step that executed without
  friction but also without doing any real work for this particular run.
  Flag as a *candidate* to question, not evidence the step is dead — one
  run isn't enough to tell "always a no-op" from "no-op this time."

**3. Classify each real finding** (skip step 2 items that resolved cleanly
— this report is about friction, not a step-by-step recap):
- **Category**: `ambiguous-instruction` / `missing-guardrail` (a stop-and-ask
  B should have had but didn't) / `stale-reference` / `redundant-step` /
  `tooling-bug` (a script/template that's actually broken) /
  `description-triggering` (B's frontmatter `description` didn't actually
  match how/when it got invoked) / `scope-drift` (B's instructions and what
  it was actually asked to do have quietly diverged).
- **Severity**: `cosmetic` (wording, would've worked out either way) /
  `costly-guess` (produced a workable but not-obviously-right result) /
  `could-have-caused-real-damage` (a guardrail gap that, on a different run,
  skips a stop-and-ask B's own rules exist to enforce — e.g. a breaking
  change or an unattributed scope-narrowing on a skill like
  `rust-migration` whose entire point is that exact guardrail).
- **File/section** — the precise place in B to edit (`SKILL.md` step N, a
  specific `references/*.md`, a script's flag handling).
- **Proposed edit** — concrete replacement text or a specific line/step
  change, not just a description of the problem. A finding without a
  proposed edit isn't done yet.

**4. Report the findings table before proposing to touch anything** — same
read-only-checkpoint pattern as `parity-loop`'s gap-analysis or
`dedupe-loop`'s duplication-audit (see `references/retro-findings-format.md`
for the table format). This is single-run evidence: say so plainly, and
don't present a first-occurrence guess as a confirmed systemic problem —
see "Limitations."

**5. Apply only on explicit approval** — per finding, or as an approved
batch:
- Edit B's `SKILL.md`/`references/`/`scripts/` for the approved findings
  only. Declined findings are dropped from this run, not silently
  re-applied.
- Bump B's `version` in its `SKILL.md` frontmatter — semver, by hand, same
  rule the root `README.md`'s "Versioning" section already states for every
  skill here: patch for wording/doc-only fixes, minor for a new guardrail
  or step, major only if the user says this changes B's actual contract
  with callers.
- Add a dated entry to B's own `RELEASE_NOTES.md` describing what changed
  and why, explicitly tracing back to this retro (which run prompted it).
- This skill gets no shortcut around the repo's standing workflow: branch,
  PR, green CI if configured, merge with a **merge commit** — same as
  `CONTRIBUTING.md` requires for any other change here.

**6. Self-retro** — once step 5 finishes (whatever B was), turn the same
lens on `skill-retro` itself, grounded in how *this run* actually went:
did step 0's evidence-identification have any friction, did a real finding
from step 2 fail to fit cleanly into step 3's categories, did
`references/retro-findings-format.md`'s table lack a column this run
actually needed, did applying an approved edit in step 5 turn out messier
than the instructions implied? Report this as its own separate findings
table — same format, same read-only-before-write discipline, same
explicit-approval gate before touching anything — rather than merging it
into B's report even on the run where B happened to be `skill-retro`
itself.

**Guard against recursing**: if step 0's `TARGET_SKILL` for this run
already *was* `skill-retro` (someone invoked this skill directly on
itself), step 6 does not fire a second time — the pass that just finished
*is* the self-retro, and immediately re-running it would replay the same
evidence against the same file for no new signal. Step 6 only fires when B
was some *other* skill, so that every ordinary retro run also produces a
lightweight check on this skill's own instructions as a side effect,
without ever double-reporting on a direct self-retro invocation.

## Rules

- Never edit a target skill's files without explicit approval — a report
  first, always.
- Never invent a finding with no concrete incident behind it from this run's
  actual evidence. A "this could theoretically be clearer" instinct with
  nothing that actually happened to back it is worth naming as a
  speculative aside, not listed with the same weight as an observed gap.
- A stop-and-ask B's own rules call for is not a finding just because a
  question got asked — re-derive whether the ask was appropriate per B's
  *own* stated rules, don't flag every question reflexively.
- Every real finding carries a concrete proposed edit; a complaint with no
  proposed fix isn't finished.
- Ground severity in what the gap could actually cause on a *different*
  run, not just how the run in front of you happened to turn out — a
  guessed-and-got-lucky gap in a guardrail step is `could-have-caused-real-
  damage`, not `cosmetic`, even though this particular run was fine.
- Step 6's self-retro follows the same approval gate as step 5 — running it
  and reporting its findings is automatic and needs no permission, but
  applying anything it finds to `skill-retro`'s own files is exactly as
  gated as applying a finding to any other target skill.

## Limitations

- Single-run evidence by default — one retro is "this happened once," not
  proof of a pattern. `references/retro-findings-format.md`'s log convention
  exists so findings can accumulate across multiple runs of the same skill
  before a marginal one gets acted on; treat a single occurrence of a minor
  finding as worth logging, not necessarily worth an immediate edit.
- No access to a separate transcript or log by default — this skill sees
  what's in the current conversation's context (or whatever the user
  explicitly supplies). It cannot retro a run it wasn't shown.
- Judgment-heavy in the same way the rest of this repo's assessment steps
  are (`parity-loop` step 1, `dedupe-loop`'s clustering, etc.) — a
  candidate list, read before trusting.
- Doesn't wire itself into an *other* skill's run automatically. Two ways
  to actually get it invoked at the end of a skill B's run: add one line to
  B's own "Wrap up" step inviting a `skill-retro` pass (done for
  `rust-migration`), or a `PostToolUse` hook in `settings.json` matching
  the `Skill` tool (see this account's `update-config` skill for how).
  Neither is set up by `skill-retro` itself for a target skill — it's meant
  to be run by request, or wired in deliberately, not to silently attach
  itself to every skill in this repo. Step 6 is the one exception, and it's
  narrowly scoped: `skill-retro` checks *itself* at the end of every run on
  some other B, but that self-check never cascades into inviting a retro on
  B in return, and never fires twice on a direct self-retro invocation.

## Scripts

None. This skill is a reading/judgment/writing pass — `git`/`gh` for the
eventual PR are the only tools it shells out to, same as any other change
in this repo, with no wrapper beyond what `CONTRIBUTING.md` already
describes.
