# Release Notes

sovereignty-loop lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/sovereignty-loop),
pushed direct to `main` (no PR workflow yet) — this log tracks commits instead of
PRs, the same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.4.0 — Don't depend on an executable bit the sync drops
**2026-08-17**

- **Added:** a first item in step 0's tooling preflight documenting how to restore the executable bit —
  `chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true`, with naming the
  interpreter (`bash scripts/x.sh`) as the fallback where the skill directory
  is read-only.
- **Why ([#1](https://github.com/baileyrd/skill_pack/issues/1)):** the sync
  that delivers a skill to a session doesn't preserve mode bits. Measured in a
  live session: **31 of 31 shebanged scripts across all ten skills arrive as
  `0644`**, so any step written `scripts/x.sh` fails with `permission denied`.
  The issue had recorded this as an occasional symptom; it is universal.
- **Scope note:** this documents a recovery rather than fixing the sync, which
  lives outside this repo. #1 stays open.

---

## v1.3.0 — Tooling preflight and an infrastructure stop condition
**2026-08-16**

- **Added:** a **tooling preflight** as the first bullet of step 0 — `command
  -v gh`, one cheap API read, and a note on which CI-status mechanism the
  target uses. The bullets it sits above all validate the *target*; this one
  validates the loop's own execution environment, which is what actually fails
  first when it fails.
- **Added:** an **infrastructure stop condition** — an unreachable or
  rate-limited GitHub API halts cleanly and reports three lists (completed, in
  flight with branch and PR named, never started) plus the retry path. Every
  other stop condition in this skill is about work state; this is the one where
  partial state exists and something can be stranded unnamed.
- **Added:** the preflight names the two CI-status traps by their symptom:
  a repo reporting via Actions checks returns `total_count: 0` from the
  commit-status endpoint (not evidence CI is missing), and runs associate to
  PRs by *branch*, so a stale run from an earlier PR on a reused branch can
  read as a pass for code it never ran against. Match by `head_sha`.
- **Documented:** which scripts require `gh`, in both the Scripts section and
  Limitations. All three (`next_issue.sh`, `watch_and_merge.sh`,
  `scan_platform_repos.sh`) do; the fallback to the GitHub MCP tools is a
  substitution the run makes deliberately, since the scripts have no MCP path
  of their own. Limitations previously said nothing about `gh` at all.

**Evidence, stated honestly:** only `issue-loop` actually failed this way in a
live run — `gh` absent in a web session, so its scripts couldn't run and the
loop had to be re-derived mid-flight. The gap here was confirmed structurally
by reading this skill, not by a failing run of it. The change is documentation
only — no behavior changes and no scripts touched — so the cost of being wrong
is low, but it isn't the same grade of evidence
([#61](https://github.com/baileyrd/skill_pack/issues/61)).

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
