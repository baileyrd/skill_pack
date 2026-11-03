---
name: project-handoff
description: >-
  Turns a design conversation, or a grown project's scattered record, into a handoff pack Claude
  Code can build from without coming back to ask what was already settled: SPEC, DECISIONS (each
  with why, rejected options and provenance), OPEN_QUESTIONS, and a per-project expert
  subagent that answers design questions from the pack, logs defaults and escalates only intent,
  scope or taste. Handoff mode builds the pack from a design chat. Harvest mode builds it from
  repo docs, merged PRs and reviews, remind-me and Mill Board cards. Refresh mode appends what was
  decided since. Resolve mode answers Claude Code's open questions. Cloud-safe: a fallback covers
  sessions where the agent type doesn't load. Use at the end of any chat where an idea was
  fleshed out and is about to be built ("hand this off", "write me a prompt for Claude Code",
  "stand this up in CC"), or when a grown project needs its decisions gathered ("harvest X",
  "build an expert for X", "refresh the X pack", "answer the open questions for X").
compatibility: >-
  Best with the rusty-remind-me MCP server and GitHub access (gh or a connected repo). Without
  them it still produces the pack as files to drop into the repo.
metadata:
  version: "1.3.0"
---

# project-handoff

A kickoff prompt is a lossy summary of the design chat. It carries *what* to
build and drops the *why*: rejected alternatives, edge cases already talked
through, defaults that were agreed. Claude Code then hits those gaps and asks,
and the user ends up relaying questions between surfaces by hand. This skill
replaces the prompt with a pack the implementer can search, plus a
**project expert**: a subagent in the repo that answers design questions from
the pack and the saved dialog, so threads ask it instead of the user and no
question is asked twice. It lives in the repo because CLAUDE.md and the agent
file travel with the checkout; mods and local config don't reach cloud
sessions. Cloud sessions do not always load `.claude/agents/`, so CLAUDE.md
carries a fallback that runs the same file by hand (see Layout and naming).

Modes:

- **Handoff** — end of a design chat → pack + remind-me records + kickoff prompt.
- **Harvest** — a grown project with no single chat → pack built from the repo,
  PRs, remind-me and cards. See [references/harvest.md](references/harvest.md).
- **Refresh** — pack exists, project moved on → append what was decided since.
- **Resolve** — "answer the open questions for X" → read Claude Code's
  `OPEN_QUESTIONS.md`, answer from the design record, write the answers back.

## Provenance: the one rule that makes the pack trustworthy

Every decision and every answer carries one tag. The implementer treats them
differently, so mixing them up does more damage than leaving a gap:

| Tag | Meaning | Implementer may change it? |
|---|---|---|
| `[stated]` | The user said it, picked it from options you offered, or it's a standing preference of theirs | No — ask first |
| `[agreed]` | Claude proposed one thing, the user accepted it | No — ask first |
| `[default]` | Claude's choice, never discussed | Yes — record why in DECISIONS.md |
| `[open]` | Genuinely undecided and needs the user | Pick the reversible option and keep going, or ask if it blocks |

Do not promote a `[default]` to `[agreed]` because the user didn't object; a
missing objection isn't agreement. If you can't tell, use `[default]`.
Harvest is stricter: `[stated]` needs a quote of the user's words, and there
is no `[agreed]`. Details in harvest.md.

## Layout and naming

- **Expert:** `.claude/agents/<slug>-expert.md`, agent name `<slug>-expert`.
  Unique per project, so one repo can hold several.
- **Pack root `<root>`:** `docs/handoff/` by default; in a monorepo,
  `<project dir>/handoff/`. Write the literal root into the expert file.
- **Routing:** the repo's root CLAUDE.md holds ONE "Project experts" table,
  path globs → expert, one row per expert, plus the cloud fallback rule. Add a
  row for a new expert; never add a second block (template in
  [references/templates.md](references/templates.md)).
