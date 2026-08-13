# Release Notes

yt-search lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/yt_research_for_cc/yt-search),
pushed direct to `main` (no PR workflow yet) — this log tracks commits instead of
PRs, the same convention as
[repo-config's RELEASE_NOTES.md](../../my_loops/repo-config/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.1.0 — Wire skill-retro into wrap-up
**2026-08-13**

- **Added:** a "Wrap-up retro" section — after presenting results, runs a
  `meta/skill-retro` pass on `yt-search` itself, grounded in the
  invocation (flag handling, error paths, engagement-ratio behavior
  against this result set). Read-only; applying anything found is a
  separate, explicitly-approved follow-up.
- Part of extending the wrap-up-retro convention (first used on
  `my_loops/rust-migration` v1.1.0) to `yt_research_for_cc`.
  `notebooklm` is excluded — it's vendored from `notebooklm-py` and this
  repo's own convention says never hand-edit it (see
  `yt_research_for_cc/README.md`).

## v1.0.0 — Initial versioned release
**2026-08-12**

- **Added:** `version: 1.0.0` to `SKILL.md` frontmatter and this file — first
  formally versioned cut of the skill. No behavior change; establishes the
  baseline the next entry will diff against.
