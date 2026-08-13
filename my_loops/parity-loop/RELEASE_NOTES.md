# Release Notes

parity-loop lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/parity-loop),
pushed direct to `main` (no PR workflow yet) — this log tracks commits instead of
PRs, the same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

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
