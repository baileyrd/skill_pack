# duplication-audit.md format

Written at the end of step 3, before any issues are filed. One table, one
row per candidate cluster that survived step 2's grouping.

| Capability | Repos (local name) | Classification | Behavioral differences | Reconciliation size | Hoist target | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| HTTP client wrapper | rust-shell (`shell::net::fetch`), nexus-forge (`forge::http_client`) | exact/near-duplicate | none material | S | rustils | Both wrap `reqwest` with the same retry-once-on-5xx behavior |
| Config loader | rust-shell (`shell::cfg::load`), tailscale-rs (`config::read`), pacifist-score (`load_config`) | convergent-but-diverged | rust-shell supports env-var overrides, the other two don't | M | rustils | Decide: overrides become a default, an opt-in flag, or stay rust-shell-only |
| `Client` struct | nexus-forge (`forge::http_client::Client`), replay-watcher (`uploader::Client`) | coincidental-similarity | — | — | — | Same name, unrelated concerns (HTTP vs. ballchasing.com upload session) — not a hoist candidate |

Columns:
- **Capability** — a short label for what the cluster does, not a symbol
  name (symbol names differ per repo by definition).
- **Repos (local name)** — every repo in the cluster, with its own local
  name for the thing, so the eventual adoption PRs know what they're
  replacing.
- **Classification** — `exact/near-duplicate` / `convergent-but-diverged` /
  `coincidental-similarity`, per step 2's three buckets.
- **Behavioral differences** — populated only for `convergent-but-diverged`
  rows; this is what step 4.1's design question is actually about.
- **Reconciliation size** — S/M/L/XL, blank for `coincidental-similarity`.
  A rough gut call for scoping the hoist-plus-adopt work, not a commitment.
- **Hoist target** — usually the run's configured `HOIST_TARGET`, but call
  out here if a specific cluster genuinely belongs somewhere else.
- **Notes** — anything else worth carrying into the issues: which repo's
  version is furthest along, test coverage gaps, a repo that might want to
  opt out even after the hoist lands.

Report the table before filing anything. A `coincidental-similarity` row
stays in the table as a logged non-candidate rather than disappearing, so a
later re-scan doesn't re-surface it as new.
