# Contributing

## Before you start
- Match surrounding conventions when editing existing code.
- Keep diffs focused — one logical change per PR.
- For large or hard-to-reverse changes (schema/data migrations, public API changes,
  deletions, dependency/toolchain bumps), open an issue or draft PR to discuss first.

## Workflow
1. Branch off the default branch.
2. Make your change. State the *why* in commit messages or PR description for any
   non-obvious decision.
3. Run `python3 scripts/check_repo.py` before opening the PR — it's the same
   five checks CI runs (exec bits, line endings, doc references, skill
   manifests, packaging), and it's faster to fix locally than in review.
4. Add tests for non-trivial logic — happy path and at least one
   failure/boundary case. **There is no test harness in this repo yet**: no
   runner, no test directory, nothing for CI to execute. Until there is, this
   line applies to any code that arrives with one, and PRs should say plainly
   that tests were not added rather than ticking a box that isn't real. The
   repo lint above is not a substitute — it checks structure, not behavior.
5. Add or update docstrings on any public surface you touched.
6. Open a PR — pick the template that matches (feature / bug fix / docs / chore).

## Code style
- Explicit over implicit; type hints/annotations always.
- Flat control flow — guard clauses, early returns, avoid >3 levels of nesting.
- Short, single-purpose functions.
- Minimal dependencies — justify any new third-party one in the PR description.
- Never commit or log secrets/credentials. Validate external input at the boundary.
- Never silently swallow exceptions — handle, propagate with context, or log.

## Review & merge
- Every change lands through a PR — no direct pushes to the default branch.
- CI must be green before merge. `.github/workflows/ci.yml` runs
  `scripts/check_repo.py` on every PR. Note it only *reports* until it's set as
  a required status check in branch protection — until then a red run is a
  signal a human has to notice, not a block.
- At least one approval required (see CODEOWNERS if present).
- Reviewers: check for scope creep, missing tests, and unexplained non-obvious decisions.
- Merge with a **merge commit** ("Create a merge commit" — merge and sync). Do **not**
  squash-merge or rebase-merge: full commit history is preserved deliberately.