- **Cloud fallback:** if `subagent_type: "<slug>-expert"` isn't available,
  read `.claude/agents/<slug>-expert.md` fresh, spawn a general-purpose Agent
  whose prompt is that file's body plus the question. That counts as the
  expert. Improvising an answer without it is not allowed. The agent file stays
  the only copy of its text.
- **Escalation** stays three-tier (answer, default, escalate) and the expert
  stays the single writer of settled answers.

## Handoff mode

1. **Ground.** Run `rusty-remind-me:remind_me_search` on the project name to
   pick up earlier decisions. If the design happened in another chat, find it
   with `conversation_search`. Settle on a short project **slug** (the repo
   name if one exists). This slug is the tag on everything that follows.
   Find the **design chat link** too: the `url` that `recent_chats` or
   `conversation_search` returns for the chat. If you can't get it, ask for it
   along with any step-4 questions, or record it as `unknown`. Never make up a
   link. It goes in SPEC.md and the remind-me capture, so a later session knows
   where the full discussion lives whenever the saved copy falls short.
2. **Pick the target.** Find out whether a repo exists and is reachable, and
   whether it is a monorepo (that sets `<root>`). If it isn't clear, ask once,
   along with any step-4 questions; don't make it a separate stop.
3. **Implementer pass.** Imagine being the engineer who has to build this
   tomorrow from the pack alone. Work through
   [references/implementer-questions.md](references/implementer-questions.md)
   and write down every question you'd ask, usually 20–40. Answer each one from
   the conversation and tag it. Anything you can't answer from the
   conversation is `[default]` (state your choice) or `[open]`.
4. **Close the cheap gaps now.** Ask only about `[open]` items that are
   blocking or expensive to reverse: at most 4 questions, one round, with
   `AskUserQuestion`. The answers become `[stated]`. If nothing qualifies,
   don't ask anything. A pack that ships with honest open items is better
   than interrogating the user.
5. **Write the pack** from [references/templates.md](references/templates.md):
   - `<root>/SPEC.md`: intent, scope, non-goals, constraints, shape, acceptance
   - `<root>/DECISIONS.md`: one row per decision, with why, what was rejected, and its tag
   - `<root>/QA.md`: the step-3 questions, grouped by area
   - `<root>/OPEN_QUESTIONS.md`: the `[open]` items, and where Claude Code adds new ones
   - `.claude/agents/<slug>-expert.md`: the subagent. It loads the remind-me
     tools, then looks in the pack, remind-me, and the user's standing
     principles; answers with a cited source, logs a `[default]` for
     implementation detail, and escalates only intent, scope or taste, or a
     reversal of a `[stated]` row. It is the one writer of settled answers
     (DECISIONS.md row, `remind_me_add`, tick in OPEN_QUESTIONS.md), which
     keeps each one recorded exactly once.
   - the "Project experts" table in the root CLAUDE.md (created, or a row added).

   Keep it terse. The pack gets searched, not read cover to cover, so short,
   tagged, greppable lines beat prose.
