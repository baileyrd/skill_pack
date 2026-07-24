# dependency-audit.md format

Written to the target repo's root (or wherever the user prefers) at the end
of step 3, before anything is filed as an issue. One table, one row per
direct dependency that survived step 0's floor-dependency exclusions.

| Dependency | Purpose | Classification | Internal candidate | Size | Recommended action | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `rand` | CSPRNG for token generation | covered | `rustils::platform::random` | — | Swap to internal | rustils already wraps `getrandom` per-platform; drop the direct dep |
| `reqwest` | HTTP client for the update checker | partial | `rustils::net::http` (GET only) | — | Extend rustils' client + swap | Update checker needs POST too; rustils' wrapper doesn't have it yet |
| `once_cell` | Lazy statics | hand-roll candidate | none found | S | Hand-roll if approved | std's `OnceLock` may already cover this — check MSRV before building anything |
| `tokio` | Async runtime | keep external | — | — | Keep | Foundational, no sovereignty case strong enough to justify hand-rolling an async runtime |

Columns:
- **Dependency** — crate name as it appears in the manifest.
- **Purpose** — one line, from the manifest description or the call sites
  themselves if the network can't reach crates.io.
- **Classification** — `covered` / `partial` / `hand-roll candidate` /
  `keep external`, per step 3's four buckets.
- **Internal candidate** — which platform repo/module surfaced in step 2, if
  any. Blank for `hand-roll candidate` and `keep external`.
- **Size** — S/M/L/XL, only populated for `hand-roll candidate` rows. Routes
  S/M into the loop (if approved) and L/XL into a dedicated-repo proposal
  instead of an inline attempt.
- **Recommended action** — what step 4 would do if this row gets approved.
  Not a commitment — the user picks which rows actually proceed.
- **Notes** — anything the other columns don't capture: partial-coverage
  gaps, MSRV/version constraints worth checking before hand-rolling,
  ambiguity in what the dependency is actually used for.

Report the table before filing anything — this is the sign-off point. A row
with no action taken this run (declined, deferred) stays in the table on the
next audit rather than disappearing, so "keep external" reads as a decision
on record, not a gap in coverage.
