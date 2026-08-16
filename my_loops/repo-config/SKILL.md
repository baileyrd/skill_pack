---
name: repo-config
description: >-
  Scans a repo and applies the standard governance file set — PR templates, issue templates,
  README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG, RELEASE_NOTES, ARCHITECTURE, an ADR
  seed, and a `.gitattributes` that forces LF line endings so a Windows-authored repo stops
  shipping scripts that die on their own shebang. Asks only what the scan can't infer, falling
  back to greenfield defaults (modular monolith, ports-and-adapters), deferring to
  `rusty_foundation_akb`/`Atlas_Engineering_Standards_Library` where more concrete. Use whenever
  the user wants to set up repo standards, bootstrap a new repo, add PR/issue templates, run a
  "new repo checklist," or add any of CONTRIBUTING/SECURITY/ARCHITECTURE/CHANGELOG/RELEASE_NOTES —
  even if they only name one file, since this applies the whole set together. Also use on an
  ongoing basis: whenever a meaningful change lands in a repo that already has a RELEASE_NOTES.md
  or CHANGELOG.md, add an entry to each before ending the turn.
version: 1.4.0
---

# repo-config

Applies a standard governance-file set to a repo: two `.github/` template folders
plus eight root/docs markdown files and a `.gitattributes`. Scans first, adapts to
what's already there instead of overwriting, and falls back to greenfield defaults
when there's nothing
yet to scan.

`assets/templates/` is the payload written into the TARGET repo. This skill's own
files (SKILL.md, scripts/, references/) describe repo-config itself — never confuse
the two.

## Run (when invoked)

**0. Scan the target repo**
- `git -C <target> remote get-url origin` → owner/repo, for `{{OWNER_REPO}}`
  and, by default, `{{SECURITY_CONTACT}}` too — the repo owner is the
  default security POC (see step 2).
- Which standard files already exist — run `scripts/audit.sh <target>` first, it
  doubles as the starting score. **If it won't run**, the run isn't blocked:
  the checklist is 11 named files, checkable by hand in a minute. A synced
  copy arriving with CRLF (`$'\r': command not found`) or without its `+x`
  bit has happened; say the script failed, check by hand, and carry on rather
  than treating the gateway as a dependency.
- Any stack manifest (`Cargo.toml` / `pyproject.toml` / `package.json`) → language,
  for README's dev-command section
- **Greenfield check**: no manifest, no existing standard files, no git remote yet →
  nothing to scan. Skip step 2 entirely and apply the greenfield defaults instead
  (details: `references/scan-and-defaults.md`).
- **Multi-product check — look for the standard set *below* the root, not only
  at it.** A merged workspace or monorepo can already carry governance files a
  level down, and the root scan will report them as missing:

  ```sh
  find <target> -mindepth 2 -maxdepth 3 \
    \( -name 'RELEASE_NOTES.md' -o -name 'CHANGELOG.md' -o -path '*/docs/adr' \) \
    -not -path '*/.git/*'
  ```

  A real case (`rusty_recall`, two merged repos each under its own prefix) had
  `remind_me/docs/adr/` and `dbs/docs/adr/` **each numbered from 0001**, plus two
  `RELEASE_NOTES.md` and a `CHANGELOG.md`. Seeding the root set blind would have
  produced a *third* ADR series also starting at 0001, and root notes files with
  no stated relationship to the four already in the tree.

  Surface any hits in step 1's gap table, and make it a step 2 question — see
  "Multi-product repos" in `references/scan-and-defaults.md`. Note the failure is
  quiet: the audit reports 11/11 either way, so nothing in the score distinguishes
  "the root files were placed thoughtfully" from "the root files now contradict
  the ones a level down."

**1. Report** the gap table from `audit.sh`.

**If the audit is already at full marks, say so and skip to step 4.** Steps 2
and 3 have nothing to ask and nothing to generate — a re-run against an
already-configured repo is a *currency* check, not a setup pass, and that's
the common case after the first run. Step 0's greenfield check handles the
opposite end (nothing exists yet); this is the other one, and without it three
mandatory-looking steps get skipped on a judgment the instructions don't
sanction.

**2. Ask only what the scan didn't answer** (skip entirely if greenfield):
- One-line project description for README
- Anything the manifest didn't make obvious (e.g. a non-standard test command)

Security contact is no longer a standing question: default it to the repo
owner resolved from `{{OWNER_REPO}}` in step 0. Only ask if step 0 found no
git remote yet (i.e. greenfield, where step 2 is skipped entirely anyway) or
the user names a different contact unprompted — don't ask by default.

