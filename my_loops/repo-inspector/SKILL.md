---
name: repo-inspector
description: Dry-run inspector for the RustyMill Cargo-workspace monorepo — ports dedupe-loop's clustering/classification (exact-duplicate / near-duplicate / diverged) and sovereignty-loop's external-dependency detection, adapted to work across crates in one workspace instead of across separate repos. Produces one repo-inspector-report.md, a duplication-clusters section (candidate crates, classification, completeness, recommended crate to extract) plus a sovereignty-findings section (external deps, internal RustyMill/baileyrd equivalent if any, a note to run parity-loop when none exists). v1 is report-only — no issues, no PRs, no code changes, no auto-merge — every row is left for human review. Trigger on requests to audit the RustyMill monorepo for duplicated crates, find crates worth hoisting into a shared dependency, or check the monorepo's external dependencies against the platform ecosystem. Checks repo-config has been applied first, same as the sibling loop skills.
version: 1.0.0
---

# repo-inspector

A standalone inspector for the RustyMill monorepo (one Cargo workspace,
`crates/*`, consolidating what used to be separate `baileyrd/rusty_*`
repos). It ports two things wholesale rather than reinventing them:

- **`dedupe-loop`'s clustering/classification logic** — group candidates by
  normalized name, then judge each cluster as exact/near-duplicate,
  convergent-but-diverged, or coincidental-similarity. `dedupe-loop` clusters
  across separate repo checkouts; this clusters across workspace members of
  one Cargo workspace instead — the unit changes from *repo* to *crate*, the
  classification logic doesn't.
- **`sovereignty-loop`'s external-dependency detection logic** — inventory a
  target's direct dependencies via `cargo metadata`, then search for
  existing internal coverage. `sovereignty-loop` searches a `PLATFORM_REPOS`
  list that has to be cloned; this workspace already has every sibling crate
  checked out locally under `crates/`, so the search is a local grep with no
  clone step.

**v1 is dry-run only.** Unlike its two source skills, this one has no step 4
— no issues filed, no branch, no PR, no merge, no code change. The run ends
at one report, `repo-inspector-report.md`, with two sections (format:
`references/repo-inspector-report-format.md`): duplication clusters and
sovereignty findings. Acting on any row — actually hoisting a cluster,
actually swapping a dependency, actually running `parity-loop` against an
external crate's API — is a separate, explicitly-approved follow-up this
skill only points at. That's also why there's no `LOOP_HARNESS_MODE`/auto
section the way the sibling loops have one: there's no unattended action
step here to gate.

## Run (when invoked)

