# Release Notes

my-skill-creator lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/meta/my-skill-creator) —
this log tracks commits against `main`, same convention as
[skill-retro's RELEASE_NOTES.md](../skill-retro/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

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