Batch these into one question round. Don't ask about anything `git remote` or the
manifest already answered.

**2.5. Check development standards** — before generating ARCHITECTURE.md or
falling back to the greenfield architecture defaults, consult
`references/development-standards.md`: it points at two external repos
(`Rusty-Mill/rusty_foundation_akb`, `baileyrd/Atlas_Engineering_Standards_Library`)
that are the normative source for architecture/development standards, as
distinct from this skill's own governance-process scaffolding. A specific
applicable standard from either repo wins over the generic greenfield
default; cite the requirement ID or doc section in ARCHITECTURE.md rather
than asserting the pattern as this skill's own opinion.

**3. Generate** — run:
```
bash scripts/apply.sh <target-dir> [--config <file>] [--force]
```
Non-destructive by default: existing files are skipped and reported, not
overwritten. Substitutes `{{OWNER_REPO}}` and `{{SECURITY_CONTACT}}` from the scan,
the Q&A answers, or the greenfield defaults — write a small config file first if you
have values from steps 0–2 (see `references/scan-and-defaults.md` for the format).

CI workflows are stack-selected, not copied blanket: `apply.sh` drops in
`ci-rust.yml` if the target has a `Cargo.toml`, `ci-python.yml` if it has a
`pyproject.toml`/`setup.py`, both for a polyglot repo, and neither (with a note) if
there's no manifest yet — an always-red workflow is worse than none. After applying,
the CI check only actually gates merges once it's set as a required status check in
branch protection — see `references/ci-and-branch-protection.md`, and surface that as
a manual follow-up in step 4.

`.gitattributes` is the one item in the set that is drop-in by design — it carries
no tokens and needs no per-repo judgment, because the failure it prevents (a `.sh`
file reaching a Linux harness with CRLF and dying on its own shebang) doesn't vary
by project. If the target already has one, `apply.sh` skips it like any other
existing file; check by hand whether that existing file actually sets `eol=lf`,
since `audit.sh` will flag a present-but-toothless one but can't fix it.

Two files are worth hand-adapting after the copy rather than leaving as scaffold:
README's prose and ARCHITECTURE's boundary table. Match the tone in
`references/examples.md` — terse, reasoning included, honest about limitations.
Everything else in the set is close to drop-in once the tokens are substituted.

**4. Re-audit** — rerun `scripts/audit.sh <target>`, report the before/after score
and what's still manual (README's Getting Started section, ARCHITECTURE's boundary
table, the first real ADR replacing the seed).

`audit.sh` checks file *presence*, not *currency* — a stale log still scores as
present. So step 4 also includes a judgment the script can't make, and it applies
to **every log-shaped file in the set, not just `RELEASE_NOTES.md`**: today that
means `RELEASE_NOTES.md` and `CHANGELOG.md`, and it means any log added later
without this section needing another edit. For each of them:

- **Coverage** — did any real change happen this session (setup counts, and so does
  any later fix or feature) that isn't yet logged? If so, add the entry now before
  reporting done — see "Ongoing maintenance" below.
- **Links** — does every entry whose PR has since merged actually carry its link?
  The "log it without a link" rule below is deliberate, but it defers an obligation
  to *here*: step 4 runs after the work is pushed, which is the first moment the
  link can be added honestly. An entry can cover its change perfectly and still
  violate the file's own stated convention.

