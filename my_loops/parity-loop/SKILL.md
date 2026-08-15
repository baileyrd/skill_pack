---
name: parity-loop
description: Runs an autonomous "close the capability gap" loop against a reference API surface — assess what a target codebase is missing relative to a reference (e.g. the `libc` crate, POSIX, another package/spec), check whether a sibling repo across the Rusty-Mill/baileyrd platform namespaces already implements the gap before writing anything from scratch, open one GitHub issue per gap, then work each issue end-to-end (implement or port, test, PR, wait for green CI, merge with a merge commit, sync) — looping until the gap list is empty or told to stop. Use whenever the user asks to assess a codebase for missing coverage against a reference library/spec and close the gaps, wants "parity" or "coverage" work automated as a repeatable issue-to-merged-PR loop, or references this by name (parity-loop, gap loop, coverage loop). Companion to the repo-config skill — assumes repo-config's PR/issue templates and RELEASE_NOTES.md convention if present, but works without them.
version: 1.2.1
---

# parity-loop

Turns "make X have full/better coverage of Y" into a bounded, autonomous loop:
assess → check RustyMill siblings for something to port → file issues →
implement or port → PR → merge on green CI → sync → repeat.

Written Rust-first (the worked example is `rusty_libc` vs. the `libc` crate) since
that's the common case here, but the phases generalize to any target/reference pair —
see "Adapting to other stacks" below.

`assets/templates/` is the payload copied into the TARGET repo (an issue body
template). This skill's own files describe the loop itself — don't confuse the two.

## Run (when invoked)

