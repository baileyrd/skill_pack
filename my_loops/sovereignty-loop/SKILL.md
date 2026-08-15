---
name: sovereignty-loop
description: Audits a repo's external dependencies, checks whether an existing repo, library, or component across the Rusty-Mill org or baileyrd's personal rusty_* repos already covers the same capability, and proposes a swap-to-internal or a scoped hand-rolled replacement for each — turning "we depend on too many external crates" into a bounded loop. Trigger on requests to reduce external dependencies, consolidate around the platform layer, check for supply-chain/sovereignty exposure, or "do we already have something for this" against the user's own repo ecosystem. Companion to parity-loop (same PR/CI/merge mechanics) and repo-config (same governance conventions) — checkpointed with per-row sign-off by default since replacing a dependency is a toolchain change, but proceeds unattended on pre-classified-safe rows when `LOOP_HARNESS_MODE=auto` (hand-roll L/XL and ambiguous rows always still wait).
version: 1.2.0
---

# sovereignty-loop

Turns "do we really need this dependency" into a checkpointed loop: inventory
→ search RustyMill (repos, libraries, components alike) for existing coverage
→ classify each dependency → get sign-off → act (swap to internal, hand-roll
small ones, or log a deliberate keep). The motivating case here is
sovereignty, not tidiness — a NIPR/SIPR-constrained environment can't always
freely pull crates.io, and every external dependency is something to trust
and re-verify across the network boundary. That's also why this skill is
more conservative than `parity-loop`: closing a capability gap is additive;
replacing a dependency touches the toolchain, so nothing here merges without
a human picking it.

`assets/templates/` is the payload copied into the TARGET repo (an issue body
template). This skill's own files describe the loop itself — don't confuse
the two.

## Run (when invoked)

