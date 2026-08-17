---
name: issue-loop
description: Runs an autonomous "clear the open issue backlog" loop against a target repo's existing GitHub issues — any label, not skill-generated ones like parity-loop's gaps. Triages each issue (actionable, breaking-change, needs-new-dependency, or not actionable), checks the platform-repo directory for something to port before hand-rolling, implements per the two development-standards repos where applicable, then works each actionable issue end-to-end (branch, implement, test, PR, green CI, merge commit, sync) — looping until none remain or told to stop. Use whenever the user asks to clear/work through open issues on a repo automatically, wants a repeatable issue-to-merged-PR loop not scoped to a specific label, or references this by name (issue-loop, backlog loop). Fourth companion to parity-loop/sovereignty-loop/dedupe-loop (same PR/CI/merge mechanics) — checks repo-config has been applied to the target before starting, same as its siblings.
version: 1.6.1
---

# issue-loop

Turns "clear the open issues on this repo" into a bounded, autonomous loop:
triage → reuse-check → implement per development standards → PR → merge on
green CI → sync → repeat. Unlike `parity-loop`, this skill doesn't generate
its own issues — it works whatever's already open in the target repo,
regardless of label or origin (human-filed, filed by another loop skill,
whatever).

This skill has no issue-body template of its own — it consumes issues, it
doesn't file them. `references/` describes the loop's supporting data
(platform directory, standards pointer); `scripts/` are the loop's tools.

## Run (when invoked)

**0. Scope**
- `TARGET_REPO` — whose open issues are being worked. Not always passed
  explicitly: if exactly one repo is attached to the session, infer
  `TARGET_REPO` from it rather than halting on a technicality — the halt
  rule below is for genuine ambiguity (multiple repos attached, none
  named), not for "the caller didn't spell out a name that was already
  obvious from context."
- **Extra arguments beyond `TARGET_REPO`** (a caller can pass free text —
  e.g. "against &lt;file&gt;", a label, a keyword) are a **filter** on which
  *already-open* issues to work, nothing more. They are never license to
  manufacture new issues out of a doc's own prose, a file's TODO comments,
  or anything else that isn't a real, already-filed issue — this skill
  doesn't generate issues (see the intro). If a filter matches zero open
  issues, say so plainly in the wrap-up report and stop there; don't
  reinterpret the filter more expansively to find something to do.
