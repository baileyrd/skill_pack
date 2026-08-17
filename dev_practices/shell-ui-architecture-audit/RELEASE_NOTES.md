# Release Notes

shell-ui-architecture-audit lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/dev_practices/shell-ui-architecture-audit) —
this log tracks commits against `main`: reverse chronological, one entry per
meaningful change, honest about what's still open.

---

## v1.0.0 — Productized out of `need_to_productize/`
**2026-08-17**

Moved from `need_to_productize/shell-ui-architecture-audit.skill` (a staged zip
archive, neither versioned nor packaged nor installed) into `dev_practices/` as
a real skill directory.

Audits the **shell** of a UI — outer chrome, layout regions, navigation,
command surfaces, theming, persistence, extensibility — across desktop
(Tauri/Electron), web (React/Vue/Svelte/hypermedia), and terminal
(Textual/Rich/Ink/Ratatui/Bubble Tea) targets. Fifteen phase files opened one at
a time, five runtime-probe references selected by detected shell type, verdicts
scored Pass/Warn/Fail against cited evidence, output a backlog ranked by
CVSS-style severity.

The audit content is untouched: all 15 `phases/`, all 5 `references/`, and both
`assets/` files are exactly as staged.

### Changed on productization

- **Removed the `tags:` frontmatter key.** Not in this repo's allowed
  property set (`quick_validate.py` rejected the skill outright), and nothing
  here consumes it.
- **Deleted the bundled `install-claude-code.sh`.** It copied the skill into
  `~/.claude/skills/` on its own and documented itself as "run this from inside
  the unzipped directory" — an assumption that stops being true the moment the
  skill lives in a repo. This repo installs every skill through
  `scripts/install_skills.py`, which mirrors the whole tree in one pass; a
  second, skill-specific installer is a way for the two to disagree about what
  is installed.
- **Added `RELEASE_NOTES.md`** and kept the existing `version: 1.0.0`, which
  was already correct.
- **Added a `Limitations` section**, which the staged archive had none of. Two
  entries are load-bearing: **the runtime phases need a runnable target**, and
  degrade silently to static-only in a sandbox with no display — a partial
  audit reported as a clean one is the failure mode. And **fifteen phases is a
  long run**; the phase files are independent by design, so scoping to the four
  that answer the question beats abandoning a full pass halfway.

### Not changed

- No eval set, no benchmark. Verdict quality across the three shell families is
  unmeasured, and the runtime probes were not exercised here — this container
  has no display and no target application to audit.

**Category note:** lands in `dev_practices/` rather than opening a category for
audits. That folder's charter is already "design guidance applied while a
decision is live, and structured review of what already exists" — the second
half is exactly this, and `unix-philosophy` already carries an audit mode under
the same roof.
