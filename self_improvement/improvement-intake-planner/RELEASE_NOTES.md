# Release Notes

Reverse chronological, one entry per meaningful change.

---

## v1.0.0 — Imported and fitted to repo conventions
**2026-11-10**

- **Imported** from an upload of the "AIOS self-improvement starter" (no
  upstream repo or license named), with `data-intake`. Maintained here from
  now on.
- **Frontmatter:** dropped `user-invocable` and `argument-hint`; `>-`
  description; `compatibility` (PyYAML); `metadata.version`.
- **Fixed:** `scan_mcp_sources.py` and `write_plan.py` were documented as
  commands but had no entry point, so running them did nothing. Each now has a
  small CLI (server names in, JSON out; `--candidates` JSON in, plan out).
  `write_plan` now keeps a refined `mcp_tool` and `pull` line from step 3
  instead of always writing the placeholder.
- **Removed** `scaffold_evidence.py --with-schedule`, which POSTed to a
  local "Command Centre" dashboard that is not part of this pack; schedule
  with cron, a desktop task or a cloud trigger.
- **Removed** references to `data-map`, `signal-capture` and
  `evidence-router`, which are not in this pack.
- **Added** step 6, wrap-up retro. Paths are relative to the skill folder.
