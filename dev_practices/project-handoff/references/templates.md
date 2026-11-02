# Pack templates

These are sensible defaults; adapt headings to the project. Keep every file
short, tagged, and greppable. `<slug>` is the project slug from step 1.

## Contents
- docs/handoff/SPEC.md
- docs/handoff/DECISIONS.md
- docs/handoff/QA.md
- docs/handoff/OPEN_QUESTIONS.md
- CLAUDE.md block
- Kickoff prompt

## docs/handoff/SPEC.md

```markdown
# <Project> — spec
Source: design chat <date>; remind-me tag `<slug>`. Tags: [stated] [agreed] [default] [open].

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

## CLAUDE.md block

Append this to the repo's CLAUDE.md, or create the file with it. Keep the wording; it's the rule that keeps questions from coming back.

```markdown
## Before asking the user a design question
1. Search `docs/handoff/` (QA.md, DECISIONS.md, SPEC.md).
2. If rusty-remind-me is connected: `remind_me_search` with tags `["<slug>"]`,
   `include_raw: true` — that includes the verbatim design chat.
3. Still unanswered?
   - Blocking or hard to reverse → ask.
   - Otherwise → take the reversible option, log it as a `[default]` row in
     DECISIONS.md, add it to OPEN_QUESTIONS.md, keep going.

## After the user answers anything
Write it down once: a DECISIONS.md row tagged `[stated]`, and `remind_me_add`
(`memory_type: decision`, `metadata.rationale`, tags `["<slug>"]`).
The same question must never need asking twice.
```

## Kickoff prompt

No more than 6 lines. The files hold the content; the prompt only points at them.

```text
Build <project>. Everything decided is in docs/handoff/ — read SPEC.md, then skim
DECISIONS.md and QA.md. Follow the "Before asking" rule in CLAUDE.md.
Start with the first slice in SPEC.md § Acceptance. [default] decisions are yours
to revise (log why); [stated]/[agreed] are not. Non-blocking questions go to
OPEN_QUESTIONS.md, not to me.
```
