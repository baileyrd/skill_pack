# Release Notes

sovereignty-loop lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/sovereignty-loop),
pushed direct to `main` (no PR workflow yet) — this log tracks commits instead of
PRs, the same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.2.0 — Require a reachability check before calling a dependency removable
**2026-08-15**

- **Added: step 2.5, a required reachability check.** Before any dependency is
  classified `covered`/`partial`/`hand-roll candidate`, the loop now runs
  `cargo tree -i <crate>` (with `pipdeptree --reverse` / `npm ls` equivalents
  given) and reads the full reverse tree. A crate anything else in the graph
  reaches is `keep external` however small its use in the target looks; when
  the other path is an internal repo, that repo becomes the follow-up — usually
  the higher-value finding.
- **Added:** a required **Reachable via** column in
  `references/dependency-audit-format.md`, populated on every row including
  clean ones (`target only`). A blank cell is indistinguishable from a skipped
  check, which is the failure mode this guards against.
- **Why:** auditing `rusty_tokio`, `syn`/`quote`/`proc-macro2` were classified
  as its only removable dependency. A complete hand-rolled replacement for the
  proc-macro crate was built and verified — then `cargo tree -i syn` showed all
  three still arriving via `platform` → `thiserror` → `thiserror-impl`, with
  the lockfile unchanged at 38 packages either way. The work was discarded
  (baileyrd/rusty_tokio#268, PR #270). One command before classifying would
  have caught it, and would have pointed straight at the single `thiserror`
  derive in `rustils` that was the actual lever (baileyrd/rustils#128).
- **Changed:** the "direct dependencies only" limitation now separates what
  step 2.5 fixes (a wrong verdict on a named dependency) from what it doesn't
  (surfacing risky transitive dependencies nobody names — still a separate
  exercise), plus a note that the check says whether another path exists, not
  how hard it is to change.
- **Fixed:** `references/platform-directory.md` refreshed against the live
  namespaces — see the parity-loop/issue-loop/dedupe-loop notes for the same
  fix; the file is shared verbatim across all four.

## v1.1.1 — Declare jq, and split required from optional
**2026-08-15**

- **Fixed:** the Scripts note said "shell out to `gh`/`git`/`ripgrep` only —
  no extra dependencies." `ripgrep` was named but **`jq`** wasn't, despite
  `next_issue.sh:31` piping through it unguarded. The note now separates the
  two by kind: `jq` required, `ripgrep` optional (`scan_platform_repos.sh:50`
  guards on `command -v rg` and falls back to `grep`).
- Found by `docs-loop` row 5.

## v1.1.0 — Wire skill-retro into wrap-up (step 5)
**2026-08-13**

- **Added:** step 5, "Wrap-up retro" — after step 4 ends (rows swapped,
  hand-rolled, some deferred, or stopped mid-way), runs a
  `meta/skill-retro` pass on `sovereignty-loop` itself, grounded in this
  run's step 3 classification and step 4 hand-roll sizing calls. Read-only,
  safe unattended in either harness mode; applying anything found is a
  separate, explicitly-approved follow-up.
- Part of a batch wiring the same convention into every remaining
  `my_loops` skill, following the pattern first used on
  `my_loops/rust-migration` v1.1.0 and `meta/skill-retro`'s own step 6.

## v1.0.0 — Initial versioned release
**2026-08-12**

- **Added:** `version: 1.0.0` to `SKILL.md` frontmatter and this file — first
  formally versioned cut of the skill. No behavior change; establishes the
  baseline the next entry will diff against.
