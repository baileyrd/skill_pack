---
name: rust-migration
description: Runs an autonomous "migrate this repo/application to Rust" loop built to prevent the recurring failure mode where a migration quietly treats an existing capability as optional and drops or downgrades it. Before any Rust is written, inventories every observable capability of the source (public APIs, CLI flags, HTTP routes, config/env, jobs, file formats, error/exit behavior, existing tests) into a manifest where every row defaults to REQUIRED — a row moves to OUT-OF-SCOPE only by explicit, written, user-attributed sign-off, never inferred by Claude. Files one issue per capability, checks platform siblings (Rusty-Mill/baileyrd rusty_* repos) for something to port before hand-rolling, verifies behavioral parity before closing, and won't report the migration done while any REQUIRED row is undone. Use whenever the user asks to migrate/port/rewrite a repo or application to Rust, wants a repeatable migration-to-merged-PR loop, or references this by name (rust-migration, migration loop).
version: 1.2.0
---

# rust-migration

Turns "migrate this to Rust" into a bounded, autonomous loop: inventory the
source repo's full capability surface → lock it as the boundary contract →
file one issue per capability → check RustyMill siblings for something to
port → implement → verify parity → PR → merge on green CI → sync → repeat.

**Why this skill exists, specifically**: migrations of this shape have a
recurring failure mode — a capability that's inconvenient to port, thinly
tested, undocumented, or just not obviously "core" gets quietly dropped,
stubbed, or "we can add that later"'d, and the migration gets reported as
done anyway. This skill's structure exists to make that failure mode hard to
fall into by accident: every capability starts REQUIRED, closing a
capability's issue requires demonstrated parity evidence, and the wrap-up
report is mechanically checked against the manifest rather than eyeballed.
See "The boundary contract" below — it's the load-bearing part of this
skill, more than any individual step.

`assets/templates/` is the payload copied into the TARGET repo (an issue
body template). This skill's own files describe the loop itself.

## The boundary contract

This is the rule the rest of the skill exists to enforce, stated once so
every step below can point back to it instead of re-deriving it:

> **Every capability the source repo exhibits is REQUIRED by default.**
> Nothing becomes optional because it's hard to port, has no test, is
> undocumented, seems like dead code, seems unlikely to matter, or would
> take longer than expected. The *only* way a capability moves to
> OUT-OF-SCOPE is a written line in `capability-manifest.md` naming the
> capability and the reason, attributed to the user's decision — never
> inferred, assumed, or defaulted by Claude. When in doubt whether something
> is a capability worth tracking or incidental noise, it goes in the
> manifest as REQUIRED; the user can strike it, but Claude does not
> pre-filter.

Concretely, this means:
- "Looks like dead code" is a hypothesis to raise in step 1's report, not a
  license to omit a manifest row.
- A capability with no source-repo test still gets a manifest row — a
  missing test is a testing gap in the source, not evidence the behavior is
  unused. Extract intended behavior from the code and any docs instead.
