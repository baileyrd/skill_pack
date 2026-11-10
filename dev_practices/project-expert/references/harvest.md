# Harvest and refresh

For a project that has outgrown its design chat: decisions live in repo docs,
merged PRs and their reviews, remind-me and Mill Board cards. Harvest builds
the same pack and `<slug>-expert` as handoff mode from those sources, with or
without an existing pack (SKILL.md core procedure step 1 decides). Refresh
tops it up later.

## Contents
- Harvest steps
- Provenance and precedence
- Large and merged projects
- Refresh steps

## Harvest steps

1. **Ground.** Settle the slug, the pack root (`<root>`) and who the user is:
   their GitHub login (`get_me`), board actor (`board_whoami`), and remind-me
   writer. Provenance depends on this. The board actor may be a service name (`admin`) and
   agent text is often posted under the owner's login: neither makes the text
   the user's words. Glob for existing packs
   (`**/handoff/SPEC.md`) and experts (`.claude/agents/*-expert.md`); note them.
2. **Alias first.** Look the project up (`remind_me_project`). If memories use
   variant tags (`tickdigest`, `tick_digest`), `remind_me_entity_upsert`
   (`kind: project`, `aliases: [...]`) so every variant resolves to one project
   before any search. Do this before step 3 or the harvest silently misses
   memories.
3. **Read the sources.** Collect candidates: claim, locator, date, actor.

   | Source | How |
   |---|---|
   | Repo docs | README, ARCHITECTURE, CLAUDE.md, `docs/`, ADRs. Code only to check a claim. |
   | Merged PRs + reviews | `gh pr list --state merged --json number,title,body,author,mergedAt`, then per PR `gh pr view N --json reviews,comments` and `gh api repos/<o>/<r>/pulls/N/comments`. No gh (cloud)? GitHub MCP `list_pull_requests` and `pull_request_read`. |
   | remind-me | `remind_me_search` with a `query` (project name) plus tags `[<slug>]`, `include_raw: true`; the tool rejects `include_raw`/`detail` without a query. Results are trimmed to a token budget: fetch the trimmed ids with `remind_me_get`. Keep `written_by` and the memory id. Discount memories written by earlier runs of this skill. |
   | Design chat | `WebFetch` the link. A share page that renders without the conversation is unread: say so, don't infer it. |
   | Existing decision log | A found `DECISIONS.md` or ADR folder is the source: point to it, keep its numbering. |
   | Board | `board_list` ignores some filters and can return every card; filter by `.project` yourself. Try both `_` and `-` project spellings. |
   | Cards | `board_list` for the project, `card_get` for each card; take comments and the actor. |

   A candidate is a chosen design, a rejected alternative, a constraint or a
   scope cut. Skip chatter and status.
4. **Tag** each candidate by provenance (next section).
5. **Resolve** overlaps by precedence (next section).
6. **Write** the pack with a `Source` column on every DECISIONS row (see
   templates). QA is seeded only from questions the sources settle (below).
7. **Persist.** `remind_me_add` only `[stated]` rows not already stored (search
   first). Open items as `action_item`, tags `[<slug>, open-question]`. Add one
   `fact` for the run: date, sha, sources read, counts per tag.
8. **Deliver** as core procedure steps 7 and 8 (PR, acceptance).

## Provenance and precedence

Harvest uses three tags. There is no `[agreed]`: an acceptance can't be
verified from a trail without the user's words.

| Tag | Only when |
|---|---|
| `[stated]` | A quoted source in the user's own words: their PR approval or comment, a remind-me decision that records their statement, a card comment by them. Put the quote and locator in `Source`. |
| `[default]` | Anything settled by an agent (Dottius, a thread) or a review, or by the user's words you can't quote. |
| `[open]` | Untraceable: asserted somewhere, no source found. |

Never promote. A tag moves up only when a quote is found, never because nobody
objected. A remind-me memory with `written_by: model` is not the user's words
unless it quotes them.

Precedence: **code and repo docs beat memory; a newer decision beats an older
one.** The row follows precedence and cites the winning source. Every conflict
(two sources disagree) is also logged in OPEN_QUESTIONS with both sources, so
the user sees it. Keep the superseded row; the new row says `supersedes D<n>`.

## Large and merged projects

- **SPEC.md is an index**: subsystem → doc paths, owners, status. It holds
  pointers, not copies. The expert opens the listed docs at call time, so the
  pack can't drift from them.
- **QA.md** holds only questions the sources settle, each citing its source,
  plus any the expert later answers from sources. No guessed answers.
- **Merged projects** get one pack with a section per subsystem. A subsystem
  that already has its own pack and expert is kept: its section is a pointer to
  that pack, and the routing table sends its paths to its own expert. Don't
  fold or re-harvest it.
- Owner: CODEOWNERS, else the most frequent merged-PR author, else `unknown`.
  Status: `active` (merged PR in the last 90 days), `stable`, `dormant`, or
  `unknown`.

## Refresh steps

Use when the pack exists and the project has moved on. SPEC.md carries
`Harvested: <date> @ <sha>`. No such line: run harvest instead.

1. Read the line. Harvest only what is newer: `git log <sha>..HEAD` for
   docs/ADR changes, PRs merged after `<date>`, remind-me with `since: <date>`,
   `board_events` after `<date>`. If `<sha>` is gone (force-push), use the date
   alone and say so.
2. Tag and resolve candidates exactly as in harvest.
3. **Append** new D-rows, continuing the numbering. A candidate whose locator
   is already in a row's `Source` is skipped. A newer decision on an existing
   row's subject is a new row saying `supersedes D<n>`. Conflicts go to
   OPEN_QUESTIONS.
4. **Never rewrite** an existing row, its tag included. The one in-place edit
   is the `Harvested:` line, set to today's date and the current HEAD sha.
5. Persist and deliver as harvest steps 7 and 8; the PR is titled "refresh".
