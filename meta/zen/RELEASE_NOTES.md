# Release Notes

Reverse chronological, one entry per meaningful change.

---

## v1.0.0 — Imported and fitted to repo conventions
**2026-11-10**

- **Imported** from an upload (no upstream repo or license named). Maintained
  here from now on.
- **Frontmatter:** `>-` description; the "not for" pointers no longer name
  `/aios-audit`, `/aios-health-check` and `/security-audit`, which are not in
  this pack, and now point at `context-audit` instead; `compatibility`;
  `metadata.version`.
- **Added** step 9, wrap-up retro (skipped on unattended scheduled scans).
- Scripts, references and `assets/review.html` unchanged. Reviewed: the scan
  is read-only (`du`, `claude mcp list`, `launchctl list`, `crontab -l`,
  `systemctl --user list-timers`, PowerShell `Get-ScheduledTask`);
  `zen_apply.py` only moves files into an archive, pauses jobs, toggles
  plugins, and logs every change for `undo`. The review page loads Google
  Fonts.
