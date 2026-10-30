# Retro by default

Read this when drafting or substantively improving any skill authored in
skill_pack: it says which shape of wrap-up-retro step to add and when not to
add one.

Every skill this tool drafts from scratch, or substantively improves (a
real behavioral/content change, not a typo fix), gets a **wrap-up-retro
step wired to `meta/skill-retro`** added at the same time — this is the
one behavioral difference from upstream `skill-creator`. It follows the
convention already applied across every authored skill in `skill_pack`
(`my_loops/rust-migration` and its five siblings, `yt-search`,
`yt-pipeline`, `meta/skill-retro`'s own step 6, `meta/learn-it`'s own step
6). Build it into the first draft the same way `name`/`description`/
`version` are part of every draft — not an afterthought to suggest once
the skill is otherwise "done."

Before picking a shape, check the retro's cost against a **typical**
invocation of the skill, not just its heaviest one. Every existing skill
carrying a wrap-up retro is a long-running loop, where a retrospective is
small next to the work it reflects on. Shape-matching without that check is
how you end up with a final step that runs routinely fail to execute — and a
step a run reports skipping is worse than no step, because it teaches the
reader that this skill's instructions are advisory.

How to phrase it depends on the skill's own shape — match what's already
established here, don't invent a new pattern:
- **A skill with numbered `Run`/`Procedure` steps** (the `my_loops` shape):
  add a final numbered step, "Wrap-up retro," right after whatever step
  reports back to the user — see `my_loops/rust-migration/SKILL.md` step 4
  or `yt_research_for_cc/yt-pipeline/SKILL.md` step 8 for the phrasing
  pattern. Ground it in *that skill's own* specific steps, not generic
  boilerplate — name what this particular skill's retro should actually
  check (which step's judgment call, which classification, which script).
- **A single-shot utility with no numbered steps** (the `yt-search` shape):
  add a short closing section, "## Wrap-up retro," after whatever the
  skill's last section already is.
- **A skill that is itself explicitly self-referential or meta** (like this
  one, or `skill-retro`): follow `skill-retro`'s own step 6 pattern —
  grounded in how *this run* of the tool went, guarded against firing
  twice on a direct self-invocation.
- **A skill with multiple modes of differing weight** — a quick consultation
  versus a full report-producing pass: scope the retro to the mode that
  produces a substantial artifact, and say so in the section heading and its
  first line, e.g. `## Wrap-up retro — audit mode only`. State plainly why the
  lighter mode is excluded, and offer the retro there as an explicit user
  request rather than an automatic step.
  This bullet exists because `dev_practices/unix-philosophy` was drafted
  against the three shapes above, none of which fit: it has a design mode that
  may be three paragraphs answering one question and an audit mode that emits a
  full report. Shape 2 was applied unconditionally, and **two independent
  design-mode eval runs reported *skipping* the retro** — correctly, since a
  retrospective on the skill's own instructions is disproportionate appended to
  a short chat answer, and it fires in contexts that can't support it (a
  read-only sandbox, no subagents). Fixed downstream in that skill's v1.1.0.

Always state explicitly that running/reporting the retro is automatic and
safe to run unattended, but *applying* anything `skill-retro` finds is a
separate, explicitly-approved follow-up — never bundle an applied fix into
the run that triggered the retro. And never add this step to a skill
that's vendored from elsewhere and not meant to be hand-edited (the
`notebooklm` exception, documented in `yt_research_for_cc/README.md`) —
check whether the target skill is actually authored in this repo before
adding anything to it.
