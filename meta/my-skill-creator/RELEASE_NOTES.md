# Release Notes

my-skill-creator lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/meta/my-skill-creator) —
this log tracks commits against `main`, same convention as
[skill-retro's RELEASE_NOTES.md](../skill-retro/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.3.0 — Don't depend on an executable bit the sync drops
**2026-08-17**

- **Added:** a rule in the repo-integration checklist documenting how to restore the executable bit —
  `chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true`, with naming the
  interpreter (`bash scripts/x.sh`) as the fallback where the skill directory
  is read-only.
- **Why ([#1](https://github.com/baileyrd/skill_pack/issues/1)):** the sync
  that delivers a skill to a session doesn't preserve mode bits. Measured in a
  live session: **31 of 31 shebanged scripts across all ten skills arrive as
  `0644`**, so any step written `scripts/x.sh` fails with `permission denied`.
  The issue had recorded this as an occasional symptom; it is universal.
- **Scope note:** this documents a recovery rather than fixing the sync, which
  lives outside this repo. #1 stays open.

- **Also:** the rule is stated for *skills this one drafts*, not just for
  itself — a newly drafted skill that ships scripts must name the interpreter
  or document the recovery, enforced by `tests/test_script_invocation.py`.

---

## v1.2.0 — Four findings from its own skill-retro
**2026-08-16**

All four were filed as issues from a `skill-retro` on the run that drafted
`dev_practices/unix-philosophy`, and are applied here together.

- **Fixed ([#52](https://github.com/baileyrd/skill_pack/issues/52)):**
  `aggregate_benchmark.py` hardcoded `runs_per_configuration: 3` and
  `executor_model: "<model-name>"`, rendering both verbatim into
  `benchmark.md`. A run with one run per configuration advertised "3 runs each
  per configuration" — a claim about statistical strength, and exactly the
  number a reader uses to weigh a pass-rate delta. The count is now derived
  from the data, and `--model` is optional with the `**Model**:` line omitted
  entirely when unset rather than printed as a placeholder.
  Worth recording: the obvious fix — `len(results[config])` — is also wrong.
  That list is flat across every eval, so a 6-eval run with one run apiece
  reports "6 runs each", swapping one false claim for another. The count is per
  (configuration, eval) pair, and reports a range like `1-2` when they differ.
- **Added ([#53](https://github.com/baileyrd/skill_pack/issues/53)):** a fourth
  shape in "Retro by default" for **multi-mode skills**, plus a preamble
  instruction to check the retro's cost against a *typical* invocation rather
  than the heaviest one. `unix-philosophy` fit none of the three existing
  shapes; shape 2 was applied unconditionally and two design-mode eval runs
  reported *skipping* the retro. A step a run reports skipping is worse than no
  step.
- **Added ([#54](https://github.com/baileyrd/skill_pack/issues/54)):** the
  1024-character `description` ceiling, framed as the budget it is — the
  "write it long and dense" guidance and this limit genuinely conflict, and the
  limit wins. Also says which half to cut first (trigger phrases before the
  statement of what the skill does). A second bullet now requires a `>-` block
  scalar unless the description certainly contains no `": "`, after four skills
  shipped descriptions that no real YAML parser would accept.
- **Fixed ([#55](https://github.com/baileyrd/skill_pack/issues/55)):** the
  headless-environment note is now capability-based ("any environment without a
  display") rather than a list of product names that will always lag reality,
  and "Test Cases" permits launching backgroundable runs in the same turn as
  presenting the prompts instead of blocking on a confirm while nothing
  executes.

---

## v1.1.1 — Allow `version` in the frontmatter allowlist
**2026-08-16**

- **Fixed ([#58](https://github.com/baileyrd/skill_pack/issues/58)):**
  `scripts/quick_validate.py`'s `ALLOWED_PROPERTIES` is vendored from upstream
  `skill-creator`, which has no `version` convention, so it rejected the key
  outright. Since `validate_skill()` is a hard gate in front of
  `package_skill.py`, and this repo *requires* `version` on every authored
  skill, the two validators contradicted each other: `check_repo.py` fails a
  skill without `version`, `quick_validate.py` failed the same skill with it.
  Net effect — `package_skill.py` could not package **any** skill in this repo,
  including the one it was pointed at (`yt_research_for_cc/video-teardown`).
- **Added:** `tests/test_quick_validate.py` — 4 tests. Beyond asserting that
  `version` validates, they pin the two ways a careless fix goes wrong: that
  adding the key doesn't make it *required* here (`check_repo.py` owns that),
  and that the allowlist still rejects a misspelled key, so replacing the check
  with a no-op wouldn't pass. Per ADR-0002, verified by reverting the fix and
  watching the two relevant tests go red.
- **Note for future re-syncs:** this is a deliberate local divergence from
  upstream and is easy to lose. The line carries a comment saying so, and the
  end-to-end test fails loudly if it's dropped.

### Found while fixing this, not fixed here

The end-to-end test was written as "every skill in this repo validates
cleanly" and failed — for a *different* reason. Four skills
(`dev_practices/unix-philosophy`, `meta/learn-it`, `meta/skill-retro`,
`my_loops/repo-config`) have descriptions containing an unquoted `": "`, which
is invalid YAML that `check_repo.py`'s hand-rolled parser tolerates and PyYAML
rejects. Filed as [#59](https://github.com/baileyrd/skill_pack/issues/59). The
test is scoped to allowlist rejections until that's fixed, with a comment
explaining why — narrowing it was preferable to shipping a red test, but the
narrowing is temporary and marked as such.

---

## v1.1.0 — Fix the two silent failures in the eval loop
**2026-08-16**

From a `skill-retro` pass on this skill, grounded in a real run of it
(drafting `dev_practices/unix-philosophy` through two eval iterations).
Both findings cost real time on that run and both failed *silently*, which
is what makes them worth fixing rather than documenting.

- **Fixed ([#50](https://github.com/baileyrd/skill_pack/issues/50)):** step 4.1
  restated the `grading.json` schema inline as `text`/`passed`/`evidence` —
  authoritative-sounding but incomplete. `scripts/aggregate_benchmark.py`
  reads `summary.pass_rate`, defaulting to `0.0`. On the run that found this,
  the benchmark reported **0.0% for both configurations** against actual
  scores of 22/23 and 21/23, with no warning. Step 4.1 now shows both halves
  of the schema and names which consumer reads which, and adds the diagnostic
  that matters: *if a benchmark comes back at 0.0%, check for `summary`
  before believing it.* The script now derives a summary from `expectations`
  when it's missing and says so, rather than scoring zero in silence.
- **Fixed ([#51](https://github.com/baileyrd/skill_pack/issues/51)):** the
  documented workspace layout omitted the `run-N/` level that
  `aggregate_benchmark.py` requires (`config_dir.glob("run-*")`), so
  following the instructions exactly produced a workspace the aggregator
  found zero runs in. The layout is now shown as a directory tree with
  `run-1/` marked as required-even-with-one-run and the reason it exists,
  and the paths in steps 1 and 3 match it. The script now warns when a
  config directory holds a `grading.json` or `outputs/` but no `run-*`
  child — the specific mistake the old layout invited.
- **Note on the pattern:** in both cases the complete, correct information
  already existed in `agents/grader.md`, `references/schemas.md`, or the
  script's own docstring. The defect was SKILL.md restating a partial
  version of it in the reader's path. Partial restatements of a schema
  documented elsewhere are worse than a pointer, because they look complete.

Still open from the same retro, filed but not fixed:
[#52](https://github.com/baileyrd/skill_pack/issues/52) (hardcoded model
name and run count in `benchmark.md`),
[#53](https://github.com/baileyrd/skill_pack/issues/53) (no "Retro by
default" shape for multi-mode skills),
[#54](https://github.com/baileyrd/skill_pack/issues/54) (description length
limit unstated), [#55](https://github.com/baileyrd/skill_pack/issues/55)
(eval workflow assumes an interactive local session).

---

## v1.0.1 — Declare the PyYAML dependency
**2026-08-15**

- **Fixed:** `scripts/quick_validate.py:8` does an unguarded top-level
  `import yaml` (PyYAML) to parse SKILL.md frontmatter, and nothing said so.
  Without it that script dies with `ModuleNotFoundError`; the rest of the
  skill is unaffected. New "Dependencies" section states it and the install
  fix.
- **Context, verified across all 17 tracked `.py` files:** `yaml` is the only
  third-party module *imported* anywhere in this repo. External binaries are
  a separate matter and several skills need one (`gh`, `git`, `jq`,
  optionally `ripgrep`, and `yt-dlp` for `yt_research_for_cc`) — a
  distinction an earlier draft of this entry blurred and the check caught.
- **This was `docs-loop` row 5's original finding**, and fixing it properly
  surfaced the same defect class in five `my_loops` skills.

## v1.0.0 — Initial release
**2026-08-13**

- **Added:** forked from Anthropic's `skill-creator` example skill
  (`/mnt/skills/examples/skill-creator`, Apache 2.0 — `LICENSE.txt` carried
  over unchanged) into this repo as `meta/my-skill-creator`, versioned and
  maintained here rather than used from outside it. The full upstream
  workflow (interview → draft → eval/benchmark loop with subagents →
  description optimization → packaging) is unchanged; two things were
  added on top:
  - **"This repo's own conventions"** — a new section in "Write the
    SKILL.md" that applies `skill_pack`'s own authoring rules (semver
    `version:` field, `RELEASE_NOTES.md`, category-folder placement, the
    `build_skill_zips.py` sanity check, the `core.fileMode=false`
    executable-bit gotcha) whenever the target skill is meant to live in
    this repo. Points at `meta/learn-it/references/skill-authoring-
    conventions.md` rather than duplicating it.
  - **"Retro by default"** — the actual behavioral change from upstream:
    every skill this tool drafts or substantively improves gets a
    wrap-up-retro step wired to `meta/skill-retro` added at draft time,
    not proposed as a separate follow-up change afterward. Phrasing
    guidance covers the three shapes already established across this
    repo's skills (numbered-step loop, single-shot utility, self-
    referential meta-skill), and explicitly excludes vendored/non-authored
    skills (the `notebooklm` precedent).
  - `my-skill-creator` also dogfoods its own rule: a new "Wrap-up retro"
    subsection after "Package and Present" runs `skill-retro` on
    `my-skill-creator` itself at the end of a run, following
    `skill-retro`'s own step 6 guard against double-firing on a direct
    self-invocation.
- Renamed self-references from `skill-creator` to `my-skill-creator` in
  the two spots upstream referred to itself by directory name (the
  benchmark-aggregation step, the eval-viewer launch command); everything
  else — `agents/`, `references/`, `scripts/`, `eval-viewer/`,
  `assets/eval_review.html` — carried over unmodified, since none of it
  hardcodes the skill's own directory name.
- Deliberately did **not** copy this behavior back into the generic
  upstream `skill-creator` (out of scope — that's Anthropic's file, not
  this repo's).
