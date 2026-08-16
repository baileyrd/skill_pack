---
name: learn-it
description: >-
  Runs a post-session distillation pass that turns what actually happened in this session into a
  new (or updated) Claude skill, using the same evidence-grounded, report-before-write discipline
  as skill-retro but pointed the opposite direction: it reconstructs the preferred patterns,
  anti-patterns, gotchas, and sequencing this session actually demonstrated, checks whether an
  existing skill in this repo already covers the ground (merge) or nothing does (create new),
  drafts a SKILL.md matching this repo's authoring conventions (frontmatter, versioning, category
  placement, RELEASE_NOTES), and reports the full draft for approval before writing anything. Use
  when a session's problem-solving revealed reusable guidance worth keeping past this
  conversation, when the user says "turn this into a skill", "save this as a skill", "capture what
  we just learned", "update the X skill with this", or references this by name (learn-it). Never
  write one for a one-off fact or fix specific to this task; qualify first.
version: 1.2.0
---

# learn-it

Turns "we figured out something worth remembering" into a structured pass:
reconstruct this session's actual patterns → qualify whether they're
skill-worthy → find or pick the target → draft against this repo's own
conventions → report the draft before writing anything → write and version
it → the normal PR workflow.

**Companion to `skill-retro`, opposite direction.** `skill-retro` reviews
whether *following* an existing skill's instructions went cleanly.
`learn-it` reviews whether *this session's own work* — with or without any
particular skill involved — contains a pattern worth turning into
instructions for next time. If a single session surfaces both (friction
with a skill B's steps, *and* new domain knowledge learned while using B),
that's two separate outputs — a `skill-retro` pass on B and a `learn-it`
pass proposing where the new domain knowledge goes — not one blended
report. Don't run both and merge their findings into a single artifact.

This skill absorbs and supersedes the draft approach in
`need_to_productize/research-to-skill.skill`: same core distinction (facts
vs. patterns, qualify before writing, description is the trigger
mechanism), rebuilt against this repo's actual conventions — real category
folders, semver `version:` + `RELEASE_NOTES.md`, a PR-gated write instead of
a bare filesystem write to a hardcoded path.

## Run (when invoked)

**0. Ground the evidence and qualify it before drafting anything**
- Evidence source — by default, this session's own conversation. Same rule
  as `skill-retro`: no backfilling from assumption about work this skill
  wasn't shown. If the user supplies a separate transcript or notes, that's
  fine — just say what the draft is actually grounded in.
- **Qualify** (this is the gate that keeps `learn-it` from generating
  low-value skills): is what happened *reusable behavioral guidance* —
  something that changes how Claude should act next time it's in a similar
  situation — or a *fact* / one-off fix specific to this task? A skill
  needs real depth: several distinct, concrete patterns/gotchas, not one
  trivial fact ("this API returns JSON") or a single bug fix with no
  generalizable shape. If it doesn't qualify, say so plainly and suggest
  the alternative (a note in the project's own docs, not a skill) rather
  than drafting something thin just because it was asked for.
- Determine the shape of this run: **new skill** (no existing skill covers
  this ground) or **update** (an existing skill in this repo is the right
  home for what was learned). Step 2 checks this for real rather than
  assuming from the qualify pass alone.

**1. Reconstruct this session's actual patterns** — work back through what
happened and extract, grounded in real incidents only (nothing invented
because it "seems like the kind of thing that should be true"):
- **Preferred patterns** — approaches that were tried and worked, worth
  defaulting to next time. State *why* each is preferred, not just that it
  is — a rule with no reason behind it is weak guidance.
- **Anti-patterns** — approaches tried and specifically rejected or
  corrected. Often the most valuable category: these come from a real
  wrong turn in this session, not from documentation.
- **Gotchas / non-obvious behavior** — things that actually tripped up the
  session (a surprising default, a version-specific quirk, an edge case
  documentation undersold) — not hypothetical gotchas.
- **Sequence / workflow** — if order genuinely mattered this session
  (setup steps, an initialization order, a dependency between actions),
  document it explicitly rather than leaving it implicit.
- **Concrete examples** — a real snippet, command, or config from this
  session, not an invented illustration.

**2. Find or pick the target** — check this repo's existing skills first
(every category folder, plus the staging areas `need_to_productize/` and
`trying/`) for something this should extend instead of duplicate.
`references/skill-authoring-conventions.md` lists the categories, with an
instruction to confirm the list against the repo rather than trusting it.

**Locate the repo before searching.** `${CLAUDE_SKILL_DIR}` and
`~/.claude/skills/` are the **installed** copy: a flat directory of skills by
name, with no category folders, no `scripts/`, no root `README.md`, and no git
history. It looks enough like the repo to fool a search — you get plausible
hits while silently missing the layout every instruction here depends on. Work
from the source checkout instead, and confirm you're in it by the presence of
`scripts/build_skill_zips.py` *alongside* the category folders. If you can't
determine where it is, ask; it is one question, and guessing costs a turn.

- **Match found** → usually an update. Two cases first, because both make
  "update in place" the wrong answer:
  - **The candidate is a `.skill` zip archive** (everything in
    `need_to_productize/` and `trying/` is). `cat` gives you binary; extract it
    to a temp dir before you can read its `SKILL.md` at all.
  - **The candidate is vendored third-party code** — it carries `LICENSE`,
    `homepage`, `repository` or `author` frontmatter, or the root `README.md`
    lists it as vendored (`notebooklm` is called out there explicitly). Editing
    it forks someone else's work and forfeits upstream updates, however good
    the match is.

  In either vendored case, take the third outcome this step used to lack:
  **adjacent** — build a new skill that explicitly scopes itself against the
  existing one, states the relationship in its own `description`, and records
  the rationale in its `RELEASE_NOTES.md`. That is what `video-teardown` did
  against the vendored `trying/watch.skill`.

  Otherwise: read the existing `SKILL.md` (and its `references/`) in full
  first. Identify what's genuinely new, what contradicts existing guidance
  (flag this explicitly to the user — old guidance may have been intentional;
  don't silently overwrite it), and what's already covered and shouldn't be
  repeated. Merge into the existing structure rather than appending a
  changelog-shaped tail.
- **No match** → this is a new skill. Pick a name (lowercase-hyphenated,
  specific enough to be unambiguous — `fastapi-async-patterns`, not
  `python`) and a category: an existing one it genuinely fits, or flag
  "this doesn't fit an existing category" as its own small decision to
  confirm before creating one (a new category folder means updating
  `ARCHITECTURE.md`'s Structure section too — see
  `references/skill-authoring-conventions.md`).

**3. Draft against this repo's real conventions** — read
`references/skill-authoring-conventions.md` first; it captures the
frontmatter shape, file-layout rules (`references/`/`scripts/`/
`assets/templates/`), versioning, and — most load-bearing — the
description-quality bar every skill in this repo is held to, since the
`description` field is the *only* mechanism that decides whether a skill
ever triggers again. Start from `assets/templates/skill-draft.md`. Keep
`SKILL.md` itself lean (this repo's existing skills stay well under 500
lines by pushing detail into `references/`) — a long list of gotchas or a
per-stack playbook belongs in its own reference file, not inline.

**4. Report the full draft before writing anything** — the complete
`SKILL.md` text, the proposed path, and (if this is an update) a
diff-style summary of what's added/changed and *why the description
changed*, since that's easy to forget and is exactly what breaks future
triggering. This is the checkpoint, same discipline as `skill-retro` step 4
and every other read-before-write pattern in this repo — nothing gets
written on this step.

**5. On approval, write it**
- Create/update the files. New skill → `version: 1.0.0` and a first
  `RELEASE_NOTES.md` entry. Update → bump semver by hand (patch for
  wording, minor for new guidance, major only if the user says this
  changes the skill's actual contract) and append a dated
  `RELEASE_NOTES.md` entry naming what changed and why, tracing back to
  this session.
- Bookkeeping: add the new/changed skill's row to the root `README.md`'s
  category table (or its Categories section blurb, for a new category),
  and a root `CHANGELOG.md` `Unreleased/Added` (or `Changed`) line.
- **Gate on `python3 scripts/check_repo.py`** — that is what CI runs, and it
  enforces five checks (`exec-bits`, `line-ends`, `doc-refs`, `manifests`,
  `packaging`). Run it **after `git add`**: `exec-bits` reads the git index, so
  a file that isn't staged is invisible to it.
  `python3 scripts/build_skill_zips.py` is a secondary packaging check, not the
  gate. It covers only the packaging concern and reports `Built N skill zip(s)`
  regardless — it happily packaged a skill whose description was over
  `manifests`' 1024-character limit, and said nothing about an unresolvable
  inline path that `doc-refs` caught. Naming it as *the* pre-commit check gives
  false confidence: the named command passes while the actual gate fails.
- If any scripts were added, verify their exec bits landed as `100755` after
  `git add` — this repo runs `core.fileMode=false`, so a brand-new script needs
  an explicit check (`git ls-files -s`), not an assumption that `chmod +x`
  alone survives staging. Note `scripts/restore_exec_bits.py` does **not** help
  here: it only repairs files whose content matches an already-`100755` blob at
  `HEAD`, which a genuinely new file never does. Use
  `git update-index --chmod=+x`.
- Caveat on `doc-refs` output from a Windows checkout: fixed in `docs-loop`
  v1.3.2, but if you are on an older copy, its findings there were unreliable
  (see #49) — trust CI over a local run.
- No shortcut around the standing workflow: branch, PR, green CI if
  configured, merge with a **merge commit** — same as
  `CONTRIBUTING.md` requires for any other change here.

**6. Wrap-up retro** — regardless of how this run ended (a new skill
written, an existing one updated, a draft declined, or step 0's qualify
gate saying this didn't warrant a skill at all), run a `meta/skill-retro`
pass on `learn-it` itself, evidence-grounded in the run that just
happened: did step 0's qualify gate hold up, did step 2's existing-skill
search actually find what it should have, did the draft in step 3 need
something `references/skill-authoring-conventions.md` didn't cover, did
step 4's report format serve the approval decision well? Read-only, safe
to run unattended — `skill-retro` never edits `learn-it`'s own files
without separate, explicit approval of its findings (see `skill-retro`'s
own Rules), same as any other target it's pointed at. Note that this also
triggers `skill-retro`'s own step 6 (it self-checks at the end of every run
on another skill) — that produces a second, separate report about
`skill-retro` itself, not to be conflated with the findings about
`learn-it` this step exists to surface. Report `learn-it`'s findings
alongside whatever this run's primary outcome was; applying any of them is
its own follow-up change through the normal PR workflow, not part of this
run.

## Rules

- Never write a skill file — new or updated — without explicit approval of
  the reported draft first.
- Never include a pattern, anti-pattern, or gotcha with no real incident
  behind it from this session's actual evidence.
- Qualify before drafting: a single fact or one-off fix doesn't get a
  skill. Say so and suggest the non-skill alternative instead of drafting
  something thin because it was asked for.
- Check for an existing skill covering the same ground before proposing a
  new one — merge, don't duplicate.
- The description is the single most important part of the draft — it's
  the only trigger mechanism. Name the domain explicitly, list realistic
  trigger phrasings (including casual ones a user might actually say), and
  err toward encouraging triggering when in doubt rather than a narrow
  exact-match description.
- If updating a skill and the new material contradicts existing guidance,
  surface the conflict explicitly (what it said, what changed, why) rather
  than silently overwriting it.
- Keep `SKILL.md` lean; push depth into `references/`.

## Limitations

- Single-session evidence, same caveat as `skill-retro` — a pattern
  observed once this session is a candidate, not a confirmed general rule.
  A thin, single-incident pattern is worth naming as such in the draft
  rather than presented with the same confidence as something corroborated
  by multiple incidents in the same session.
- No access to a separate transcript or log by default — only what's in
  this conversation's context, or whatever the user explicitly supplies.
- The "match found" check in step 2 is a read-and-judge pass over this
  repo's own skill directories, not an exhaustive semantic search — a
  near-duplicate under an unexpected name can still be missed. Worth a
  second look before assuming "no match" on a domain with any ambiguity.
- Doesn't wire itself into anything automatically — same note as
  `skill-retro`: getting it invoked reliably at the end of a session (vs.
  by explicit request) is a separate decision, e.g. a `Stop`-event hook in
  `settings.json`, not something this skill sets up on its own.

## Scripts

None. Same as `skill-retro` — this is a reading/judgment/writing pass;
`git`/`gh` for the eventual PR are the only tools it shells out to.
