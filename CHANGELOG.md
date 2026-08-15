# Changelog

All notable changes to this repo are documented here.
Format: Added / Changed / Deprecated / Removed / Fixed / Security, newest first.

## [Unreleased]
### Added
- `my_loops/docs-loop` skill — thorough documentation review/update loop
  against a repo's current state: ground truth built from the code before
  any prose doc is opened, a six-way classified `docs-audit.md` checkpoint,
  then per-doc PRs through the sibling loops' CI-gated merge mechanics.
  Complements `repo-config`, whose `audit.sh` deliberately checks doc
  *presence* and says so — this is the skill that checks their *content*.
  Ships two scripts (`inventory_docs.sh` drift ranking,
  `check_references.py` link/anchor/path resolution); running the latter
  against this repo turned up two real broken references (dedupe-loop's
  `platform-directory.md`, datastar-pro's `core.md` TOC anchor) among 16
  cross-repo false positives — logged as a follow-up rather than fixed in
  the same change.
- `my_loops/rust-migration` skill — migrates a repo/application to Rust
  with a capability manifest (every item defaults REQUIRED, only a
  written user sign-off moves one to OUT-OF-SCOPE) as the mechanism for
  the "capabilities treated as optional" failure mode this was built to
  close.
- New `meta/` category: `meta/skill-retro` (post-execution retrospective on
  a skill's own instructions — findings with proposed edits, applied only
  on approval) and `meta/learn-it` (distills a session's actual patterns
  into a new or updated skill, same evidence-grounded discipline as
  skill-retro in the opposite direction).
- `meta/my-skill-creator` — this repo's own fork of Anthropic's
  `skill-creator` example skill, with this repo's authoring conventions
  applied automatically and a `skill-retro` wrap-up step built into every
  skill it drafts or improves by default (rather than wired in afterward
  as a separate change, the way the rest of this batch of changes had to
  be).
- New `web_dev/` category: `web_dev/datastar-pro` — generates Datastar Pro
  web apps, reviewed and imported from `baileyrd/datastar-pro-skill`'s
  audited v1.0 milestone. Proprietary vendored library source
  (`datastar-pro-main/`) and upstream development-process scaffolding
  (`CLAUDE.md`, `.planning/`) deliberately excluded from the import.
### Changed
- `my_loops/rust-migration` (v1.0.0 → v1.1.0) — step 4's wrap-up now runs a
  `meta/skill-retro` pass on the skill itself before ending the run.
- `meta/skill-retro` (v1.0.0 → v1.1.0) — new step 6 self-retros
  `skill-retro` itself at the end of every run on another skill, guarded
  against recursing on a direct self-retro invocation.
- `meta/learn-it` (v1.0.0 → v1.1.0) — new step 6 runs a `skill-retro` pass
  on `learn-it` itself at the end of every run, regardless of outcome.
- `meta/skill-retro` wired into the wrap-up of every remaining `my_loops`
  skill as a new step 5, "Wrap-up retro": `my_loops/dedupe-loop`
  (v1.0.0 → v1.1.0), `my_loops/issue-loop` (v1.0.0 → v1.1.0),
  `my_loops/parity-loop` (v1.1.0 → v1.2.0), `my_loops/repo-config`
  (v1.0.0 → v1.1.0), `my_loops/sovereignty-loop` (v1.0.0 → v1.1.0).
- `meta/skill-retro` wired into `yt_research_for_cc/yt-search`
  (v1.0.0 → v1.1.0) and `yt_research_for_cc/yt-pipeline`
  (v1.0.0 → v1.1.0, new step 8). `yt_research_for_cc/notebooklm`
  deliberately excluded — vendored from `notebooklm-py`, never
  hand-edited per this repo's own convention.
### Removed
- `need_to_productize/datastar-pro.skill` — superseded by
  `web_dev/datastar-pro`, an updated, properly-authored version reviewed
  from the actual upstream source rather than this repo's own stale,
  never-reviewed export.
### Fixed
- `my_loops/dedupe-loop` (v1.1.0 → v1.1.1) — `references/platform-directory.md`
  documented a `scripts/scan_platform_repos.sh` the skill doesn't have,
  copied in from a sibling that does. Reading it revealed the real gap:
  dedupe-loop has no clone path at all, so `PLATFORM_REPOS` entries must be
  checked out before step 1. Section rewritten, prerequisite stated in step
  1, and the missing clone path recorded in Limitations as a deliberate
  choice rather than an oversight ([#16](https://github.com/baileyrd/skill_pack/issues/16)).
- `web_dev/datastar-pro` (v1.0.0 → v1.0.1) — `references/core.md`'s TOC
  linked `#operators-in-expressions` against a heading that slugs to
  `#operators`, and listed it out of document order. Fixed the pointer, not
  the heading ([#17](https://github.com/baileyrd/skill_pack/issues/17)).
- Both were the two genuine findings from `docs-loop`'s first run; the other
  16 `broken` rows it reported were the documented cross-repo
  false-positive class and were correctly left alone.
### Security

<!-- ## [0.1.0] - YYYY-MM-DD
### Added
- Initial release -->
