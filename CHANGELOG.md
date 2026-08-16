# Changelog

All notable changes to this repo are documented here.
Format: Added / Changed / Deprecated / Removed / Fixed / Security, newest first.

## [Unreleased]
### Fixed
- `meta/my-skill-creator` (v1.1.0 → v1.1.1) — `quick_validate.py`'s vendored
  frontmatter allowlist rejected `version`, and since it gates
  `package_skill.py`, **no skill in this repo could be packaged by it** (#58).
  This repo requires `version`; upstream `skill-creator`, where the allowlist
  comes from, has no such convention — so `check_repo.py` failed a skill
  *without* the key and `quick_validate.py` failed the same skill *with* it.
  `version` is now allowed, with a comment marking the divergence for future
  upstream re-syncs.

### Added
- `tests/test_quick_validate.py` — 4 tests over the frontmatter allowlist,
  including the end-to-end invariant that no skill in the repo is rejected by
  it. Pins the two ways a careless fix goes wrong: adding `version` must not
  make it *required* (that's `check_repo.py`'s job), and a misspelled key must
  still be rejected. 76 tests total. Writing them surfaced #59 — four skills
  have descriptions containing an unquoted `": "`, invalid YAML that
  `check_repo.py`'s hand-rolled parser tolerates and PyYAML rejects.

### Fixed
- `meta/my-skill-creator` (v1.0.1 → v1.1.0) — the two silent failures in the
  eval loop, both found by a `skill-retro` pass on a real run. `grading.json`
  needs a `summary` block that step 4.1's inline schema omitted, and a missing
  one scored **0.0% for every configuration** with no warning (#50); the
  documented workspace layout omitted the `run-N/` level `aggregate_benchmark.py`
  requires, so following the instructions exactly produced a benchmark of zero
  runs (#51). Both are now documented correctly *and* fail loudly in the script.
  In both cases the correct information already existed in `agents/grader.md`,
  `references/schemas.md`, or the script's docstring — the defect was SKILL.md
  restating a partial version of it in the reader's path.
- `meta/skill-retro` (v1.1.2 → v1.2.0) — from its own step 6 self-retro:
  recording a finding as an issue is now a named third disposition alongside
  applied and declined, with a `filed (#N)` Status — the retro that found this
  had all seven findings filed rather than applied, an outcome the skill had no
  vocabulary for; the findings-format pointer moved from step 4 into step 3, so
  the table's required columns are known before the table is drafted; and the
  severity scale now rates a false statement in a user-facing artifact at least
  `costly-guess` regardless of whether the run itself was harmed.

### Added
- `dev_practices/unix-philosophy` (v1.1.0 → v1.1.1) — `evals/analysis/` now
  tracks the analyst passes and benchmark aggregates from both eval iterations.
  The run outputs stay scratch under the gitignored `*-workspace/`, but the
  conclusions were dying with the session: what the evidence supports (the skill
  makes recommendations accountable; it does not make the analysis smarter),
  what it doesn't (eval-5 scored 8/8 both ways, leaving the "when not to apply
  this" section unvalidated), and the note that several discriminating
  assertions were rewritten after a first iteration failed to discriminate.
- `dev_practices/unix-philosophy` (v1.0.0 → v1.1.0) — the wrap-up `skill-retro`
  step now fires only after an **audit report**, not after every invocation.
  Two design-mode eval runs reported *skipping* it (read-only sandbox, no
  subagents) and both were right to; a final step a run routinely reports not
  doing is worse than no step. Design mode instead offers the retro as an
  explicit request when a conversation turns into substantial work. This is the
  one place where the repo's retro-by-default convention was applied by habit
  rather than by fit — the sibling skills carrying it are long-running loops,
  where a retrospective is small next to the work it reflects on.
- `dev_practices/unix-philosophy` (v1.0.0) — new skill applying Unix software
  design philosophy in two modes: design mode (a checklist for a live design
  decision) and audit mode (eight dimensions scored Pass/Warn/Fail against
  cited evidence, findings ranked by present cost, report-and-stop). Three
  references carry the depth: the source philosophy plus the *cost* of each
  principle, the audit rubric and report template, and translations to
  non-CLI surfaces (libraries, HTTP/RPC services, background pipelines, agent
  tools) including where the analogy breaks for distributed systems.
- `dev_practices/` — fifth authored category folder, for design- and
  coding-discipline skills. The four existing categories are each scoped to a
  target (external repos, this repo's own skills, a research pipeline, a web
  framework); guidance on how software is shaped fits none of them, so per
  `meta/learn-it`'s category-placement rule this is a deliberate new category
  rather than a forced fit. `ARCHITECTURE.md`'s Structure section and the root
  `README.md` updated to match.
- `yt_research_for_cc/video-teardown` (v1.0.0) — new skill for turning a video
  into a verified, structured deliverable (build guide, runbook, parts list,
  checklist) rather than a one-off answer about its contents. Pairs a cheap
  captions pass with targeted ffmpeg extraction, then triages frames by
  scene-change detection and `showinfo` mean-luma sorting so only the few
  carrying real information get read — 73 frames down to the 9 that held every
  config value in the originating session. Second half is the verification
  discipline: reconstructed menu paths, flags and versions checked against
  official docs before shipping, each claim tagged on-screen-with-timestamp or
  reconstructed. Distilled by `meta/learn-it`. Deliberately a new skill rather
  than an edit to `trying/watch`, which overlaps on download-and-sample but is
  vendored third-party MIT code with its own upstream — rationale recorded in
  the skill's `RELEASE_NOTES.md`.
- `my_loops/repo-config` (v1.3.1 → v1.3.2) — step 4's currency check now covers
  **every log-shaped file in the set**, not just `RELEASE_NOTES.md`, and also
  verifies that entries whose PRs have merged carry their links. Written as a
  general rule rather than a two-filename enumeration so a log added later
  doesn't reintroduce the gap. `audit.sh` emits its presence-only caveat per
  log accordingly.
- `check_repo.py`'s `manifests` check now enforces claude.ai's 1024-character
  `description` limit, so an over-length description fails locally and in CI
  instead of at upload. Backed by `read_description()`, which handles YAML
  block scalars: the first version reused `read_frontmatter()`, which skips
  continuation lines by design and so measured `datastar-pro`'s `>` block as
  1 character — the guard would have shipped with the blind spot it was added
  to close.
- `tests/test_install_skills.py` — 9 tests over the file set shared by
  `build_skill_zips.py` and `install_skills.py`: artifact exclusion, nested
  walking, the stale-removal self-heal, that the installer uses the shared
  helper rather than its own walk, and the invariant that a zip and an
  install contain the same files for every skill. Plus 9 in
  `test_check_repo.py` over inline vs. block-scalar descriptions. 72 tests
  total.
- `scripts/retro_reminder.py` + `.claude/settings.json` — a `PostToolUse` hook
  on the `Skill` tool that reminds when an invoked skill carries a wrap-up
  `skill-retro` step. Twelve skills carry one; it fired zero times out of two
  opportunities today, so the step is now wired rather than restated. Silent
  for skills without one and for `skill-retro` itself. Project-scoped, and it
  reminds rather than enforces — both limits documented.
- `tests/test_retro_reminder.py` — 11 tests over the hook's silence
  guarantees and its recursion guard (mutation-verified).
- `docs/adr/0003-gitattributes-in-scope-gitignore-out.md` — records why
  `repo-config` admits `.gitattributes` but not `.gitignore`, as a reusable
  test (same-everywhere? loud or silent when wrong?) rather than a one-off
  verdict.
- `tests/` — 44 stdlib `unittest` tests over `check_references.py`'s parsing
  and classification logic and `check_repo.py`'s frontmatter parser, run by
  CI as a step separate from the lint checks. Each regression test names the
  bug it would have caught and was verified by reverting that fix and
  watching it fail. Resolves `CONTRIBUTING.md`'s long-aspirational "add tests
  for non-trivial logic" — the last open row from docs-loop's first run.
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
- `my_loops/repo-config` (v1.2.1 → v1.3.0) — two findings from its own
  skill-retro: an early exit when the audit is already at full marks (steps
  2–3 have nothing to do, and were being silently skipped), and a fallback
  when `audit.sh` itself won't run, which happened this session.
- `my_loops/docs-loop` (v1.2.1 → v1.3.0) — six findings applied from the
  first `meta/skill-retro` pass on it. Chief among them: step 4 now stops and
  re-reports when an approved row outgrows its approval (row 5 was approved
  as one line in one file and delivered as six skills), and doc-comments drop
  out of default scope because the loop provides no way to audit them and was
  claiming whole-repo coverage without them.
- `my_loops/repo-config` (v1.2.0 → v1.2.1) — Limitations cites ADR-0003 for
  the scope boundary instead of only asserting it. Doc-only.
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
- Five skill `description` fields were over claude.ai's 1024-character upload
  limit and were rejected one at a time at upload: `rust-migration` (1354),
  `docs-loop` (1274), `learn-it` (1209), `repo-config` (1146), `skill-retro`
  (1135). Trimmed to 979–1009 with every trigger phrase kept; no behavior
  changed. Nothing local could have caught it — `install_skills.py` and
  `build_skill_zips.py` both copy frontmatter without reading it, and Claude
  Code loads an over-length description fine, so the limit was enforced only
  by the one install path that can't be scripted.
- `scripts/install_skills.py` mirrored build artifacts into
  `~/.claude/skills/<name>/scripts/`. The "what counts as part of a skill"
  filter lived only in `build_skill_zips.py`, so the zips stayed clean while
  the installed tree collected `__pycache__` on every install that followed a
  `check_repo.py` run — the order the README recommends. Now both call a
  shared `iter_skill_files()`; the existing stale-file pass removes anything
  an earlier install left behind.
- `meta/skill-retro` (v1.1.0 → v1.1.1) — `redundant-step` now covers both a
  step that added nothing *and* a step stated unconditionally that's only
  sometimes correct, since the second takes a condition rather than a
  deletion as its fix. From this skill's own self-retro, where a `docs-loop`
  finding had to be filed under a category that implied the wrong edit.
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
