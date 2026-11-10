---
name: project-expert
description: >-
  Builds a project expert: an in-repo subagent plus a path-scoped CLAUDE.md routing rule, backed
  by a handoff pack (SPEC, DECISIONS with why, rejected options and provenance, QA,
  OPEN_QUESTIONS), so threads and orchestrators ask it design questions instead of the user. It
  answers from the pack, logs defaults and escalates only intent, scope or taste. Works with or
  without a pack and with or without a design chat. Handoff mode builds from a chat; harvest mode
  from repo docs, merged PRs, remind-me and cards; refresh appends; resolve answers Claude Code's
  open questions. Cloud-safe, monorepo-aware, points at an existing decision log instead of
  copying it. Formerly project-handoff. Use for "hand this off", "build an expert for X",
  "harvest X", "apply project-handoff to X", "stop relaying questions between sessions".
compatibility: >-
  Best with the rusty-remind-me MCP server and GitHub access (gh or a connected repo). Without
  them it still produces the pack as files to drop into the repo. WebFetch is optional.
metadata:
  version: "2.0.0"
---

# project-expert

A kickoff prompt is a lossy summary of the design chat: it carries *what* to
build and drops the *why*, so Claude Code asks, and the user ends up relaying
questions between sessions. This skill leaves a **project expert** in the repo:
a subagent that answers design questions from a searchable pack and the saved
dialog, so threads ask it, not the user, and no question is asked twice. It
lives in the repo because CLAUDE.md and the agent file travel with the checkout;
mods and local config don't reach cloud sessions. Cloud sessions don't always
load `.claude/agents/`, so CLAUDE.md carries a fallback that runs the same file
by hand.

Modes (all share the core procedure below):

- **Handoff**: end of a design chat. Source is the chat.
- **Harvest**: no single chat; a grown project, with or without a pack. Source
  is repo docs, PRs, remind-me, cards. See [references/harvest.md](references/harvest.md).
- **Refresh**: pack exists, project moved on. Append what was decided since.
- **Resolve**: "answer the open questions for X". Read OPEN_QUESTIONS.md, answer
  from the record, write answers back.
- **Migrate**: v1.x repo (`project-expert.md` agent, per-project CLAUDE.md block).

## Provenance: the rule that makes the pack trustworthy

Every decision and answer carries one tag; implementers treat them differently.

| Tag | Meaning | Implementer may change it? |
|---|---|---|
| `[stated]` | The user said it, picked it from options, or it's a standing preference | No, ask first |
| `[agreed]` | Claude proposed, the user accepted (handoff only) | No, ask first |
| `[default]` | Claude's or an agent's choice, never discussed | Yes, record why |
| `[open]` | Undecided; needs the user | Take the reversible option, or ask if blocking |

Never promote a `[default]` because nobody objected. When unsure: `[default]`.
Harvest is stricter: `[stated]` needs a quote of the user's own words (their
prompt, a chat turn, a memory that quotes them) and there is no `[agreed]`.
Not quotes, so `[default]`: agent-written docs, PRs and reviews posted under the
user's login; "owner approved" claims in docs (a lead to chase, not a source);
a model-written memory that paraphrases the user. A verbatim "User:" turn in a
dialog capture counts as a quote even if a model saved the capture. Discount the
summaries, memories and transcripts an earlier run of this skill wrote (they
repeat its guesses), but you may lift a verbatim user turn out of one. Quotes
may be trimmed, not reworded.

## Layout and naming

- **Slug:** the repo name (tags, pack). Agent name is the slug with `_` as `-`.
  Register other spellings (board key, entity) as remind-me aliases.
- **Expert:** `.claude/agents/<slug>-expert.md`, agent name `<slug>-expert`.
- **Pack root `<root>`:** `docs/handoff/`; monorepo: `<project dir>/handoff/`.
  Write the literal root into the expert file.
- **Routing:** the root CLAUDE.md holds ONE "Project experts" table (path globs
  to expert) plus the cloud fallback rule. Add a row; never a second block. A
  repo with only AGENTS.md gets a CLAUDE.md and one pointer line in AGENTS.md.
  Monorepo rows scope to the project's own paths so other projects are unaffected.
- **Cloud fallback:** if `subagent_type: "<slug>-expert"` isn't available, read
  the agent file fresh, spawn a general-purpose Agent whose prompt is its body
  plus the question. That counts as the expert; improvising does not.
- **Escalation** is three tiers (answer, default, escalate); the expert is the
  single writer of settled answers. Use the template's wording as is.

## Core procedure

1. **Fork: is there already a pack?** Before any sweep, glob
   `**/handoff/SPEC.md` and `.claude/agents/*-expert.md`, then check what is not
   on the default branch: open PRs and remote branches touching `**/handoff/` or
   `.claude/agents/`. PRs can't be searched by path, so list the open ones and then each one's
   changed file *names* with REST: `gh api repos/<o>/<r>/pulls/N/files --jq
   '.[].filename'`. The GitHub MCP `get_files` returns whole patches even with
   `perPage=1`, and `list_pull_requests` returns full bodies; avoid both when
   you must stay blind. A title proves nothing. An open PR that adds a pack **is the
   pack**: do not build a second. Report it and ask once: extend it, supersede
   it, or leave it. Pack on main: refresh (below) and wire only the expert and
   routing row. None anywhere: continue.
