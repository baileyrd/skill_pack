# gap-analysis.md format

Written to the target repo's root (or wherever the user prefers) at the end of
step 1, before any issues are created. One table, one row per surviving
candidate after judgment has been applied.

| Symbol | Category | Source | Platforms | Reference | Existing RustyMill impl | Breaking? | Est. size | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `pipe2` | fn | diff | linux | `libc::pipe2` | — | no | S | Needs `O_CLOEXEC`/`O_NONBLOCK` flag support |
| `sockaddr_un` | type | diff | both | `libc::sockaddr_un` | — | no | S | Plain struct, no logic |
| `getrandom` | fn | roadmap | linux | `libc::getrandom` | — | no | M | Roadmap item "randomness" — existing `rand_bytes` helper could wrap it, check overlap first |
| `open` flags arg | fn (existing) | spec | both | `libc::open` | — | **yes** | M | Current `open()` doesn't accept `O_TMPFILE` — would need a signature change |
| socket options parsing | fn | diff | both | `libc::setsockopt` | `rusty_wire` (has a similar option-parsing table) | no | S (was M) | Port and adapt rather than write fresh — check `rusty_wire`'s licensing/attribution expectations, if any |

Columns:
- **Symbol** — the exact name from the reference surface.
- **Category** — `fn` / `type` / `const` / `macro`. `fn (existing)` marks a
  function that already exists in the target but is missing capability
  (flags, error cases) rather than being wholly absent — these are the ones
  most likely to be `Breaking? yes`.
- **Source** — which of step 1's three assessment paths produced this row:
  `roadmap` (audited against an existing hand-curated scope doc), `diff`
  (mechanical `cargo public-api` comparison), or `spec` (read directly from a
  spec/man page/doc with nothing comparable to diff). Lets anyone reading the
  table later know what to check it against — a `roadmap`-sourced row that
  disagrees with the roadmap itself is a signal to go reconcile, not to
  re-derive from scratch.
- **Platforms** — which of the in-scope platforms the gap applies to. A gap
  that's Linux-only doesn't need a Windows label even if the run covers both.
- **Reference** — a locator back to the reference surface (crate path, man
  page section, roadmap item, spec URL) so the issue and PR can cite it.
- **Existing RustyMill impl** — which sibling repo, if any, already
  implements this gap (from `scan_rustymill_repos.sh`). Blank/— means either
  nothing was found or nothing was worth checking for this row; either way,
  step 3 re-checks before assuming there's genuinely nothing before
  hand-rolling. A populated cell routes step 3 toward porting instead of
  writing from scratch, and usually shrinks **Est. size**.
- **Breaking?** — `yes` only when closing the gap requires changing an
  *existing* public signature or behavior. New additions are always `no`.
  This column is what step 3 checks before implementing unattended.
- **Est. size** — S/M/L, rough gut call. Used to keep issues small in step 2;
  an L candidate is a signal to split it into multiple rows/issues before
  filing rather than after.
- **Notes** — anything a future issue/PR author needs that the other columns
  don't capture: overlap with existing code, ambiguity in the reference,
  platform quirks, "confirm this isn't already handled by X."

Report the table to the user (or the log, in headless mode) before step 2 runs
— it's the natural point to trim scope, or reconcile something against the
roadmap, before 40 issues get filed.
