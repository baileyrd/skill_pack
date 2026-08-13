# capability-manifest.md format

Written to the target repo's root (or wherever the user prefers) at the end
of step 1, before any issues are created, and kept updated through step 3 as
the running source of truth for coverage — it isn't a one-shot artifact.
One table, one row per capability.

This file *is* the boundary contract in concrete form: the **Status**
column has exactly three legal values, and moving a row to the third one is
gated the way "The boundary contract" section of `SKILL.md` describes.

| ID | Capability | Category | Source | Existing RustyMill impl | Status | Reason (if OUT-OF-SCOPE) | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C001 | `POST /users` validates email format before insert | behavior | test | — | REQUIRED | | |
| C002 | `--dry-run` CLI flag suppresses all writes | interface | docs+test | — | DONE | | PR #14, test `test_dry_run_suppresses_writes` |
| C003 | `RETRY_BACKOFF_MS` env var, default 500 | config | code | `rusty_http` (has a backoff helper) | REQUIRED | | |
| C004 | Legacy `/v0/ping` endpoint (superseded by `/v1/health`, unused per access logs — confirmed with the user) | interface | code | — | OUT-OF-SCOPE | User confirmed 2026-08-13: `/v0/ping` has zero traffic in 90d access logs and no external doc references it; dropped rather than ported. | |
| C005 | SIGTERM triggers graceful drain of in-flight requests | behavior | code | — | REQUIRED | | |

Columns:
- **ID** — stable short ID (`C001`, `C002`, ...), assigned once and never
  reused, even if a row is later split or merged — issues and commit
  messages reference this ID, so it needs to survive manifest edits.
- **Capability** — precise enough to write an issue and a parity test
  against. Not "handles config" — "`RETRY_BACKOFF_MS` env var, default
  500ms, applied to outbound HTTP retries."
- **Category** — `interface` / `config` / `behavior`, per `SKILL.md` step
  1's extraction categories.
- **Source** — how this row was found: `interface` (public API/CLI/route
  surface), `code` (behavior read directly from implementation), `test`
  (a passing test in the source repo encodes this), `docs` (README/docs/
  CHANGELOG). Multiple sources are common (`docs+test` above) — list all
  that apply, since a row backed by both a doc and a test is stronger
  evidence than one inferred from code alone.
- **Existing RustyMill impl** — which sibling repo, if any, already
  implements something close to this capability (from
  `scan_platform_repos.sh`). Blank/— means nothing found, or nothing worth
  checking for this row; step 3 re-checks before hand-rolling regardless.
- **Status** — exactly one of:
  - `REQUIRED` — the default for every row on creation. Not yet migrated.
  - `DONE` — migrated, with parity evidence in the **Evidence** column.
    `check_manifest_coverage.sh` requires this column non-empty for a
    `DONE` row — a status flip with no evidence doesn't pass the gate.
  - `OUT-OF-SCOPE` — the *only* other terminal state, and it requires the
    **Reason** column filled in, explicitly attributed to a user decision
    (a date and a summary of what was confirmed and by whom, as in C004
    above). A row Claude wants to mark `OUT-OF-SCOPE` on its own judgment
    stays `REQUIRED` and gets raised to the user instead — see `SKILL.md`'s
    boundary contract.
- **Reason (if OUT-OF-SCOPE)** — required and only meaningful for
  `OUT-OF-SCOPE` rows; leave blank for `REQUIRED`/`DONE`.
- **Evidence** — required and only meaningful for `DONE` rows: the merged
  PR and the specific parity test name that demonstrates the behavior
  matches. "Compiles" or "no test failures" alone is not evidence for this
  column — name the test that specifically covers this capability.

`scripts/check_manifest_coverage.sh` parses this table mechanically: every
row must be `DONE` (Evidence non-empty) or `OUT-OF-SCOPE` (Reason
non-empty) for the check to pass. A `REQUIRED` row, or a `DONE`/`OUT-OF-SCOPE`
row missing its required column, fails the check and is printed by name —
this is what step 4 runs before the migration can be reported finished.
