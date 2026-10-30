# parity-loop: limitations

Read this before treating a finished run as proof of completeness, or when
deciding whether this loop fits a job.

- **Why the `new-subsystem` stop-and-ask exists**: an earlier gap-closing
  effort let the assessing/implementing agent unilaterally mark
  architecturally-large items out of scope and record that reasoning only
  in the target's own docs — the actual mandate was full parity, and the
  pattern went uncorrected for many rounds before the user caught it and
  had to explicitly push back. Well-written justification for an
  exclusion is not the same thing as the user actually agreeing to it;
  the `new-subsystem` label and its stop-and-ask (step 3.4) exist
  specifically to make that decision visible per-gap, at the moment it's
  made, instead of buried in a doc the user has no reason to reread.
- On the diff path specifically: matching is by symbol name, not semantics —
  a same-named function with a different signature or behavior shows up as
  "present" when it may not actually match. Worth a spot-check on anything
  safety-relevant.
- On the roadmap path: this skill treats the roadmap as authoritative for
  scope, not as verified-current — a stale roadmap item marked "done" that
  isn't will read as no-gap. Worth a periodic real check, not this skill's job.
- The RustyMill sibling check is keyword/grep-surfaced candidates plus
  judgment, same as the search steps in `sovereignty-loop`/`dedupe-loop` —
  it can miss a match hiding under different naming, and it only checks
  repos worth scanning for a given gap (step 1), not the full org every
  time. `references/platform-directory.md` can also drift from the live
  org; confirm rather than assume it's complete.
- Assumes CI is configured as a required status check on the default branch;
  the "on green CI" gate only actually gates merges if branch protection
  requires it (same caveat as repo-config).
- All three scripts require `gh` on `PATH` and authenticated. Step 0's
  preflight checks for it and routes to the GitHub MCP tools when it's
  missing, but that fallback is a documented substitution the run has to
  make deliberately — the scripts themselves have no MCP path.
- Built for a single target/reference pair per run. Comparing against several
  references at once (e.g. libc *and* a BSD extension set) means running the
  assessment phase once per reference and merging the gap lists by hand.
- Rust/cargo-shaped by default. See "Adapting to other stacks" for other
  ecosystems.
