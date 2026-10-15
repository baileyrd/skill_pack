# Release Notes

visual lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/diagrams/visual) —
this log tracks commits against `main`: reverse chronological, one entry per
meaningful change, honest about what's still open.

---

## v1.0.1 — Fixes from the first eval pass
**2026-10-15**

Ran `meta/my-skill-creator`'s eval loop: 3 prompts (recap, plan, map) x with-skill
vs no-skill baseline, one run each, 5 assertions per prompt. Chrome was not
installed in the eval sandbox, so the self-check never ran and no page was
viewed in a browser; grading was structural (file contents, git state), not
visual.

- **Fixed:** `render --out DIR` crashed with `IsADirectoryError` (hit by all
  three with-skill runs); a directory now takes the generated filename.
- **Fixed:** `render` died with a traceback after writing the page when
  `xdg-open` was missing; the opener failure is now ignored. SKILL.md names
  `--no-open` and says a skipped Chrome check must be reported, not hidden.
- **Fixed:** `assets/template.html` linked Google Fonts, contradicting
  "no runtime CDN" and breaking offline pages; the system font stack the CSS
  already falls back to is used instead.
- **Fixed:** `slug: "x-recap"` produced `x-recap-recap.html`.
- **Changed:** `sections.md` is flagged as not needed in map mode;
  `sourcesBase` comment clarified.
- **Result:** with-skill pages were self-contained, git-grounded (hunks
  resolved, `missingHunks` empty) and clean on the repo; baselines were smaller
  hand-written pages with no hunk grounding or audit. Baselines had no
  drill-down map beyond a plain tree.
- **Harness note:** the first eval-1 run shared a working directory with eval 2
  and its `data.json` was overwritten (the page showed the plan); it was re-run
  isolated. Run concurrent renders from separate directories.
- **Open:** no visual verification (needs Chrome); `skillmap` skeleton was
  sparse for `dev_practices` (4 nodes, 0 edges, empty `when`), so map mode is
  mostly hand enrichment; description-trigger optimisation not run.

---

## v1.0.0 — Imported into skill_pack
**2026-10-15**

Imported from a standalone `/visual` skill (adapted from BuilderIO/skills and
tt-a1i/archify, both MIT — see `THIRD_PARTY_NOTICES.md`) and maintained here
from now on — this repo's own versioned copy, not a live sync.

- **Changed:** frontmatter to repo conventions — `>-` description in the third
  person naming the mechanism and sibling `fireworks-tech-graph`, top-level
  `version`, `compatibility`.
- **Added:** `RELEASE_NOTES.md`, a `## Contents` list in `references/schema.md`
  (past 100 lines), and a `Wrap-up retro` step.
- **Removed:** the skill-level `README.md` (its content duplicated `SKILL.md`;
  its install note described the origin pack's `install.sh`, not this repo's
  `scripts/install_skills.py`). Origin-pack names in `schema.md` examples and a
  comment in `visual.py` replaced with neutral ones.
- **Placed in `diagrams/`:** the deliverable is a picture-bearing page.
- **Open:** not yet evaluated with `my-skill-creator` evals.
