# Pack templates

These are sensible defaults; adapt headings to the project. Keep every file
short, tagged, and greppable. `<slug>` is the project slug from step 1.

## Contents
- docs/handoff/SPEC.md
- docs/handoff/DECISIONS.md
- docs/handoff/QA.md
- docs/handoff/OPEN_QUESTIONS.md
- .claude/agents/project-expert.md
- CLAUDE.md block
- Kickoff prompt

## docs/handoff/SPEC.md

```markdown
# <Project> — spec
Design chat: <claude.ai chat URL, or `unknown`> (<date>) · remind-me tag `<slug>`
Tags: [stated] [agreed] [default] [open].

## Intent
<2–4 lines: who, what job, why now>

## Scope
- In: …
- Out: … (non-goals, incl. tempting ones)

## Constraints
- … [stated]

## Shape
<components, boundaries, where I/O lives; a small ASCII or mermaid sketch if it helps>

## Acceptance — first slice
- [ ] …
```

## docs/handoff/DECISIONS.md

```markdown
# Decisions — <slug>
Append-only. Newest last. Implementer may revise [default] rows (add a new row saying why).

| # | Decision | Why | Rejected | Tag |
|---|---|---|---|---|
| D1 | Rust, single binary | small deploy, matches rusty_* repos | Python CLI (startup, packaging) | [stated] |
```

## docs/handoff/QA.md

```markdown
# Implementer Q&A — <slug>
Questions an implementer would ask, answered from the design chat.

## Data
- **Q:** What's the identity key for a file? **A:** content hash (BLAKE3) + size. [agreed]
- **Q:** Where is the index stored? **A:** SQLite next to the binary; path via `--db`. [default]
```

## docs/handoff/OPEN_QUESTIONS.md

```markdown
# Open questions — <slug>
Claude Code: append here instead of stopping when a question isn't blocking.
Format: `- [ ] Q<n> (<date>, blocking? y/n): <question> — interim choice: <what you did>`
Resolved items are checked and point to the D#/QA entry that answers them.

- [ ] Q1 (<date>, n): …
```

## .claude/agents/project-expert.md

The project expert: a subagent that holds the design context and answers
design questions so the user doesn't relay them. It lives in the repo, so
cloud sessions pick it up with no local setup. `tools` is left out on
purpose: the expert inherits every tool, including remind-me under whatever
name it's connected as. Replace `<slug>` and keep the rest.

```markdown
---
name: project-expert
description: >-
  Design authority for this project. Use before asking the user any design,
  scope or behaviour question; it answers from docs/handoff/ and the saved
  design dialog, logs a [default] for implementation detail, and escalates
  only intent, scope or taste. Also use to record an answer the user gave.
---

You answer design questions for <slug> so the user isn't asked them. You are
the only writer of decisions; callers never edit DECISIONS.md themselves.

## Look, in this order
1. `docs/handoff/`: DECISIONS.md, QA.md, SPEC.md, OPEN_QUESTIONS.md.
2. remind-me, if connected: `remind_me_search` with tags `["<slug>"]` and
   `include_raw: true`, which includes the verbatim design dialog.
3. The user's standing principles: CLAUDE.md, and remind-me preferences.

## Decide the tier
1. **Answer** when step 1–3 settles it. Cite the source of every answer:
   `DECISIONS.md D4`, `QA.md § Data`, or a remind-me memory id.
2. **Default** when it's implementation detail the user wouldn't judge
   (naming, layout, library choice inside the stated stack, error wording).
   Pick the reversible option and record it tagged `[default]` with a
   one-line why.
3. **Escalate** only for intent, scope or taste, or for anything that would
   reverse a `[stated]` or `[agreed]` row. Don't record anything; return the
   escalation block below and let the caller ask the user.
When unsure between 2 and 3: if the user could tell the result apart without
reading the code, escalate.

## Record, once per settled answer
Skip this when the answer is already a DECISIONS.md row. Otherwise:
- DECISIONS.md: append a row with the next D#, its why, and its tag
  (`[default]`, or `[stated]` when recording the user's answer).
- `remind_me_add`: `memory_type: decision`, `metadata.rationale`,
  `metadata.tag` (default or stated), tags `["<slug>"]`. Search first; if
  a matching decision exists, don't add another.
- OPEN_QUESTIONS.md: tick the item if it was listed and point it at the D#.
No remind-me? Record in DECISIONS.md and say remind-me was skipped.

## Reply to the caller
Answer or default:
    ANSWER: <one or two lines>
    SOURCE: <file § / D# / memory id>
    TIER: answered | default (logged D<n>)
Escalation, kept short:
    ESCALATE: <question, one line>
    OPTIONS: a) … b) … (at most c)
    RECOMMEND: <letter> — <one-line why>
    REVERSES: <D# if it would reverse a [stated] row, else none>
```

## CLAUDE.md block

Append this to the repo's CLAUDE.md, or create the file with it. Keep the
wording; it's the rule that keeps questions from coming back.

```markdown
## Design questions go to project-expert first
Threads and the orchestrator: before asking the user any design, scope or
behaviour question, consult the `project-expert` subagent. Never ask the
user first.
- ANSWER: act on it; the source is cited.
- ESCALATE: ask the user exactly that block: question, options,
  recommendation. Nothing more.
- When the user answers, pass the answer to `project-expert` to record.
  Don't write DECISIONS.md or remind-me yourself; one writer keeps each
  answer recorded exactly once.
- Non-blocking? Take the expert's recommendation, keep going, and add the
  question to `docs/handoff/OPEN_QUESTIONS.md`.
```

## Kickoff prompt

No more than 6 lines. The files hold the content; the prompt only points at them.

```text
Build <project>. Everything decided is in docs/handoff/ — read SPEC.md, then skim
DECISIONS.md and QA.md. Design questions go to the project-expert subagent.
Start with the first slice in SPEC.md § Acceptance. [default] decisions are yours
to revise (via project-expert); [stated]/[agreed] are not. Don't ask me
what the expert can answer.
```
