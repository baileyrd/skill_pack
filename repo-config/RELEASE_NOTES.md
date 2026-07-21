# Release Notes

repo-config lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/repo-config),
pushed direct to `main` (no PR workflow yet) — this log tracks commits instead of
PRs, the same way
[AISF's RELEASE_NOTES.md](https://github.com/baileyrd/AISF/blob/main/RELEASE_NOTES.md)
tracks PRs: reverse chronological, one entry per meaningful change, honest about
what's still open.

---

## Add stack-selected CI workflows
**2026-07-21**

- **Added:** `ci-rust.yml` (fmt --check, clippy -D warnings, test) and
  `ci-python.yml` (ruff lint + format check, mypy, pytest) to the template payload,
  each triggered on PRs and pushes to `main`.
- **Added:** `apply.sh` now stack-selects CI by manifest — `Cargo.toml` → rust,
  `pyproject.toml`/`setup.py` → python, both for polyglot, neither (with a note) when
  no manifest exists. CI is excluded from the blanket copy so a repo never gets a
  workflow for a stack it doesn't have.
- **Added:** `audit.sh` reports CI conditionally — expected only when a manifest is
  present, so a no-manifest repo isn't dinged for missing a workflow it can't use.
- **Added:** `references/ci-and-branch-protection.md` — the GitHub settings (required
  status check, squash/rebase disabled, up-to-date-before-merge) that turn the
  generated workflow and the merge-commit rule from convention into enforcement.
- **Changed:** reversed the earlier decision to exclude CI entirely. Basic CI was out
  of scope originally (copied from oss-launch's public-launch framing), but that
  conflicted with the "on green CI, merge" rule added the same session — the rule
  needs a check to gate on. Public-launch CI (matrices, publish pipelines) stays out.
- **Why:** the repo owner expected CI setup and it was missing — the exclusion was
  the wrong call once green-CI-gated merge became a standing rule.

## Codify the PR + merge-commit workflow as a standing rule
**2026-07-21**

- **Added:** every change to a repo lands through a PR against the default branch;
  on green CI, merge with a merge commit ("Create a merge commit" — merge and sync),
  never squash or rebase. Full history is preserved deliberately.
- Written into both the template `CONTRIBUTING.md` (human-facing convention, under a
  renamed "Review & merge" section) and `SKILL.md`'s Rules (so the skill applies it
  to its own repo work, not just documents it for others).
- **Why:** this was a rule the repo owner kept having to restate by hand — making it
  a standing rule means it stops needing to be re-asked per repo.

## Track RELEASE_NOTES currency, not just presence
**2026-07-21**

- **Added:** `SKILL.md` now makes ongoing `RELEASE_NOTES.md` upkeep an explicit
  rule — after any meaningful change to a repo that has the file, add a dated entry
  before ending the turn, without being asked. New "Ongoing maintenance" section
  plus a step-4 re-audit check for it.
- **Changed:** step 4 now distinguishes file *presence* from *currency* — a stale
  RELEASE_NOTES still scores as present in `audit.sh`, so the re-audit adds the
  judgment the script can't: is the newest entry covering the latest change?
- **Added:** `audit.sh` prints a caveat when RELEASE_NOTES.md is present, so a
  standalone run (outside the skill) doesn't mistake a passing presence score for
  an up-to-date file.
- **Fixed:** a bare colon in the SKILL.md frontmatter `description` broke YAML
  parsing — the packager's validator rejected it, a plain upload would have failed.
  Reworded to drop the colon.
- **Why this exists:** the currency gap was found the hard way — RELEASE_NOTES went
  un-updated across several changes this session until the repo owner flagged it
  three times. These changes make the omission structurally harder to repeat.

## Restore executable bit on scripts
**2026-07-21** · [7c14141](https://github.com/baileyrd/skill_pack/commit/7c14141)

- **Fixed:** `scripts/apply.sh` and `scripts/audit.sh` lost their executable bit
  (`100755` → `100644`) somewhere between downloading the `.skill` zip and pushing
  to `skill_pack`. Confirmed the zip itself stores the correct `0o755` — the loss
  happened locally, most likely because the unzip tool used didn't restore Unix
  permission bits from the zip's stored metadata.
- **Fixed** by setting the mode through git directly
  (`git update-index --chmod=+x`) instead of the OS `chmod`, since that works
  identically regardless of shell — relevant here since the repo owner is on
  PowerShell, where `chmod` isn't a native command at all.
- Verified via `git ls-tree` against the pushed commit: both scripts show `100755`.

## Package and validate the skill
**2026-07-21** · shipped in [f91b0bc](https://github.com/baileyrd/skill_pack/commit/f91b0bc)

- **Added:** packaged `repo-config` as a `.skill` file via skill-creator's
  `package_skill.py`. Validation passed on the first run.

## Fix owner/repo extraction from git remotes
**2026-07-21**

- **Fixed:** `apply.sh`'s `git remote` parser left a trailing `.git` on the repo
  name (`nexus-forge.git` instead of `nexus-forge`) when a remote had one.
- **Root cause:** the regex used `[^/]+?`, a non-greedy quantifier — which GNU
  `sed -E` doesn't support. It was silently accepted rather than rejected, and
  matched differently than intended instead of erroring loudly.
- Fixed by stripping `.git` in bash first (`${remote_url%.git}`), then a plain
  greedy regex for the owner/repo split. Verified against both SSH
  (`git@github.com:owner/repo.git`) and HTTPS (`https://github.com/owner/repo`,
  no suffix) remote forms.

## Wire up greenfield defaults
**2026-07-21**

- **Added:** a greenfield check in the scan step — no manifest, no existing
  standard files, no git remote — skips the Q&A round and applies defaults from
  `references/scan-and-defaults.md` instead: internal-only license line, modular
  monolith + ports-and-adapters as the architecture default, placeholder
  `{{OWNER_REPO}}`/`{{SECURITY_CONTACT}}` tokens.
- **Added:** token substitution in `apply.sh`, resolved in order: `--config` file
  → `git remote` → greenfield placeholder.
- **Known limitation:** greenfield placeholders are a starting point, not a final
  answer — nothing currently forces a repo to come back and replace them once a
  real owner/repo or security contact exists.

## Convert repo-standards into the repo-config skill
**2026-07-21**

- **Changed:** restructured the static template kit (`repo-standards/`) into a
  Claude Code skill (`repo-config/`) — `SKILL.md`, `scripts/`, `references/`,
  `assets/templates/` — following skill-creator's anatomy instead of a bare
  script-plus-folder.
- **Added:** `scripts/audit.sh`, a gap checklist scoring a target repo against
  the 10 standard items.
- Scoped deliberately narrower than
  [github.com/AnayDhawan/oss-launch](https://github.com/AnayDhawan/oss-launch),
  which this is modeled on: no LICENSE, `.gitignore`, CI workflows, or
  launch-phase content (Show HN, badges, release automation) — none of that fits
  internal, non-public repos.

## Establish the standard file set
**2026-07-20 – 2026-07-21**

- **Added:** `.github/PULL_REQUEST_TEMPLATE/` (feature, bug_fix, docs, chore) and
  `.github/ISSUE_TEMPLATE/` (bug_report, feature_request, config.yml).
- **Added:** README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG,
  ARCHITECTURE, and an ADR seed as the standard root/docs file set.
- **Added:** `RELEASE_NOTES.md` as one of the standard template files, format
  modeled on AISF's own — PR-per-entry (or version-per-entry once tags exist),
  bolded inline category tags, honest callouts of known limitations.
