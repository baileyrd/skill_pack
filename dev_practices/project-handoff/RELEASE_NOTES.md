# Release Notes

project-handoff lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/dev_practices/project-handoff) —
this log tracks commits against `main`.

---

## v1.0.0 — Initial release
**2026-11-02**

- **Added:** handoff mode, which turns a design chat into `docs/handoff/` (SPEC,
  DECISIONS, QA, OPEN_QUESTIONS), a CLAUDE.md rule to look before asking and
  write answers back, the design dialog and decisions captured to remind-me,
  delivery as a PR or as files, and a kickoff prompt of six lines or fewer.
- **Added:** resolve mode, which answers Claude Code's OPEN_QUESTIONS from the
  design record and writes the answers back without any copy-paste.
- **Added:** provenance tags (`[stated]`/`[agreed]`/`[default]`/`[open]`), so
  the implementer knows which choices it may revise.
- **Why:** prompt-only handoffs dropped rationale. Claude Code then asked
  questions the design chat had already settled, and Nano relayed them between
  surfaces by hand.
- **Tested:** two dry runs (handoff and resolve) on a synthetic design chat,
  saved in `evals/`. The runs turned up gaps that were fixed before release:
  how to tag the user picking one of Claude's options, asking nothing in step
  4 when nothing blocks, saving open items to remind-me as action_items so
  resolve mode works without the repo, keeping `[default]`s out of remind-me,
  not capturing the dialog twice, a RESOLVED addendum file when the repo is
  unreachable, and replacing the user's name with "the user" in the CLAUDE.md
  block.
