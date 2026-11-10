---
name: project-expert
description: >-
  Stands up an in-repo project expert: a subagent plus a scoped CLAUDE.md routing rule, so
  threads and the orchestrator ask it design questions instead of relaying them to the user.
  Works with or without an existing handoff pack. With a pack it wires the expert and routing
  to it; without one it harvests a minimal pack (SPEC, DECISIONS, QA, OPEN_QUESTIONS) from repo
  docs, remind-me, a design-chat link and board cards, and lists whatever it could not source.
  Handles monorepos (path-scoped), an existing decision log (pointed to, never copied) and an
  unmerged docs branch. Use for "build an expert for X", "apply project-handoff to X", "set up
  a project expert", "stop me relaying questions between sessions".
compatibility: >-
  Needs the project-handoff skill alongside it (shared templates). Best with GitHub access and
  the rusty-remind-me MCP server; WebFetch is optional, for design-chat links.
metadata:
  version: "1.0.0"
---

# project-expert

The user does not want to relay design questions between sessions. This skill
puts an expert in the repo that holds the project's design context, so threads
ask it first and the user only sees what it cannot settle. It reuses
[project-handoff](../project-handoff/SKILL.md): the pack layout, provenance
tags, expert template and routing table live in its
[templates](../project-handoff/references/templates.md) and
[harvest](../project-handoff/references/harvest.md). Read both before writing
anything; this skill only adds intake, the with/without-pack fork and the
checks. If project-handoff is missing, stop and say so rather than improvising
templates.

## 1. Fork: is there a pack? (before any sweep)

Glob `**/handoff/SPEC.md` and `.claude/agents/*-expert.md` for the slug, then
check what is not on the default branch yet: open PRs and remote branches that
touch `**/handoff/` or `.claude/agents/` (`list_pull_requests`, `list_branches`).
**An open PR that changes `**/handoff/` or `.claude/agents/` (check its file list with
`pull_request_read`, not its title) is the pack.** Do not open a duplicate, even if
it is the user's own and still in review: report it, then extend that PR or stop. Only
a merged pack, or none anywhere, decides the two cases below.

- **Pack exists** (cases: v1.3 pack; v1.2 pack with `project-expert.md` or a
  per-project CLAUDE.md block). Keep its SPEC and DECISIONS untouched. Add or
  migrate only the expert file and routing row (project-handoff
  "Migrating a v1.2 repo"). Run a refresh sweep (step 3) for decisions made
  since `Harvested:`; append rows, never edit.
- **No pack.** Harvest one (step 3), then write it.

## 2. Intake: fill this table, ask only for what is blocking

Take values from the user's request first, then the repo, then remind-me.
Record each as `[stated]` (user said it) or `[default]` (yours), and log the
`[default]`s in the PR.

| Field | Default |
|---|---|
| slug, repo | repo name (tags, pack). Agent name is the slug with `_` as `-`. Add other spellings (board key, entity) as aliases |
| pack root | `docs/handoff/`; monorepo: `<project dir>/handoff/` |
| scope globs | `**` single repo; monorepo: the project's own paths only. Get them from the board (`board_projects`; try both `_` and `-` spellings, use the key that has cards), manifests or the user's list |
| existing decision log | search for `DECISIONS.md`, ADR folders; found one means point, don't copy |
| design-chat link | from the request, else `unknown` |
| remind-me tags / entity | `[<slug>]`, entity `{kind: project, name}`; add `project-handoff`, `project-expert` |
| escalation | three tiers, fixed (below) |
| reviewer | from the request, else none |

Escalation tiers are the contract, restate them in the expert's own words:
answer when the pack, saved dialog or standing principles settle it; log a
`[default]` for implementation detail; escalate only intent, scope or taste, or
anything that would reverse a `[stated]` row. Never invent a decision:
unsourced goes to OPEN_QUESTIONS.md.

## 3. Sweep sources, in this order

1. Repo docs: README, DECISIONS/ADRs, CLAUDE.md. The in-repo record wins ties.
2. remind-me: `remind_me_search` with a `query` (the project name) plus tags
   `[<slug>]`, `include_raw: true`, detail full, paged; the tool rejects those
   options without a query. Alias variant tags first (harvest step 2) unless
   `remind_me_project` shows they already resolve.
3. Design chat: try `WebFetch` on the link. Share pages often render without
   the conversation. If you only get a shell, **say you could not read it** and
   rely on 1, 2 and 4. Never infer its content.
4. Board cards for the project (`board_list`, `card_get`): current state.
5. Merged PRs and reviews when the project has no decision log of its own.

Tag with harvest's strict provenance: `[stated]` only with a quote of the
user's own words (their prompt, a chat turn, a memory that quotes them). Docs,
PRs and reviews posted under the user's login but written by an agent are not
quotes: `[default]`, and a doc claiming "owner approved" is a lead to chase,
not a source; agent-settled is `[default]`; untraceable is `[open]`. A source
you could not reach is a gap to report, not a reason to guess.

## 4. Write

- **SPEC.md**: first lines `Design chat: <link|unknown>` and
  `remind-me tag: <slug>`. Index form for grown projects.
- **DECISIONS.md**: with an existing log, a short pointer file: the log's path,
  its numbering (keep it; new rows continue it) and where new rows go. Without
  one, the template table with a Source column.
- **QA.md**: pre-answered implementer questions, each citing its source. This
  overrides harvest's "QA starts empty". Take the question list from
  project-handoff `implementer-questions.md`, answer only what sources settle,
  drop the rest into OPEN_QUESTIONS. Leave out volatile facts (test counts)
  unless you re-ran them.
- **OPEN_QUESTIONS.md**: every `[open]` and every unsourced question.
- **Expert** `.claude/agents/<slug>-expert.md` from the template, pack root
  written literally. The expert is the single writer of settled answers: the
  caller passes the user's answer back; the expert writes the DECISIONS row and
  `remind_me_add` once.
- **CLAUDE.md** (create it if the repo only has AGENTS.md, and add one line in
  AGENTS.md pointing to it): one "Project experts" table. In a monorepo the row's globs are
  the project's scope only, so other projects' paths are unaffected. Add a row;
  never a second block.

## 5. Deliver

1. Unmerged docs branch holding the decision log? Branch from it and say so in
   the PR. Otherwise branch `handoff/<slug>` from the default branch.
2. One PR; request the named reviewer. The PR body lists **every
   OPEN_QUESTIONS item you could not source**, any source you could not read,
   and the `[default]`s you chose. Use the repo's PR template if it has one.
3. `remind_me_add` the PR (opened, branch, why) with the tags above. Save
   `[stated]` decisions as `decision` with `metadata.rationale`. Skip if
   remind-me is unavailable, and say so.
4. Run the checks in [references/acceptance.md](references/acceptance.md); they
   replace project-handoff's post-merge smoke test. Report each pass or fail; a
   fail means not done. Escalation wording comes from the template as is.

## 6. Wrap-up retro

After delivery, run a [`meta/skill-retro`](../../meta/skill-retro) pass on this
skill: was the with/without-pack fork clear, did intake miss a field, did a
source turn out unreadable? Running it is automatic and safe unattended;
applying findings is a separate step the user must approve through the normal
PR workflow. Skip it for a pure migration of a v1.2 repo.
