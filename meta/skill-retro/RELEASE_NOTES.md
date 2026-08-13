# Release Notes

skill-retro lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/meta/skill-retro) —
this log tracks commits against `main`, same convention as
[parity-loop's RELEASE_NOTES.md](../../my_loops/parity-loop/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.0.0 — Initial release
**2026-08-13**

- **Added:** first cut of the skill. Introduces the `meta/` category —
  tooling about this repo's own skills, distinct from `my_loops/`
  (Rusty-Mill platform maintenance) and `yt_research_for_cc/` (YouTube
  pipeline).
- **Core mechanism:** an evidence-grounded, single-run retrospective on a
  target skill's own `SKILL.md`/`references/`/`scripts/` — reconstructs
  what actually happened against the skill's stated steps (skipped/
  reordered steps, questions that should have been pre-answered by the
  instructions, guesses made where the text ran out, stale references,
  broken scripts), classifies each as a category/severity finding with a
  concrete proposed edit, reports before writing anything, and only
  applies approved edits — followed by a version bump and
  `RELEASE_NOTES.md` entry on the target skill, through this repo's normal
  PR workflow. Never auto-applies, never fabricates a finding with no
  concrete incident behind it.
- Explicitly does not wire itself into anything automatically (no hook, no
  auto-invoke at the end of another skill's run) — that's flagged as a
  deliberate follow-up decision, not bundled into this initial cut.
- No `scripts/` — this skill is a reading/judgment/writing pass; it shells
  out to nothing beyond the `git`/`gh` any other change in this repo
  already needs for its PR.
