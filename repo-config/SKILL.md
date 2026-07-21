---
name: repo-config
description: Scans a repo and applies the standard governance file set — PR templates, issue templates, README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG, RELEASE_NOTES, ARCHITECTURE, and an ADR seed. Asks only what it can't infer from the scan, and falls back to greenfield defaults (modular monolith, ports-and-adapters, internal-only license line) for a brand-new repo with nothing yet to scan. Use whenever the user wants to set up repo standards, bootstrap a new repo, add PR/issue templates, run a "new repo checklist," or add any of CONTRIBUTING/SECURITY/ARCHITECTURE/CHANGELOG/RELEASE_NOTES — even if they only name one file, since this applies the whole set together. Also use on an ongoing basis, separate from initial setup — whenever a meaningful change is made to a repo that already has a RELEASE_NOTES.md, whether repo-config put it there or not, add a dated entry for that change before ending the turn, without being asked.
---

# repo-config

Applies a standard governance-file set to a repo: two `.github/` template folders
plus eight root/docs markdown files. Scans first, adapts to what's already there
instead of overwriting, and falls back to greenfield defaults when there's nothing
yet to scan.

`assets/templates/` is the payload written into the TARGET repo. This skill's own
files (SKILL.md, scripts/, references/) describe repo-config itself — never confuse
the two.

## Run (when invoked)

**0. Scan the target repo**
- `git -C <target> remote get-url origin` → owner/repo, for `{{OWNER_REPO}}`
- Which standard files already exist — run `scripts/audit.sh <target>` first, it
  doubles as the starting score
- Any stack manifest (`Cargo.toml` / `pyproject.toml` / `package.json`) → language,
  for README's dev-command section
- **Greenfield check**: no manifest, no existing standard files, no git remote yet →
  nothing to scan. Skip step 2 entirely and apply the greenfield defaults instead
  (details: `references/scan-and-defaults.md`).

**1. Report** the gap table from `audit.sh`.

**2. Ask only what the scan didn't answer** (skip entirely if greenfield):
- Security contact (team alias or individual)
- One-line project description for README
- Anything the manifest didn't make obvious (e.g. a non-standard test command)

Batch these into one question round. Don't ask about anything `git remote` or the
manifest already answered.

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

Two files are worth hand-adapting after the copy rather than leaving as scaffold:
README's prose and ARCHITECTURE's boundary table. Match the tone in
`references/examples.md` — terse, reasoning included, honest about limitations.
Everything else in the set is close to drop-in once the tokens are substituted.

**4. Re-audit** — rerun `scripts/audit.sh <target>`, report the before/after score
and what's still manual (a placeholder security contact, README's Getting Started
section, ARCHITECTURE's boundary table, the first real ADR replacing the seed).

`audit.sh` checks file *presence*, not *currency* — a stale `RELEASE_NOTES.md`
still scores as present. So step 4 also includes a judgment the script can't make:
did any real change happen this session (setup counts, and so does any later fix or
feature) that isn't yet logged in `RELEASE_NOTES.md`? If so, add the entry now
before reporting done — see "Ongoing maintenance" below. Report RELEASE_NOTES as
current only after that check, not on the strength of the presence score alone.

## Ongoing maintenance — not just initial setup

`RELEASE_NOTES.md` isn't a one-time drop. Once a repo has one, keep it current:

- After any meaningful change to that repo — a fix, a feature, a behavior change,
  not a typo or formatting-only edit — add a new entry at the top before ending
  the turn. Don't wait to be asked. This applies whether or not repo-config was
  what put the file there in the first place; any repo with a `RELEASE_NOTES.md`
  qualifies.
- Match the format already in the file: dated, bolded inline category tag
  (`**Added:**` / `**Changed:**` / `**Fixed:**`), reasoning included, known
  limitations stated plainly rather than glossed over — see `references/examples.md`.
- Link the real commit/PR once the change is actually pushed; if it isn't pushed
  yet, log it without a link rather than inventing one.
- This was missed once already on repo-config's own `RELEASE_NOTES.md` — a real fix
  shipped with no entry, caught only because the repo owner pointed it out. That's
  the failure mode this rule exists to prevent.

## Rules
- Keep `RELEASE_NOTES.md` current, not just seeded — see "Ongoing maintenance"
  above.
- Every change to a target repo lands through a PR against the default branch, never
  a direct push. On green CI, merge with a **merge commit** (GitHub's "Create a merge
  commit" — merge and sync) — never squash-merge or rebase-merge. Full history is
  preserved deliberately. This is the standing workflow; don't re-ask it per repo.
- Never overwrite an existing file without `--force`; report what was skipped either
  way.
- Greenfield defaults are a starting point, not a final answer — say so in the
  re-audit output so a placeholder security contact doesn't get mistaken for a real
  one.
- Adapt, don't paste: once a real git remote exists, `{{OWNER_REPO}}` should get
  substituted for real, not left as a token.
- Match the tone the templates already model — see `references/examples.md`.

## Limitations
- Governance-file scaffolding plus basic CI. Unlike a public-launch OSS tool, this
  deliberately doesn't touch LICENSE, `.gitignore`, or anything aimed at going
  public (badges, release automation, star growth) — these are internal repos.
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
| `audit.sh` | Gap checklist against the 10 standard items, with a score | `[target-dir]` (default `.`) |
| `apply.sh` | Copies `assets/templates/` into target, substitutes placeholders, non-destructive by default | `<target-dir> [--config <file>] [--force]` |

Both scripts resolve their own root relative to their own location, so they run
whether this skill is installed or just checked out locally.
