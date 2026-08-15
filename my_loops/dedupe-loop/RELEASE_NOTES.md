# Release Notes

dedupe-loop lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/dedupe-loop),
pushed direct to `main` (no PR workflow yet) — this log tracks commits instead of
PRs, the same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.1.1 — Stop documenting a clone script this skill doesn't have
**2026-08-15**

- **Fixed:** `references/platform-directory.md`'s "Resolving a bare repo
  name" section told the reader that `scripts/scan_platform_repos.sh` would
  clone a repo not checked out locally. This skill has no such script — its
  four are `index_capabilities.sh`, `find_clusters.py`, `next_issue.sh`,
  `watch_and_merge.sh` — and nothing in it clones anything. The paragraph
  came along when the reference file was copied from a sibling that *does*
  ship that script; the script didn't come with it.
- **Fixed by:** rewriting the section for how this skill actually works —
  `index_capabilities.sh` takes a local path, so an un-checked-out repo
  needs a `gh repo clone ... --depth 1` first, and the Namespace column is
  what builds that slug. Shallow is enough; the indexer reads the working
  tree and never touches history.
- **Changed:** step 1 now says the argument is a local path rather than
  leaving it to the script's usage error, and Limitations records the
  missing clone path as a deliberate choice — porting the sibling's
  `scan_platform_repos.sh` would add a `gh` dependency this skill otherwise
  doesn't need, so it stays a separate decision rather than an assumed gap.
- **Found by:** `my_loops/docs-loop`'s first run against this repo
  ([#16](https://github.com/baileyrd/skill_pack/issues/16)) — surfaced by
  `check_references.py` as an unresolvable path, confirmed by reading, which
  is what turned "wrong filename" into "no clone path at all."

## v1.1.0 — Wire skill-retro into wrap-up (step 5)
**2026-08-13**

- **Added:** step 5, "Wrap-up retro" — after step 4 ends (clusters fully
  adopted, some deferred, or stopped mid-way), runs a `meta/skill-retro`
  pass on `dedupe-loop` itself, grounded in this run's step 2 clustering/
  classification and step 4.1 behavioral calls. Read-only, safe unattended
  in either harness mode; applying anything found is a separate,
  explicitly-approved follow-up.
- Part of a batch wiring the same convention into every remaining
  `my_loops` skill, following the pattern first used on
  `my_loops/rust-migration` v1.1.0 and `meta/skill-retro`'s own step 6.

## v1.0.0 — Initial versioned release
**2026-08-12**

- **Added:** `version: 1.0.0` to `SKILL.md` frontmatter and this file — first
  formally versioned cut of the skill. No behavior change; establishes the
  baseline the next entry will diff against.