6. **Persist to remind-me** (skip if it isn't connected, and say you skipped it):
   - `remind_me_auto_capture` with the **full** design dialog, tags `[<slug>, handoff]`,
     and `metadata.chat_url` set to the design chat link.
     That verbatim record is what lets Claude Code search the original
     reasoning. This capture also counts as the conversation's end-of-chat
     capture, so don't capture it a second time.
   - `remind_me_add` for each `[stated]`/`[agreed]` decision, using
     `memory_type: decision`, `metadata.rationale`, and tags `[<slug>]`. Search
     first so you don't duplicate a decision that's already stored.
   - `remind_me_add` for each `[open]` item, using `memory_type: action_item`
     and tags `[<slug>, open-question]`, so resolve mode can find them even
     without the repo.
   - Leave `[default]` items and QA answers in the pack only. They're the
     implementer's to revise, and storing them would harden them into
     decisions nobody made.
7. **Deliver.**
   - Reachable repo: create a branch `handoff/<slug>`, commit the pack, open a
     PR, and record the PR with `remind_me_add`.
   - No repo yet: send the files with `SendUserFile`. If the user is on Windows,
     add a one-line PowerShell command for placing them. You can offer to
     create the repo, but don't create it unless the user asks.
   - **Cloud smoke test** (repo delivery): after merge, in a fresh cloud
     session on the merged branch, call the expert through the routing table
     with three real questions: one the pack settles (expect ANSWER with a
     source), one of implementation detail (expect a logged `[default]` row),
     one that reverses a `[stated]` row (expect ESCALATE with `REVERSES`). Post
     pass or fail per question as a PR comment and `remind_me_add` it (tags
     `[<slug>, smoke-test]`). On a fail, report it; don't call the handoff done.
   - Either way, end the reply with a **kickoff prompt** of no more than 6 lines
     that points Claude Code at `<root>/` and names the first slice to
     build. Don't paste the spec into the prompt, since the files are the
     source of truth.
8. **Wrap-up retro** — see the end of this file.

## Harvest and refresh modes

Triggered by "harvest X", "build an expert for X", "refresh the X pack", or a
project with decisions in many places. Follow
[references/harvest.md](references/harvest.md). The pack, expert, routing
table, persistence and delivery are the same as handoff; what changes is the
source (repo, PRs, remind-me, cards), the stricter provenance, and that
SPEC.md becomes an index. SPEC.md records `Harvested: <date> @ <sha>`.

## Resolve mode

Run this when the user comes back with Claude Code's questions ("answer the
open questions for X"), so they never have to paste anything. Inside the repo
the project expert handles most of them; resolve mode is for its escalations
and for repos set up before v1.2.0.

1. Collect the questions: the ones the user gave, plus
   `<root>/OPEN_QUESTIONS.md` from the repo. If the repo isn't
   reachable, use the `[<slug>, open-question]` items in remind-me.
2. Answer each one from the design record. Check the pack first, then
   remind-me (`include_raw: true` for the dialog). Go to the original chat with
   `conversation_search` only if neither one covers the question. Open it at
   the `Design chat:` link in SPEC.md if there is one. Tag every
   answer. Ask the user about anything still `[open]` in one batched
   `AskUserQuestion` round. When a question comes up that the design never
   considered, say so plainly, since that's how gaps in the design come to
   light.
3. Write the answers back, following the same storage rules as handoff step 6:
   `remind_me_add` only for `[stated]`/`[agreed]` answers, and
   `remind_me_resolve` for each open-question item that's now settled.
   - Repo reachable: add the answers as rows in DECISIONS.md or QA.md, tick
     them off in OPEN_QUESTIONS.md, and open a PR from a branch.
   - Repo not reachable: write `<root>/RESOLVED-<date>.md`, with one
     entry per question giving the answer, its tag, and its target file, so
     Claude Code can merge it. Send that file.
4. Reply with a short list of what was answered and what is still open.

## Migrating a v1.2 repo

A repo with a v1.2 pack (`project-expert`, a per-project CLAUDE.md block)
changes three things, as one PR:

1. Rename `.claude/agents/project-expert.md` to `<slug>-expert.md`, set its
   `name`, and add the remind-me load step and the precedence lines from the
   v1.3 template. Keep its pack and DECISIONS untouched.
2. Replace the old "Design questions go to project-expert first" block with
   the "Project experts" table and fallback rule. One table per repo.
3. Run the cloud smoke test.

Known v1.2 repos: PythRust (PR #100), and Let Em Loose if its pack landed.

## Wrap-up retro — handoff and harvest modes only

When a handoff or harvest pack is delivered, run a
[`meta/skill-retro`](../../meta/skill-retro) pass on this skill, based on how
this run actually went. Did the implementer checklist turn up the questions
this project needed, or were some areas missing or padded? Was provenance
tagging hard to apply anywhere? Did delivery work against this repo and
environment? Running and reporting the retro is automatic and safe to leave
unattended. *Applying* any of its findings is a separate follow-up the user
has to approve, through skill_pack's normal PR workflow.

Resolve and refresh modes do not trigger a retro. They're usually a few
answers or rows written back, and a retrospective on the skill's own
instructions would outweigh the work. The user can still ask for one.
