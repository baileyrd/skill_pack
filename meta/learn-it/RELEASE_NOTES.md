# Release Notes

learn-it lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/meta/learn-it) —
this log tracks commits against `main`, same convention as
[skill-retro's RELEASE_NOTES.md](../skill-retro/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.2.0 — Four findings from the run that produced PR #44
**2026-08-16**

- **Fixed ([#45](https://github.com/baileyrd/skill_pack/issues/45)):**
  `references/skill-authoring-conventions.md` listed three category folders;
  there are five, plus two staging areas that are *not* categories and hold no
  skill directories at all. A placement decision made against a stale list is
  wrong in a way that's expensive to undo once the directory exists, so the
  section now leads with an instruction to confirm the list against the repo
  rather than trusting it, and is dated.
- **Added ([#46](https://github.com/baileyrd/skill_pack/issues/46)):** step 2
  now anticipates two candidate shapes that make "update in place" the wrong
  answer — a `.skill` **zip archive** (everything in the staging areas is one;
  `cat` gives you binary), and **vendored third-party code** carrying
  `LICENSE`/`homepage`/`repository`/`author` frontmatter. Editing the second
  forks someone else's work and forfeits upstream updates however good the
  match. A third outcome, **adjacent**, is now named alongside new/update: a
  skill that explicitly scopes itself against the existing one and says so in
  its own description. That is what `video-teardown` did against
  `trying/watch`, arrived at by noticing the vendored markers by chance while
  the skill's own text pointed toward merging.
- **Added ([#47](https://github.com/baileyrd/skill_pack/issues/47)):** a
  "locate the repo" note. `${CLAUDE_SKILL_DIR}` and `~/.claude/skills/` are
  the *installed* flat copy — no category folders, no `scripts/`, no git
  history — and they look enough like the repo to return plausible search hits
  while missing the layout every instruction depends on. Confirm the source
  checkout by `scripts/build_skill_zips.py` sitting alongside the category
  folders; ask if unsure, since guessing cost a full turn last time.
- **Fixed ([#48](https://github.com/baileyrd/skill_pack/issues/48)):** step 5
  named `build_skill_zips.py` as the pre-commit sanity check. **CI runs
  `check_repo.py`**, which enforces five checks; the zip build covers only
  packaging and reports success regardless. It packaged a skill whose
  description was over the 1024-character limit and said nothing about an
  unresolvable inline path. Step 5 now gates on `check_repo.py`, run *after*
  `git add` since `exec-bits` reads the index, with the zip build demoted to a
  secondary check. Also records that `restore_exec_bits.py` cannot fix a
  genuinely new script — it only repairs content matching an already-`100755`
  blob at `HEAD` — so `git update-index --chmod=+x` is the actual remedy.

---

## v1.1.2 — YAML-safe description
**2026-08-16**

- **Fixed ([#59](https://github.com/baileyrd/skill_pack/issues/59)):** the
  frontmatter `description` was an unquoted plain scalar containing `": "`,
  which is invalid YAML — a colon-space inside a plain scalar reads as the start
  of a nested mapping. It is now a `>-` block scalar. The *value* is byte-for-byte
  unchanged; this is a representation fix, verified by round-tripping the parsed
  string before and after.
- **Why it went unnoticed:** `scripts/check_repo.py` parses frontmatter with a
  hand-rolled line-based parser that tolerates the construct, so CI stayed green
  and packaging worked, while anything using a real YAML parser rejected the file
  outright. `quick_validate.py` was the instance that surfaced it. The repo was
  validating with a parser more permissive than its consumers'.

---

## v1.1.1 — Description under claude.ai's upload limit
**2026-08-16**

- **Fixed:** the `description` was 1209 characters, over the 1024-character
  limit claude.ai enforces on skill upload, so the zip was rejected outright.
  Trimmed to 1008 (16 characters of headroom) with every trigger phrase kept —
  the cuts are the "bias toward proposing" preamble, keeping the one-off-fix
  exclusion that actually gates triggering. Nothing about what the skill does
  changed.
- **Context:** five skills here shipped over the limit at once, and none of the
  local tooling noticed: `install_skills.py` copies frontmatter without reading
  it, `build_skill_zips.py` zips it the same way, and Claude Code itself loads
  an over-length description fine. Only claude.ai rejects it, at upload, one
  file at a time. `check_repo.py`'s `manifests` check now enforces the limit so
  this fails locally and in CI instead.

## v1.1.0 — Wire skill-retro into learn-it's own wrap-up (step 6)
**2026-08-13**

- **Added:** step 6, "Wrap-up retro" — regardless of how the run ended (a
  new skill written, an existing one updated, a draft declined, or step 0's
  qualify gate saying this didn't warrant a skill at all), runs a
  `meta/skill-retro` pass on `learn-it` itself, grounded in how that run's
  qualify gate, existing-skill search, draft, and report actually held up.
  Read-only, safe to run unattended; applying anything found is still its
  own separate, explicitly-approved follow-up.
- Noted explicitly that this also triggers `skill-retro`'s own step 6 (it
  self-checks on every run against another skill) — a second, distinct
  report about `skill-retro` itself, not to be conflated with `learn-it`'s
  own findings.
- Third instance of the wiring pattern first used on `my_loops/rust-
  migration` v1.1.0 and then on `skill-retro`'s own step 6 — a one-line
  addition to a target skill's wrap-up, not a `settings.json` hook.

## v1.0.0 — Initial release
**2026-08-13**

- **Added:** first cut of the skill, built as `skill-retro`'s companion in
  the `meta/` category — same evidence-grounded, report-before-write
  discipline, opposite direction: `skill-retro` reviews whether following
  an existing skill's instructions went cleanly; `learn-it` reviews whether
  this session's own work contains a pattern worth turning into a new (or
  updated) skill.
- **Core mechanism:** reconstructs preferred patterns / anti-patterns /
  gotchas / sequencing actually demonstrated in-session (nothing invented
  without a real incident behind it), qualifies whether that's genuinely
  reusable behavioral guidance versus a one-off fact/fix before drafting
  anything, checks this repo's existing skills for something to merge into
  instead of duplicating, drafts against
  `references/skill-authoring-conventions.md` (this repo's real frontmatter/
  file-layout/versioning/description-quality rules, not a generic
  template), and reports the full draft for approval before writing or
  versioning anything.
- **Supersedes:** the draft approach in
  `need_to_productize/research-to-skill.skill` — kept the useful ideas
  (facts-vs-patterns, qualify-before-writing, description-is-the-trigger),
  dropped the hardcoded `/mnt/skills/user/` path assumption in favor of
  this repo's actual category folders and PR-gated write flow. The old
  draft file itself was left as-is in `need_to_productize/` — retiring or
  removing it is a separate decision, not made as part of adding this
  skill.
- `references/skill-authoring-conventions.md` doubles as living
  documentation of this repo's own authoring conventions, distilled from
  every skill that already exists here — written once so future
  `learn-it` drafts (and human authors) don't have to re-derive it from
  reading six SKILL.md files each time.
- No `scripts/` — same as `skill-retro`, this is a reading/judgment/writing
  pass with no automation beyond the standing `git`/`gh` PR flow.
