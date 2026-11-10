# Release Notes

Reverse chronological, one entry per meaningful change.

---

## v1.0.0 — Imported and fitted to repo conventions
**2026-11-10**

- **Imported** from an upload of the "AIOS self-improvement starter" (no
  upstream repo or license named), with `improvement-intake-planner`.
  Maintained here from now on.
- **Frontmatter:** dropped `user-invocable` and `argument-hint`; `>-`
  description; `compatibility` (PyYAML); `metadata.version`.
- **Removed** references to `data-map` and `signal-capture`, which are not in
  this pack; upstream is now `improvement-intake-planner`, downstream is a
  human review of `raw-events/`.
- **Fixed** common mistake 3, which said `resolve_folder` raises on an unknown
  source; the code slugifies it into its own folder.
- **Added** a wrap-up retro scoped to `plan` and `scaffold` modes. Paths are
  relative to the skill folder.
