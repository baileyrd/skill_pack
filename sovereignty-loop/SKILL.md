---
name: sovereignty-loop
description: Audits a repo's external dependencies, checks whether an existing repo, library, or component under the RustyMill org already covers the same capability, and proposes a swap-to-internal or a scoped hand-rolled replacement for each — turning "we depend on too many external crates" into a bounded, checkpointed loop. Trigger on requests to reduce external dependencies, consolidate around the platform layer, check for supply-chain/sovereignty exposure, or "do we already have something for this" against the user's own repo ecosystem. Companion to parity-loop (same PR/CI/merge mechanics) and repo-config (same governance conventions) — unlike parity-loop, nothing here auto-merges without per-row sign-off, since replacing a dependency is a toolchain change by definition.
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
- `TARGET_REPO` — whose manifest is being audited.
- `PLATFORM_REPOS` — defaults to every repo, library, and component under
  the RustyMill org (`references/rustymill-directory.md` has the current
  snapshot; confirm against `gh repo list RustyMill` since the org grows).
  This is opt-out, not opt-in — include all of it unless the user excludes
  a specific repo, rather than proposing a subset to approve. Many RustyMill
  repos are purpose-built stand-ins for a specific external crate
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
  don't just flag it "keep external."

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

**3. Classify & report** — one row per dependency in `dependency-audit.md`
(format: `references/dependency-audit-format.md`):
- **covered** — an internal repo already does this; recommend swap-to-internal.
- **partial** — internal repo covers part of it; recommend extend-and-swap,
  keep external for the remainder.
- **hand-roll candidate** — no internal coverage, and the surface is small
  and bounded enough to build; note a rough size (S/M/L/XL).
- **keep external** — a deliberate decision (too foundational, too large a
  surface, low sovereignty relevance for this dependency specifically), not
  a silent skip. Log the reason.

Report this before doing anything else — it's the checkpoint. **Nothing in
step 4 starts without the user picking which rows to act on.** There's no
"pure additions merge unattended" carve-out like `parity-loop` has — every
row here is a toolchain change by definition, which the standing working
agreement already requires asking about.

**4. Act, per approved row only:**
- **Swap-to-internal**: branch, replace the external import/usage with the
  internal crate's equivalent, run the target's existing tests plus whatever
  the swap needs new, PR against default, `scripts/watch_and_merge.sh` —
  CI-gated, merge commit, sync. Same mechanics as `parity-loop` step 3.
- **Hand-roll, size S/M**: same implement-test-PR loop as `parity-loop`:
  build the minimal replacement (`Result`+`?`, no `unwrap()`/`expect()`
  outside tests, tests for happy path + boundary/failure, doc-comments),
  swap usage, PR, CI-gate, merge.
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

## Stop conditions

- All approved rows from step 3 are resolved (merged, or hand-roll L/XL
  handed back as a proposal) → done, report what's left in `keep external`.
- User says stop, in chat or (headless mode) via a `.sovereignty-loop-stop`
  file at the repo root, checked each iteration.
- A PR's CI stays red after one fix-up attempt → pause on that row, leave
  the PR open, report it, don't force a merge or skip ahead silently.
- Any row not yet explicitly approved stays in the report, not the loop —
  there's no default path from "classified" to "worked."

## Rules

- No auto-merge default for anything in this skill — every row needs
  explicit sign-off before step 4, swap or hand-roll alike.
- Never relitigate an already-decided floor dependency — check
  RFC/ARCHITECTURE in step 0 before the audit runs, not after.
- Hand-roll size L/XL is never attempted inline — hand back a dedicated-repo
  proposal instead, per the tailscale-rs precedent.
- Same standing workflow as `parity-loop`/`repo-config`: PR against default
  branch, never a direct push; merge with a **merge commit** on green CI,
  never squash/rebase.
- Keep `RELEASE_NOTES.md` current if the repo has one — one entry per merged
  change from this loop.
- A "keep external" row is a logged decision, not an absence of one — don't
  let it silently vanish from the report on a re-run.

## Limitations

- Cross-repo search is keyword/grep-surfaced candidates plus judgment, not a
  guaranteed-complete scan — a platform repo solving this under different
  terminology can be missed. Worth a second pass by someone who knows the
  platform repos if the audit comes back suspiciously thin.
- The `rusty_<thing>` naming pattern is a decent first filter, not a
  guarantee — a name match still needs a source read before it counts as
  `covered`, and a genuine match can exist under an unrelated name.
  `references/rustymill-directory.md` is a snapshot and can drift from the
  live org; confirm rather than assume it's complete.
- crates.io lookups need network reachability; air-gapped/SIPR runs fall
  back to local manifest/source data only, so "purpose" may be thinner than
  a connected run would produce.
- Direct dependencies only by default. Transitive supply-chain exposure
  (what your dependencies depend on) needs a separate pass — `cargo tree` is
  a starting point — not scoped into this skill.
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

All three shell out to `gh`/`git`/`ripgrep` only — no extra dependencies.
They resolve paths relative to their own location.
