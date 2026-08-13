# This repo's skill-authoring conventions

Distilled from how every existing skill here (`my_loops/*`, `yt_research_for_cc/*`,
`meta/skill-retro`) is actually built, plus the root `README.md`/`ARCHITECTURE.md`.
Read this before drafting so a `learn-it` output looks native to the repo instead of
generic boilerplate.

## Frontmatter

```yaml
---
name: <lowercase-hyphenated, matches the directory name>
description: <one paragraph, see "Description quality" below>
version: <semver, e.g. 1.0.0>
---
```

- `name` must match the skill's own directory name.
- `description` is the *only* thing that decides future triggering — no
  other field or file content affects it. Treat drafting it as the most
  important step, not a formality.
- `version` starts at `1.0.0` for a new skill and is bumped by hand on
  meaningful changes — patch for wording/doc-only fixes, minor for new
  guidance/steps, major only for an actual contract change (what callers
  can rely on shifts). Every skill here carries this field; don't omit it.

## Description quality

A strong description (every existing skill here follows this shape):
- Names the domain/tool/task explicitly, not a vague category.
- States *what the skill does* and *the mechanism it uses to do it*, not
  just a label — e.g. not "helps with Rust migrations" but "inventories
  the source repo's capability surface into a manifest where every item
  defaults REQUIRED..." A reader should understand the skill's actual
  approach from the description alone.
- Lists realistic trigger phrasings, including casual ones a user might
  actually type, not just the formal name.
- Names companion/sibling skills and how this one relates to them, when
  relevant (e.g. "Companion to parity-loop... same PR/CI/merge mechanics").
- Errs toward encouraging triggering when in doubt over a narrow exact-match
  phrasing — a skill that only fires on its own name is nearly useless.
- Is long. Every skill in this repo has a multi-sentence, information-dense
  description — this is deliberate, not something to trim for brevity.

## File layout

```
<category>/<skill-name>/
  SKILL.md              # required — the skill itself
  RELEASE_NOTES.md       # required — this skill's own authoring history
  references/            # optional — detail too long for SKILL.md's body:
                          #   format specs, external-repo pointers, per-stack
                          #   playbooks, standards references
  scripts/                # optional — only if the skill genuinely automates
                          #   something beyond reading/writing/judgment.
                          #   Shell out to gh/git only, no extra runtime
                          #   deps, resolve paths relative to their own
                          #   location (works whether installed or checked
                          #   out locally). chmod +x before `git add` — see
                          #   "Executable bits" below.
  assets/templates/      # optional — payload copied INTO a target repo
                          #   (an issue-body template, a governance-file
                          #   template) — distinct from this skill's own
                          #   files, which describe the skill itself.
```

Not every skill needs `references/`/`scripts/`/`assets/` — `skill-retro` and
`learn-it` themselves have neither `scripts/` nor `assets/` beyond this
reference file, because they're judgment/writing passes, not automation.
Add a directory only when there's real content for it.

Keep `SKILL.md` itself lean — every skill here stays well under ~500 lines
by pushing depth (long lists, per-stack detail, format specs) into
`references/*.md` and linking to them by relative path from `SKILL.md`.

## RELEASE_NOTES.md

Reverse-chronological, one entry per meaningful change, modeled on
`repo-config`'s original log:

```markdown
# Release Notes

<skill-name> lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/<category>/<skill-name>) —
this log tracks commits against `main`.

---

## v1.0.0 — Initial release
**YYYY-MM-DD**

- **Added:** ...
```

## Category placement

Three category folders exist today:
- `my_loops/` — autonomous, bounded backlog loops maintaining the
  Rusty-Mill/`baileyrd` Rust platform repos (assess → issue → implement →
  PR → merge → repeat).
- `yt_research_for_cc/` — the YouTube research pipeline (search → curate →
  NotebookLM → deliverable).
- `meta/` — tooling about this repo's own skills (`skill-retro`,
  `learn-it`) — retrospection and distillation, not external repo
  maintenance.

A skill that clearly fits one of these goes there. A skill that doesn't fit
any of them is a real decision, not a default — flag it rather than forcing
a fit or silently creating a fourth category. If a new category genuinely
is warranted, `ARCHITECTURE.md`'s "Structure" section names the category
folders explicitly and needs a matching update, and the root `README.md`
needs a new "### `<folder>/` — ..." section with its own skill table (same
shape as the existing two/three sections).

## Standing rules nearly every skill here repeats

Don't reinvent these per skill — cite them:
- Every change lands through a PR against the default branch, never a
  direct push (`CONTRIBUTING.md`).
- Merge with a **merge commit** on green CI — never squash/rebase-merge;
  full history preserved deliberately.
- A read-only assessment/report step before any write — every loop skill's
  step 1 (`gap-analysis.md`, `duplication-audit.md`, a `skill-retro`/
  `learn-it` findings report) is a checkpoint the user sees before
  anything gets filed or edited.
- Breaking changes / new dependencies are a stop-and-ask, never an
  auto-apply, in every loop skill that touches code.
- If the target has `RELEASE_NOTES.md`, keep it current — one entry per
  meaningful change.

## Bookkeeping when landing a new or changed skill in this repo

- Root `README.md` — add/update the row in the relevant category table.
- Root `CHANGELOG.md` — an `Unreleased` entry (`Added` for a new skill,
  `Changed` for a meaningful update to an existing one).
- `python3 scripts/build_skill_zips.py` — sanity-check it packages cleanly
  alongside every other skill before committing.
- **Executable bits**: this repo runs `core.fileMode=false` (worked on from
  Windows), so `git add` never derives a script's `+x` bit from the OS — a
  brand-new script file needs `chmod +x` *before* `git add` (or an explicit
  `git update-index --chmod=+x` after), then verify with
  `git ls-files -s <path>` shows `100755`. `scripts/restore_exec_bits.py`
  only fixes files whose *content* matches an already-`100755` blob at
  `HEAD` (a moved/copied unchanged file) — it does not help a genuinely new
  script.