2. **Intake.** Fill this from the request, then the repo, then remind-me. Mark
   each `[stated]` or `[default]` and list the `[default]`s in the PR body. Ask
   only about what blocks.

   | Field | Default |
   |---|---|
   | slug, repo | repo name; the current repo |
   | pack root | `docs/handoff/`; monorepo `<project dir>/handoff/` |
   | scope globs | `**`; monorepo: project paths only (board `board_projects`, trying `_` and `-` spellings and using the key with cards; manifests; the user's list) |
   | existing decision log | search `DECISIONS.md`, ADR folders; found means point, don't copy |
   | design chat link | from the request, else `unknown`; never invent one |
   | remind-me tags / entity | `[<slug>]`, `{kind: project, name}`, plus `project-expert` |
   | reviewer | from the request, else none |
3. **Source** by mode (below). Imagine the engineer building this tomorrow and
   answer what sources settle; the rest is `[default]` or `[open]`. Never invent
   a decision: unsourced goes to OPEN_QUESTIONS. Report every source you could
   not read (an unreachable chat link, a share page that renders empty, a
   filtered-out board) instead of guessing its content.
4. **Close cheap gaps.** Ask only about `[open]` items that are blocking or
   expensive to reverse: at most 4 questions, one round, `AskUserQuestion`.
   Answers become `[stated]`. If nothing qualifies, ask nothing.
5. **Write the pack** from [references/templates.md](references/templates.md):
   SPEC.md (first lines `Design chat:` link and `remind-me tag:`), DECISIONS.md,
   QA.md, OPEN_QUESTIONS.md, the expert file, the routing row. With an existing
   decision log, DECISIONS.md is a short pointer: the log's path, its numbering
   (kept; new rows continue it) and where new rows go. QA.md holds
   pre-answered questions, each citing its source, only what sources settle.
   Keep volatile facts (test counts, board state) out unless re-verified. Keep
   it terse: the pack is searched, not read.
6. **Persist to remind-me** (skip if absent and say so). Handoff: one
   `remind_me_auto_capture` of the full dialog, tags `[<slug>, project-expert]`,
   `metadata.chat_url`; that is the end-of-chat capture. Then `remind_me_add`
   each `[stated]`/`[agreed]` decision (`memory_type: decision`,
   `metadata.rationale`; search first) and each `[open]` as `action_item`, tags
   `[<slug>, open-question]`. Leave `[default]`s and QA in the pack only, since
   storing them hardens choices nobody made. Harvest also adds one `fact`: date,
   sha, sources read, counts per tag.
7. **Deliver.** Reachable repo: branch `handoff/<slug>` from the default branch,
   or from the unmerged docs branch that holds the decision log (say so in the
   PR). One PR, the repo's PR template if any. Request the named reviewer; the PR
   author can't be one, so with none named say in the body that review is needed. The body lists
   the intake `[default]`s, every unreadable source, and **every OPEN_QUESTIONS
   item you could not source**. `remind_me_add` the PR (opened, branch, why).
   No repo yet: `SendUserFile` (offer to create the repo; don't unasked).
   Handoff mode ends with a kickoff prompt of at most 6 lines pointing at
   `<root>/` and the first slice; the files are the source of truth.
8. **Acceptance.** Run [references/acceptance.md](references/acceptance.md)
   with a separate agent, not the author. A fail means not done.
9. **Wrap-up retro** (end of file).

## Handoff mode sources

Run `remind_me_search` on the project first. Find the design chat link from
`recent_chats` / `conversation_search` (the `url`); ask or record `unknown`. Work
through [references/implementer-questions.md](references/implementer-questions.md)
and write down every question you'd ask, usually 20 to 40; answer each from the
chat and tag it.

## Harvest mode sources

Follow [references/harvest.md](references/harvest.md): repo docs and the
existing log first, then remind-me, the chat link (try WebFetch; a share page
that renders without the conversation is *not* read), board cards, merged PRs.
Sweeps are tag + `query`; trimmed results are fetched with `remind_me_get`.

## Refresh mode

Pack exists. Re-harvest only what changed since `Harvested: <date> @ <sha>`;
append D-rows, never edit one. Handled in harvest.md.

## Resolve mode

When the user returns Claude Code's questions ("answer the open questions for
X"). Inside the repo the expert handles most; resolve is for its escalations
and pre-expert repos.

1. Collect questions: the user's, plus `<root>/OPEN_QUESTIONS.md`, else the
   `[<slug>, open-question]` items in remind-me.
2. Answer from the record: pack, then remind-me (`include_raw: true`), then the
   original chat at the `Design chat:` link. Tag each. Ask anything still `[open]`
   in one batched `AskUserQuestion`. Say plainly when the design never
   considered a question; that is how design gaps surface.
3. Write back as step 6: `remind_me_add` only `[stated]`/`[agreed]`, and
   `remind_me_resolve` each settled item. Repo reachable: rows in DECISIONS.md /
   QA.md, tick OPEN_QUESTIONS.md, PR from a branch. Else write
   `<root>/RESOLVED-<date>.md` (answer, tag, target file) and send it.
4. Reply with a short answered / still-open list.

## Migrate mode

A repo with the old `.claude/agents/project-expert.md` or a per-project
CLAUDE.md block changes as one PR: rename the agent to `<slug>-expert.md`, set
its `name`, add the remind-me load step and precedence lines from the template;
replace the old block with the single "Project experts" table; keep the pack
untouched; run acceptance. Known: PythRust (PR #100).

## Wrap-up retro: handoff, harvest and first-time builds only

When a pack is delivered, run a [`meta/skill-retro`](../../meta/skill-retro)
pass on this skill, based on how the run went: did the fork and intake catch
what they should, was provenance hard to apply, did delivery work in this
environment, were any sources unreadable? Running it is automatic and safe
unattended; *applying* findings is a separate follow-up the user approves
through skill_pack's PR workflow. Refresh, resolve and migrate don't trigger it
(a few rows written back; a retro would outweigh the work). The user can ask.
