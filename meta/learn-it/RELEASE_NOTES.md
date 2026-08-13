# Release Notes

learn-it lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/meta/learn-it) —
this log tracks commits against `main`, same convention as
[skill-retro's RELEASE_NOTES.md](../skill-retro/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

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
