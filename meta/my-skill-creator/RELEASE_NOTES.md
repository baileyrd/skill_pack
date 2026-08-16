# Release Notes

my-skill-creator lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/meta/my-skill-creator) —
this log tracks commits against `main`, same convention as
[skill-retro's RELEASE_NOTES.md](../skill-retro/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

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
