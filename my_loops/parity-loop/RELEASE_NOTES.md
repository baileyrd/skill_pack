# Release Notes

parity-loop lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/parity-loop),
pushed direct to `main` (no PR workflow yet) — this log tracks commits instead of
PRs, the same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.5.0 — Don't depend on an executable bit the sync drops
**2026-08-17**

- **Added:** a first item in step 0's tooling preflight documenting how to restore the executable bit —
  `chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true`, with naming the
  interpreter (`bash scripts/x.sh`) as the fallback where the skill directory
  is read-only.
- **Why ([#1](https://github.com/baileyrd/skill_pack/issues/1)):** the sync
  that delivers a skill to a session doesn't preserve mode bits. Measured in a
  live session: **31 of 31 shebanged scripts across all ten skills arrive as
  `0644`**, so any step written `scripts/x.sh` fails with `permission denied`.
  The issue had recorded this as an occasional symptom; it is universal.
- **Scope note:** this documents a recovery rather than fixing the sync, which
  lives outside this repo. #1 stays open.

---

## v1.4.0 — Tooling preflight and an infrastructure stop condition
**2026-08-16**

- **Added:** a **tooling preflight** as the first bullet of step 0 — `command
  -v gh`, one cheap API read, and a note on which CI-status mechanism the
  target uses. The bullets it sits above all validate the *target*; this one
  validates the loop's own execution environment, which is what actually fails
  first when it fails.
- **Added:** an **infrastructure stop condition** — an unreachable or
  rate-limited GitHub API halts cleanly and reports three lists (completed, in
  flight with branch and PR named, never started) plus the retry path. Every
  other stop condition in this skill is about work state; this is the one where
  partial state exists and something can be stranded unnamed.
- **Added:** the preflight names the two CI-status traps by their symptom:
  a repo reporting via Actions checks returns `total_count: 0` from the
  commit-status endpoint (not evidence CI is missing), and runs associate to
  PRs by *branch*, so a stale run from an earlier PR on a reused branch can
  read as a pass for code it never ran against. Match by `head_sha`.
- **Documented:** which scripts require `gh`, in both the Scripts section and
  Limitations. All three (`next_issue.sh`, `watch_and_merge.sh`,
  `scan_rustymill_repos.sh`) do; the fallback to the GitHub MCP tools is a
  substitution the run makes deliberately, since the scripts have no MCP path
  of their own.
- **Fixed:** the `## Stop conditions` heading was missing entirely — the
  bullets were there, sitting unheaded under `## Harness mode`, and step 3's
  cross-reference to "Stop conditions" pointed at nothing. Restored over the
  existing content; no bullet was changed by the fix itself.

**Evidence, stated honestly:** only `issue-loop` actually failed this way in a
live run — `gh` absent in a web session, so its scripts couldn't run and the
loop had to be re-derived mid-flight. The gap here was confirmed structurally
by reading this skill, not by a failing run of it. The change is documentation
only — no behavior changes and no scripts touched — so the cost of being wrong
is low, but it isn't the same grade of evidence
([#61](https://github.com/baileyrd/skill_pack/issues/61)).

---

## v1.3.0 — Refresh the stale platform repo directory
**2026-08-15**

- **Fixed:** `references/platform-directory.md` was wrong in a way that broke
  the scan step, not just incomplete. It listed ~25 repos under `Rusty-Mill/*`
  — rustils, rusty_json, rusty_http, rusty_libc, rusty_tokio, rusty_wire and
  others — when all of them live under `baileyrd`. Only four repos are actually
  in the Rusty-Mill org. Since the file's own "Resolving a bare repo name"
  section tells the scan script to build clone URLs from that column, every one
  of those lookups would 404.
- **Fixed:** it listed 30 repos against an actual 80+, missing `rusty_sync`,
  `rusty_wire`, `rusty_codec`, `rusty_stream` and others. Two of those turned
  out to be the relevant candidates in a real audit.
- **Fixed:** three entries don't exist under the names given — `rush`,
  `rusty_compactor` (it's `rusty_token_compactor`), `rusty_tail` (it's
  `rusty_tailscale`). `rusty_async` exists but is an empty repository.
- **Changed:** regrouped by function; purposes not confirmed by reading source
  are now marked `†` rather than asserted; added a note that `platform`'s
  `thiserror` dependency pulls syn/quote/proc-macro2/unicode-ident into every
  consumer of the platform layer.

## v1.2.1 — Declare jq and ripgrep
**2026-08-15**

- **Fixed:** the Scripts note said "shell out to `gh` and `git` only — no
  extra dependencies." `next_issue.sh:26` requires **`jq`**;
  `scan_rustymill_repos.sh:56` uses **`ripgrep`** when present and `grep`
  otherwise. Required vs. optional is now stated per tool.
- Found by `docs-loop` row 5.

## v1.2.0 — Wire skill-retro into wrap-up (step 5)
**2026-08-13**

- **Added:** step 5, "Wrap-up retro" — after step 4's report, runs a
  `meta/skill-retro` pass on `parity-loop` itself, grounded in this run's
  step 1 path selection and step 3 breaking-change/new-subsystem calls.
  Read-only, safe unattended in either harness mode; applying anything
  found is a separate, explicitly-approved follow-up.
- Part of a batch wiring the same convention into every remaining
  `my_loops` skill, following the pattern first used on
  `my_loops/rust-migration` v1.1.0 and `meta/skill-retro`'s own step 6.

## v1.1.0 — `new-subsystem` stop-and-ask
**2026-08-13**

- **Fixed:** a real gap-closing run let the assessing/implementing agent
  unilaterally decide architecturally-large capabilities ("needs a new
  subsystem") were out of scope, recording that reasoning only in the
  target repo's own docs. The actual mandate was full parity, and the
  pattern went uncorrected for many rounds before the user caught it.
- **Added:** a `new-subsystem` tag/label, parallel to the existing
  `breaking-change` one throughout the loop:
  - Step 0: default posture is now explicit — everything in the
    reference is in scope; architecture/effort required is a sizing
    question, never a scope question.
  - Step 1: a candidate needing a new subsystem is flagged, not dropped
    from `gap-analysis.md`.
  - Step 2: `new-subsystem` candidates still get an issue filed (even if
    the honest sizing is "design/scoping issue" rather than
    implementation-ready), and get the new label.
  - Step 3: a new stop-and-ask trigger (3.4) alongside the existing
    breaking-change one (3.3) — don't auto-implement, and, the actual
    fix, don't auto-skip either. Renumbered steps 3.4–3.11 → 3.5–3.12.
  - "Stop conditions" and "Harness mode": the new trigger is listed
    alongside breaking-change and is likewise unaffected by
    `LOOP_HARNESS_MODE=auto`.
  - Rules: added an explicit rule that a gap only leaves scope two ways —
    an explicit user decision, or a real external dependency the target
    can't reach (with a proposed pragmatic translation attempted first).
  - Step 4 (wrap-up): split the old single "left out of scope" report
    bucket into user-excluded (with their reason) vs. still-open
    `new-subsystem` issues awaiting a decision — these aren't the same
    thing and were being conflated.
  - Limitations: added a bullet naming the failure mode directly and
    explaining why the stop-and-ask exists.
- Fixed two stale internal cross-references to the old step numbering
  (development-standards.md consult point, now step 3.6).
- No changes to the scripts, templates, or "Adapting to other stacks"
  section.

---

## v1.0.0 — Initial versioned release
**2026-08-12**

- **Added:** `version: 1.0.0` to `SKILL.md` frontmatter and this file — first
  formally versioned cut of the skill. No behavior change; establishes the
  baseline the next entry will diff against.
