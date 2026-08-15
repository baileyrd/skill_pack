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
   failure/boundary case. `python3 -m unittest discover -s tests` runs the
   suite; CI runs the same command. Stdlib `unittest`, no third-party runner,
   so there's nothing to install first.

   Two things the suite expects of a new test, both from ADR-0002's rules for
   repo checks, which apply here for the same reason:
   - **Name the bug it would have caught.** Coverage isn't the goal; the
     specific mistakes this code has already proven it makes are.
   - **Show it failing before you rely on it.** Revert the fix, watch the
     test go red, restore. Two of the five CI checks silently passed their
     first fault injection, and the mutation harness for these very tests was
     itself broken on the first attempt — reporting `ImportError` as if it
     were a caught regression.
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
