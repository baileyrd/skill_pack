# Release Notes

issue-loop lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/issue-loop),
pushed direct to `main` (no PR workflow yet) — this log tracks commits instead of
PRs, the same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.1.1 — Declare jq and ripgrep
**2026-08-15**

- **Fixed:** the Scripts note said "shell out to `gh`/`git` only — no extra
  dependencies." Both false. `next_issue.sh:27` pipes through **`jq`**
  (required), and `scan_platform_repos.sh:51` uses **`ripgrep`** when
  present, falling back to `grep` — so optional, and now documented as such
  rather than as an absence.
- Found by `docs-loop` row 5.

## v1.1.0 — Wire skill-retro into wrap-up (step 5)
**2026-08-13**

- **Added:** step 5, "Wrap-up retro" — after step 4's report, runs a
  `meta/skill-retro` pass on `issue-loop` itself, grounded in this run's
  step 1 triage and step 2 reuse-check calls. Read-only, safe unattended in
  either harness mode; applying anything found is a separate,
  explicitly-approved follow-up.
- Part of a batch wiring the same convention into every remaining
  `my_loops` skill, following the pattern first used on
  `my_loops/rust-migration` v1.1.0 and `meta/skill-retro`'s own step 6.

## v1.0.0 — Initial versioned release
**2026-08-12**

- **Added:** `version: 1.0.0` to `SKILL.md` frontmatter and this file — first
  formally versioned cut of the skill. No behavior change; establishes the
  baseline the next entry will diff against.
