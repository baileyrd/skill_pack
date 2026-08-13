# Changelog

All notable changes to this repo are documented here.
Format: Added / Changed / Deprecated / Removed / Fixed / Security, newest first.

## [Unreleased]
### Added
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
### Changed
- `my_loops/rust-migration` (v1.0.0 → v1.1.0) — step 4's wrap-up now runs a
  `meta/skill-retro` pass on the skill itself before ending the run.
### Fixed
### Security

<!-- ## [0.1.0] - YYYY-MM-DD
### Added
- Initial release -->
