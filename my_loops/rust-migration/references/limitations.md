# rust-migration: limitations

Read this before treating a finished run as proof of completeness, or when
deciding whether this loop fits a job.

- Step 1's extraction is judgment plus tooling, not a formal proof of
  completeness — a capability with no test, no doc, and an obscure code
  path can still be missed on a first pass. The step-1 report is the
  checkpoint to catch that; `check_manifest_coverage.sh` only verifies that
  *rows already in the manifest* reach a terminal state, not that the
  manifest itself is complete. Treat a "coverage: 100%" result as "every
  known row is resolved," not "nothing was missed."
- The RustyMill sibling check is keyword/grep-surfaced candidates plus
  judgment, same as the search steps in `sovereignty-loop`/`dedupe-loop` —
  it can miss a match hiding under different naming, and
  `references/platform-directory.md` can drift from the live org; confirm
  rather than assume it's complete.
- Assumes CI is configured as a required status check on the default branch;
  the "on green CI" gate only actually gates merges if branch protection
  requires it (same caveat as repo-config).
- Three of the four scripts require `gh` on `PATH` and authenticated
  (`check_manifest_coverage.sh` is the exception). Step 0's preflight checks
  for it and routes to the GitHub MCP tools when it's missing, but that
  fallback is a documented substitution the run has to make deliberately —
  the scripts themselves have no MCP path.
- Built for a single source/target pair per run. A multi-service migration
  run one service at a time means one capability manifest per service,
  reconciled by hand into an overall picture if the user wants one.
- The parity test in step 3.6 checks behavioral equivalence for what the
  test asserts — it's only as strong as the test written. Safety-relevant
  capabilities are worth a spot-check beyond the automated gate.
