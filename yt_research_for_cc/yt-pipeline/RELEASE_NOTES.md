# Release Notes

yt-pipeline lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/yt_research_for_cc/yt-pipeline),
pushed direct to `main` (no PR workflow yet) — this log tracks commits instead of
PRs, the same convention as
[repo-config's RELEASE_NOTES.md](../../my_loops/repo-config/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.1.0 — Wire skill-retro into wrap-up (step 8)
**2026-08-13**

- **Added:** step 8, "Wrap-up retro" — after step 7's report-back, runs a
  `meta/skill-retro` pass on `yt-pipeline` itself, grounded in this run's
  step 1 selection/backup logic, step 3 ingestion-failure handling, and
  step 5 deliverable generation. Read-only, safe unattended (this pipeline
  already runs unattended end to end); applying anything found is a
  separate, explicitly-approved follow-up.
- Explicitly scoped to `yt-pipeline` itself, not `yt-search` or
  `notebooklm` — `notebooklm` is vendored from `notebooklm-py` and this
  repo's own convention says never hand-edit it (see
  `yt_research_for_cc/README.md`); it stays outside this wiring entirely.
- Part of extending the wrap-up-retro convention (first used on
  `my_loops/rust-migration` v1.1.0) to `yt_research_for_cc`.

## v1.0.0 — Initial versioned release
**2026-08-12**

- **Added:** `version: 1.0.0` to `SKILL.md` frontmatter and this file — first
  formally versioned cut of the skill. No behavior change; establishes the
  baseline the next entry will diff against.
