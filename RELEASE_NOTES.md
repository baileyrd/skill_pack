# Release Notes

This repo has no version tags yet, so this file tracks by PR against `main` —
one entry per merged PR, reverse chronological, each linking to its PR.

---

## issue-loop learns its own gh-less path
**2026-08-19** — [#82](https://github.com/baileyrd/skill_pack/pull/82)

Applied from `issue-loop`'s step-5 wrap-up retro on the run against
`rusty_naner` that shipped `naner suggest`
([rusty_naner#108](https://github.com/baileyrd/rusty_naner/pull/108)) — a
Claude Code web session with no `gh` binary, where every scripted step needed
a substitute and the instructions named only "the MCP tools." Five findings,
applied as one user-approved batch (issue-loop v1.6.1 → v1.7.0): the
preflight now names the working substitute per script (reuse search =
attach-read-only + shallow clone + `rg`; CI-wait = `subscribe_pr_activity` +
a `send_later` check-in, merging on `head_sha`-matched green checks), the
repo-config prerequisite gets a governance-file-inspection fallback for its
own `gh`-dependent `audit.sh`, step 3.4's branch naming yields to a
harness-designated branch, and unset-harness-mode ambiguity degrades to the
`needs-human` label instead of a question nobody will answer.

---

## repo-config's currency check stops having a blind spot
**2026-08-16** — [#39](https://github.com/baileyrd/skill_pack/pull/39)

Applied from the step-5 wrap-up retro on the `/repo-config` run that produced
[#36](https://github.com/baileyrd/skill_pack/pull/36). Both findings were filed
as issues first ([#37](https://github.com/baileyrd/skill_pack/issues/37),
[#38](https://github.com/baileyrd/skill_pack/issues/38)) and applied only after
sign-off — the separation `skill-retro` requires between finding and fixing.

- **Fixed (repo-config v1.3.2) — the currency check named one file and meant
  two.** Step 4 exists precisely to catch what `audit.sh` structurally can't: a
  file that is present but stale. It scoped that judgment to `RELEASE_NOTES.md`
  in all five places the rule appeared. `CHANGELOG.md` sits in the same
  checklist and counts toward the same 11/11, so it collected full presence
  credit with nothing ever asking whether it was current. **On the run that
  found this, the changelog had no record of the latest PR at all.** It surfaced
  only because the file set got inspected by hand — not a step the instructions
  contained. A run that followed them exactly would have reported a fully
  current repo.
- **Fixed (repo-config v1.3.2) — a correct rule that guaranteed a later
  violation.** "Log it without a link if the PR doesn't exist yet" is right;
  inventing a PR number is worse. But nothing ever came back to add the link,
  so following the rule correctly at write time reliably left an entry
  violating the convention `RELEASE_NOTES.md`'s own header states. Step 4 now
  closes it, which is the right place: step 4 runs after the work is pushed,
  the first moment a link can be added honestly. That only 2 of this file's
  entries carried links suggests it had been recurring quietly for a while.
- **The generalization is the actual fix.** Both issues proposed naming
  `CHANGELOG.md` alongside `RELEASE_NOTES.md`. That would have worked and
  would have been wrong — it's the same enumeration one item longer, waiting
  for a third log. The rule now reads "every log-shaped file in the set."
- **Left undone, deliberately:** step 0 still infers language from a stack
  manifest only, so this repo — no manifest, unmistakably Python — scans as
  having no language. It did not fire on the run that found the other two, so
  under `skill-retro`'s evidence-grounded rule it stayed an observation. Not
  filed, not fixed, recorded here so it isn't rediscovered as new.

---

## Two ship blockers the local tooling couldn't see
**2026-08-16** — [#35](https://github.com/baileyrd/skill_pack/pull/35)

Both found by installing this repo's skills and then uploading them — not by
any check here, which is the point of the entry.

- **Five descriptions were over claude.ai's 1024-character limit** and were
  rejected at upload, one file at a time: `rust-migration` (1354),
  `docs-loop` (1274), `learn-it` (1209), `repo-config` (1146), `skill-retro`
  (1135). Trimmed to 979–1009, every trigger phrase and by-name reference
  kept; the cuts are positioning prose and detail each skill already states
  in its body. No behavior changed. Patch bumps and per-skill notes.
- **Nothing local could have caught it.** `install_skills.py` copies
  frontmatter without reading it, `build_skill_zips.py` zips it the same way,
  and Claude Code loads an over-length description fine. The limit is enforced
  only by the one install path that can't be scripted. `check_repo.py`'s
  `manifests` check now enforces it.
- **The first version of that check had the blind spot it was added to
  close.** `read_frontmatter` deliberately skips continuation lines, so it
  measured `datastar-pro`'s `>` block scalar as **1 character** — any wrapped
  description would have passed. Added `read_description`, which handles both
  forms.
- **`install_skills.py` was installing build artifacts.** The "what counts as
  part of a skill" filter lived only in `build_skill_zips.py`; the installer
  mirrored `rglob("*")` wholesale, so `__pycache__` landed in
  `~/.claude/skills/<name>/scripts/` on every install following a
  `check_repo.py` run — the order the README recommends. Zips were clean the
  whole time, which is how two tools disagreed about the contents of a skill
  without anyone noticing.
- **Fixed as a shared helper, not a copied filter** (`iter_skill_files`),
  since duplicated logic is what let them drift. The stale-file pass now
  removes any `__pycache__` an earlier install wrote, so it self-heals.
- **18 new tests** across `test_check_repo.py` and a new
  `test_install_skills.py`: inline vs. block-scalar descriptions, block
  termination at the next top-level key, artifact exclusion, and the
  invariant that a zip and an install contain the same file set.

---

## skill-retro on repo-config — and the wrap-up retro finally wired
**2026-08-15**

- **Ran** `meta/skill-retro` against `my_loops/repo-config`, grounded in this
  session's `/repo-config` run. Stated up front in the report: that run
  executed **v1.1.0** while the skill on disk was v1.2.1, so every finding was
  re-checked against current text before being called real. All three
  survived two intervening versions.
- **Fixed (repo-config v1.3.0):** an early exit for the already-saturated
  repo. The run scored 10/10, so steps 2, 2.5 and 3 were **silently skipped** —
  three mandatory-looking steps skipped on a judgment the text didn't
  sanction. Greenfield covers "nothing exists"; nothing covered "everything
  exists," which is every re-run after the first.
- **Fixed (repo-config v1.3.0):** a fallback when `audit.sh` won't run. Step 0
  makes it the gateway and it *failed* this run — the synced copy had CRLF and
  died on its shebang. The checklist is 11 named files; a dead script is not a
  blocked run.
- **The third finding is the one that mattered, and it indicted an earlier
  fix.** Step 5's wrap-up retro didn't fire — the *second* occurrence, after
  `docs-loop`'s identical step. **Twelve skills carry that step; it ran twice
  today and fired zero times.** An hour earlier I'd "fixed" the docs-loop
  instance by defining when a run has *ended*, which treated a symptom: the
  step was never ambiguous, it was simply forgotten, by the same reader, twice.
- **Wired instead of reworded:** `scripts/retro_reminder.py`, a `PostToolUse`
  hook on the `Skill` tool in `.claude/settings.json`. It reads the payload,
  finds the invoked skill's `SKILL.md`, and injects a reminder only if that
  skill carries a retro step. Silent otherwise; silent for `skill-retro`
  itself, whose own step 6 handles that and for which a reminder would be the
  recursion its guard exists to stop; and it says the retro fires when the
  *run* ends, not per invocation, so it doesn't become the noise that trains
  you to ignore it.
- **Pipe-tested across seven payload shapes before wiring** (skill with a
  retro step, `skill-retro`, a skill without one, unknown skill,
  `plugin:skill` form, malformed JSON, empty stdin), then validated with
  `jq -e` against the settings schema. Eleven tests added — the recursion
  guard's test was mutation-checked by removing the guard and watching it go
  red. Suite now 55 tests.
- **Two limits stated rather than glossed:** the hook is project-scoped, so it
  fires when working *in this repo* — using one of these skills against an
  external target from elsewhere needs the same block in
  `~/.claude/settings.json`. And **the hook could not be proven to fire in
  this session**: `.claude/` didn't exist when the session started, so the
  settings watcher isn't watching it. Pipe-test and schema validation both
  pass; live firing needs a `/hooks` open or a restart, which is the user's to
  do. A hook can only remove "I forgot" as a failure mode — it cannot make the
  retro run.

## skill-retro v1.1.1 — its own self-retro, one finding applied
**2026-08-15**

- **Fixed:** `skill-retro`'s step 3 gave `redundant-step` no definition, and
  the name alone pushes toward deletion. Found by its own step-6 self-retro,
  run automatically after the `docs-loop` retro: one of that retro's six
  findings didn't fit any category cleanly. `docs-loop`'s per-run tracking
  issue wasn't redundant — it was correct when auditing and fixing are split,
  and stated unconditionally. The right edit was a condition, not a cut, and
  the category name argued for the opposite.
- The category now names both shapes explicitly, with the warning attached.
  A taxonomy gap that quietly recommends the wrong fix is worth closing on
  first occurrence, unlike the two below.
- **Logged, deliberately not applied:** step 0 assumes B's run is a discrete
  "just finished" block, where this one spanned eight turns with unrelated
  work interleaved and four PRs landing on top before the retro was asked
  for; and the findings format has nowhere to record a rule that *fired and
  prevented* a defect, so the evidence that `docs-loop` step 4's
  checkable-claims rule caught two false sentences had to go outside the
  table as prose. Both `cosmetic`, both single-run — and this skill's own
  Limitations argue that one occurrence of a minor finding is worth logging
  rather than acting on. Applying its own advice to itself seemed like the
  point.
- **The recursion guard worked:** B was `docs-loop`, so step 6 fired once and
  did not cascade into retro-ing the self-retro.

## skill-retro on docs-loop — six findings, all applied
**2026-08-15**

- **Ran** `meta/skill-retro` against `my_loops/docs-loop`, grounded in this
  session's own run of it: the audit, the rows 1–3 pass, the row 5 pass, and
  the `my_loops/README.md` deletion. Six findings, every one with a concrete
  incident behind it; all approved and applied (`docs-loop` v1.2.1 → v1.3.0).
- **The finding worth reading:** row 5 was approved as *"declare PyYAML — one
  line in that skill's Scripts section"* and delivered as edits to **six
  skills**. The step-3 checkpoint is the loop's core safety mechanism, and it
  widened silently because nothing in step 4 said to stop when a row outgrows
  its approval. Now it does, in auto mode too. Classified
  `could-have-caused-real-damage` on skill-retro's own rule that severity is
  judged by what the gap could cause on a *different* run — here, six files
  edited on a one-file approval happened to be correct work, which is exactly
  what makes it easy to miss.
- **The skill was making the same class of claim it exists to catch.** Step 0
  put doc-comments in *default* scope while providing no extraction pass for
  any language — so the run audited zero of them and still reported whole-repo
  coverage. Now opt-in, with Limitations updated to agree rather than
  contradict.
- **Also applied:** step 1 must declare prior exposure when the docs were
  already read earlier in the session (this run had read README and
  ARCHITECTURE hours before building ground truth, and caught it only by
  improvisation); the per-run tracking issue became conditional on auditing
  and fixing being split; step 5 stopped asking for a re-run that says
  nothing; step 6 got a definition of when a run has *ended*, since it never
  fired on its own and had to be requested four turns late.
- **Logged, not acted on:** `inventory_docs.sh` contributed nothing this run —
  38 of 98 docs share one bulk-commit date, so its ranking was a flat tie at
  the top. One run is not enough to call a step dead, per skill-retro's own
  single-run-evidence limitation.
- **Validated:** step 4's "every claim you write must be checkable against
  something in the tree" caught two false sentences before they landed, on two
  separate passes. Left exactly as written.

## ADR-0003 — `.gitattributes` in scope, `.gitignore` out
**2026-08-15**

- **Added:** `docs/adr/0003-gitattributes-in-scope-gitignore-out.md`,
  recording the scope decision made when `repo-config` v1.2.0 took
  `.gitattributes` into its template set. Until now the reasoning lived only
  in a Limitations paragraph and a release note.
- **The decision it records is a test, not a verdict.** `repo-config`'s
  boundary used to be drawn by category — repo-level git config was excluded
  wholesale, so `.gitignore` and `.gitattributes` sat on the same side of the
  line without the line being argued. It's now drawn by two questions: does
  this file have the same correct content everywhere, and does getting it
  wrong fail loudly or silently? `.gitattributes` is same-everywhere and
  fails loudly (a script that won't run). `.gitignore` is per-project and
  fails silently, in the worst direction — a file that should have been
  committed simply isn't.
- **Four alternatives recorded with why they lost**, including the cheap one
  (fix only this repo, leave the template alone) and the consistent-looking
  one (bring `.gitignore` in too, which fails on the asymmetry above).
- **Consequences stated, including the unwelcome one:** `audit.sh`'s
  denominator moved 10 → 11, so every repo the skill has already been run
  against now scores 10/11 until the file is applied. Intended signal, not a
  regression — but it will surface.
- **Changed:** `repo-config` (v1.2.0 → v1.2.1) — its Limitations now cite
  ADR-0003 for the reasoning instead of only asserting the conclusion, so a
  future proposal to add repo-level config has a test to meet rather than a
  precedent to point at.
- **Cross-referenced with ADR-0002:** `.gitattributes` cannot fix the
  executable bit — git has no attribute for permissions — so the two halves
  of the same Windows-authored/Linux-consumed problem are handled by
  different mechanisms, and the ADR says so rather than leaving a reader to
  assume one covers both.

## Build a test harness — 44 tests, each naming the bug it would have caught
**2026-08-15**

- **Added:** `tests/`, run by `python3 -m unittest discover -s tests` and by
  CI as a step separate from the lint checks. Stdlib `unittest`, **no
  third-party runner**: PyYAML is already the only third-party import in this
  repo and is documented as an exception, not a precedent, and a suite you
  can only run after `pip install` is a suite that stops being run.
- **Resolves** `CONTRIBUTING.md`'s "add tests for non-trivial logic", open as
  `aspirational` since docs-loop's first run and the last unresolved row in
  `docs-audit.md`. Every finding from that run is now resolved, deferred with
  a written reason, or logged as an accepted non-finding.
- **The admission rule is ADR-0002's, applied to tests:** a test earns its
  place by naming the bug it would have caught. Not coverage — the specific
  mistakes this code has already proven it makes. `check_references.py` alone
  was wrong four separate ways on the day it was written, each in a way that
  read as obviously correct, so most of the suite is those four plus the
  classification logic they exposed.
- **Every regression test was verified by reverting its fix and watching it
  fail** — slugify collapsing whitespace (the 12-false-anchor bug), the
  `:line` suffix, single-backtick-only code spans, `docs-audit.md` not
  counted as historical (today's red-build), and component-root resolution.
  All five went red on mutation and green on restore.
- **The mutation harness was itself broken on the first attempt**, which is
  the honest headline. It reported `FAILED (errors=1)` for all five and I
  nearly wrote that up as "all five caught" — but they were `ImportError`s
  from running `unittest` with a module path that isn't importable from the
  repo root. The tests never executed. Re-run with
  `discover -s tests -k <name>`, all five produce real `failures=1`. A
  verification step that can't itself be verified is worth exactly nothing,
  and this one nearly shipped as evidence.
- **Tests run as a separate CI step, not a sixth check in
  `check_repo.py`** — ADR-0002 governs repo *checks* (lint over structure,
  admitted only for a failure that actually happened) and states that lint is
  not tests. Folding the suite in would blur the line that ADR exists to
  draw.
- **What isn't unit-tested, and why:** the git-dependent checks (`exec-bits`,
  `line-ends`) and the packaging smoke test. Their behavior *is* the
  integration with git and the filesystem; a mock of `git cat-file` would
  test the mock. They stay verified by fault injection, which is what caught
  the two cases where a check silently passed when it shouldn't have.

## ADR-0002 — a repo check needs a real failure behind it
**2026-08-15**

- **Added:** `docs/adr/0002-repo-checks-require-a-real-failure.md`, the ADR
  log's first actual decision. Records why CI was added as a deliberate
  exception to `repo-config`'s "no manifest, no workflow" rule, and the
  constraint that makes the exception safe: **a check earns its place by
  naming the commit it would have failed.**
- **Three corollaries recorded because each is load-bearing:** a check must
  be demonstrated failing before it ships (two of the five silently passed
  their first fault injection); a check that can't be green on day one gets
  a baseline with written reasons, not a waiver; and lint is not tests and
  must not be described as tests.
- **Four rejected alternatives written down with why they lost** — including
  the genuinely reasonable one (keep no CI, delete the claim from
  CONTRIBUTING) and the conventional one (adopt an off-the-shelf lint stack,
  which would have caught none of the four defects that prompted this and
  arrived with a backlog of unrelated style findings).
- **What it forecloses, stated plainly:** a sixth check now needs an
  incident, not an argument. That's the point — but it's a real constraint
  and belongs in the record rather than in someone's memory.
- **Resolved:** `ARCHITECTURE.md`'s "See `docs/adr/` for the record of
  individual decisions and their tradeoffs", open as `aspirational` since
  docs-loop's first run. The log now points at a decision instead of at an
  unfilled `# ADR-0001: <Title>` template.
- **Found while writing it:** adding CI yesterday-afternoon made
  `ARCHITECTURE.md`'s Non-goals claim — "`scripts/*.py` are one-shot tooling
  invoked by hand" — inaccurate, since `check_repo.py` is now invoked by the
  workflow too. A small drift introduced by my own change a few hours
  earlier, caught only because writing the ADR meant re-reading what the repo
  claims about how its scripts run. Fixed by naming which three are
  hand-invoked and which one CI also runs.
- **Not written:** a second ADR for the `.gitattributes`-in-scope /
  `.gitignore`-out-of-scope decision from `repo-config` v1.2.0. It's a real
  decision with a real rationale and would make a reasonable ADR-0003 — left
  for a separate call rather than bundled in.

## Delete my_loops/README.md — the stub that said `# skill_pack`
**2026-08-15**

- **Removed:** `my_loops/README.md`. It contained one line — `# skill_pack`,
  the *root repo's* own title — in a category folder, with no trailing
  newline and nothing else. A copy-paste stub that was never filled in.
- **Why deleting rather than writing one:** the repo owner's call, after
  docs-loop flagged it and stopped. Deleting a whole doc file is one of the
  things the skill never does unattended in either harness mode, and this is
  why — "write it" and "delete it" are both defensible, and the difference is
  a judgment about whether category-level READMEs are wanted at all. The
  answer turned out to be no: `meta/` and `web_dev/` have none either, so the
  stub was the outlier, not the norm. `yt_research_for_cc/` keeps its real
  one because it documents that pipeline's dependencies.
- **Checked before deleting:** no doc links to it. The only mentions anywhere
  are in this file's own earlier entries, which are historical record and are
  left alone per the rule against rewriting past entries.
- **CI caught the follow-on problem immediately, which is the first time
  that's happened here.** Deleting the file made `docs-audit.md` — which
  records the finding *and* its resolution — reference a path that no longer
  exists, and `doc-refs` failed the run. The fix wasn't a baseline entry:
  `docs-audit.md` persists rows across runs by design, so it necessarily
  accumulates references to things a run deliberately removed. It now joins
  `CHANGELOG`/`RELEASE_NOTES` in the checker's historical set
  (`docs-loop` v1.2.1), where a row recording a deletion reads as the report
  working rather than as drift. Verified the change is scoped: a doc with a
  similar name still reports `broken` normally.
- **It also fixes a sentence I got slightly wrong.** The row-1 fix earlier
  today rewrote the root README to say "the other categories don't have one"
  — which wasn't quite true while `my_loops/` still had its stub. That claim
  is now exactly accurate. A small thing, but it's the same failure mode this
  loop keeps catching: a sentence that reads true, isn't, and nobody notices
  because it's *nearly* right.

## Add CI — five checks, each for a bug this repo actually had
**2026-08-15**

- **Added:** `.github/workflows/ci.yml` and `scripts/check_repo.py`. The
  design rule was that a check earns its place by naming the commit it would
  have failed, not by being good practice in the abstract:
  | Check | The failure behind it |
  | --- | --- |
  | `exec-bits` | 18 tracked scripts committed `100644` despite a shebang, shipped non-executable for months (PR #22) |
  | `line-ends` | The synced `audit.sh` arriving with CRLF and dying on its shebang (PR #20) — regression guard, since the index was clean that time |
  | `doc-refs` | docs-loop's first run: a dead script path in dedupe-loop, a TOC anchor pointing at nothing in datastar-pro (#16, #17) |
  | `manifests` | `name`/directory match, semver `version`, `RELEASE_NOTES.md` present — the "real fix shipped with no entry" failure repo-config's own log records |
  | `packaging` | `build_skill_zips.py` still runs — smoke test before anyone relies on its output |
- **Each check was verified by reproducing its historical bug**, not by
  assuming: a shebang file forced to `100644`, a CRLF blob written straight
  into the index with `git hash-object` (normal `git add` can't produce one
  any more — `.gitattributes` normalizes it, which is the earlier fix
  working), a new broken reference, a skill with a wrong name and bad
  version, and a deliberately broken packager. All five failed as intended,
  then passed again once reverted.
- **Two of those tests initially failed to fail**, which is the reason for
  testing this way. `line-ends` didn't fire on `git add` of a CRLF file —
  `.gitattributes` had silently fixed it — so the check needed a blob written
  past the filters to prove its detection works at all. And `packaging`
  didn't fire when a `raise` was appended to the end of
  `build_skill_zips.py`: the script's own `raise SystemExit(main())` runs
  first, so the injected fault was unreachable code. A check that can't be
  shown to fail is not a check.
- **Added:** `docs-refs-baseline.tsv`, 3 accepted rows each with a written
  reason. Wired in without it, `doc-refs` would have been red on day one from
  the documented structural false-positive class (most docs here describe
  *other* repos) — and repo-config's own rule is that an always-red workflow
  is worse than none. `--baseline` support went into
  `my_loops/docs-loop`'s `check_references.py` (v1.1.0 → v1.2.0), keyed on
  `kind + doc + detail` *without* the line number so an accepted row doesn't
  return as new when a paragraph is added above it. Stale entries are
  reported, never fatal.
- **Fixed a flaky-CI bug in the new code before it shipped:** the `packaging`
  check builds into `zip/`, and a `zip/` that exists changes what `doc-refs`
  sees — a doc quoting `zip/x-v1.0.0.zip` only resolves as "broken" when the
  directory is there. Caught by running the two checks in isolation and
  getting a different answer than the full suite gave. `packaging` now
  restores the tree, while keeping zips a developer built on purpose.
- **Side effect worth noting:** creating `.github/workflows/` resolved 3 of
  the 6 outstanding broken doc references on its own — three docs referenced
  that directory, which until now didn't exist.
- **Resolved:** `CONTRIBUTING.md`'s "CI must be green before merge", open as
  `aspirational` since docs-loop's first run. It now points at something
  real, with the honest caveat that a workflow only *reports* until it's set
  as a required status check in branch protection — which needs a repo admin,
  not a commit.
- **Deliberately NOT resolved:** "Add tests for non-trivial logic." These
  five checks are lint over repo structure, not behavior, and calling them
  tests would be exactly the kind of green-badge dishonesty this whole
  exercise has been about. CONTRIBUTING now states plainly that no harness
  exists and asks PRs to say so rather than tick a box that isn't real. The
  underlying question — build one, or drop the requirement — is still open.

## docs-loop row 5: dependency declarations, six skills wide
**2026-08-15**

- **Fixed:** the row logged as "one line to declare PyYAML" turned out to be
  a dependency-declaration defect in six skills, in both directions.
  `meta/my-skill-creator` (v1.0.1) documented no dependency while
  `scripts/quick_validate.py:8` does an unguarded `import yaml`. Five
  `my_loops` skills — `dedupe-loop` (v1.1.2), `issue-loop` (v1.1.1),
  `parity-loop` (v1.2.1), `rust-migration` (v1.1.1), `sovereignty-loop`
  (v1.1.1) — each asserted "no extra dependencies" while requiring **`jq`**
  in their issue-picking script.
- **One went the other way:** `dedupe-loop` documented a `ripgrep`
  dependency that **no script of its own has** — inherited when its Scripts
  note was copied from a sibling. Overstating a dependency is the rarer
  failure and the one a "just add the missing thing" fix would have left
  untouched.
- **Required vs. optional is now stated per tool**, because it differs:
  `jq` is piped unguarded, so it's a hard requirement, while `ripgrep` is
  guarded by `command -v rg` with a `grep` fallback in all four scripts that
  use it. Documenting both as "dependencies" would be as wrong as omitting
  them.
- **Two near-misses, both caught by checking before writing.** `jq` appears
  in every `watch_and_merge.sh` as `gh --jq` — gh's own built-in JSON flag,
  needing no `jq` binary — so counting those would have invented a
  dependency for `docs-loop`, which has none. And a draft sentence calling
  PyYAML "the only third-party dependency anywhere in this repo's skills"
  ignored `yt-dlp`, which `yt_research_for_cc` needs as an external binary;
  the claim was narrowed to third-party *imports*, which is what the scan
  actually establishes (17 tracked `.py` files, `yaml` the only one).
- **Every citation verified** rather than asserted: each `jq` pipe and
  `command -v rg` guard was read back at the exact line number quoted in the
  six release notes.
- This is the second consecutive fix pass where writing the fix surfaced a
  larger finding than the audit row it came from — worth noting as a pattern
  when judging how much a `docs-audit.md` row's size estimate is worth.

## docs-loop rows 1–3: fix the verifiable findings
**2026-08-15**

- **Fixed:** `README.md` intro claimed "see each category's own README for
  dependencies specific to it." Only `yt_research_for_cc/` has one;
  `meta/` and `web_dev/` have none and `my_loops/README.md` is a stub. Now
  points at the one that exists and sends the reader to the individual
  `SKILL.md` otherwise.
- **Fixed:** `README.md`'s zip example cited `zip/dedupe-loop-v1.0.0.zip`;
  that skill is v1.1.1. Replaced with `zip/dedupe-loop-v<version>.zip` and a
  note that the version comes from the skill's own frontmatter — a
  version-free example can't rot again, which is a better fix than bumping
  the number and waiting for it to go stale.
- **Fixed:** `ARCHITECTURE.md`'s Structure section named four category
  folders and `scripts/`, but `need_to_productize/` (4 files) and `trying/`
  (3) appeared in no doc anywhere. Both now described by what's checkable:
  they hold exported `.skill` zip archives rather than unpacked skills,
  contain no `SKILL.md`, and are therefore skipped entirely by
  `build_skill_zips.py`/`install_skills.py`, which enumerate via
  `rglob("SKILL.md")`.
- **Deliberately not asserted:** what `trying/` is *for*, as distinct from
  `need_to_productize/`. The repo records it nowhere — the folder name is
  the only evidence, and a name isn't ground truth.
  `need_to_productize/` did get a purpose sentence, because `CHANGELOG.md`'s
  `Removed` entry for `datastar-pro.skill` documents it.
- **New finding, found by fixing the first one:** the initial replacement
  for the README line asserted the other categories needed "nothing beyond
  `git`, `gh`, and the Python standard library." Checking it before
  committing — per docs-loop's rule that every written claim must point at
  something in the tree — showed it was false:
  `meta/my-skill-creator/scripts/quick_validate.py` imports PyYAML, and the
  loop shell scripts invoke `jq`/`rg`. The sentence was rewritten to claim
  only what it can show, and the undeclared PyYAML dependency was logged as
  a new `missing` row in `docs-audit.md` rather than fixed in this pass.
  A confident, plausible, wrong sentence is precisely what this loop exists
  to keep out of a README, and it nearly wrote one.
- **Verified**, not eyeballed: every claim written was re-derived
  (`ls` on the two absent READMEs, `git ls-files` counts for both archive
  folders, zero `SKILL.md` inside either, `rglob("SKILL.md")` present in the
  enumerator, the CHANGELOG entry cited), and the documented zip command was
  actually run — it emits `zip/dedupe-loop-v1.1.1.zip`, matching the new
  version-free wording.
- **Still open:** the four rows needing a decision (delete-or-write
  `my_loops/README.md`; CI and tests claimed by `CONTRIBUTING.md` but never
  built; `docs/adr/` holding only an unfilled template), plus the new
  PyYAML row.

## docs-loop's first real run — docs-audit.md checkpoint
**2026-08-15**

- **Added:** `docs-audit.md` — the checkpoint from `my_loops/docs-loop`'s
  first end-to-end run against this repo. Committed rather than handed back
  because the skill's own `references/docs-audit-format.md` says to: the
  `accurate` and `unverifiable` rows persist so a re-run starts from the
  last run's verdicts instead of re-litigating every claim.
- **Found:** 7 real findings — 3 stale/missing facts, 1 orphaned stub
  (`my_loops/README.md` contains the *root repo's* title and nothing else),
  and 3 `aspirational`. **No doc edits made yet**; the run is paused at its
  step-3 checkpoint with `LOOP_HARNESS_MODE` unset, so nothing proceeds
  without a per-row pick.
- **The aspirational three are the interesting result:** `CONTRIBUTING.md`
  requires green CI (there are no workflows), requires tests for non-trivial
  logic (there is no test harness), and `ARCHITECTURE.md` points at
  `docs/adr/` "for the record of individual decisions" when that directory
  holds one unfilled template. These were never true rather than having
  rotted — and every PR merged today ticked "Tests added/updated: n/a"
  against a CONTRIBUTING that requires them. Whether to build those
  practices or document their absence is a decision, not a docs edit, which
  is why all three wait in either harness mode.
- **One code finding, reported not fixed** (docs-loop never edits code):
  `scripts/build_skill_zips.py` ignores `--help` and builds all 14 zips
  instead of printing usage. Both siblings handle it correctly.
- **Logged against the run itself:** the auditor had already read `README.md`
  and `ARCHITECTURE.md` earlier in the session before building ground truth
  — precisely the confirmation-reading failure the skill's step order exists
  to prevent. Every claim was re-derived from `git ls-files` and `SKILL.md`
  frontmatter rather than recall, but a first run from a clean context would
  be a stronger test of the skill than this one was.

## Fix the exec-bit half: 18 scripts committed non-executable
**2026-08-15**

The line-ending fix in the two entries below is what prompted the obvious
follow-up question — what about the executable bit? `.gitattributes` can't
help: git has no attribute for permissions, the mode lives in the index, and
there's no `eol=`-style equivalent. Different mechanism, different fix.

- **Found:** 18 tracked files start with `#!` and were committed as
  `100644` — every script in `dedupe-loop`, `issue-loop`, `parity-loop` and
  `sovereignty-loop`, both `yt_research_for_cc` scripts, and all three of
  this repo's own tooling scripts under `scripts/`. `restore_exec_bits.py`
  could never have caught them: it restores `+x` only for content
  byte-identical to a blob that was already `100755` at `HEAD`, and a
  brand-new file has no prior blob to match.
- **Root cause of the gap:** PR #4 added shebang detection, but only to
  `build_skill_zips.py`. So zips shipped correct at `0o755` while the index
  they were built from was wrong — which is why this went unnoticed. The
  same two-line check never reached `restore_exec_bits.py`, the script whose
  entire job is staging that bit.
- **Fixed:** `restore_exec_bits.py` now takes a shebang as an independent,
  decisive signal, read from the *staged blob* rather than the working-tree
  file (what's about to be committed is what matters, and the two can
  differ). The content-match check stays — it's still the only thing that
  helps an executable with no shebang. Ran it: all 18 corrected, 35 files
  now `100755`, re-run is a clean no-op.
- **Fixed, second-order:** the script now also chmods the file on disk, not
  just the index. On a `core.fileMode=true` clone — any Linux/macOS checkout,
  including the one this ran on — fixing only the index leaves git reporting
  an unstaged `old mode 100755 / new mode 100644`, which the documented
  `git add -A && python scripts/install_skills.py` workflow then silently
  reverts. The fix would have undone itself on the next run. Windows is a
  no-op; there's no bit on disk to mirror.
- **Verified** with a scratch file inside the repo (the script is pinned to
  its own `REPO_ROOT`, so it can't be tested against an arbitrary target):
  a new 644 shebang script goes to `100755` in the index *and* `755` on
  disk, a non-script alongside it is left alone, and the fix survives a
  subsequent `git add -A`.
- **Still not fixed, and not fixable here:** the copies under
  `~/.claude/skills/synced/`, which arrive `-rw-r--r--` even for scripts
  that are correctly `100755` in the index. That's the claude.ai sync path,
  not one this repo controls. `install_skills.py` is unaffected — it already
  gets `0o755` via `git_file_mode`, which it imports from
  `build_skill_zips.py`.

## repo-config v1.2.0 — .gitattributes joins the standard set
**2026-08-15**

- **Added:** `.gitattributes` to `repo-config`'s template set and to
  `audit.sh` as its 11th checklist item, so every repo the skill touches
  gets the fix this repo just applied to itself rather than each one
  rediscovering it after a script fails somewhere downstream.
- **Added:** a correctness check the other ten items don't get. Presence is
  the wrong question here — a repo can carry a `.gitattributes` that only
  marks binaries and still hand out CRLF shell scripts — so `audit.sh` greps
  for `eol=lf` and warns when a present file doesn't enforce it. This is the
  same presence-vs-currency gap the script already flags for
  `RELEASE_NOTES.md`, applied to the one item where a wrong file is worse
  than a missing one.
- **Changed:** the skill's Limitations, which previously ruled out
  repo-level git config wholesale. The line is now drawn on which kind of
  file it is: `.gitignore` stays out because what's ignorable is genuinely
  per-project and a wrong guess silently stops a real file from being
  committed; `.gitattributes` comes in because there's one correct answer
  for every repo here and getting it wrong breaks scripts at a distance, in
  a copy nobody is looking at.
- **Verified end to end** against a scratch repo rather than assumed: a
  template-root dotfile was the real risk in `apply.sh`'s `find -type f`
  copy loop, so that got tested first. `apply.sh` delivers it, `audit.sh`
  scores 11/11, a binaries-only `.gitattributes` triggers the warning, a
  second run skips it non-destructively, and a committed CRLF `.sh` comes
  back from `git checkout` as LF.
- Template also handles what this repo's own copy didn't need to: `.bat`,
  `.cmd` and `.ps1` are pinned to `eol=crlf`, since Windows-native scripts
  genuinely want it, and a blanket LF rule would break them on the way to
  fixing the shell scripts.

## Add .gitattributes — force LF working-tree line endings
**2026-08-15**

- **Fixed:** the synced copy of `repo-config`'s `audit.sh` at
  `~/.claude/skills/synced/repo-config/scripts/audit.sh` had CRLF line
  endings and wouldn't run on Linux — `line 5: $'\r': command not found`,
  then `set: pipefail: invalid option name`. Found by invoking `/repo-config`
  against this repo, where step 0's very first command failed; ran the repo's
  own LF copy instead to finish the audit.
- **Fixed by:** `.gitattributes` with `* text=auto eol=lf`. `eol=lf` forces
  LF in the **working tree** on every platform, not just in the index (which
  was already clean — `git add --renormalize .` produced zero changes,
  confirming the corruption happens after checkout, not in git's storage).
  A Windows checkout now produces the same bytes a Linux one does, so
  anything copying files out of it — skill sync, `install_skills.py`,
  `build_skill_zips.py` — carries LF along. `.skill`/`.zip` archives are
  marked `binary` explicitly so `text=auto` can never guess wrong on one;
  verified they still report `attr/-text` afterward.
- **Same root cause as the exec-bit problem** already documented for
  `restore_exec_bits.py`: this repo is authored on Windows and consumed by
  Linux/macOS harnesses, and git's platform-adaptive defaults are wrong for
  that split in both directions. This closes the line-ending half; the
  exec-bit half stays as it is.
- **Known limits, stated rather than glossed:** adding the file doesn't
  retroactively fix a checkout that already has CRLF files (needs one
  `git add --renormalize .`), and it cannot reach an already-synced copy
  under `~/.claude/skills/` — that one needs a re-sync or a re-run of
  `install_skills.py` before it becomes runnable. Documented in README
  alongside the exec-bit note rather than left as tribal knowledge.
- **Out of repo-config's scope, deliberately:** the skill's own Limitations
  say it doesn't touch `.gitignore` or repo-level git config, so this is a
  fix to this repo rather than something `repo-config` generated. Whether
  `.gitattributes` should join its template set is a separate question —
  it would help every Windows-authored target repo, but it widens a scope
  that was drawn narrow on purpose.

## docs-loop v1.1.0 — cut check_references.py's false positives 26 → 6
**2026-08-15**

- **Added:** component-relative path resolution. Candidates resolve against
  the doc's directory, its nearest enclosing component (a directory with a
  `SKILL.md` or a language manifest), then the repo root. This repo is a
  tree of independently-packaged skills, so shorthand like `scripts/run.sh`
  inside a skill's `references/` was being reported broken on every single
  skill. It now resolves the way a reader reads it. 23 → 18 inline-path
  rows.
- **Fixed:** the checker was parsing markdown link syntax quoted inside
  backticks as a real link, so a release note *documenting* a broken link
  re-reported that link forever. Found because this repo's own release notes
  did exactly that — the entry describing the `#operators-in-expressions`
  fix was itself reported as a broken anchor, twice. Code spans are now
  masked before link extraction; path candidates still come from the code
  spans. 3 broken anchors → 0.
- **Added:** `historical-*` verdicts for non-resolving paths in
  `CHANGELOG`/`RELEASE_NOTES` files. A path in a past entry that no longer
  exists is usually the log doing its job, and docs-loop's own Rules already
  say never to rewrite a past entry — so reporting those as `broken` was
  sending an auditor at rows they're forbidden to act on. 55 rows moved off
  the action list without disappearing from the report.
- **Verified no real finding was lost:** the two genuine findings from the
  v1.0.0 run were already fixed in the previous change, and the remaining 6
  `broken` rows were each read individually. All 6 are the structural class
  the skill's Limitations already names — a doc describing a *different*
  component or repo — or build-state-dependent (`README.md`'s `zip/`
  example, which resolves or not depending on whether zips were built).
- **Not chased:** the ~150 `unresolved` rows. That verdict exists precisely
  to hold "might be a runtime file, an example, or prose with a slash in
  it," and driving it to zero would mean tightening heuristics until real
  findings vanish with the noise.

## Work docs-loop's first two findings (#16, #17)
**2026-08-15** · [#16](https://github.com/baileyrd/skill_pack/issues/16) · [#17](https://github.com/baileyrd/skill_pack/issues/17)

- **Fixed:** `my_loops/dedupe-loop` (v1.1.1) —
  `references/platform-directory.md` told the reader
  `scripts/scan_platform_repos.sh` would clone a repo that wasn't checked
  out. That script exists in four sibling skills and not in this one. What
  the reading turned up is bigger than the wrong filename: dedupe-loop has
  no clone path at all, and `index_capabilities.sh` takes a local directory,
  so an un-checked-out `PLATFORM_REPOS` entry silently can't be indexed. The
  section now documents the actual workflow (`gh repo clone ... --depth 1`,
  namespace caveat intact), step 1 states the local-path requirement instead
  of leaving it to a usage error, and Limitations records the absent clone
  path as a deliberate choice — porting the sibling's script would add a
  `gh` dependency this skill otherwise doesn't need.
- **Fixed:** `web_dev/datastar-pro` (v1.0.1) — `references/core.md`'s TOC
  entry `[Operators in Expressions](#operators-in-expressions)` pointed at
  nothing; the heading is `### Operators` (slug `#operators`), and the entry
  was listed after `Action Calls` when its section precedes it. Fixed the
  TOC rather than the heading: the heading is the content, the TOC is a
  pointer at it.
- **Not fixed, deliberately:** the other 16 `broken` rows from the same
  checker run. They're the documented cross-repo false-positive class —
  docs here describing *other* repos, skill-relative shorthand, and
  `CHANGELOG.md`'s pointer to a file it correctly records as removed. Two
  real findings out of 18 candidates is the ratio the skill's own
  Limitations predicts, and acting on the other 16 would have meant
  vandalising accurate docs.
- **Follow-up worth doing, not done here:** `check_references.py` resolves
  a candidate path against the doc's own directory and the repo root only.
  Most of this repo's shorthand (`scripts/audit.sh` inside a
  `references/` subdirectory) would resolve if it also tried the nearest
  ancestor containing a `SKILL.md`. That would cut the false-positive class
  substantially — a change to the tool, kept out of a change that was
  supposed to be about the two findings.

## Add my_loops/docs-loop — documentation review/update loop
**2026-08-15** · branch `claude/docs-review-loop-skill-ih5zhr`

- **Added:** `my_loops/docs-loop` (v1.0.0) — reviews a target repo's
  documentation against the current state of its code and updates it. Order
  is the whole point: ground truth from manifests/entry points/`--help`/CI/
  the real tree *first*, prose second, because reading the docs first turns
  an audit into a proofread. Findings are classified six ways (`stale` /
  `missing` / `orphaned` / `aspirational` / `unverifiable` / `accurate`) in a
  `docs-audit.md` checkpoint before any edit; `accurate` and `unverifiable`
  rows persist across runs so a re-audit doesn't re-litigate settled claims.
- **Added:** `scripts/inventory_docs.sh` (per-doc drift ranking: last
  changed, plus commits to non-doc files since) and
  `scripts/check_references.py` (relative links, GitHub heading anchors,
  backticked repo paths, shell-block paths — stdlib only). The checker
  separates `broken` (path anchored in a directory that really exists, so
  the claim is about this tree and is false) from `unresolved` (could be a
  runtime file, an example, or prose with a slash in it) — conflating them
  buried 11 real findings under ~300 rows of noise in the first pass here.
- **Found while testing, not fixed here:** the checker reports 18 `broken`
  rows against `skill_pack`. Reading each one — which is exactly the step
  the skill insists on, since the script surfaces candidates and never
  renders a verdict — **two** are real drift:
  `my_loops/dedupe-loop/references/platform-directory.md:60` names
  `scripts/scan_platform_repos.sh`, which its three sibling copies do have
  and dedupe-loop does not (its scripts are `index_capabilities.sh` /
  `find_clusters.py`); and
  `web_dev/datastar-pro/references/core.md:11`'s TOC links
  `#operators-in-expressions` against a heading that slugs to `operators`.
  Both left for a real docs-loop run to take through its own checkpoint
  rather than hand-patched inside the change that added the tool.
- **The other 16 are the documented false-positive class**, and the ratio is
  the point: most docs here describe *other* repos or use skill-relative
  shorthand (`scripts/audit.sh` meaning repo-config's), and `CHANGELOG.md`'s
  pointer to the removed `need_to_productize/datastar-pro.skill` is correct
  history, which this skill's own rules say never to "fix." Documented in
  the skill's Limitations and the script's docstring rather than filtered
  out by a heuristic that would have hidden the two real findings with them.
  One row is also build-state-dependent (`README.md`'s
  `zip/dedupe-loop-v1.0.0.zip` resolves or not depending on whether
  gitignored `zip/` output is present) — run against a clean tree.

## PR #4 — Fix silent exec-bit loss in build_skill_zips.py
**2026-08-12** · [#4](https://github.com/baileyrd/skill_pack/pull/4)

- **Fixed:** `scripts/build_skill_zips.py` shipped scripts non-executable
  (`0o644`) in the built zip whenever a `scripts/*.sh`/`*.py` file was
  genuinely edited and its `+x` bit didn't survive `git add` — the only
  safety net, `restore_exec_bits.py`, restores `+x` by matching a file's
  *content* against a blob that was `100755` at `HEAD`, so it only
  catches unmodified moves/copies, not real edits. Reproduced against a
  scratch clone: edited `apply.sh`, staged it at `644`,
  `restore_exec_bits.py` correctly no-op'd (content genuinely changed),
  and the built zip shipped `apply.sh` at `0o644` with no warning.
- **Fixed by:** `git_file_mode()` now checks the file's shebang (`#!`)
  first — a signal independent of git's index or the OS-reported mode
  entirely — and only falls back to the git-index check for the rare
  executable with no shebang. Verified the fix against the same
  reproduction: same edit, same staged `644`, zip now ships `0o755`.
  Rebuilt all 8 skills' zips and confirmed every `.sh`/`.py` file across
  all of them lands at `0o755`.
- **Traced to:** the `rusty_dbs` sync-gap finding logged in
  `my_loops/repo-config/RELEASE_NOTES.md` ("Third occurrence of the same
  sync-gap pattern") — this fixes the exec-bit half of that finding at
  the source (the build script), not just the symptom. The `.github/`-
  missing half is unaffected by this change; `Path.rglob("*")` was
  checked directly and does traverse dot-prefixed directories correctly
  in this repo's Python, so that symptom still points at something
  upstream of the build (a stale/incomplete local clone at build time),
  not at `build_skill_zips.py`.

## PR #2 — Apply repo-config's standard governance file set to skill_pack itself
**2026-08-12** · [#2](https://github.com/baileyrd/skill_pack/pull/2)

- **Added:** `.github/PULL_REQUEST_TEMPLATE/` (feature, bug_fix, docs, chore),
  `.github/ISSUE_TEMPLATE/` (bug_report, feature_request, config.yml),
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`,
  `ARCHITECTURE.md`, and a `docs/adr/0001-template.md` seed — the standard
  set the repo's own `my_loops/repo-config` skill applies to other repos,
  run here against `skill_pack` for the first time.
- **Changed:** `README.md` gained Architecture/Contributing/Security/License
  sections linking to the new files; existing prose left untouched.
- `ARCHITECTURE.md`'s boundary table and non-goals were filled in for real
  rather than left as scaffold — this repo has no service/process boundary
  between skills (each is independently consumed by an external harness), so
  the generic ports-and-adapters default doesn't apply as written. Per
  `ATLAS-100`'s own trigger clause and `ATLAS-PHIL-0102` (Justified
  Complexity) in `baileyrd/Atlas_Engineering_Standards_Library`, the real
  boundary documented instead is the `SKILL.md` manifest contract between a
  skill directory and the harnesses that load it.
- **No CI workflow added:** neither `Cargo.toml` nor `pyproject.toml`/
  `setup.py` exists at repo root (the `.py` scripts under `scripts/` have no
  package manifest), so `apply.sh`'s stack-selected CI step had nothing to
  select — consistent with the skill's "no manifest, no workflow" rule
  rather than a gap.
- `SECURITY_CONTACT` resolved to the repo owner's email from the existing
  `git remote` (`baileyrd/skill_pack`), not a placeholder — this repo was
  non-greenfield going in (README and git history already existed).
- This root-level file is separate from the per-skill `RELEASE_NOTES.md`
  files each skill under `my_loops/`/`yt_research_for_cc/` already keeps
  (e.g. `my_loops/repo-config/RELEASE_NOTES.md`) — those track that skill's
  own authoring history; this one tracks changes to `skill_pack` as a repo.
