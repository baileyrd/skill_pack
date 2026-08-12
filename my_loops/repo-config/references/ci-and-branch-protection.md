# CI and branch protection

The generated files establish the *convention*; these repo settings are what
*enforce* it. Applying the skill doesn't set these — they're GitHub-side settings a
human toggles once per repo. Surface them as a manual follow-up in step 4.

## Why this is separate from file generation

`apply.sh` writes a CI workflow, but a workflow file alone gates nothing — a PR can
merge red unless the check is *required*. And the merge-commit-only rule
(CONTRIBUTING) is just prose unless squash/rebase are actually disabled in settings.
So three things have to line up: the workflow exists (skill does this), the check is
required (manual), and the merge buttons are restricted (manual).

## Settings to set, once per repo

Settings → General → Pull Requests:
- Untick **Allow squash merging**
- Untick **Allow rebase merging**
- Leave only **Allow merge commits** ticked

This makes the "merge commit, not squash/rebase" rule impossible to violate from the
merge button, rather than relying on everyone remembering it.

Settings → Branches → add a branch protection rule for `main`:
- **Require a pull request before merging** (enforces "no direct pushes")
- **Require status checks to pass before merging** → add the CI job (`check`) as a
  required check. This is the half that makes "on green CI, merge" real — until the
  check is marked required, a red CI doesn't block anything.
- **Require branches to be up to date before merging** (the "sync" half — the PR
  branch must have the latest `main` before it can merge)

## Note on required-check names

The required status check matches on the *job* name (`check`), not the workflow file
name — so `ci-rust.yml` and `ci-python.yml` both expose a `check` job, and a polyglot
repo requiring `check` will wait on whichever workflows run. If you rename the job,
update the required-check setting to match or merges will block forever waiting on a
check that never reports.
