# This repo's skill-authoring conventions

Distilled from how every existing skill here (`my_loops/*`, `yt_research_for_cc/*`,
`meta/skill-retro`) is actually built, plus the root `README.md`/`ARCHITECTURE.md`.
Read this before drafting so a `learn-it` output looks native to the repo instead of
generic boilerplate.

## Contents

- [Frontmatter](#frontmatter)
- [Description quality](#description-quality)
- [File layout](#file-layout)
- [RELEASE_NOTES.md](#release_notesmd)
- [Category placement](#category-placement)
- [Anthropic's authoring guidance, as applied here](#anthropics-authoring-guidance-as-applied-here)
- [Standing rules nearly every skill here repeats](#standing-rules-nearly-every-skill-here-repeats)
- [Bookkeeping when landing a new or changed skill in this repo](#bookkeeping-when-landing-a-new-or-changed-skill-in-this-repo)

## Frontmatter

```yaml
---
name: <lowercase-hyphenated, matches the directory name>
description: <one paragraph, see "Description quality" below>
version: <semver, e.g. 1.0.0>
compatibility: <optional, ≤500 chars — only real environment requirements>
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
  It is a deliberate extra over the Agent Skills spec (which would put it
  under `metadata:`); `scripts/check_repo.py` and `build_skill_zips.py`
  both read it from the top level.
- `compatibility` names binaries, network access, or the intended product a
  skill genuinely needs (`yt-dlp`, `cargo`, "gh CLI or GitHub MCP tools").
  Leave it out when there is nothing to say — most skills don't need it.
- No other keys. `context`, `paths`, `disable-model-invocation` and the rest
  are Claude Code-only and make a claude.ai upload fail with "unexpected
  key"; this repo packages for both.

## Description quality

A strong description (every existing skill here follows this shape):
- Is written in the third person ("Runs…", "Audits…"), never "I can…" or
  "You can use this to…" — it is injected into the system prompt alongside
  every other skill's, and a point-of-view mismatch hurts selection.
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
- **Has a hard ceiling of 1024 characters** — claude.ai's limit, enforced by
  `scripts/check_repo.py`'s `manifests` check. This and the "is long" rule
  below genuinely pull against each other, and the ceiling wins; following
  "is long" as written naturally overshoots. Trim trigger-phrase examples
  before trimming the statement of what the skill does and how.
- **Is written as a `>-` block scalar**, not one long plain line, unless you
  are certain it contains no `": "`. A colon-space inside an unquoted plain
  scalar is invalid YAML, and a description quoting a trigger phrase hits it
  easily. `check_repo.py`'s hand-rolled parser tolerates it, so the repo's own
  checks stay green while every real consumer rejects the file — four skills
  shipped that way before anyone noticed.
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

Keep `SKILL.md` itself lean — under 500 lines, enforced by
`scripts/check_repo.py`'s `manifests` check — by pushing depth (long lists,
per-stack detail, format specs) into `references/*.md` and linking to them by
relative path from `SKILL.md`, each with a line on when to read it. Keep
references one level deep: every reference links from `SKILL.md` directly,
none chains to another. Any reference over 100 lines opens with a
`## Contents` list of its headings, so a partial read still shows the scope.

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

**Confirm this list against the repo before relying on it** — `ls -d */` at
the root, or the category tables in the root `README.md`. It has been stale
before, and a placement decision made against a stale list is wrong in a way
that is expensive to undo once the directory exists.

Six category folders exist (verify with `ls -d */`):
- `my_loops/` — autonomous, bounded backlog loops maintaining the
  Rusty-Mill/`baileyrd` Rust platform repos (assess → issue → implement →
  PR → merge → repeat).
- `yt_research_for_cc/` — video research: the YouTube search → curate →
  NotebookLM pipeline, plus `video-teardown` for working a single video into
  a verified deliverable.
- `meta/` — skills whose subject is skills themselves (`skill-retro`,
  `learn-it`, `my-skill-creator` on this repo's own; `find-skills` on the
  external ecosystem).
- `web_dev/` — skills for generating applications in a specific web framework
  (`datastar-pro`), reviewed and imported from their own standalone repos then
  maintained here.
- `dev_practices/` — software design and coding discipline
  (`unix-philosophy`, the three architecture audits). Defined by *subject*
  rather than by target: invoked against whatever the user is building.
- `diagrams/` — the picture is the deliverable (`fireworks-tech-graph`).
  Defined by *output*: `dev_practices/` reasons about software without
  emitting an artifact, this one emits the artifact.

One further top-level folder is **not** a category and holds no skill
directories — `trying/` contains exported `.skill` zip archives. Nothing in it
has a `SKILL.md`, so `build_skill_zips.py` and `install_skills.py` skip it
entirely: neither versioned, packaged, nor installed. A skill does not "live"
there in any working sense.

A skill that clearly fits one of the six goes there. A skill that fits none
is a real decision, not a default — flag it rather than forcing a fit or
silently creating a new category. If a new one genuinely is warranted,
`ARCHITECTURE.md`'s "Structure" section names the category folders explicitly
and needs a matching update, and the root `README.md` needs a new
"### `<folder>/` — ..." section with its own skill table, same shape as the
existing ones.

## Anthropic's authoring guidance, as applied here

Anthropic's skill-authoring best practices (platform.claude.com → Agent
Skills → best practices; the Agent Skills spec at agentskills.io) and this
repo's conventions above. Treat it as the review checklist for any draft:

**Structure**
- Body under 500 lines; detail in `references/`, one level deep, each file
  linked from `SKILL.md` with a line on when to read it.
- References over 100 lines open with a `## Contents` list.
- Forward slashes in every path. Descriptive file names
  (`capability-manifest-format.md`, not `doc2.md`); organize by domain.
- Scripts: say whether to *run* a script or *read* it as reference. Scripts
  handle their own error cases with specific messages rather than failing
  and leaving Claude to guess, and every constant carries its reason.

**Frontmatter**
- `description` in the third person, ≤1024 chars, what + when, with the
  trigger phrases a user would actually type.
- `compatibility` only for real environment requirements; never assume a
  binary is installed — name it, and give the install or fallback.
- MCP tools by fully qualified name (`github:issue_write`, not
  `issue_write`).

**Content**
- Only what Claude doesn't already know. Challenge each paragraph: does it
  justify its tokens?
- Match freedom to fragility: heuristics where several approaches are
  valid, a template where a pattern is preferred, an exact command where
  the operation is fragile and sequence matters. One default with an escape
  hatch, not a menu.
- Multi-step work gets a copyable checklist and a verification step that
  loops *back* on failure ("validate; if it fails, fix and validate again").
- Explain why instead of ALL-CAPS musts; one term per concept throughout;
  no time-sensitive wording (use a current-method / old-patterns split);
  concrete examples over abstract ones, input/output pairs for anything
  stylistic.

**Testing**
- Three realistic evaluations before extensive writing, baseline without
  the skill first (`my-skill-creator` runs this loop).
- Test on every model the skill will run under — Haiku needs more guidance
  than Opus tolerates — and watch how Claude actually navigates the files:
  a reference never read is unsignalled or unnecessary; one read every time
  belongs in the body.

Where this repo deliberately departs from the published guidance: `version`
sits at the top level rather than under `metadata:` (tooling reads it there),
skill names are noun phrases (`parity-loop`) rather than the suggested
gerunds (`closing-parity-gaps`) because they are already installed under
those names, and every authored skill ends with a `Wrap-up retro` step the
guidance doesn't call for.

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