- "This would be cleaner/idiomatic in Rust without preserving X" is a
  design proposal to bring to the user (step 0 or as it's discovered), not
  something to decide unilaterally by omission.
- A capability that turns out to be genuinely dead (verified, not assumed)
  still needs the OUT-OF-SCOPE line — the manifest is the record either way.

## Run (when invoked)

**0. Settle scope and identify the source and target — before step 1 runs**
- **Tooling preflight — do this before reporting that the loop has started.**
  The bullets below validate the *target*; this one validates the loop's own
  execution environment, which is what actually fails first when it fails.
  1. `command -v gh`. If `gh` is absent — Claude Code on the web, a container
     without it installed — the three scripts that shell out to it **cannot
     run**. The GitHub MCP tools are the substitute: use them for step 2's issue
     filing, step 3's capability picking, and step 3's CI-wait-and-merge. Say so
     in the wrap-up report, so the run's mechanics are legible rather than
     looking like the scripts ran, and do **not** silently skip a step just
     because its script is unavailable.
     (`check_manifest_coverage.sh` doesn't touch `gh` and still works.)
  2. One cheap read against the API (list issues, page size 1). A rate limit or
     an auth failure discovered here costs nothing; discovered mid-loop it
     strands work in flight. See "Stop conditions" for what to do when it fails
     later.
  3. Note which CI-status mechanism the target uses. A repo whose CI reports via
     **Actions checks** returns `total_count: 0` from the commit-status
     endpoint — that is *not* evidence CI is missing, and reading it that way
     will make you think a green run never happened. Match a run to the PR by
     `head_sha`, never by branch: runs are associated to PRs by branch name, so
     a stale run from an earlier PR on a reused branch can appear attached to
     the current one and read as a pass for code it never ran against.
- `SOURCE_REPO` (what's being migrated, any language) and `TARGET_REPO` (the
  Rust repo/crate the migration lands in — may be the same repo migrated in
  place, a new repo, or an existing `rusty_*` repo being extended).
- **repo-config prerequisite**: run `repo-config`'s `scripts/audit.sh
  <TARGET_REPO>` first. If the standard governance-file score is
  low/missing, run repo-config on the target before doing any
  rust-migration-specific work — issue templates, PR templates, and the
  RELEASE_NOTES convention this skill leans on all assume it's already in
  place. Skip only if a prior step in the same session already confirmed it.
- Check the source repo for an existing migration plan, RFC, or scope doc
  before generating anything. If one exists, reconcile step 1's inventory
  against it rather than inventing a competing scope — same rule as
  `parity-loop`'s step 0, and same reasoning: a hand-curated doc is the
  user's intent, a mechanical inventory is a way to *check* it, not
  override it.
- Confirm whether this is a **full migration** (target replaces source
  entirely — the common case) or a **partial/staged migration** (e.g. one
  service extracted at a time). Partial migrations still get a full
  capability inventory of the *piece* being migrated in this run — the
  boundary contract applies at whatever scope is agreed, it just doesn't
  get silently narrowed mid-run.
- Sibling repos for reuse — `references/platform-directory.md` has the
  current repo/purpose/namespace snapshot for `Rusty-Mill/*` and
  `baileyrd/rusty_*`; confirm against `gh repo list Rusty-Mill` and the
  `baileyrd` namespace since both drift.
- Development standards — `references/development-standards.md` points at
  the two external standards repos, consulted in step 3.5.
- Harness mode: check `LOOP_HARNESS_MODE` (`auto` or unset/anything else =
  `interactive`) — see "Harness mode" below.
- Batch this into one question round; skip anything the repo's own docs
  already answer. If step 0 can't be fully answered and no one's available
  to ask (auto mode, headless), halt and report what's blocking start
  rather than guessing scope, and never guess the boundary contract's
  REQUIRED/OUT-OF-SCOPE split specifically — that's the one thing this
  skill never defaults on its own.

**1. Inventory the source repo's capability surface** — read-only, no
issues or code yet. Be exhaustive, not representative; see
`references/source-extraction-playbook.md` for source-language-specific
techniques (Python/Node/Go/JVM/etc. all extract differently). Pull from
every angle:
- **Public interface**: exported functions/classes/modules, CLI
  commands/subcommands/flags (including ones only reachable via `--help` or
  argument-parser source, not just the README), HTTP/RPC routes and their
  request/response shapes, library entry points.
- **Configuration surface**: config file keys, environment variables,
  CLI-flag defaults, feature flags — including ones with no visible
  default, which usually means "required at deploy time," itself a
  capability to preserve.
- **Behavioral surface**: background jobs/schedulers/retries, file formats
  read or written, protocols spoken, side effects (logging shape,
  telemetry/metrics emitted, signal handling), error/exit-code contracts.
- **Tests as spec**: read the source repo's existing test suite as a
  behavior specification, not just as QA — a passing test encodes a
  capability whether or not it's mentioned anywhere else. This is usually
  the single richest source of "the thing nobody wrote down."
- **Docs as spec**: README, docs/, inline comments describing intent,
  CHANGELOG entries describing behavior that shipped.

For each surviving item: name it precisely enough to write an issue and a
parity test against, tag its source (`interface` / `config` / `behavior` /
`test` / `docs`, per the extraction categories above), and — per the
boundary contract — default its status to **REQUIRED**. Then check each
against both platform namespaces
(`scripts/scan_platform_repos.sh <capability> --repos rusty_json,rusty_http,...`
— start from `references/platform-directory.md`'s purpose list to pick
which siblings are worth checking) for something to port instead of
hand-roll. Write `capability-manifest.md` (format:
`references/capability-manifest-format.md`). Report it before moving on —
the natural checkpoint to catch a missed capability, or reconcile against
an existing migration plan, before 60 issues get filed. This report is
where the user exercises the *only* path to OUT-OF-SCOPE — flag anything
suspected dead-or-unneeded explicitly and let the user strike it; don't
pre-strike it yourself.

**2. Capture as issues**
- One issue per capability (or a tight, clearly-related group — not "port
  the whole CLI"). Use `assets/templates/issue-body.md`, filled from the
  manifest row, and include the manifest row's ID so the issue and the
  manifest stay linked in both directions.
- Before creating, search for an existing open/closed issue on the same
  capability (`gh issue list --search "<capability> in:title"`) to stay
  idempotent across re-runs of step 1.
- Label every issue `migration-item`, plus a category label
  (`interface`/`config`/`behavior`) and, if step 1 flagged a likely-dead
  candidate, `needs-human` (never silently pre-excluded — see the boundary
  contract).
- If the target repo has repo-config's issue templates already, prefer
  those over this skill's own template; don't run two competing
  conventions in one repo.

**3. Work the loop** — repeat until no open `migration-item` issues remain,
a stop condition below fires, or the user says stop:
1. Check for a stop condition first (see "Stop conditions"). If one's live,
   halt cleanly — don't abandon a half-pushed branch mid-step.
2. Pick the next open `migration-item` issue (`scripts/next_capability.sh`)
   — skips anything labeled `blocked` or `needs-human`.
3. **Tempted to skip, simplify, or defer this capability?** That impulse is
   exactly the failure mode this skill exists to catch — it is never a
   valid reason to close the issue as anything but done. If the capability
   turns out genuinely inapplicable to the target (verified, not assumed),
   or would require a breaking change / new dependency, stop and ask —
   don't resolve it unilaterally by omission, downgrade, or a partial
   implementation reported as complete.
4. Branch off the latest default branch: `migrate/<issue-number>-<slug>`.
5. Check the issue's `Existing RustyMill impl` field (from
   `capability-manifest.md`, carried into the issue body). If it names a
   sibling repo: port that implementation in — adapt it to the target
   repo's conventions rather than assuming the source complies (`Result` +
   `?`, no `unwrap()`/`expect()` outside tests, doc-comments, tests), and
   note the source repo in the commit message. Copying the code in is a
   pure addition like any hand-rolled fix; *depending on* the sibling repo
   as a crate instead of copying is its own stop-and-ask — an internal
   RustyMill dependency is still a new dependency. If no match was found
   (or the row predates this check — re-run `scan_platform_repos.sh` before
   assuming there's genuinely nothing), check
   `references/development-standards.md` for an applicable requirement from
   either standards repo before falling back to writing it from scratch:
   conform to the requirement if one applies (cite the `ATLAS-###` ID or
   doc section in the commit message), otherwise `Result` + `?`, no
   `unwrap()`/`expect()` outside tests, doc-comments on the new public
   surface. Preserve the *source's* behavior — idiomatic Rust is how it's
   implemented, not a license to change what it does; a genuine
   behavior-improvement idea goes to the user as a proposal, not a silent
   substitution.
6. **Parity verification is mandatory before this issue can close** — not
   optional polish. Write a test that demonstrates the Rust
   implementation matches the source's documented/observed behavior for
   this capability: port the source's own test if one exists (step 1's
   `test`-tagged rows), or write one from the behavior spec if the source
   had none. "The Rust build passes" is not parity evidence; "this specific
   capability behaves the same as the source, verified by this test" is.
7. Local gate before pushing (fail fast, don't burn CI cycles):
   `cargo build && cargo test && cargo clippy -- -D warnings && cargo fmt
   --check`.
8. If the repo has `RELEASE_NOTES.md`, add the dated entry now
   (repo-config's ongoing-maintenance rule applies here too).
9. Commit (`Closes #<N>` in the message, naming the parity test), push,
   `gh pr create` against the default branch — use repo-config's PR
   template if present.
10. `scripts/watch_and_merge.sh <pr-number>`: waits for CI, and on green,
    merges with a **merge commit** (never squash/rebase) and syncs the
    local default branch. On red, one bounded fix-up attempt before
    surfacing the failure instead of forcing a merge or dropping the issue.
11. Confirm the issue actually closed, and mark the corresponding
    `capability-manifest.md` row **DONE** with a link to the merged PR and
    the parity test — the manifest is the running source of truth for
    coverage, not just an artifact from step 1.
12. Back to step 1's issue list.

**4. Wrap up** — before reporting the migration finished, run
`scripts/check_manifest_coverage.sh capability-manifest.md`: it fails loudly
if any row is neither `DONE` nor `OUT-OF-SCOPE` with a reason. Only after it
passes, report: capabilities migrated (with PR links), explicitly
OUT-OF-SCOPE and why (each one user-attributed per the boundary contract),
still open and why (blocked on CI, needs-human, breaking-change), and
anything flagged in step 1 as a likely-dead candidate that the user hasn't
yet ruled on. **Never report "migration complete" while
`check_manifest_coverage.sh` fails** — a partial migration gets reported as
partial, with the gap named, not rounded up.

After that report — regardless of whether the run ended in a full
migration, a partial one, or a stop — run a `meta/skill-retro` pass on
**this skill itself**, evidence-grounded in the run that just happened: did
`rust-migration`'s own steps hold up, or did something get skipped,
reordered, or guessed that step 0-3's instructions should have covered
without a guess? This is read-only and safe to run unattended in either
harness mode — `skill-retro` never edits `rust-migration`'s own files
without separate, explicit approval of its findings (see `skill-retro`'s
own Rules); running the retro pass itself needs no such approval, only
*applying* something it finds does. Surface its findings alongside the
wrap-up report, not as an afterthought tacked on after the user has moved
on. If the user approves any finding, that's its own follow-up change to
`rust-migration` through the normal PR workflow — not part of finishing
this migration, and not blocking on it either.

## Harness mode

Named here for consistency with the sibling skills, which gate their
checkpoint on it. Step 3 already proceeds unattended on any non-blocked
capability in both harness modes, same as `parity-loop`.

What it does change: in **auto** mode, if step 0's scope questions can't be
answered from the target's own docs and no one's available to ask, halt and
report what's blocking start rather than guessing — same rule as the
sibling skills. In **interactive** mode (default, or unset), ask as normal.

The boundary contract itself is never affected by harness mode: in neither
mode does Claude move a capability to OUT-OF-SCOPE on its own judgment.
Auto mode with no one available to rule on a step-1-flagged candidate means
that row stays REQUIRED (and therefore blocks step 4's coverage check,
correctly) — it does not mean the row gets silently dropped or silently
accepted as out of scope.

## Stop conditions

Check these every iteration, not just at start:
- No open `migration-item` issues left (skipping `blocked`/`needs-human`)
  **and** `check_manifest_coverage.sh` passes → done.
- User says stop, in chat or (headless mode) via a `.rust-migration-stop`
  file at the repo root — check for it each iteration, remove it on
  graceful halt. Honored in both harness modes.
- A PR's CI stays red after the fix-up retry budget → pause on that issue,
  leave the PR open, report it, don't skip ahead silently.
- A capability needs a breaking change or a new dependency, or step 3.3's
  "tempted to skip" moment fires → pause and ask, don't auto-resolve.
- **The GitHub API is unreachable or rate-limited** → halt cleanly and report
  three lists: capabilities completed, work *in flight* (naming the branch and
  any open PR, so nothing is stranded unnamed), and capabilities never started —
  plus the retry path. Every other stop condition here is about work state; this
  one is about the tooling, and it's the case where partial state exists and
  matters. Never lower the bar on step 1's inventory or step 3's triage to keep
  going — waiting is cheap, and a capability misclassified from a title alone
  and then worked unattended is not.

## Rules

- **The boundary contract is the standing rule of this skill**: every
  capability defaults REQUIRED; only a user-attributed, written manifest
  line moves one to OUT-OF-SCOPE. Re-read "The boundary contract" above
  before any step that touches manifest status.
- Never generate `capability-manifest.md` or file issues without first
  checking for an existing hand-curated migration plan (step 0). Reconcile
  against it, don't duplicate or contradict it.
- Same standing workflow as repo-config: every change lands through a PR
  against the default branch, never a direct push; on green CI, merge with
  a **merge commit**, never squash/rebase-merge; full history preserved
  deliberately. Don't re-ask this per run.
- A capability's issue does not close without a parity test demonstrating
  the Rust implementation matches the source's behavior for that
  capability — "it compiles" is not evidence.
- A capability needing a breaking change to the target's own already-shipped
  public surface, or a new third-party (or new internal RustyMill)
  dependency, is not auto-implemented — stop and ask.
- Check both platform namespaces (`Rusty-Mill/*` and `baileyrd/rusty_*`) for
  an existing implementation before hand-rolling a capability (step 1).
  Prefer porting a match over writing new code, still held to the target
  repo's own conventions.
- Check `references/development-standards.md` for an applicable requirement
  before falling back to generic conventions (step 3.5).
- Keep issues small; a "capability" that's really ten unrelated behaviors
  gets split before step 2, not lumped into one issue.
- If the repo has `RELEASE_NOTES.md`, keep it current — one entry per merged
  PR from this loop, same as repo-config's rule.
- Never force a merge on red CI, and never abandon an issue silently — a
  stuck issue gets reported, not dropped.
- Never report the migration finished while
  `scripts/check_manifest_coverage.sh` fails.

## Limitations

- Step 1's extraction is judgment plus tooling, not a formal proof of
  completeness — a capability with no test, no doc, and an obscure code
  path can still be missed on a first pass. The step-1 report is the
  checkpoint to catch that; `check_manifest_coverage.sh` only verifies that
  *rows already in the manifest* reach a terminal state, not that the
  manifest itself is complete. Treat a "coverage: 100%" result as "every
  known row is resolved," not "nothing was missed."
- The RustyMill sibling check is keyword/grep-surfaced candidates plus
  judgment, same as the search steps in `sovereignty-loop`/`dedupe-loop` —
  it can miss a match hiding under different naming, and
  `references/platform-directory.md` can drift from the live org; confirm
  rather than assume it's complete.
- Assumes CI is configured as a required status check on the default branch;
  the "on green CI" gate only actually gates merges if branch protection
  requires it (same caveat as repo-config).
- Three of the four scripts require `gh` on `PATH` and authenticated
  (`check_manifest_coverage.sh` is the exception). Step 0's preflight checks
  for it and routes to the GitHub MCP tools when it's missing, but that
  fallback is a documented substitution the run has to make deliberately —
  the scripts themselves have no MCP path.
- Built for a single source/target pair per run. A multi-service migration
  run one service at a time means one capability manifest per service,
  reconciled by hand into an overall picture if the user wants one.
- The parity test in step 3.6 checks behavioral equivalence for what the
  test asserts — it's only as strong as the test written. Safety-relevant
  capabilities are worth a spot-check beyond the automated gate.

## Scripts

Three of these scripts shell out to `gh` — `next_capability.sh`,
`watch_and_merge.sh`, and `scan_platform_repos.sh`. If step 0's preflight found
`gh` absent they cannot run, and the GitHub MCP tools are the substitute; see
step 0.

| Script | Purpose | Args |
| --- | --- | --- |
| `next_capability.sh` | Picks the next open `migration-item` issue, skipping `blocked`/`needs-human` | `[--repo <owner/repo>]` |
| `watch_and_merge.sh` | Waits for a PR's CI, merges (merge commit) + syncs on green, retries once on red before surfacing failure | `<pr-number> [--retries N] [--repo <owner/repo>]` |
| `scan_platform_repos.sh` | Greps platform sibling repos for an existing implementation of a capability | `<capability> [keyword ...] --repos <repo1,repo2,...>` |
| `check_manifest_coverage.sh` | Fails if any `capability-manifest.md` row is neither `DONE` nor `OUT-OF-SCOPE` with a reason — the boundary contract's mechanical gate on step 4 | `<path-to-capability-manifest.md>` |

All four shell out to `gh`/`git` (or plain text parsing for the coverage
check), plus **`jq`** (required — `next_capability.sh` pipes `gh` output
through it) and **`ripgrep`** (optional — `scan_platform_repos.sh` uses it
when present, `grep` otherwise). They resolve paths relative to their
own location, so they work whether this skill is installed or just checked
out locally.
