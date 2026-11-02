---
name: project-handoff
description: >-
  Turns a design conversation into a handoff pack Claude Code can build from without coming back
  to ask what was already settled: SPEC, DECISIONS (each with why, rejected options and
  provenance), a pre-answered implementer Q&A, OPEN_QUESTIONS, and a CLAUDE.md rule to look
  before asking and write back every answer. Also saves the design dialog and decisions to
  remind-me so Claude Code can search the original reasoning. Resolve mode closes the loop when
  Claude Code's open questions come back, with no copy-paste. Use at the end of any chat where
  an idea or project was fleshed out and is about to be built: "write me a prompt for Claude
  Code", "hand this off", "stand this up in CC", "kick off the repo", "give CC the context", or
  "answer the open questions for my project". Use it even when the user only asks for a kickoff
  prompt, because a prompt alone is the lossy handoff this replaces.
compatibility: >-
  Best with the rusty-remind-me MCP server and GitHub access (gh or a connected repo). Without
  them it still produces the pack as files to drop into the repo.
metadata:
  version: "1.1.0"
---

# project-handoff

A kickoff prompt is a lossy summary of the design chat. It carries *what* to
build and drops the *why*: rejected alternatives, edge cases already talked
through, defaults that were agreed. Claude Code then hits those gaps and asks,
and the user ends up relaying questions between surfaces by hand. This skill
replaces the prompt with a pack the implementer can search, plus a rule that
makes it search before asking and save every new answer, so no question is
asked twice.

Two modes:

- **Handoff** — end of a design chat → pack + remind-me records + kickoff prompt.
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
2. **Pick the target.** Find out whether a repo exists and is reachable. If it
   isn't clear, ask once, along with any step-4 questions; don't make it a
   separate stop.
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
   - `docs/handoff/SPEC.md`: intent, scope, non-goals, constraints, shape, acceptance
   - `docs/handoff/DECISIONS.md`: one row per decision, with why, what was rejected, and its tag
   - `docs/handoff/QA.md`: the step-3 questions, grouped by area
   - `docs/handoff/OPEN_QUESTIONS.md`: the `[open]` items, and where Claude Code adds new ones
   - a `CLAUDE.md` block appended to the repo's CLAUDE.md, or used to create one

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
   - Either way, end the reply with a **kickoff prompt** of no more than 6 lines
     that points Claude Code at `docs/handoff/` and names the first slice to
     build. Don't paste the spec into the prompt, since the files are the
     source of truth.
8. **Wrap-up retro** — see the end of this file.

## Resolve mode

Run this when the user comes back with Claude Code's questions ("answer the
open questions for X"), so they never have to paste anything.

1. Collect the questions: the ones the user gave, plus
   `docs/handoff/OPEN_QUESTIONS.md` from the repo. If the repo isn't
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
   - Repo not reachable: write `docs/handoff/RESOLVED-<date>.md`, with one
     entry per question giving the answer, its tag, and its target file, so
     Claude Code can merge it. Send that file.
4. Reply with a short list of what was answered and what is still open.

## Wrap-up retro — handoff mode only

When a handoff pack is delivered, run a
[`meta/skill-retro`](../../meta/skill-retro) pass on this skill, based on how
this run actually went. Did the implementer checklist turn up the questions
this project needed, or were some areas missing or padded? Was provenance
tagging hard to apply anywhere? Did delivery work against this repo and
environment? Running and reporting the retro is automatic and safe to leave
unattended. *Applying* any of its findings is a separate follow-up the user
has to approve, through skill_pack's normal PR workflow.

Resolve mode does not trigger a retro. It's usually a few answers written back,
and a retrospective on the skill's own instructions would outweigh the work.
The user can still ask for one.