**0. Scope**
- **Tooling preflight — do this before reporting that the loop has started.**
  1. Restore this skill's own script permissions:
     `chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true`. The sync that
     delivers a skill to a session doesn't preserve mode bits — every script
     can arrive as `0644`, which fails a step written
     `scripts/index_workspace_capabilities.sh` with `permission denied`
     ([baileyrd/skill_pack#1](https://github.com/baileyrd/skill_pack/issues/1)).
     Where the skill directory is read-only and `chmod` can't take, name the
     interpreter instead (`bash scripts/index_workspace_capabilities.sh`,
     `python3 scripts/find_clusters.py`): it doesn't need the bit.
  2. `command -v cargo` and `command -v python3`. Both scripts shell out to
     `cargo metadata`; without it, this skill cannot inventory the
     workspace at all — there's no manifest-parsing fallback the way
     `sovereignty-loop` has one, since a Cargo workspace's member list and
     per-crate dependency list are exactly what `cargo metadata` exists to
     give cleanly. Unlike the sibling loops, **no `gh` dependency at all** —
     v1 never touches issues, PRs, or CI, so there's nothing for it to do.
  3. `cargo metadata --no-deps` once, cheap, to confirm `WORKSPACE_ROOT` is
     actually a Cargo workspace root before either script runs against it.
     `--no-deps` is enough for both scripts here — neither needs the
     resolved dependency graph, only each member's own manifest-declared
     dependencies, and skipping resolution avoids a slow, possibly
     network-dependent full-graph solve on a workspace this size.
- **repo-config prerequisite**: run `repo-config`'s `scripts/audit.sh
  <WORKSPACE_ROOT>` first, same as `dedupe-loop`/`sovereignty-loop` do
  against their targets. If the standard governance-file score is
  low/missing, run `repo-config` before proceeding — skip only if a prior
  step in the same session already confirmed it.
- `WORKSPACE_ROOT` — the RustyMill monorepo checkout (the directory
  containing the workspace's own root `Cargo.toml`, i.e. the ancestor of
  `crates/`, not any one crate inside it).
- `FOCUS` (optional) — narrow either pass: a keyword for the duplication
  scan (skip step 2, hand `find_clusters.py`'s output through a filter for
  the term) or `--crate <name>` for the sovereignty scan (step 3) to audit
  one crate's dependencies instead of the whole workspace. A full scan on a
  workspace this size produces a lot to review at once; a focused run is the
  better default when the user already has something specific in mind.
- Check `WORKSPACE_ROOT`'s own `ARCHITECTURE.md`/ADRs for contracts already
  established (e.g. ADR-011's mechanism/policy split, if RustyMill has an
  equivalent) so this run doesn't propose re-doing an already-decided
  extraction or re-litigate an already-decided floor dependency — it's
  looking for *new*, not-yet-addressed findings.

**1. Build a per-crate capability index** — `scripts/index_workspace_capabilities.sh
<workspace-root>` runs `cargo metadata --no-deps` to enumerate workspace
members, then walks each member's source tree extracting module-level `//!`
doc comments plus public item signatures (`pub fn` / `pub struct` / `pub
trait` / `pub enum`) with their first doc line — one row per item, tagged by
crate name rather than repo name. Mechanical extraction, not judgment yet;
identical algorithm to `dedupe-loop`'s `index_capabilities.sh`, just scoped
to one workspace's members instead of one repo-path argument per invocation.

**2. Cluster candidates within the workspace, then classify** —
`scripts/find_clusters.py` takes the index and groups items by normalized
name/keyword overlap across *different crates* (a single crate matching
itself isn't duplication — same "at least two" rule `dedupe-loop` applies to
repos, applied here to crates). It surfaces candidate clusters, it doesn't
classify them. Read each cluster's actual source across the crates involved
and judge, same three buckets `dedupe-loop` uses:
- **exact/near-duplicate** — same functionality, reimplemented almost
  identically. Strong extraction candidate.
- **convergent-but-diverged** — same purpose, meaningfully different
  behavior (one crate's HTTP layer is sans-IO, another's bakes in a runtime;
  one supports a case the other doesn't). Still an extraction candidate, but
  the behavioral difference is a real decision — surface it, don't silently
  pick a winner.
- **coincidental-similarity** — similar names/keywords, different actual
  concerns (a `Client` for an MCP transport and a `Client` for a cloud-search
  upload session). Not an extraction candidate — log why and move on.

For every cluster that isn't `coincidental-similarity`, write a short
summary per candidate crate: what it does, and how complete/fleshed-out it
is — tested, handles edge cases, vs. a stub or subset. That's the evidence
the "recommended crate to extract" column needs, and skimming
`find_clusters.py`'s 80-character doc preview isn't enough to write it —
read the actual source.

**3. Sovereignty pass** — `scripts/scan_workspace_sovereignty.sh
<workspace-root> [--crate <name>]` runs `cargo metadata --no-deps` to
inventory every crate's direct, non-dev/build, non-path dependencies
(a dependency also satisfied by another workspace member by registry name is
excluded — that's intra-workspace, not external), aggregates by dependency
name across the workspace, then greps every *other* crate's source/manifest/
README for that name — a candidate list for internal coverage, not a
verdict. `Cargo.lock` is excluded from the search on purpose: a lockfile
reflects the resolved *transitive* graph, so a popular dependency shows up
in nearly every crate's lockfile regardless of whether that crate does
anything with it, and searching it drowns real hits in noise (confirmed in
testing against this exact workspace).

For each dependency, read the grep hits and classify:
- **covered** — a workspace crate (or, per `references/platform-directory.md`,
  a `Rusty-Mill/*`/`baileyrd/rusty_*` repo not yet merged into this
  monorepo) already does this. Name it.
- **partial** — internal coverage exists but doesn't reach the dependency's
  full surface (e.g. `rusty_request` covers `reqwest`'s GET path but not its
  POST path yet). Say what's missing.
- **none found** — no internal equivalent surfaced. This is the row that
  gets **a note recommending `parity-loop` be run against that external
  crate's API** to scope and build a sovereign replacement — this skill
  doesn't run `parity-loop` itself, it only flags where running it would be
  worth it.

The `rusty_<thing>` naming pattern (`rusty_json` ~ `serde_json`, `rusty_tls`
~ `rustls`, and so on — `references/platform-directory.md` has the current
snapshot) is a useful first filter for `covered`/`partial`, same caveat
`sovereignty-loop` states: it's a heuristic, not proof. Confirm by reading
the source before writing `covered`.

**4. Report** — write `repo-inspector-report.md` at `WORKSPACE_ROOT`'s root
(format: `references/repo-inspector-report-format.md`), both sections
together: duplication clusters (step 2) and sovereignty findings (step 3).
This is the whole deliverable — **no issues, no branch, no PR, no code
change, no auto-merge**. Every cluster and every dependency row is left for
per-cluster / per-row human review, same spirit as the checkpoint the
sibling loops hold before their own step 4, except here there's no step 4
to unblock — reviewing the report *is* the next action, and it belongs to
whoever reads it next.

**5. Wrap-up retro** — regardless of how the run ended (full report written,
narrowed by `FOCUS`, or stopped mid-way), run a `meta/skill-retro` pass on
`repo-inspector` itself, grounded in this run: did step 2's clustering and
classification hold up on a monorepo of this size, did step 3's
Cargo.lock-noise exclusion (or any other filter) need adjusting, was the
report's "recommended extraction" / "run parity-loop" guidance the right
level of actionable? Read-only, safe to run unattended; applying anything
`skill-retro` finds is a separate, explicitly-approved follow-up.

## Stop conditions

- `repo-inspector-report.md` written, both sections populated → done.
- Tooling preflight fails (`cargo`/`python3` missing, or `WORKSPACE_ROOT`
  isn't a Cargo workspace root) → halt before starting either pass and say
  what's blocking.
- User says stop, in chat or (headless mode) via a `.repo-inspector-stop`
  file at `WORKSPACE_ROOT`'s root, checked before each of steps 1–4.

## Rules

- **v1 never modifies code, opens an issue, or files a PR.** The report is
  the entire output. A future version that acts on approved rows is out of
  scope for this skill as written — don't improvise one.
- A duplication cluster needs items from **at least two different crates**
  to count — one crate doing something on its own is just an
  implementation, not a hoist candidate, same rule `dedupe-loop` applies to
  repos.
- A dependency needs an actual source read before its row says `covered` —
  a `rusty_<thing>` name match or a keyword grep hit is a candidate, not
  confirmation.
- Never propose relitigating an already-decided floor dependency or an
  already-decided extraction — check `WORKSPACE_ROOT`'s own
  ARCHITECTURE/ADR docs in step 0 before either pass runs.
- A `coincidental-similarity` cluster and a `keep external`-shaped
  (`covered`-with-no-action-taken) dependency both stay logged in the
  report rather than silently dropped, so a later re-run doesn't re-surface
  either as new.

## Limitations

- Cluster and dependency detection are keyword/structural matching plus
  judgment — same caveat as `dedupe-loop`/`sovereignty-loop`'s search steps.
  It can miss duplication or coverage hiding under unrelated names, and it
  can surface coincidental matches that aren't real findings; step 2's
  generic-name clusters (`fn: new`, `fn: get`, `fn: parse`, and similarly
  the `module: src/lib.rs` cluster every crate trivially joins) are the
  expected, high-volume shape of that noise on a workspace this size —
  triage them as `coincidental-similarity` rather than reading each one as
  a real signal.
- No clone path, and deliberately none needed: unlike `sovereignty-loop`'s
  `scan_platform_repos.sh`, `scan_workspace_sovereignty.sh` never shells out
  to `gh repo clone` — every sibling crate is already local under
  `crates/`. A `references/platform-directory.md` repo that hasn't been
  migrated into this monorepo yet is still a manual clone if its source
  needs reading to confirm coverage.
- `references/platform-directory.md` is a snapshot and can drift from the
  live namespaces (see its own header) — confirm rather than assume it's
  complete, same caveat `sovereignty-loop` states.
- Reconciling a `convergent-but-diverged` cluster is a design decision this
  skill surfaces in the report, not one it resolves — same as
  `dedupe-loop`'s step 4.1, minus the step 4 that would act on the answer.
- Direct dependencies only, same scope `sovereignty-loop` uses — this
  doesn't run `sovereignty-loop`'s step 2.5 reachability check
  (`cargo tree -i <crate>`) since v1 never classifies a row as *eliminable*
  or removes anything; a `covered` row here is "worth investigating," not
  "safe to delete." Run `sovereignty-loop` itself (or its reachability
  check specifically) before treating any row as a removal.
- No `LOOP_HARNESS_MODE`/auto mode: there is no action step to gate, so
  nothing here proceeds unattended past the report — every finding is
  reviewed at the pace the reader chooses.

## Scripts

Neither script shells out to `gh` — this is the one loop-family skill where
that's true throughout, not just for a subset of scripts (see step 0). Both
require `cargo` and `python3` (stdlib only); `scan_workspace_sovereignty.sh`
also uses `ripgrep` when present, falling back to `grep`.

| Script | Purpose | Args |
| --- | --- | --- |
| `index_workspace_capabilities.sh` | Extracts module docs + public item signatures from every workspace member into a flat, crate-tagged index | `<workspace-root> [--out <file>]` |
| `find_clusters.py` | Groups indexed items by normalized name/keyword across crates, filters to clusters spanning ≥2 crates | `<index.tsv> [index2.tsv ...]` |
| `scan_workspace_sovereignty.sh` | Inventories each crate's direct external dependencies via `cargo metadata`, then greps the rest of the workspace for internal-coverage candidates | `<workspace-root> [--crate <name>]` |

`find_clusters.py` is a near-verbatim port of `dedupe-loop`'s script of the
same name (the clustering algorithm doesn't change, only the unit — crate
instead of repo). `index_workspace_capabilities.sh` and
`scan_workspace_sovereignty.sh` are new: they wrap `cargo metadata` to
enumerate workspace members instead of taking one repo-path/`PLATFORM_REPOS`
list per invocation, since a single Cargo workspace already knows its own
member list.