**0. Settle what "parity" means for this run — before anything else, including
before step 1 runs**
- **repo-config prerequisite**: run `repo-config`'s `scripts/audit.sh <target>`
  first. If the standard governance-file score is low/missing (repo-config
  hasn't been applied here), run repo-config on the target before doing any
  parity-loop-specific work — issue templates, PR templates, and the
  RELEASE_NOTES convention this skill leans on all assume it's already
  in place. Skip this check only if a prior step in the same session already
  confirmed it.
- Check the target repo for an existing hand-curated roadmap or scope doc
  (`ROADMAP.md`, a `docs/` planning file, an RFC/ARCHITECTURE section, a
  project board, issues already carrying intent) before generating anything.
  If one exists, it *is* the definition of parity for this run — step 1
  audits implementation status against it rather than inventing a competing
  scope from scratch. Filing a second, unreconciled gap list next to a
  hand-curated one is the failure mode this step exists to prevent.
- If no such document exists, or it doesn't fully answer scope, ask before
  proceeding: what capability set counts as "parity" here, what's the
  reference (a crate, a spec, a roadmap section, a doc), and what's
  explicitly out for this round. Don't default to a mechanical diff just
  because the tooling for one happens to exist — a diff produces *a*
  candidate list, not necessarily *the* list the user actually wants worked.
- **Default posture: everything in the reference is in scope**, including
  capabilities that would need a new subsystem, a different execution
  model, or major rearchitecture in the target — "parity" was the word
  the user chose, and a capability the target has no easy analog for is
  still a gap, not an exemption. How much work a gap takes is a sizing
  and sequencing question (split it smaller, tackle it later, ask for a
  design decision on the target's own terms) — it is never, on its own,
  a reason to leave something off the list. If step 1 later finds "this
  needs a new subsystem," that's a `new-subsystem` tag on the gap (see
  step 1/3), not an implicit exclusion nobody signed off on.
- Platform floor — if the repo states one (e.g. rustils' RFC v2: `libc` floor
  on Linux, `windows-sys` floor on Windows), use it; otherwise it's part of
  the question above.
- Sibling repos for reuse — check both `Rusty-Mill/*` and `baileyrd/rusty_*`
  (`references/platform-directory.md` has the current repo/purpose/namespace
  snapshot; confirm against `gh repo list Rusty-Mill` and the `baileyrd`
  namespace since both grow and repos move between them — migration isn't
  complete). Default to checking all of it in step 1 rather than asking
  which siblings count — narrow only if the user says a specific repo is
  out of bounds.
- Development standards — `references/development-standards.md` points at
  two external repos (`rusty_foundation_akb`,
  `Atlas_Engineering_Standards_Library`) that are the normative source for
  architecture/implementation standards. Consult them in step 3.6 below
  before falling back to this skill's own generic conventions.
- Batch this into one question round; skip anything the repo's own docs
  already answer. Once scope is settled, note which of step 1's three
  assessment paths applies (below) and don't switch it mid-run.

**1. Assess** — read-only, no issues or code yet. Which path applies was
decided in step 0:

- **Roadmap-defined scope**: audit the roadmap's stated items against the
  target's current implementation — done / partial / not started. A partial
  item gets the same judgment pass as below (does finishing it stay additive,
  or does it touch an existing signature).
- **Comparable reference surface exists** (a crate/package shaped enough like
  the target to diff — e.g. `libc` against a from-scratch libc reimplementation
  that's far enough along to have a real public surface): `cargo public-api`
  against the pinned reference version and the target (`cargo install
  cargo-public-api` if missing — check `cargo public-api --help` for current
  flags), diffed by symbol name (ignore module path). This is a *candidate*
  list, not a final one — expect noise from platform-`cfg`'d items and
  type/const-only entries. Only use this path when step 0 didn't already
  settle scope from a roadmap; a diff is a way to *discover* candidates, not
  to override an already-defined scope.
- **No comparable surface to diff, and no roadmap** (a spec, man pages, or a
  target too early-stage to have anything a tool can diff against): extract
  required capabilities by reading the reference directly. This is a
  documentation-driven judgment pass, not a fallback to apologize for — it's
  the normal path whenever there's nothing structurally comparable to run
  `cargo public-api` against.

Across all three paths: categorize each surviving candidate (function / type
/ const / macro), note which platform(s) it applies to, flag anything whose
fix would touch an *existing* public signature rather than purely add (a
breaking-change flag, handled specially in step 3), and tag which path
produced it. Also flag — don't drop — anything that would need a new
subsystem the target has no analog of (a `new-subsystem` tag, handled the
same "stop and ask, don't silently implement or silently exclude" way as
a breaking change in step 3). The instinct to reason "this is architecturally
big, so it's out of scope" belongs to the user, not to this assessment pass —
write the reasoning down as a tag on the candidate, not as a justification
for leaving it out of `gap-analysis.md` altogether.

Then check each candidate against both platform namespaces
(`scripts/scan_rustymill_repos.sh <symbol> --repos rusty_json,rusty_http,...`
— start from `references/platform-directory.md`'s purpose list to pick
which siblings are worth checking for a given gap, rather than scanning
every repo for every row): a sibling repo that already implements the gap is a
strong reason to port instead of hand-roll, and shrinks the size estimate
accordingly. This is a candidate list, same caveat as any of the search
steps in this skill family — read the actual source before trusting a name
or keyword match. Write `gap-analysis.md` (format:
`references/gap-analysis-format.md`). Report it before moving on — this is a
natural checkpoint to trim scope, or reconcile something the audit flagged
against the roadmap, before it becomes 40 issues.

**2. Capture as issues**
- One issue per gap, sized small (a function or a tight group of related
  functions — not "implement all of string.h"). Use
  `assets/templates/issue-body.md`, filled from the gap-analysis row. A
  `new-subsystem` gap doesn't get to skip this step for being big — file
  it too, even if the honest sizing is "design/scoping issue: figure out
  what a first slice looks like" rather than an implementation-ready
  ticket. Capturing intent to revisit beats leaving it undocumented
  outside a scope-notes file only this assessment pass will reread.
- Before creating, search for an existing open/closed issue on the same symbol
  (`gh issue list --search "<symbol> in:title"`) to stay idempotent across
  re-runs of step 1.
- Label every issue `parity-gap`, plus a platform label (`platform:linux` /
  `platform:windows` / `platform:both`) and, if step 1 flagged it,
  `breaking-change` and/or `new-subsystem`.
- If the target repo has repo-config's issue templates already, prefer those over
  this skill's own template; don't run two competing conventions in one repo.

**3. Work the loop** — repeat until no open `parity-gap` issues remain, a stop
condition below fires, or the user says stop:
1. Check for a stop condition first (see "Stop conditions"). If one's live,
   halt cleanly — don't abandon a half-pushed branch mid-step.
2. Pick the next open `parity-gap` issue (`scripts/next_issue.sh`) — skips
   anything labeled `blocked` or `needs-human`.
3. **`breaking-change`-labeled issue** → don't implement automatically. Stop,
   explain what existing public API the fix would touch, and ask — this is the
   standing "ask before public API changes" rule, not a suggestion.
4. **`new-subsystem`-labeled issue** → same treatment as a breaking change,
   for a different reason: it's too big to land as one PR as filed, *and*
   it's not this loop's call to make the target's architecture bigger on
   its own initiative. Stop, propose a decomposition (what a first real
   slice would look like) or lay out the design question the target's
   architecture needs answered, and don't proceed until the user has
   actually weighed in — not once a justification for skipping it has
   been written down. This is the direct fix for the failure mode
   described in "Limitations" below: silently excluding a gap here is
   exactly the mistake this step exists to prevent.
5. Branch off the latest default branch: `parity/<issue-number>-<slug>`.
6. Check the issue's `Existing RustyMill impl` field (from
   `gap-analysis.md`, carried into the issue body). If it names a sibling
   repo: port that implementation in — adapt it to this repo's conventions
   rather than assuming the source already complies (`Result` + `?`, no
   `unwrap()`/`expect()` outside tests, doc-comments, tests), and note the
   source repo in the commit message. Copying the code in is a pure
   addition like any hand-rolled fix; *depending on* the sibling repo as a
   crate instead of copying is its own stop-and-ask — an internal RustyMill
   dependency is still a new dependency, "ours" doesn't exempt it. If no
   match was found (or the row predates this check — re-run
   `scripts/scan_rustymill_repos.sh` before assuming there's nothing),
   check `references/development-standards.md` for an applicable
   requirement from either standards repo before falling back to writing
   it from scratch: conform to the requirement if one applies (cite the
   `ATLAS-###` ID or doc section in the commit message), otherwise
   `Result` + `?`, no `unwrap()`/`expect()` outside tests, doc-comments on
   the new public surface, tests covering the happy path plus real
   boundary/failure cases. A new third-party dependency needed to close the
   gap is its own stop-and-ask, same as a breaking change — don't add one
   silently.
7. Local gate before pushing (fail fast, don't burn CI cycles):
   `cargo build && cargo test && cargo clippy -- -D warnings && cargo fmt --check`.
8. If the repo has `RELEASE_NOTES.md`, add the dated entry now (repo-config's
   ongoing-maintenance rule applies here too).
9. Commit (`Closes #<N>` in the message), push, `gh pr create` against the
   default branch — use repo-config's PR template if present.
10. `scripts/watch_and_merge.sh <pr-number>`: waits for CI, and on green, merges
    with a **merge commit** (never squash/rebase) and syncs the local default
    branch. On red, it makes one bounded fix-up attempt (see script header for
    the retry count) before giving up and surfacing the failure instead of
    forcing a merge or silently dropping the issue.
11. Confirm the issue actually closed (merge with `Closes #N` should do it
    automatically — verify rather than assume).
12. Back to step 1.

**4. Wrap up** — when the loop ends for any reason, report: issues opened,
merged, still open and why (blocked on CI, needs-human, breaking-change,
new-subsystem, out of gaps). Keep two things separate in this report,
not one merged "left out of scope" bucket — they mean different things:
- **User-excluded**: candidates the user explicitly took off the list,
  either in step 0's scope conversation or in answer to a `new-subsystem`/
  `breaking-change` stop-and-ask — include their stated reason.
- **Still open, awaiting a decision**: `new-subsystem` issues nobody has
  actually resolved yet either way. These are not "out of scope" — they're
  unfinished business this loop couldn't close alone, and reporting them
  as settled would recreate the exact failure this skill now guards
  against (see "Limitations").

**5. Wrap-up retro** — after step 4's report, run a `meta/skill-retro` pass
on `parity-loop` itself, grounded in this run: did step 1's path selection
(roadmap/diff/spec) fit cleanly, did a `breaking-change` or
`new-subsystem` call in step 3 need something the instructions didn't
cover, did the User-excluded/still-open split in step 4 actually capture
what happened? Read-only, safe to run unattended in either harness mode —
applying anything `skill-retro` finds is a separate, explicitly-approved
follow-up, never bundled into the wrap-up report itself.

## Harness mode

Named here for consistency with the sibling skills (`sovereignty-loop`,
`dedupe-loop`, `issue-loop`), which gate their checkpoint on it. This skill
never had a per-row sign-off checkpoint to gate — step 3 already proceeds
unattended on any gap that isn't `breaking-change` or `new-subsystem` in
both harness modes — so `LOOP_HARNESS_MODE=auto` changes nothing about
step 3 or 4 here.

What it does change: in **auto** mode, if step 0's scope questions can't be
answered from the target's own docs and no one's available to ask, halt and
report what's blocking start rather than guessing scope — same rule as the
sibling skills. In **interactive** mode (default, or unset), ask as normal.

The **breaking-change** stop in step 3.3 and the **new-subsystem** stop in
step 3.4 are never affected by harness mode — both pause and ask in both
modes; `LOOP_HARNESS_MODE=auto` unblocks unattended *work*, not unattended
*scope decisions*.



Check these every iteration, not just at start:
- No open `parity-gap` issues left (skipping `blocked`/`needs-human`) → done.
- User says stop, in chat or (headless mode) via a `.parity-loop-stop` file at
  the repo root — check for it each iteration, remove it on graceful halt.
  Honored in both harness modes.
- A PR's CI stays red after the fix-up retry budget → pause on that issue,
  leave the PR open, report it, don't skip ahead silently.
- An issue is `breaking-change`-labeled → pause and ask (step 3.3), don't
  auto-implement or auto-skip.
- An issue is `new-subsystem`-labeled → pause and ask (step 3.4), don't
  auto-implement or auto-skip.

## Rules

- Never generate a `gap-analysis.md` or file issues without first checking
  for an existing hand-curated roadmap/scope doc (step 0). Reconcile against
  it, don't duplicate or contradict it.
- Same standing workflow as repo-config: every change lands through a PR
  against the default branch, never a direct push; on green CI, merge with a
  **merge commit**, never squash/rebase-merge; full history preserved
  deliberately. Don't re-ask this per run.
- A gap whose fix touches an *existing* public signature, needs a new
  third-party (or new internal RustyMill) dependency, or needs a new
  subsystem the target has no analog of, is not auto-implemented — stop and
  ask. Pure additions — hand-rolled or ported in from a sibling repo — are
  the only thing this loop merges unattended.
- **A gap is never silently excluded from the backlog for being large or
  needing new target-side infrastructure.** There are exactly two ways a
  candidate leaves scope, and both require someone other than this loop to
  say so: (a) the user explicitly excludes it, either in step 0's scope
  conversation or in answer to a `new-subsystem` stop-and-ask (step 3.4) —
  record their stated reason; or (b) it depends on a real external
  system/account/service the target has no way to reach, in which case
  propose a pragmatic partial translation using what the target already
  has *before* treating the capability as unreachable, and still ask
  rather than deciding alone. "This would take a lot of new
  infrastructure" is a reason to flag and ask, never a reason to quietly
  drop something from `gap-analysis.md` or leave it out of the wrap-up
  report.
- Check both platform namespaces (`Rusty-Mill/*` and `baileyrd/rusty_*`) for
  an existing implementation before hand-rolling a gap fix (step 1). Prefer
  porting a match over writing new code, but still hold it to this repo's
  own conventions rather than trusting the source as-is.
- Check `references/development-standards.md` for an applicable requirement
  before falling back to generic conventions (step 3.6).
- Keep issues small; a "gap" that's really ten unrelated functions gets split
  before step 2, not lumped into one issue.
- Pin the reference version for the whole run — don't let the target drift
  mid-loop because upstream shipped a new release.
- If the repo has `RELEASE_NOTES.md`, keep it current — one entry per merged
  PR from this loop, same as repo-config's rule.
- Never force a merge on red CI, and never abandon an issue silently — a
  stuck issue gets reported, not dropped.

## Limitations

- **Why the `new-subsystem` stop-and-ask exists**: an earlier gap-closing
  effort let the assessing/implementing agent unilaterally mark
  architecturally-large items out of scope and record that reasoning only
  in the target's own docs — the actual mandate was full parity, and the
  pattern went uncorrected for many rounds before the user caught it and
  had to explicitly push back. Well-written justification for an
  exclusion is not the same thing as the user actually agreeing to it;
  the `new-subsystem` label and its stop-and-ask (step 3.4) exist
  specifically to make that decision visible per-gap, at the moment it's
  made, instead of buried in a doc the user has no reason to reread.
- On the diff path specifically: matching is by symbol name, not semantics —
  a same-named function with a different signature or behavior shows up as
  "present" when it may not actually match. Worth a spot-check on anything
  safety-relevant.
- On the roadmap path: this skill treats the roadmap as authoritative for
  scope, not as verified-current — a stale roadmap item marked "done" that
  isn't will read as no-gap. Worth a periodic real check, not this skill's job.
- The RustyMill sibling check is keyword/grep-surfaced candidates plus
  judgment, same as the search steps in `sovereignty-loop`/`dedupe-loop` —
  it can miss a match hiding under different naming, and it only checks
  repos worth scanning for a given gap (step 1), not the full org every
  time. `references/platform-directory.md` can also drift from the live
  org; confirm rather than assume it's complete.
- Assumes `gh` is authenticated and CI is configured as a required status
  check on the default branch; the "on green CI" gate only actually gates
  merges if branch protection requires it (same caveat as repo-config).
- Built for a single target/reference pair per run. Comparing against several
  references at once (e.g. libc *and* a BSD extension set) means running the
  assessment phase once per reference and merging the gap lists by hand.
- Rust/cargo-shaped by default. See "Adapting to other stacks" for other
  ecosystems.

## Adapting to other stacks

The loop mechanics (issue → branch → implement → PR → watch → merge → sync)
don't depend on Rust. What's Rust-specific is step 1's extraction tool
(`cargo public-api`) and step 3's local gate command. Swap those for the
target ecosystem's equivalents (e.g. a Python package: `griffe` or a
`__all__`/AST-based export dump for extraction, `pytest` + `ruff`/`mypy` for
the local gate) and the rest of this skill applies unchanged.

## Scripts

| Script | Purpose | Args |
| --- | --- | --- |
| `next_issue.sh` | Picks the next workable `parity-gap` issue, skipping `blocked`/`needs-human` | `[--repo <owner/repo>]` |
| `watch_and_merge.sh` | Waits for a PR's CI, merges (merge commit) + syncs on green, retries once on red before surfacing failure | `<pr-number> [--retries N] [--repo <owner/repo>]` |
| `scan_rustymill_repos.sh` | Greps RustyMill sibling repos for an existing implementation of a gap | `<symbol> [keyword ...] --repos <repo1,repo2,...>` |

All three shell out to `gh` and `git`, plus **`jq`** (required —
`next_issue.sh` pipes `gh` output through it) and **`ripgrep`** (optional —
`scan_rustymill_repos.sh` uses it when present, `grep` otherwise). They
resolve paths relative to their own location, so they work whether this skill
is installed or just checked out locally.