**0. Scope**
- **repo-config prerequisite**: run `repo-config`'s `scripts/audit.sh
  <TARGET_REPO>` first. If the standard governance-file score is
  low/missing, run repo-config on the target before proceeding — the
  issue-body template, PR mechanics, and RELEASE_NOTES convention this
  skill uses all assume it's already there. Skip only if a prior step in the
  same session already confirmed it.
- `TARGET_REPO` — whose manifest is being audited.
- `PLATFORM_REPOS` — defaults to every repo, library, and component across
  both `Rusty-Mill/*` and `baileyrd/rusty_*` (`references/platform-directory.md`
  has the current snapshot; confirm against `gh repo list Rusty-Mill` and
  the `baileyrd` namespace since both grow and repos move between them —
  migration isn't complete). This is opt-out, not opt-in — include all of
  it unless the user excludes a specific repo, rather than proposing a
  subset to approve. Many of these repos are purpose-built stand-ins for a
  specific external crate
  (`rusty_json` ~ `serde_json`, `rusty_regx` ~ `regex`, `rusty_tls` ~
  `rustls`, and so on) — that naming pattern is a useful first filter for
  which repos to check first for a given dependency, but it's a heuristic,
  not proof; confirm by reading the source. rustils (`rust-platform-core`)
  is still the usual landing spot for a swap since it's the designated floor
  other repos already consume via ADR-011, but it's not the only repo in
  scope for the search itself.
- Manifest scope — default to direct, non-dev, non-build dependencies (the
  ones that actually ship). Dev/build deps only if asked; they don't carry
  the same supply-chain weight.
- Exclusions — read the repo's own RFC/ARCHITECTURE docs first for
  dependencies that are an intentional, already-decided floor (e.g. rustils'
  RFC v2 names `libc`/`windows-sys` as the deliberate floor, with its own
  separate, already-planned raw-syscall track). Never propose relitigating
  an already-decided floor dependency — exclude it from the audit entirely,
  don't just flag it "keep external." The Rust standard library (`std`,
  `core`, `alloc`) is excluded from the audit entirely too, not logged as a
  "keep external" row — it isn't a crates.io dependency and carries none of
  the supply-chain concern this skill exists to address; `cargo metadata`
  won't surface it as a direct dependency anyway, so this is mostly a
  reminder for the classification judgment in step 3, not a filter step 1
  needs to apply.

**1. Inventory** — `cargo metadata --no-deps` (or a manifest parse) for
`TARGET_REPO`'s direct dependencies: name, version, which features are
actually enabled, and purpose. Purpose comes from the manifest's own
description first; the crates.io API can fill gaps if the network reaches it
— it often won't from an air-gapped or SIPR-side run, so fall back to
whatever's local (README, doc comments, the call sites themselves) rather
than stalling on a fetch that isn't coming back.

**2. Cross-repo search** — for each dependency, check `PLATFORM_REPOS` for
existing coverage:
- `scripts/scan_platform_repos.sh` greps each platform repo (checked out
  locally, or shallow-cloned into scratch if not) for the dependency's name
  and purpose keywords. It surfaces candidates, it doesn't render a verdict —
  read the hits and judge.
- A platform repo that *itself* still depends on the same external crate
  isn't "no coverage." If it wraps that crate behind its own module/API, the
  target depending on that wrapper instead of the raw external crate still
  consolidates the dependency to one place — real progress even without
  eliminating it at the floor. Note this distinction in the report (see
  step 3) rather than collapsing it into a flat yes/no.

**2.5. Reachability check — required before any row is called eliminable**

Removing a dependency from the target's own manifest only removes it from the
build if **nothing else in the graph pulls it**. This step is not optional and
not a judgment call: run it for every dependency that steps 1–2 leave looking
like a `covered`, `partial`, or `hand-roll candidate` row.

```
cargo tree --workspace -e normal,build -i <crate>     # Rust
pipdeptree --reverse --packages <pkg>                 # Python
npm ls <pkg>                                          # Node
```

Read the *whole* reverse tree, not just the first line. Three outcomes:

- **Only the target reaches it** → the row is genuinely eliminable. Classify
  normally.
- **Something else also reaches it** → the row is **not** eliminable, and
  must not be classified `covered`/`hand-roll candidate` as though it were.
  Reclassify as `keep external` and record the other path. The most this row
  can achieve is "stop naming it directly," which is worth doing only as a
  *precondition* for a change somewhere else — say so explicitly rather than
  presenting it as a removal.
- **The other path is itself an internal repo** → the real target is that
  repo, not this one. Say where, and propose the audit there as the
  follow-up. That is usually the higher-value finding.

Why this is a hard requirement rather than a nicety: step 1's direct-dependency
scope makes a transitively-reachable crate look identical to an eliminable one.
In the audit this rule comes from, `syn`/`quote`/`proc-macro2` were classified
as the target's only removable dependency, a complete hand-rolled replacement
was built and verified, and only then did `cargo tree -i syn` reveal all three
still arriving via `platform` → `thiserror` → `thiserror-impl`. The lockfile
was unchanged either way. One command before classifying would have caught it,
and would have pointed straight at the single `thiserror` derive that was the
actual lever.

**3. Classify & report** — one row per dependency in `dependency-audit.md`
(format: `references/dependency-audit-format.md`):
- **covered** — an internal repo already does this; recommend swap-to-internal.
- **partial** — internal repo covers part of it; recommend extend-and-swap,
  keep external for the remainder.
- **hand-roll candidate** — no internal coverage, the surface is small and
  bounded enough to build, **and step 2.5 confirmed nothing else in the graph
  reaches it**; note a rough size (S/M/L/XL).
- **keep external** — a deliberate decision (too foundational, too large a
  surface, low sovereignty relevance for this dependency specifically, or
  transitively reachable regardless per step 2.5), not a silent skip. Log the
  reason.

Record the step 2.5 result in every row's Notes, including the ones that came
back clean — "only the target reaches it" is evidence the check ran, and its
absence on a later re-read is indistinguishable from the check being skipped.


Report this before doing anything else — it's the checkpoint. In
**interactive** harness mode (default), **nothing in step 4 starts without
the user picking which rows to act on** — no "pure additions merge
unattended" carve-out like `parity-loop` has, since every row here is a
toolchain change by definition. In **auto** harness mode (see "Harness
mode" below), **swap-to-internal** and **hand-roll S/M** rows proceed to
step 4 without waiting for a human pick; **hand-roll L/XL** and any row
whose classification is genuinely ambiguous still pause and report — auto
mode removes the approval wait on pre-classified-safe work, not the
judgment calls.

## Harness mode

Checked once at the start of step 4: the `LOOP_HARNESS_MODE` environment
variable. `auto` permits proceeding straight through the step-3 checkpoint
for **swap-to-internal** and **hand-roll S/M** rows — the two act-per-row
paths that stay within this repo, add no new external surface, and are
already gated by CI. Unset or any other value means **interactive** — the
existing checkpoint behavior, unchanged.

Auto mode does **not** touch any of the following — they pause and report
regardless of harness setting:
- **hand-roll L/XL** — always a handed-back proposal, never inline, per the
  tailscale-rs precedent.
- A dependency the classification pass couldn't cleanly place (genuinely
  ambiguous between covered/partial/hand-roll) — surfaced for a human read,
  not auto-resolved.
- An already-decided floor dependency the audit flags for relitigation —
  this should have been excluded in step 0, but if it surfaces here anyway,
  stop rather than auto-decide it.
- Red CI past the one-attempt fix-up budget (see Stop conditions).
- The step 0 scope questions themselves (exclusions, `PLATFORM_REPOS`
  narrowing) — auto mode changes what happens *after* classification, not
  whether scope gets defined. If step 0 can't be answered from the repo's
  own docs and no one's available to ask, halt and report what's blocking
  start rather than guessing scope.

**4. Act, per approved row only:**
- **Swap-to-internal**: branch, replace the external import/usage with the
  internal crate's equivalent, run the target's existing tests plus whatever
  the swap needs new, PR against default, `scripts/watch_and_merge.sh` —
  CI-gated, merge commit, sync. Same mechanics as `parity-loop` step 3.
- **Hand-roll, size S/M**: same implement-test-PR loop as `parity-loop`.
  Check `references/development-standards.md` for an applicable
  requirement from either standards repo first — conform and cite the
  `ATLAS-###` ID or doc section if one applies. Otherwise build the minimal
  replacement (`Result`+`?`, no `unwrap()`/`expect()` outside tests, tests
  for happy path + boundary/failure, doc-comments), swap usage, PR,
  CI-gate, merge.
- **Hand-roll, size L/XL**: don't attempt inline. Recommend a dedicated repo
  instead — the existing pattern here (tailscale-rs exists for exactly this
  reason) — and hand back a scoped seed: what the replacement needs to
  cover, why it's worth standalone effort, what keeps depending on the
  external crate in the meantime. This is a proposal, not a PR.
- **Keep external**: log the decision and reasoning in
  `dependency-audit.md`. Nothing further happens.

For swap-to-internal and hand-roll (S/M) rows the user approves, file an
issue first (`assets/templates/issue-body.md`, labeled `dep-sovereignty`)
before branching — same traceability convention as `parity-loop`, and it's
what `Closes #N` in the PR needs. If the repo has `RELEASE_NOTES.md`, add
the dated entry before opening the PR.

**5. Wrap-up retro** — regardless of how the run ended (rows swapped,
hand-rolled, some deferred, or stopped mid-way), run a `meta/skill-retro`
pass on `sovereignty-loop` itself, grounded in this run: did step 3's
classification (covered/partial/hand-roll/keep external) hold up, did the
hand-roll size call (S/M vs. L/XL) in step 4 turn out right, did anything
about the interactive/auto harness split need clarification this run
actually hit? Read-only, safe to run unattended in either harness mode —
applying anything `skill-retro` finds is a separate, explicitly-approved
follow-up, not part of this run.

## Stop conditions

- All approved rows from step 3 are resolved (merged, or hand-roll L/XL
  handed back as a proposal) → done, report what's left in `keep external`.
- User says stop, in chat or (headless mode) via a `.sovereignty-loop-stop`
  file at the repo root, checked each iteration — honored in both harness
  modes.
- A PR's CI stays red after one fix-up attempt → pause on that row, leave
  the PR open, report it, don't force a merge or skip ahead silently.
- **Interactive mode**: any row not yet explicitly approved stays in the
  report, not the loop — there's no default path from "classified" to
  "worked." **Auto mode**: this only applies to hand-roll L/XL and
  ambiguous rows — see "Harness mode."

## Rules

- No auto-merge default in **interactive** mode — every row needs explicit
  sign-off before step 4, swap or hand-roll alike. In **auto** mode
  (`LOOP_HARNESS_MODE=auto`), swap-to-internal and hand-roll S/M rows may
  proceed without a human pick; hand-roll L/XL and ambiguous rows always
  still wait — see "Harness mode."
- Never relitigate an already-decided floor dependency — check
  RFC/ARCHITECTURE in step 0 before the audit runs, not after.
- **Never classify a row as eliminable without the step 2.5 reachability
  check.** `cargo tree -i <crate>` (or the ecosystem equivalent) before
  `covered`/`partial`/`hand-roll candidate`, and record the result in the
  row's Notes either way. A crate something else in the graph reaches is
  `keep external`, however small and self-contained its use in the target
  looks.
- Hand-roll size L/XL is never attempted inline — hand back a dedicated-repo
  proposal instead, per the tailscale-rs precedent.
- Same standing workflow as `parity-loop`/`repo-config`: PR against default
  branch, never a direct push; merge with a **merge commit** on green CI,
  never squash/rebase.
- Keep `RELEASE_NOTES.md` current if the repo has one — one entry per merged
  change from this loop.
- A "keep external" row is a logged decision, not an absence of one — don't
  let it silently vanish from the report on a re-run.
- Check `references/development-standards.md` for an applicable requirement
  before falling back to generic conventions on any hand-roll row.

## Limitations

- Cross-repo search is keyword/grep-surfaced candidates plus judgment, not a
  guaranteed-complete scan — a platform repo solving this under different
  terminology can be missed. Worth a second pass by someone who knows the
  platform repos if the audit comes back suspiciously thin.
- The `rusty_<thing>` naming pattern is a decent first filter, not a
  guarantee — a name match still needs a source read before it counts as
  `covered`, and a genuine match can exist under an unrelated name.
  `references/platform-directory.md` is a snapshot and can drift from the
  live namespaces; confirm rather than assume it's complete.
- crates.io lookups need network reachability; air-gapped/SIPR runs fall
  back to local manifest/source data only, so "purpose" may be thinner than
  a connected run would produce.
- Direct dependencies only by default — the *audit* enumerates what the target
  itself names, not the full graph. Step 2.5 narrows this to the one question
  that changes a verdict ("does anything else reach this crate?"), but it
  doesn't make the audit a supply-chain review: it won't surface a risky
  transitive dependency nobody in the graph names directly, and it won't tell
  you what your dependencies' dependencies do. A real transitive-exposure pass
  is still a separate exercise.
- Step 2.5 answers *whether* a crate is reachable another way, not *how hard*
  that other path is to change. A row can be correctly reclassified `keep
  external` while the follow-up it points at turns out to be a fifteen-line
  fix in a sibling repo — that's a good outcome, but this skill won't size it
  for you. Chase the pointer.
- The S/M/L/XL hand-roll size is a routing gut-call (inline loop vs.
  dedicated-repo proposal), not a committed estimate — treat it as a
  starting point for scoping, not a promise.
- Doesn't decide *whether* sovereignty is worth the engineering cost for a
  given dependency — that's the judgment step 3 surfaces for the user, not
  something this skill resolves on its own.

## Scripts

| Script | Purpose | Args |
| --- | --- | --- |
| `scan_platform_repos.sh` | Greps a set of platform repos for keyword candidates matching one dependency | `<dep-name> <keywords...> --repos <path1,path2,...>` |
| `watch_and_merge.sh` | Waits for a PR's CI, merges (merge commit) + syncs on green, retries once on red before surfacing failure — identical to `parity-loop`'s copy | `<pr-number> [--retries N] [--repo <owner/repo>]` |
| `next_issue.sh` | Picks the next open, approved issue to work, skipping `blocked`/`needs-human` | `[--label dep-sovereignty] [--repo <owner/repo>]` |

All three shell out to `gh`/`git`, plus **`jq`** (required — `next_issue.sh`
pipes `gh` output through it) and **`ripgrep`** (optional —
`scan_platform_repos.sh` uses it when present, `grep` otherwise).
They resolve paths relative to their own location.
