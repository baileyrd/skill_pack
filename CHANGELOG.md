# Changelog

All notable changes to this repo are documented here.
Format: Added / Changed / Deprecated / Removed / Fixed / Security, newest first.

## [Unreleased]
### Added
- `docs/adr/0002-repo-checks-require-a-real-failure.md` — the ADR log's first
  real decision: why CI exists here as a deliberate exception to
  `repo-config`'s no-manifest rule, and the constraint that a check earns its
  place by naming the commit it would have failed. Resolves
  `ARCHITECTURE.md`'s claim that `docs/adr/` records decisions.
- `.github/workflows/ci.yml` + `scripts/check_repo.py` — five repo checks
  (exec bits, line endings, doc references, skill manifests, packaging),
  each added because that failure actually happened here, and each verified
  by reproducing its historical bug. Runnable locally with
  `python3 scripts/check_repo.py`.
- `docs-refs-baseline.tsv` — 3 accepted broken doc references with written
  reasons, so `doc-refs` fails on new breakage only rather than being red
  from day one.
- `docs-audit.md` — checkpoint from `my_loops/docs-loop`'s first end-to-end
  run against this repo: 7 findings (3 stale/missing, 1 orphaned, 3
  aspirational), no edits applied. Committed per the skill's own persistence
  convention so a re-run starts from these verdicts.
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
- `my_loops/repo-config` (v1.1.0 → v1.2.0) — `.gitattributes` joins the
  standard governance set as `audit.sh`'s 11th item, prompted by this
  skill's own synced `audit.sh` arriving with CRLF and failing on Linux.
  The audit greps for `eol=lf` rather than mere presence, since a
  binaries-only `.gitattributes` scores present while leaving the exact
  problem in place. Limitations rewritten: `.gitignore` stays out of scope
  (per-project, silent failure mode), `.gitattributes` comes in (one correct
  answer everywhere, breaks scripts at a distance when wrong).
- `my_loops/docs-loop` (v1.2.0 → v1.2.1) — `docs-audit.md` joins
  `CHANGELOG`/`RELEASE_NOTES` in the checker's historical set. Its rows
  persist across runs by design, so a run that deletes a file and records the
  deletion made the *next* run flag its own report as new breakage — with CI
  wired in, that turns a completed fix into a red build. Hit for real when
  `my_loops/README.md` was deleted.
- `my_loops/docs-loop` (v1.1.0 → v1.2.0) — `check_references.py` gains
  `--baseline FILE` so it can gate CI: without it, wiring the checker in
  makes the build red on day one from the documented structural
  false-positive class. Keyed on `kind + doc + detail` without the line
  number, so an accepted row doesn't return as new when a paragraph is added
  above it; stale entries are reported, never fatal.
- `my_loops/docs-loop` (v1.0.0 → v1.1.0) — `check_references.py` false
  positives cut 26 → 6 whole-repo (3 broken anchors → 0) via three fixes:
  component-relative path resolution (doc dir → nearest `SKILL.md`/manifest
  dir → repo root), masking inline code spans before link extraction so
  quoted markdown syntax isn't parsed as a real link, and `historical-*`
  verdicts for non-resolving paths in `CHANGELOG`/`RELEASE_NOTES`, which are
  usually correct history the skill's own Rules forbid rewriting.
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
- `my_loops/README.md` — a one-line stub containing `# skill_pack`, the root
  repo's own title, in a category folder. Never filled in, linked from
  nowhere. `my_loops/` now matches `meta/` and `web_dev/`, which have no
  category README either; `yt_research_for_cc/` keeps its real one.
- `need_to_productize/datastar-pro.skill` — superseded by
  `web_dev/datastar-pro`, an updated, properly-authored version reviewed
  from the actual upstream source rather than this repo's own stale,
  never-reviewed export.
### Fixed
- `ARCHITECTURE.md` Non-goals said "`scripts/*.py` are one-shot tooling
  invoked by hand" — no longer true of `check_repo.py` once CI ran it. Drift
  introduced by this repo's own CI change hours earlier, caught while writing
  ADR-0002.
- Dependency declarations across six skills, found by `docs-loop` row 5:
  `meta/my-skill-creator` (v1.0.1) now declares PyYAML; `dedupe-loop`
  (v1.1.2), `issue-loop` (v1.1.1), `parity-loop` (v1.2.1), `rust-migration`
  (v1.1.1) and `sovereignty-loop` (v1.1.1) each claimed "no extra
  dependencies" while requiring `jq`. `dedupe-loop` also documented a
  `ripgrep` dependency no script of its own has. Required (`jq`) vs.
  optional (`ripgrep`, guarded by `command -v`) is now stated per tool.
- Three verifiable `docs-loop` findings: `README.md`'s "each category's own
  README" claim (only `yt_research_for_cc/` has one), its stale
  `zip/dedupe-loop-v1.0.0.zip` example (now version-free so it can't rot),
  and `ARCHITECTURE.md`'s Structure section, which never mentioned
  `need_to_productize/` or `trying/` — both now described by what's
  checkable: `.skill` archives, no `SKILL.md`, skipped by the tooling.
- 18 tracked scripts were committed as `100644` despite starting with `#!` —
  every script in `dedupe-loop`/`issue-loop`/`parity-loop`/`sovereignty-loop`,
  both `yt_research_for_cc` scripts, and all three under `scripts/`. All now
  `100755`.
- `scripts/restore_exec_bits.py` — takes a shebang as an independent,
  decisive signal (read from the staged blob), which is the only thing that
  catches a *genuinely new* script; the content-match check couldn't, since
  a new file has no prior blob at `HEAD`. PR #4 added this detection to
  `build_skill_zips.py` only, so zips shipped correct while the index didn't.
  It now also chmods the file on disk, so a `core.fileMode=true` clone
  doesn't silently revert the fix on the next `git add -A`.
- `.gitattributes` added with `* text=auto eol=lf` — the synced copy of
  `repo-config`'s `audit.sh` had CRLF endings and failed on Linux with
  `$'\r': command not found`. Forces LF in the working tree on every
  platform so a Windows checkout and anything copied out of it carry LF;
  `.skill`/`.zip` marked `binary`. Same root cause as the exec-bit problem
  `restore_exec_bits.py` handles. Doesn't retroactively fix existing
  checkouts (`git add --renormalize .`) or already-synced skill copies.
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
