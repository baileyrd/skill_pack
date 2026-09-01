# repo-inspector-report.md format

Written at the end of the run, before anything else — this **is** the
deliverable (see SKILL.md's "Run" section: v1 is dry-run only, so there is
no step 4/5 action phase the way `dedupe-loop`/`sovereignty-loop` have; this
report is where the loop ends). One file, two sections, each a table.
Combines `dedupe-loop`'s `duplication-audit-format.md` and
`sovereignty-loop`'s `dependency-audit-format.md`, adapted from "one row per
repo-pair/target-dependency" to "one row per crate-cluster/workspace-
dependency" since this skill operates inside a single Cargo workspace.

## Section 1 — Duplication clusters

One row per candidate cluster that survived clustering + classification
(step 2).

| Cluster | Candidate crates | Classification | What each candidate does / completeness | Recommended extraction |
| --- | --- | --- | --- | --- |
| HTTP/1.1 message layer | `rusty_http`, `rusty_request` (internal `http`-shaped helper module) | convergent-but-diverged | `rusty_http` is the sans-IO HTTP/1.1 layer + `Url` type, feature-complete with sync/async adapters. `rusty_request`'s helper is a thin subset (headers + status parsing only, no chunked-transfer support) used internally by its async client. | `rusty_http` already is the shared crate — recommend `rusty_request` depend on it directly and delete its local subset, rather than a new extraction |
| ANSI/VT escape parsing | `rusty_term` (`src/vt/*`), `rusty_ansi` | exact/near-duplicate | Both parse CSI/OSC sequences; `rusty_ansi` is the newer, zero-allocation `no_std` core, `rusty_term`'s copy predates it and is feature-equivalent but allocates. | Extract to `rusty_ansi` (already a workspace member) — `rusty_term` adopts it, deletes its own parser |
| `Client` struct | `rusty-mcp` (`transport::Client`), `rusty_search-cloud` (`upload::Client`) | coincidental-similarity | Same name, unrelated concerns (MCP transport vs. a cloud-search HTTP session) — not a duplication candidate. | — |

Columns:
- **Cluster** — a short label for what the cluster does, not a symbol name
  (symbol names differ per crate by definition; see step 2's clustering).
  **One row per mechanically-distinct cluster — don't fold several of
  `find_clusters.py`'s separate clusters (different normalized item names)
  into one narrative row just because they're thematically related.**
  Confirmed costly in practice: a report once combined three unrelated
  clusters — an HMAC construction, an RSA key type, and a `BigUint`
  type — under one row labeled "hand-rolled crypto primitives" for
  readability. `implementation-merge`, a real downstream consumer of this
  report, had to split that row back into three separate merge candidates
  itself before it could act on any of them. Group related rows under a
  shared prose theme in the surrounding write-up if useful, but keep the
  *rows* 1:1 with actually-distinct capabilities.
- **Candidate crates** — every workspace crate in the cluster, with the
  module/item local to each, so a later extraction decision (a separate,
  explicitly-approved follow-up — see SKILL.md Rules) knows what it would be
  replacing.
- **Classification** — `exact/near-duplicate` / `convergent-but-diverged` /
  `coincidental-similarity`, the same three buckets `dedupe-loop` uses.
- **What each candidate does / completeness** — read the actual source (not
  just the doc-comment preview `find_clusters.py` prints) and summarize per
  candidate: what it does, and how complete/fleshed-out it is — has tests,
  handles edge cases, or is a stub/subset. This is what "recommended crate to
  extract" in the next column is actually judged from.
- **Recommended extraction** — populated only for `exact/near-duplicate` and
  `convergent-but-diverged` clusters (never `coincidental-similarity`, which
  isn't a duplication candidate at all). Decision rule: a cluster reaches
  this table only once its usage count is **≥ 2** workspace crates (the same
  threshold `find_clusters.py` already applies to form a cluster at all — see
  step 2), so every non-`coincidental-similarity` row here is, by that rule,
  a candidate for extraction into a shared crate. Name which existing
  workspace crate should absorb the others where one candidate is already
  the more complete/canonical implementation (as in the `rusty_http` example
  above); only propose a genuinely *new* crate when no existing candidate is
  a reasonable host.
- For `convergent-but-diverged` rows, note the behavioral difference inline
  in the completeness column — same information `dedupe-loop` puts in a
  dedicated "Behavioral differences" column, folded in here since this
  report has no action step 4.1 to hand it to.

A `coincidental-similarity` row stays in the table as a logged non-candidate
rather than disappearing, so a later re-run of this skill doesn't re-surface
it as new.

## Section 2 — Sovereignty findings

One row per external (non-workspace, non-dev/build) dependency that survived
step 3's inventory.

| Dependency | Used by (crates) | Internal equivalent | Notes |
| --- | --- | --- | --- |
| `serde` / `serde_json` | `rusty_lsp`, `rusty_jinja` | `rusty_serde` (workspace member — dependency-free `Serialize`/`Deserialize` + JSON) | `rusty_search`'s own CHANGELOG documents having already migrated off `serde`/`serde_json` onto `rusty_serde` for exactly this reason — same swap available to `rusty_lsp`/`rusty_jinja` |
| `reqwest` | `rusty_proxmox` | none found in-workspace; `rusty_request` (workspace member) is close but currently JSON-response-only | Partial — extend `rusty_request` then swap, or note the gap and run `parity-loop` against `reqwest`'s remaining surface first |
| `sqlx` | `rusty-db-sqlite`, `rusty-db-postgres`, `rusty-db-mysql` | none found; `rusty_rusqlite`/`rusty_sqlite` cover SQLite only, no Postgres/MySQL sovereign driver exists yet | **No internal equivalent — recommend running `parity-loop` against `sqlx`'s API surface** to scope a sovereign replacement, starting with whichever backend is highest-value |
| `tokio` (real, not `rusty_tokio`) | `rusty_search-tantivy` (dev-dep of a dep, confirm before acting) | `rusty_tokio` (workspace member — hand-rolled async runtime) | Confirm this is a direct dependency, not `tantivy`'s own transitive pull, before treating as a finding |

Columns:
- **Dependency** — crate name as it appears in the manifest (`cargo
  metadata`'s `dependencies` list, non-dev/build, non-path — see step 3).
- **Used by (crates)** — every workspace crate that declares it directly.
- **Internal equivalent** — the workspace crate (or, failing that, a
  `Rusty-Mill/*`/`baileyrd/rusty_*` repo from
  `references/platform-directory.md` not yet migrated into this workspace)
  that already covers the same capability, per step 3's grep-surfaced
  candidates plus a source read. `none found` if nothing surfaced.
- **Notes** — anything the other columns don't capture: partial-coverage
  gaps, a naming-heuristic hit that still needs a source read to confirm,
  ambiguity about direct vs. transitive use. **When "Internal equivalent" is
  `none found`, this column must say so explicitly and note that
  `parity-loop` is the recommended next step** to assess and close that gap
  against the external crate's own API surface — this skill doesn't run
  `parity-loop` itself (v1 is report-only), it only flags where running it
  would be worth it.

A dependency with a confirmed internal equivalent is not automatically
`covered` in the `sovereignty-loop` sense — this report doesn't classify a
swap-to-internal action the way `sovereignty-loop`'s four-bucket
classification does, since v1 takes no action. It surfaces the finding for
per-row human review; deciding whether a swap-to-internal PR is worth it
(and running `sovereignty-loop` itself, or `parity-loop` for a hand-roll
where none exists) is the explicit follow-up.

Report both sections together in one `repo-inspector-report.md` before
anything else happens — this is the whole deliverable, not a checkpoint on
the way to one.
