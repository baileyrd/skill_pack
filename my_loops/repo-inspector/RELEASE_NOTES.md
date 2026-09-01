# Release Notes

repo-inspector lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/repo-inspector),
same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.0.0 — Initial release
**2026-09-01**

- **Added:** first cut of `repo-inspector`, a standalone skill for the
  RustyMill monorepo. Ports `dedupe-loop`'s clustering/classification logic
  (exact-duplicate / near-duplicate / diverged) and `sovereignty-loop`'s
  external-dependency detection logic, both adapted from cross-repo to
  intra-workspace: the unit of comparison changes from *repo* to *crate*
  within one Cargo workspace, and the sovereignty search needs no clone step
  since every sibling crate is already local under `crates/`.
- **Scope:** v1 is dry-run only — no issues filed, no branch, no PR, no code
  change, no auto-merge. The run produces one `repo-inspector-report.md`
  with two sections (duplication clusters, sovereignty findings) and stops
  there; acting on any row is a separate, explicitly-approved follow-up
  (hoist the cluster by hand or via `dedupe-loop`, swap or hand-roll a
  dependency via `sovereignty-loop`/`parity-loop`).
- **New scripts:** `index_workspace_capabilities.sh` and
  `scan_workspace_sovereignty.sh` both wrap `cargo metadata --no-deps` to
  enumerate workspace members instead of taking a repo-path or
  `PLATFORM_REPOS` list per invocation. `find_clusters.py` is a near-verbatim
  port of `dedupe-loop`'s script of the same name — the clustering algorithm
  is unchanged, only the "at least two different X" unit (crate, not repo).
- **Reused as-is:** `references/platform-directory.md`, copied verbatim from
  `dedupe-loop`/`sovereignty-loop` (identical across all skills that need
  it) — the `Rusty-Mill/*` and `baileyrd/rusty_*` namespace convention for
  the sovereignty pass's fallback when no workspace member covers a
  dependency yet.
- **Verified against the real target**: both scripts were run end-to-end
  against `Rusty-Mill/rusty_mill` while building this skill, not just
  written and assumed correct.
  `index_workspace_capabilities.sh` indexed all ~115 workspace members
  (8,082 rows) in under 7 seconds. `find_clusters.py` on that index reproduced
  the same noise profile `dedupe-loop` documents for its own script — a
  large `module: src/lib.rs` cluster every crate trivially joins, and
  generic-name clusters (`fn: new`, `fn: get`, `fn: parse`) — now called out
  explicitly in SKILL.md's Limitations as the expected shape of that noise
  on a workspace this size, rather than left to be rediscovered.
  `scan_workspace_sovereignty.sh` initially used full `cargo metadata`
  (triggering a slow, network-dependent dependency-graph resolution) and
  piped a large per-dependency grep result straight into `head -20`, which
  SIGPIPE'd the writer under `set -o pipefail` and aborted the whole scan
  after the very first (and most common) dependency — both fixed before
  shipping: `--no-deps` (the script only needs each manifest's own declared
  dependencies, not the resolved graph) and capturing to a variable before
  slicing with `head`. A real run also surfaced that ripgrep's `toml` file
  type matches `Cargo.lock` by name, which drowned genuine source hits in
  transitive-lockfile noise for any popular dependency — `Cargo.lock` is now
  excluded explicitly. With that fixed, a real run against `rusty_json`
  surfaced a genuine, verifiable finding: `rusty_search`'s own CHANGELOG
  documents having already migrated off `serde`/`serde_json` onto
  `rusty_serde` (a workspace member) for the same reason this skill exists.
