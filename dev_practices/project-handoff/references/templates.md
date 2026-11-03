# Pack templates

These are sensible defaults; adapt headings to the project. Keep every file
short, tagged, and greppable. `<slug>` is the project slug from step 1.
`<root>` is the pack root: `docs/handoff/`, or `<project dir>/handoff/` in a
monorepo. Write the literal path into every file you generate.

## Contents
- <root>/SPEC.md (and the harvest index variant)
- <root>/DECISIONS.md
- <root>/QA.md
- <root>/OPEN_QUESTIONS.md
- .claude/agents/<slug>-expert.md
- CLAUDE.md "Project experts" table
- Kickoff prompt

## <root>/SPEC.md

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

Harvest variant: same header, plus `Harvested: <date> @ <sha>`, and the body
is an index. Pointers only; the expert reads the listed docs at call time.

```markdown
# <Project> — spec index
Harvested: 2026-11-03 @ 1a2b3c4 · remind-me tag `<slug>`
Tags: [stated] [default] [open].

| Subsystem | Docs | Owner | Status | Expert |
|---|---|---|---|---|
| ingest | docs/ingest.md, docs/adr/003-queue.md | @alice | active | this one |
| render | render/handoff/SPEC.md | @bob | stable | render-expert (own pack, kept) |
```

## <root>/DECISIONS.md

```markdown
# Decisions — <slug>
Append-only. Newest last. Implementer may revise [default] rows (add a new row saying why).

| # | Decision | Why | Rejected | Tag |
|---|---|---|---|---|
| D1 | Rust, single binary | small deploy, matches rusty_* repos | Python CLI (startup, packaging) | [stated] |
```

Harvest packs add a `Source` column: the locator, and for `[stated]` the quote
in the user's words. Never edit a row; supersede it with a new one.

```markdown
| # | Decision | Why | Rejected | Tag | Source |
|---|---|---|---|---|---|
| D1 | SQLite only | no server to run | Postgres | [stated] | PR #12 review by baileyrd: "SQLite only, I don't want a server" |
| D2 | Retry 3x | ADR-002 | none | [default] | docs/adr/002-retry.md (agent-authored) |
| D3 | Port 7421 | code beats memory | 7420 | [default] | src/config.rs:4; supersedes memory mem_x (conflict: Q2) |
```

## <root>/QA.md

```markdown
# Implementer Q&A — <slug>
Questions an implementer would ask, answered from the design chat.
Harvest packs start this file empty; the expert adds only questions actually asked.

## Data
- **Q:** What's the identity key for a file? **A:** content hash (BLAKE3) + size. [agreed]
- **Q:** Where is the index stored? **A:** SQLite next to the binary; path via `--db`. [default]
```

## <root>/OPEN_QUESTIONS.md

```markdown
# Open questions — <slug>
Claude Code: append here instead of stopping when a question isn't blocking.
Format: `- [ ] Q<n> (<date>, blocking? y/n): <question> — interim choice: <what you did>`
Resolved items are checked and point to the D#/QA entry that answers them.

- [ ] Q1 (<date>, n): …
```

## .claude/agents/<slug>-expert.md

The project expert: a subagent that holds the design context and answers
design questions so the user doesn't relay them. It lives in the repo, so
cloud sessions get it with no local setup. `tools` is left out on purpose: the
expert inherits every tool, including remind-me under whatever name it's
connected as. Replace `<slug>` and `<root>`; keep the rest.

Everything the expert needs is in the body, because the cloud fallback runs
the body (everything after the frontmatter) in a general-purpose agent. Don't
put rules in the frontmatter.

```markdown
---
name: <slug>-expert
description: >-
  Design authority for <slug>. Use before asking the user any design,
  scope or behaviour question; it answers from <root> and the saved
  design record, logs a [default] for implementation detail, and escalates
  only intent, scope or taste. Also use to record an answer the user gave.
---

You answer design questions for <slug> so the user isn't asked them. You are
the only writer of decisions; callers never edit DECISIONS.md themselves.

## First
Load the memory tools. If `remind_me_search`, `remind_me_add` and
`remind_me_resolve` are not callable, run `ToolSearch` for `remind_me`; any
connected server name works (`mcp__<server>__remind_me_*`). If none exist, say
"remind-me unavailable" in your reply, skip remind-me reads and writes, and
continue from the pack.

## Look, in this order
1. `<root>`: DECISIONS.md, SPEC.md, QA.md, OPEN_QUESTIONS.md. If SPEC.md
   indexes docs for the subsystem in question, open those docs now; they are
   the source and the pack only points at them.
2. remind-me: `remind_me_search` with tags `["<slug>"]` and
   `include_raw: true`, which includes the verbatim design record.
3. The user's standing principles: CLAUDE.md, and remind-me preferences.
Precedence: code and repo docs beat memory; a newer decision beats an older
one. If sources disagree, answer by that rule and add the conflict, with both
sources, to OPEN_QUESTIONS.md.

## Decide the tier
1. **Answer** when step 1–3 settles it. Cite the source of every answer:
   `DECISIONS.md D4`, `QA.md § Data`, a doc path, or a remind-me memory id.
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
  (`[default]`, or `[stated]` when recording the user's answer; in a Source
  column pack, quote the user's words). Never edit an existing row.
- `remind_me_add`: `memory_type: decision`, `metadata.rationale`,
  `metadata.tag` (default or stated), tags `["<slug>"]`. Search first; if
  a matching decision exists, don't add another.
- OPEN_QUESTIONS.md: tick the item if it was listed and point it at the D#.
- QA.md: if the pack has one, add the question and its answer when it was
  answered from sources rather than a new decision.
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

## CLAUDE.md "Project experts" table

ONE per repo, in the root CLAUDE.md. Create it, or add a row; never add a
second block. Replace a v1.2 "Design questions go to project-expert first"
block with it. Keep the wording; it's the rule that keeps questions from
coming back. Most specific globs first; one row per expert.

```markdown
## Project experts
Before asking the user any design, scope or behaviour question, ask the
expert for the paths involved. Never ask the user first.

| Paths | Expert |
|---|---|
| `crates/render/**` | `render-expert` |
| `**` | `<slug>-expert` |

Call it with `subagent_type: "<expert>"`. **Fallback:** if that type isn't
available (cloud sessions can fail to load agents), read
`.claude/agents/<expert>.md` fresh at call time, spawn a general-purpose Agent
whose prompt is the file's body (everything after the frontmatter) followed by
the question. That counts as the expert. Never answer without it, and never
copy the file's text anywhere.
- ANSWER: act on it; the source is cited.
- ESCALATE: ask the user exactly that block: question, options,
  recommendation. Nothing more.
- When the user answers, pass the answer to the expert to record.
  Don't write DECISIONS.md or remind-me yourself; one writer keeps each
  answer recorded exactly once.
- Non-blocking? Take the expert's recommendation, keep going, and add the
  question to the pack's OPEN_QUESTIONS.md.
```

## Kickoff prompt

No more than 6 lines. The files hold the content; the prompt only points at them.

```text
Build <project>. Everything decided is in <root> — read SPEC.md, then skim
DECISIONS.md and QA.md. Design questions go to <slug>-expert (CLAUDE.md
"Project experts" table).
Start with the first slice in SPEC.md § Acceptance. [default] decisions are yours
to revise (via the expert); [stated]/[agreed] are not. Don't ask me
what the expert can answer.
```