- **Tooling preflight — do this before reporting that the loop has started.**
  This skill validates the *target repo* below; this bullet validates its own
  execution environment, which is the thing that actually failed first.
  1. Restore this skill's own script permissions:
     `chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true`. The sync that
     delivers a skill to a session doesn't preserve mode bits — every script
     arrives as `0644`, measured at 31 of 31 in a live session — so a step
     written `scripts/next_issue.sh` fails with `permission denied`
     ([#1](https://github.com/baileyrd/skill_pack/issues/1)). Where the skill
     directory is read-only and `chmod` can't take, name the interpreter
     instead (`bash scripts/next_issue.sh`): it doesn't need the bit.
  2. `command -v gh`. If `gh` is absent — Claude Code on the web, a container
     without it installed — **none of this skill's scripts can run**, since all
     three shell out to it. The GitHub MCP tools are the substitute: use them
     for step 1's issue list, step 2's reuse search, and step 3.9's
     CI-wait-and-merge. Say so in the wrap-up report, so the run's mechanics
     are legible rather than looking like the scripts ran. Do **not** silently
     skip the reuse check just because its script is unavailable.
  3. One cheap read against the API (list issues, page size 1). A rate limit or
     an auth failure discovered here costs nothing; discovered at issue 12 of
     20 it strands work in flight. See "Stop conditions" for what to do when it
     fails mid-loop.
  4. Note which CI-status mechanism the target uses. A repo whose CI reports
     via **Actions checks** returns `total_count: 0` from the commit-status
     endpoint — that is *not* evidence CI is missing, and reading it that way
     will make you think a green run never happened. Match a run to the PR by
     `head_sha`, never by branch: runs are associated to PRs by branch name, so
     a stale run from a previous PR on a reused branch can appear attached to
     the current one and read as a pass for code it never ran against.
- **repo-config prerequisite**: run `repo-config`'s `scripts/audit.sh
  <TARGET_REPO>` first — this part always runs, it's cheap. If the score is
  low/missing, **don't bootstrap yet**: run step 1's triage first. Only
  invoke `repo-config` on the target once triage confirms at least one
  actionable issue actually exists — the PR mechanics and RELEASE_NOTES
  convention this skill leans on need to be there before that first
  actionable issue is worked, not before triage even runs. Bootstrapping a
  repo's full governance-file set ahead of a triage pass that turns up
  zero open issues is pure waste. Skip the bootstrap entirely if a prior
  step in the same session already confirmed it's present.
- **Harness mode**: check the `LOOP_HARNESS_MODE` environment variable
  (`auto` or unset/anything else = `interactive`) — see "Harness mode"
  below for what it changes here.
- If step 0 can't be fully answered (no `TARGET_REPO` given, or the
  environment can't resolve it) and no one's available to ask (auto mode,
  headless), halt and report what's blocking start rather than guessing.

**1. Triage** — read-only, no code yet. Pull every open issue
(`gh issue list --state open --json number,title,body,labels`) and classify
each:
- **not actionable** — a question, discussion, duplicate, or something that
  needs a design decision this skill can't make on its own judgment. Skip;
  note it in the wrap-up report rather than silently dropping it. Label it
  `needs-human` if it isn't already, so `next_issue.sh` stops re-surfacing
  it every run.
- **breaking-change** — implementing it would change an existing public
  signature or documented behavior. Flagged, never auto-implemented — see
  step 3.
- **needs-new-dependency** — implementing it would require a new
  third-party (or new internal platform-repo) dependency. Flagged, never
  auto-implemented — see step 3.
- **actionable** — a bug fix or additive feature that doesn't touch existing
  public surface and doesn't need a new dependency. This is the only
  category the loop implements unattended.

Judgment call, same caveat as the sibling skills' classification steps: read
the issue (and the relevant code, if the description is thin) rather than
trusting the title or existing labels alone. Report the triage table before
step 2 runs — number, title, classification, one-line reasoning — it's the
checkpoint to catch a wrong call before 20 issues get worked.

**2. Reuse check, per actionable issue** — before implementing, check
`references/platform-directory.md` (both `baileyrd/rusty_*` and
`Rusty-Mill/*`) via `scripts/scan_platform_repos.sh <keyword...> --repos
<repo1,repo2,...>` for an existing implementation of what the issue asks
for. A hit is a strong reason to port instead of hand-roll — same
"candidate list, not a verdict" caveat as the sibling skills: read the
actual source before trusting a name/keyword match.

**3. Work the loop** — repeat until no open actionable issues remain, a
stop condition below fires, or the user says stop:
1. Check for a stop condition first (see "Stop conditions"). If one's live,
   halt cleanly — don't abandon a half-pushed branch mid-step.
2. Pick the next open issue (`scripts/next_issue.sh`) — skips anything
   labeled `blocked` or `needs-human`.
3. **breaking-change or needs-new-dependency** → don't implement
   automatically, in either harness mode. Stop, explain what the fix would
   touch or what dependency it needs, and ask.
4. Branch off the latest default branch: `issue/<issue-number>-<slug>`.
5. Check step 2's reuse-check result for this issue. A match → port that
   implementation in, adapted to this repo's conventions (`Result` + `?`,
   no `unwrap()`/`expect()` outside tests, doc-comments, tests), noting the
   source repo in the commit message — copying code in is a pure addition;
   *depending on* the source repo as a crate instead is its own
   stop-and-ask, same as any new dependency. No match → check
   `references/development-standards.md` for an applicable requirement from
   either standards repo before falling back to this repo's own
   conventions; implement fresh either way.
6. Local gate before pushing (fail fast): the target's own test/lint/build
   commands — `cargo build && cargo test && cargo clippy -- -D warnings &&
   cargo fmt --check` for Rust, the ecosystem equivalent otherwise (see
   `parity-loop`'s "Adapting to other stacks" for the general pattern).
7. If the repo has `RELEASE_NOTES.md`, add the dated entry now.
8. Commit, push, `gh pr create` against the default branch — use
   repo-config's PR template. **One `Closes` keyword per issue**:
   `Closes #52, Closes #53, Closes #54`. GitHub only honours the keyword when
   it *immediately precedes* each number, so the natural-looking
   `Closes #52, #53, #54` closes **only #52** and leaves the rest silently
   open. This applies whenever one PR covers more than one issue.
9. `scripts/watch_and_merge.sh <pr-number>`: waits for CI, and on green,
   merges with a **merge commit** and syncs. On red, one bounded fix-up
   attempt before surfacing the failure — never force a merge, never drop
   the issue silently.
10. **Confirm every issue this PR was meant to close is actually closed** —
    re-list open issues rather than assuming the keyword fired. A malformed
    `Closes` list fails silently: the merge succeeds, the PR looks finished,
    and the issue stays open until someone re-reads the backlog. Close any
    stragglers by hand before moving on, so the next loop-around isn't
    triaging work that is already done.
11. Back to step 1's issue list (a re-triage isn't needed unless new issues
    were filed since the last pass — check for new ones each loop-around).

**4. Wrap up** — report: issues worked and merged, still open and why
(blocked on CI, needs-human, breaking-change, needs-new-dependency, marked
not-actionable), and anything triage deliberately left out of scope.

**5. Wrap-up retro** — after step 4's report, run a `meta/skill-retro` pass
on `issue-loop` itself, grounded in this run: did step 1's triage
classifications hold up, did step 2's reuse check actually surface what it
should have, did a `breaking-change`/`needs-new-dependency` stop in step 3
need something the instructions didn't cover? Read-only, safe to run
unattended in either harness mode — applying anything `skill-retro` finds
is a separate, explicitly-approved follow-up.

## Harness mode

`LOOP_HARNESS_MODE=auto` doesn't change step 3's merge behavior — actionable
issues already proceed to PR/merge unattended in both modes, same as
`parity-loop`. What it changes:
- If step 0 or step 1 needs a judgment call only a human can make (an
  issue whose actionability is genuinely ambiguous) and no one's available,
  auto mode logs it as `needs-human` and moves on rather than blocking the
  whole loop; interactive mode asks.
- breaking-change and needs-new-dependency issues **always** stop and wait,
  in both modes — auto mode is not a bypass for those.

## Stop conditions

- No open actionable issues left (skipping `blocked`/`needs-human`) → done.
- User says stop, in chat or (headless mode) via a `.issue-loop-stop` file
  at the repo root — checked each iteration, removed on graceful halt.
  Honored in both harness modes.
- A PR's CI stays red after the fix-up retry budget → pause on that issue,
  leave the PR open, report it, don't skip ahead silently.
- A breaking-change or needs-new-dependency issue → pause and ask (step
  3.3), in both harness modes.
- **The GitHub API is unreachable or rate-limited** → halt cleanly and report
  three lists: issues completed, issues *in flight* (naming the branch and any
  open PR, so nothing is stranded unnamed), and issues never started — plus the
  retry path. Every other stop condition here is about work state; this one is
  about the tooling, and it's the one where partial state exists and matters.
  **Never fall back to triaging from issue titles alone in order to keep
  going** — step 1 says titles and existing labels aren't sufficient, and a
  rate limit is not a reason to lower that bar. Waiting is cheap; a
  misclassified issue worked unattended is not.

## Rules

- Never implement a breaking-change or needs-new-dependency issue
  automatically, regardless of harness mode — stop and ask.
- Same standing workflow as the sibling skills: PR against default branch,
  never a direct push; merge with a **merge commit** on green CI, never
  squash/rebase-merge.
- Check `references/platform-directory.md` (both namespaces) before
  hand-rolling anything an issue asks for — prefer porting a match over
  writing new code, held to this repo's own conventions regardless of
  source.
- Check `references/development-standards.md` for an applicable requirement
  before falling back to generic conventions.
- If the repo has `RELEASE_NOTES.md`, keep it current — one entry per merged
  PR from this loop.
- Never force a merge on red CI, and never abandon an issue silently — a
  stuck issue gets reported, not dropped.
- A `not actionable` issue gets labeled `needs-human` and reported, not
  silently skipped on every re-run without a trace.

## Limitations

- Triage is judgment on the issue's own text (and code, if thin) — a
  terse or ambiguous issue can be misclassified. The triage table in step 1
  is the checkpoint to catch that before implementation starts.
- The platform-repo reuse check is keyword/grep-surfaced candidates plus
  judgment, same caveat as the sibling skills — it can miss a match hiding
  under different naming, and `references/platform-directory.md` can drift
  from the live orgs; confirm rather than assume it's complete.
- No issue-sizing control like `parity-loop`'s gap-analysis step — an issue
  that's really ten unrelated asks stays one issue unless the user splits it
  first; this skill doesn't split issues on its own.
- Assumes `gh` is **installed and** authenticated, and that CI is a required
  status check on the default branch, same as the sibling skills. Step 0's
  tooling preflight covers the case where `gh` is missing entirely — worth
  distinguishing, because "present but unauthenticated" fails loudly on first
  use while "not installed" makes every script in the table below unrunnable.
  Where CI is *not* actually a required check, a green run means the checks
  passed, not that GitHub would have blocked a merge without them.
- Rust/cargo-shaped by default for the local gate command; swap for the
  target ecosystem's equivalent same as `parity-loop`'s "Adapting to other
  stacks."

## Scripts

**All three require `gh`** (`next_issue.sh` additionally requires `jq`). If
step 0's preflight found `gh` absent, none of them run and the GitHub MCP tools
are the substitute — see step 0.

| Script | Purpose | Args |
| --- | --- | --- |
| `next_issue.sh` | Picks the next open issue (any label), skipping `blocked`/`needs-human` | `[--repo <owner/repo>]` |
| `watch_and_merge.sh` | Waits for a PR's CI, merges (merge commit) + syncs on green, retries once on red before surfacing failure | `<pr-number> [--retries N] [--repo <owner/repo>]` |
| `scan_platform_repos.sh` | Greps platform repos (both namespaces) for an existing implementation | `<symbol> [keyword ...] --repos <repo1,repo2,...>` |

All three shell out to `gh`/`git`, plus **`jq`** (required — `next_issue.sh`
pipes `gh` output through it) and **`ripgrep`** (optional —
`scan_platform_repos.sh` uses it when present and falls back to `grep`
otherwise). They resolve
paths relative to their own location, so they work whether this skill is
installed or just checked out locally.
