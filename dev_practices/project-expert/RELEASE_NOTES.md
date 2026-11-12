# Release Notes

project-expert (formerly project-handoff) lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/dev_practices/project-expert) —
this log tracks commits against `main`.

---

## v2.1.0 — Commit what the pack cites
**2026-11-12**

- **Added:** step 5 commits every document the spec or pack cites (concept doc,
  .docx, Claude Doc, chat artifact) into the repo as Markdown under
  `docs/concept/` or `<root>/sources/`, marked not binding, because a cloud
  session cannot open a chat link. Unreachable files go to OPEN_QUESTIONS and
  the PR body as unreadable.
  A Claude Doc uses the Docs `markdown` export, with the `html` export beside it
  when charts, diagrams or images carry meaning (Markdown may flatten them).
- **Added:** acceptance (step 8) greps the spec and pack for cited documents;
  each must resolve to a repo file or be listed as unreadable.
- **Added:** bootstrap mode. Step 1 first classifies the repo (none, new, active).
  A new repo (README and boilerplate only) gets repo-config on the handoff branch
  before the pack, its questions answered from the sources, and its ADR folder
  becomes the decision log the pack points at. Acceptance check 7 audits the set.
- Pulled from Nano's edit of the claude.ai account copy.

---

## v2.0.0 — Renamed from project-handoff; merged with the expert builder
**2026-11-10**

- **Changed (breaking):** skill renamed `project-handoff` to `project-expert`,
  because the expert is the product and the pack is its basis. The old name stays
  in the description so existing triggers ("apply project-handoff to X") still match.
- **Added:** core procedure with a pack check first (glob, then open PRs and
  branches by changed file names; an open PR that adds a pack is the pack, ask
  once), an intake table (scope globs, existing decision log, chat link, tags,
  reviewer), pointer-style DECISIONS for an existing log, delivery from an
  unmerged docs branch, a PR body that lists every unsourced open question and
  unreadable source, and acceptance checks by a separate agent
  ([references/acceptance.md](references/acceptance.md)) in place of the
  post-merge smoke test.
- **Fixed, found by two blind dry runs on baileyrd/portfolio_intelligence:**
  `remind_me_search` needs a `query` and trimmed results need `remind_me_get`;
  agent-written docs, PRs and reviews under the owner's login, and model-written
  memories that paraphrase the user, are `[default]`; memories from earlier runs
  of this skill are discounted; unread design-chat share pages are reported, not
  inferred; QA is seeded only from sourced answers; AGENTS.md-only repos get a
  CLAUDE.md plus a pointer; SPEC header order; optional "Hard lines" in the
  expert; board-key spelling and filter caveats.
- **Fixed after a third blind run:** step 1 lists PR file names with REST
  (`get_files` returns patches even at `perPage=1`; `list_pull_requests` returns
  bodies); a verbatim user turn may be lifted from a discounted capture; cloud
  `gh` GraphQL 403 falls back to REST; QA wording matches in templates; alias
  upsert skipped when aliases exist; user-identity mapping; PR author can't be
  the reviewer.
- **Known gap:** the fixed skill has not yet had a clean blind run (the second
  dry run leaked PR content through `get_files`; step 1 now says to list names).

---

## v1.3.0 — Harvest mode, cloud-safe expert, monorepo support
**2026-11-03**

- **Added:** harvest mode ([references/harvest.md](references/harvest.md)). Builds the
  pack for a grown project from repo docs and ADRs, merged PRs with their
  reviews, remind-me (`include_raw`) and Mill Board cards. A remind-me alias
  step runs first so variant tags resolve to one project. Provenance is
  stricter: `[stated]` only with a quote of the user's words, agent- or
  review-settled items are `[default]`, untraceable ones `[open]`, no
  `[agreed]`, never promote. Precedence: code and repo docs beat memory, newer
  beats older, conflicts go to OPEN_QUESTIONS with both sources.
- **Added:** large and merged projects. SPEC.md is an index (subsystem, doc
  paths, owner, status) and the expert reads sources at call time; QA only for
  questions actually asked. A merged project gets one pack with a section per
  subsystem; existing sub-packs and experts are kept and routed to.
- **Added:** `Harvested: <date> @ <sha>` in SPEC.md and a refresh mode that
  re-harvests only what was decided since, appends D-rows and never rewrites
  existing ones.
- **Added:** cloud smoke test in delivery: in a fresh cloud session on the
  merged branch the expert answers one known question, logs one default and
  escalates one reversal; pass or fail goes in the PR and remind-me.
- **Added:** harvest evals (synthetic history with mixed provenance, and an
  append-only refresh).
- **Changed:** the expert is `<slug>-expert`, with a first step that loads the
  remind-me tools through ToolSearch under any connected name, and carries on
  from the pack if they are absent.
- **Changed:** one "Project experts" routing table in the root CLAUDE.md (path
  globs → expert, one row each) replaces the per-project block. Pack root is
  configurable: `docs/handoff/`, or `<project dir>/handoff/` in a monorepo.
- **Fixed:** the claim that cloud sessions always load `.claude/agents/`.
  Two cloud threads could not load the PythRust agent. The routing table now
  carries a fallback: read the agent file fresh and spawn a general-purpose
  Agent with its body plus the question. That counts as the expert; improvising
  without it is not allowed, and the agent file stays the only copy of its text.
- **Migration:** v1.2 repos (PythRust, and Let Em Loose if its pack landed)
  rename `project-expert` to `<slug>-expert` and switch to the routing table.
  See SKILL.md § Migrating a v1.2 repo.
- **Why:** grown projects have no single design chat, and experts must run in
  cloud sessions with no local setup.

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
