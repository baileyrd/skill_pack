# Release Notes

Reverse chronological, one entry per meaningful change.

---

## v1.0.0 — Imported and fitted to repo conventions
**2026-11-10**

- **Imported** from an upload (no upstream repo or license named). Maintained
  here from now on.
- **Frontmatter:** dropped `user-invocable` (not a spec key; blocks claude.ai
  upload); `>-` description that also says what it is not for (zen);
  `compatibility`; `metadata.version`.
- **Paths:** the script is invoked relative to the skill folder instead of a
  hard-coded `.claude/skills/...` install path.
- **Added** a wrap-up retro section.
- `scripts/check_context.py` unchanged.
