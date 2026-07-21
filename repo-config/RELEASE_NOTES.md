# Release Notes

repo-config hasn't been pushed to a git repository yet, so there are no PRs to link
to — this log instead tracks the build session's actual units of work, the same way
[AISF's RELEASE_NOTES.md](https://github.com/baileyrd/AISF/blob/main/RELEASE_NOTES.md)
tracks PRs: reverse chronological, one entry per meaningful change, honest about
what's still open. Once this is pushed and gets real PRs, switch this file over to
linking them directly.

---

## Package and validate the skill
**2026-07-21**

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
