# Release Notes

repo-config lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/repo-config),
pushed direct to `main` (no PR workflow yet) — this log tracks commits instead of
PRs, the same way
[AISF's RELEASE_NOTES.md](https://github.com/baileyrd/AISF/blob/main/RELEASE_NOTES.md)
tracks PRs: reverse chronological, one entry per meaningful change, honest about
what's still open.

---

## v1.3.3 — YAML-safe description
**2026-08-16**

- **Fixed ([#59](https://github.com/baileyrd/skill_pack/issues/59)):** the
  frontmatter `description` was an unquoted plain scalar containing `": "`,
  which is invalid YAML — a colon-space inside a plain scalar reads as the start
  of a nested mapping. It is now a `>-` block scalar. The *value* is byte-for-byte
  unchanged; this is a representation fix, verified by round-tripping the parsed
  string before and after.
- **Why it went unnoticed:** `scripts/check_repo.py` parses frontmatter with a
  hand-rolled line-based parser that tolerates the construct, so CI stayed green
  and packaging worked, while anything using a real YAML parser rejected the file
  outright. `quick_validate.py` was the instance that surfaced it. The repo was
  validating with a parser more permissive than its consumers'.

---

## v1.3.2 — The currency check covers every log, and links get closed out
**2026-08-16**

Applied from the step-5 wrap-up retro on the run that produced
[#36](https://github.com/baileyrd/skill_pack/pull/36) — this skill run against
`skill_pack` itself. Both findings had a real miss behind them; neither was
speculative.

- **Fixed ([#37](https://github.com/baileyrd/skill_pack/issues/37)):** step 4's
  currency check named `RELEASE_NOTES.md` and silently omitted `CHANGELOG.md`,
  in all five places the rule was stated — SKILL.md steps 4, "Ongoing
  maintenance", Rules, the `description`, and `audit.sh`'s own note.
  `CHANGELOG.md` is item 23 in the same checklist, so it earned full presence
  credit while nothing ever asked whether it was current. **On the run that
  found this, the changelog had no record of the latest PR at all** — two
  shipped bug fixes missing — and it was caught only because the operator
  inspected the file set by hand, which is not a step the instructions
  contained. A run following the instructions exactly would have reported a
  current repo. Now written as a general rule (*every log-shaped file in the
  set*) rather than an enumeration, so a third log added later doesn't
  reintroduce it.
- **Fixed ([#38](https://github.com/baileyrd/skill_pack/issues/38)):** "log it
  without a link if the PR doesn't exist yet" is the right rule — inventing a
  number is worse — but it deferred an obligation nothing discharged. Following
  it correctly at write time *guaranteed* a convention violation later, in a
  file whose own header requires every entry to link its PR. Step 4 now checks
  that entries whose PRs have merged carry their links; it's the natural home,
  since step 4 runs after the work is pushed, which is the first moment the
  link can be added honestly. Evidence it was recurring rather than one-off:
  only 2 entries in this repo's `RELEASE_NOTES.md` carried links.
- **Changed:** `audit.sh` now emits its presence-only caveat for each log the
  target actually has, and mentions the link check. Naming one file implied it
  was the only one with the problem.
- **Changed:** the `description` lost the internal-only-license clause and two
  wordy phrases to make room for `CHANGELOG.md` — 984 chars, 40 under the
  limit v1.3.1 introduced. Trimmed rather than left at +3, since a limit this
  close is one edit from breaking again.
- **Not addressed:** step 0 still infers language from a stack manifest only, so
  a repo like this one — no manifest, plainly Python — reports no language. It
  didn't fire on the run that found the above (the full-marks early exit skipped
  the step that would have used it), so it stayed an observation rather than a
  finding. Unfixed and unfiled.

---

## v1.3.1 — Description under claude.ai's upload limit
**2026-08-16**

- **Fixed:** the `description` was 1146 characters, over the 1024-character
  limit claude.ai enforces on skill upload, so the zip was rejected outright.
  Trimmed to 1002 (22 characters of headroom) with every trigger phrase kept —
  the cuts are wording only — the `.gitattributes` rationale and the
  standards-repo deferral are both still named. Nothing about what the skill
  does changed.
- **Context:** five skills here shipped over the limit at once, and none of the
  local tooling noticed: `install_skills.py` copies frontmatter without reading
  it, `build_skill_zips.py` zips it the same way, and Claude Code itself loads
  an over-length description fine. Only claude.ai rejects it, at upload, one
  file at a time. `check_repo.py`'s `manifests` check now enforces the limit so
  this fails locally and in CI instead.

## v1.3.0 — Findings from its own skill-retro
**2026-08-15**

Applied from a `meta/skill-retro` pass grounded in this session's
`/repo-config` run. Note that run executed **v1.1.0**; both findings were
re-checked against the current text before being called real, and both
survived two intervening versions.

- **Added:** an early exit at step 1 for the already-saturated repo. The run
  scored 10/10, so steps 2, 2.5 and 3 had nothing to do and were **silently
  skipped** — three mandatory-looking steps skipped on a judgment the
  instructions didn't sanction. Step 0's greenfield check covers "nothing
  exists yet"; nothing covered "everything already exists," which is the
  common case on every re-run after the first.
- **Added:** a fallback when `audit.sh` won't run. Step 0 makes it the
  gateway to everything, and it **failed** — the synced copy had CRLF and
  died on its shebang. The fallback was improvised. The CRLF cause is fixed
  (v1.2.0's `.gitattributes`) but the missing-`+x` path can still produce the
  same dead end, and the checklist is 11 named files that take a minute to
  check by hand.
- **Validated, unchanged:** the "Ongoing maintenance" rule. Every meaningful
  change across ~14 PRs today got a `RELEASE_NOTES.md` entry unprompted. That
  rule exists because it was missed once before; it held all day.
- **Third finding handled elsewhere:** step 5's wrap-up retro didn't fire —
  second occurrence of that pattern, after `docs-loop`. It's now wired as a
  `PostToolUse` hook rather than reworded here; see the root `RELEASE_NOTES.md`
  and `scripts/retro_reminder.py`.

## v1.2.1 — Cite ADR-0003 for the scope boundary
**2026-08-15**

- **Changed:** Limitations now points at
  [ADR-0003](https://github.com/baileyrd/skill_pack/blob/main/docs/adr/0003-gitattributes-in-scope-gitignore-out.md)
  for *why* `.gitattributes` is in scope and `.gitignore` isn't, instead of
  only asserting it. The decision rule is the pair of questions the ADR
  records — does this file have the same correct content everywhere, and does
  getting it wrong fail loudly or silently — so a future proposal to add
  repo-level config has a test to meet rather than a precedent to point at.
- Doc-only; no behavior change to `apply.sh` or `audit.sh`.

## v1.2.0 — Add .gitattributes to the standard set (11th item)
**2026-08-15**

- **Added:** `assets/templates/.gitattributes` — `* text=auto eol=lf` plus
  explicit `binary` marks for archives/images and `eol=crlf` for
  `.bat`/`.cmd`/`.ps1`, which genuinely want CRLF. Drop-in by design: it
  carries no `{{TOKENS}}` and needs no per-repo judgment, because the
  failure it prevents doesn't vary by project.
- **Why now:** this skill's *own* `audit.sh`, synced to
  `~/.claude/skills/synced/repo-config/`, arrived with CRLF endings and
  wouldn't run on Linux — `line 5: $'\r': command not found`. Caught when a
  `/repo-config` invocation failed on its first command. The repo's copy was
  clean LF the whole time, which is the trap: the index can be perfectly
  normalized while the checkout that gets copied around is not.
- **Added:** `.gitattributes` as `audit.sh`'s 11th checklist item, with a
  correctness note the other ten don't get. A repo can carry a
  `.gitattributes` that only marks binaries and still hand out CRLF shell
  scripts, so the script greps for `eol=lf` and warns when a present file
  doesn't enforce it. Presence is the wrong question for this one item.
- **Changed:** Limitations no longer excludes repo-level git config wholesale.
  `.gitignore` stays out — what's ignorable is genuinely per-project, and a
  wrong guess silently stops a real file being committed. `.gitattributes` is
  the opposite case: one correct answer for every repo here, and getting it
  wrong breaks scripts at a distance, in a copy nobody is looking at.
- **Verified end to end** against a scratch repo: `apply.sh` delivers the
  dotfile (a template-root dotfile was the real risk — `find -type f` picks
  it up, confirmed rather than assumed), `audit.sh` scores 11/11, a
  binaries-only `.gitattributes` triggers the warning, a second `apply.sh`
  run skips it non-destructively, and a committed CRLF `.sh` file comes back
  from `git checkout` as LF.
- **Doesn't fix an existing checkout.** A clone that already has CRLF files
  needs one `git add --renormalize .`, and a copy already synced elsewhere
  needs re-syncing. Same limitation logged against this repo's own
  `.gitattributes`; adding the template doesn't change it.

## v1.1.0 — Wire skill-retro into wrap-up (step 5)
**2026-08-13**

- **Added:** step 5, "Wrap-up retro" — after step 4's re-audit report, runs
  a `meta/skill-retro` pass on `repo-config` itself, grounded in this run's
  step 0 scan and step 2 questions. Read-only; applying anything found is a
  separate, explicitly-approved follow-up.
- Part of a batch wiring the same convention into every remaining
  `my_loops` skill, following the pattern first used on
  `my_loops/rust-migration` v1.1.0 and `meta/skill-retro`'s own step 6.

## Exec-bit half of the sync-gap pattern traced to a real bug, and fixed
**2026-08-12**

- Reopened the "Third occurrence" finding below on a lead: the zip that
  installs this skill downstream is built by this repo's own
  `scripts/build_skill_zips.py`, not an external unzip/install tool as
  first assumed — worth checking the build script's own logic before
  pointing further downstream.
- Reproduced the exec-bit-loss symptom directly: `git_file_mode()` in
  `build_skill_zips.py` trusted the git index's mode for a file, and its
  only safety net (`restore_exec_bits.py`) restores `+x` by matching
  unchanged *content* against a blob that was `100755` at `HEAD` — so any
  real edit to `apply.sh`/`audit.sh` that loses its bit on `git add`
  (expected on this repo's `core.fileMode=false` + Windows setup) ships
  silently as `0o644` in the zip. Confirmed in a scratch clone before
  touching anything real here.
- **Fixed at the source** (`scripts/build_skill_zips.py`, not this
  skill's own files) — full writeup in the root `RELEASE_NOTES.md`
  entry "Fix silent exec-bit loss in build_skill_zips.py". Rebuilt this
  skill's zip and confirmed `apply.sh`/`audit.sh` both land `0o755`.
- **Still open:** the `.github/`-missing half of the pattern. Checked
  `Path.rglob("*")`'s dotfile handling directly — it does traverse
  `.github/` correctly in this repo's Python — so that symptom isn't in
  the build script either. Next data point still points at a
  stale/incomplete local clone at build time, unless a fourth occurrence
  says otherwise.

## Third occurrence of the same sync-gap pattern, now with concrete fallout
**2026-08-12**

- **Finding, not a source fix:** a session applying this skill to
  `rusty_dbs` hit the same class of gap as "Record a sync-gap finding"
  below, for the third time:
  - `assets/templates/.github/` (PR templates, issue templates, CI
    workflows) was entirely missing from that session's local sync —
    confirmed present and correct in this repo directly.
  - `scripts/apply.sh` and `scripts/audit.sh` had lost their executable
    bit (`100755` → `100644`) in the same local sync — `git ls-tree`
    against `HEAD` here confirms both are still `100755`, same check as
    the standalone "Restore executable bit on scripts" entry below.
- **New this time — concrete fallout, not just a metadata nuisance:**
  with the real `.github/ISSUE_TEMPLATE/` missing, the session
  hand-reconstructed issue templates for `rusty_dbs` from memory as plain
  Markdown. The real templates (`bug_report.yml`, `feature_request.yml`,
  `config.yml`) are GitHub issue-form YAML — structured fields, a
  `labels:` block, form validation — not Markdown with HTML comments. The
  hand-reconstructed version doesn't render as an issue form at all, so
  this gap silently downgrades what a target repo actually gets, rather
  than just being caught by a diff.
- **Why three occurrences changes the framing:** one incident is noise,
  two is "worth recording," three sharing the same two symptoms
  (`.github/` directories vanishing, executable bits dropping) across two
  different target repos is a pattern in whatever downloads/unpacks/syncs
  this skill into a session — most likely a `.skill` zip install step
  that doesn't preserve directory trees starting with `.` or POSIX
  permission bits. Still not this repo's bug: `git ls-tree` against
  `HEAD` confirms the templates and both scripts are correct and present
  here, same as the first two times.
- **No content or permission change made here** — recorded so a fourth
  occurrence has three prior data points to compare against instead of
  starting the diagnosis over. If it recurs again, the next step is
  diagnosing the sync/packaging tool itself (starting with how it handles
  dotfile-prefixed directories and stored Unix permission bits), not
  re-auditing this repo a fourth time.

## v1.0.0 — Initial versioned release
**2026-08-12**

- **Added:** `version: 1.0.0` to `SKILL.md` frontmatter, matching the
  versioning convention now applied to all skills in `skill_pack`. This file
  already existed; the other seven skills each got their own `RELEASE_NOTES.md`
  seeded with the same entry.
- **Moved:** this skill now lives at `my_loops/repo-config/` (was
  `repo-config/` at repo root) as part of grouping `skill_pack`'s skills into
  category folders. Link above updated to match.

## Default security contact to the repo owner
**2026-08-12**

- **Changed:** security contact is no longer a standing Q&A question —
  `{{SECURITY_CONTACT}}` now defaults to the repo owner resolved from
  `{{OWNER_REPO}}`'s `git remote` in step 0. Only asked when there's no git
  remote yet (greenfield, where step 2 is skipped anyway) or the user names
  a different contact unprompted.
- **Changed:** `scan-and-defaults.md`'s signal table and greenfield-defaults
  table updated to match; the "what to actually ask" list no longer
  includes security contact.

---

## Wire external development-standards repos into architecture generation
**2026-08-12**

- **Added:** `references/development-standards.md`, describing
  `Rusty-Mill/rusty_foundation_akb` and
  `baileyrd/Atlas_Engineering_Standards_Library` as the normative source for
  architecture/development standards — kept explicitly separate from this
  skill's own governance-process scaffolding, which is unchanged.
- **Changed:** `scan-and-defaults.md`'s architecture-default and
  boundary-pattern rows now note they're a fallback, checked only after the
  two standards repos for something more specific. New step 2.5 in
  `SKILL.md` makes this check explicit before ARCHITECTURE.md generation.
- **Known limitation:** both standards repos are early-stage (spec-only /
  draft volumes as of this writing) — most target repos will still land on
  the generic fallback in practice until those repos mature.

---

## Record a sync-gap finding: source was fine, a downstream install wasn't
**2026-08-12**

- **Finding, not a source fix:** a Claude Code session applying this skill to
  `Rusty-Mill/rusty_knowledge` hit `apply.sh` crashing on a missing
  `.github/workflows/ci-rust.yml` — the session's locally synced copy of this
  skill was missing its entire `assets/templates/.github/` directory (PR
  templates, issue templates, both CI workflows), and had also lost the
  executable bit on `scripts/apply.sh`/`scripts/audit.sh`.
- **Verified against this repo directly:** cloned `skill_pack` fresh and diffed
  it against the session's synced copy — every file under
  `repo-config/assets/templates/.github/` was present and correct here, and
  `git ls-tree` confirmed both scripts are `100755` in the repo. The gap was
  entirely in that session's local skill installation/sync step, not in
  anything committed to this repo.
- **Why this is worth recording rather than silently letting it pass:** it's
  the same failure *class* as "Restore executable bit on scripts" below —
  metadata (executable bits) or whole directories (dotfile-prefixed ones, like
  `.github/`) going missing somewhere in a download/unpack/sync step outside
  this repo's own git history. Two occurrences is a pattern worth a maintainer
  knowing about, even though neither one was this repo's bug to fix.
- No content or permission change was made here — this entry exists purely so
  the incident isn't lost. If it recurs a third time, especially again around
  a dotfile-prefixed directory or an executable bit, that's a signal to look
  at whatever packages/syncs this skill into a session (e.g. a `.skill` zip
  step), not at this repo.

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