Report a log as current only after both checks, not on the strength of the presence
score alone. Two separate files with separate conventions means updating one during
the work does not imply the other — the changelog being untouched while
`RELEASE_NOTES.md` was updated is the exact shape this catches
([#37](https://github.com/baileyrd/skill_pack/issues/37),
[#38](https://github.com/baileyrd/skill_pack/issues/38)).

**5. Wrap-up retro** — after step 4's re-audit report, run a
`meta/skill-retro` pass on `repo-config` itself, grounded in this run: did
step 0's scan correctly infer what it should have, did step 2's questions
actually cover what the scan couldn't answer, did `apply.sh`'s
substitution or the greenfield defaults need something the instructions
didn't cover? Read-only — applying anything `skill-retro` finds is a
separate, explicitly-approved follow-up, not part of this run.

## Ongoing maintenance — not just initial setup

The logs in the set aren't one-time drops. Once a repo has them, keep them
current — `RELEASE_NOTES.md` and `CHANGELOG.md` alike, each in its own format:

- After any meaningful change to that repo — a fix, a feature, a behavior change,
  not a typo or formatting-only edit — add a new entry at the top before ending
  the turn. Don't wait to be asked. This applies whether or not repo-config was
  what put the file there in the first place; any repo with one of these files
  qualifies.
- **Update every log the repo has, not whichever one you touched first.** They
  have separate conventions and separate audiences, so an entry in one is not an
  entry in the other. A repo with both and a change logged in only one is the
  common failure, not a rare one.
- Match the format already in each file: `RELEASE_NOTES.md` uses dated entries with
  bolded inline category tags (`**Added:**` / `**Changed:**` / `**Fixed:**`);
  `CHANGELOG.md` uses Keep-a-Changelog sections (`### Added` / `### Changed` /
  `### Fixed`) under a release heading. Reasoning included, known limitations
  stated plainly rather than glossed over — see `references/examples.md`.
- Link the real commit/PR once the change is actually pushed; if it isn't pushed
  yet, log it without a link rather than inventing one — **and add the link on the
  next pass**, which step 4 now checks for. Logging without a link is correct at
  write time; leaving it unlinked once the PR has merged is not.
- This was missed once already on repo-config's own `RELEASE_NOTES.md` — a real fix
  shipped with no entry, caught only because the repo owner pointed it out. It was
  then missed a second time in a different shape: `RELEASE_NOTES.md` was updated
  and `CHANGELOG.md` was left with no record of the same PR at all. That's the
  failure mode these rules exist to prevent.

## Rules
- Keep every log in the set current, not just seeded — `RELEASE_NOTES.md` and
  `CHANGELOG.md` both, and linked once their PRs merge. See "Ongoing maintenance"
  above.
- Every change to a target repo lands through a PR against the default branch, never
  a direct push. On green CI, merge with a **merge commit** (GitHub's "Create a merge
  commit" — merge and sync) — never squash-merge or rebase-merge. Full history is
  preserved deliberately. This is the standing workflow; don't re-ask it per repo.
- Never overwrite an existing file without `--force`; report what was skipped either
  way.
- Greenfield defaults are a starting point, not a final answer — say so in the
  re-audit output so a placeholder `{{OWNER_REPO}}` doesn't get mistaken for a
  real one; the security contact defaults to the repo owner as soon as a real
  git remote exists, so it isn't a placeholder once non-greenfield.
- Adapt, don't paste: once a real git remote exists, `{{OWNER_REPO}}` should get
  substituted for real, not left as a token.
- Match the tone the templates already model — see `references/examples.md`.
- Architecture content (ARCHITECTURE.md, the greenfield architecture/boundary
  defaults) is governed by `references/development-standards.md` first, the
  generic fallback second — never assert a pattern as this skill's own
  opinion when either standards repo already specifies one.

## Limitations
- Governance-file scaffolding plus basic CI. Unlike a public-launch OSS tool, this
  deliberately doesn't touch LICENSE or anything aimed at going public (badges,
  release automation, star growth) — these are internal repos. `.gitignore` stays
  out too: what's ignorable is genuinely per-project, and a wrong guess silently
  stops a real file from being committed. `.gitattributes` is the one piece of
  repo-level git config that *is* in scope, and only because it's the opposite
  case — the correct content is the same for every repo here, and getting it
  wrong breaks scripts at a distance, in a copy nobody is looking at. The test
  for admitting any future repo-level config is that pair of questions —
  same-everywhere, and loud-or-silent when wrong — recorded as
  [ADR-0003](https://github.com/baileyrd/skill_pack/blob/main/docs/adr/0003-gitattributes-in-scope-gitignore-out.md)
  in this skill's own repo, so it's a rule to apply rather than an argument to
  have again.
  CI *is* in scope, but only a basic per-stack test/lint/type gate so the "on green
  CI, merge" rule has a real check to gate on — not multi-version matrices or
  publish pipelines.
- Greenfield defaults assume the standing engineering principles (modular monolith,
  ports-and-adapters, internal-only license line). A repo that intentionally
  deviates should say so at generation time — the defaults aren't a policy override,
  just a sensible starting point.
- `apply.sh`'s substitution is two tokens (`{{OWNER_REPO}}`, `{{SECURITY_CONTACT}}`),
  not a template engine — anything beyond that needs a manual edit after the copy.

## Scripts
| Script | Purpose | Args |
| --- | --- | --- |
| `audit.sh` | Gap checklist against the 11 standard items, with a score | `[target-dir]` (default `.`) |
| `apply.sh` | Copies `assets/templates/` into target, substitutes placeholders, non-destructive by default | `<target-dir> [--config <file>] [--force]` |

Both scripts resolve their own root relative to their own location, so they run
whether this skill is installed or just checked out locally.
