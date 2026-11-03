# Release Notes

Reverse chronological, one entry per meaningful change.

---

## v1.0.0 — Imported and trimmed
**2026-11-03**

- **Imported** from an upload of
  [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
  (MIT; see `THIRD_PARTY_NOTICES.md`). Maintained here from now on.
- **Removed** ~2.7 MB the skill never reads at runtime or that duplicates what
  the model already knows: `validate_data.py` (upstream's data-maintenance
  tool), `__pycache__/`, `phosphor-icons-upstream.json`,
  `google-font-licenses.json`, `data-provenance.json`, `catalog-summary.json`,
  and the `google-fonts` domain with its 747 KB `google-fonts.csv` (a raw list
  of 1,934 families; font *pairing* guidance stays in `typography`). The only
  code change is dropping that domain's four entries from `scripts/core.py`.
- **Rewrote `SKILL.md`** at roughly half the size: `>-` description that names
  concrete trigger asks and what it is not for, `compatibility`,
  `metadata.version`, `python3` named at every call, workflow as six numbered
  steps, query advice in one list.
- **Added** `## Contents` to both references; a design-system-scoped wrap-up
  retro.
