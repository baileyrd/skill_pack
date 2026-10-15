# Release Notes

visual lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/diagrams/visual) —
this log tracks commits against `main`: reverse chronological, one entry per
meaningful change, honest about what's still open.

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
