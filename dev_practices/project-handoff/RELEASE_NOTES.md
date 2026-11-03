# Release Notes

project-handoff lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/dev_practices/project-handoff) —
this log tracks commits against `main`.

---

## v1.2.0 — In-repo project expert
**2026-11-03**

- **Added:** a `project-expert` subagent template
  (`.claude/agents/project-expert.md`). It answers design questions from
  `docs/handoff/`, then remind-me (`include_raw: true`), then the user's
  standing principles, and cites the source of every answer. Three tiers:
  answer when the record settles it; pick and log a `[default]` for
  implementation detail; escalate only intent, scope or taste, or a reversal
  of a `[stated]` row, as a short question, options and recommendation.
- **Changed:** the CLAUDE.md block now sends every design question from
  threads and the orchestrator to project-expert first, never to the user,
  and hands the user's answers back to it. The expert is the one writer: a
  DECISIONS.md row, one `remind_me_add`, and an OPEN_QUESTIONS.md tick per
  settled answer.
- **Superseded:** the "design advisor" mod planned in v1.1.0. Mods don't run
  in Claude Code cloud sessions; a subagent and CLAUDE.md in the repo do,
  with no local setup.
- **Why:** Nano was relaying design questions between threads and the design
  chat by hand. The agent holding the design context should answer, and only
  the questions it can't settle should reach him.

## v1.1.0 — Record the design chat link
**2026-11-02**

- **Added:** handoff step 1 now finds the design chat's claude.ai link, using
  `recent_chats`/`conversation_search` or asking the user (never invented), and
  writes it to SPEC.md as `Design chat:` and to the remind-me capture as
  `metadata.chat_url`. Resolve mode uses that link when it falls back to the
  original chat.
- **Why:** a planned Claude Code "design advisor" mod works from the saved
  dialog in remind-me. When that saved copy isn't enough, the advisor needs to
  point Nano to the exact chat instead of making him search for it.

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
