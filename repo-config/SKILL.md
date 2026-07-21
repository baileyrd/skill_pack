---
name: repo-config
description: Scans a repo and applies the standard governance file set — PR templates, issue templates, README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG, RELEASE_NOTES, ARCHITECTURE, and an ADR seed. Asks only what it can't infer from the scan, and falls back to greenfield defaults (modular monolith, ports-and-adapters, internal-only license line) for a brand-new repo with nothing yet to scan. Use whenever the user wants to set up repo standards, bootstrap a new repo, add PR/issue templates, run a "new repo checklist," or add any of CONTRIBUTING/SECURITY/ARCHITECTURE/CHANGELOG/RELEASE_NOTES — even if they only name one file, since this applies the whole set together.
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

Two files are worth hand-adapting after the copy rather than leaving as scaffold:
README's prose and ARCHITECTURE's boundary table. Match the tone in
`references/examples.md` — terse, reasoning included, honest about limitations.
Everything else in the set is close to drop-in once the tokens are substituted.

**4. Re-audit** — rerun `scripts/audit.sh <target>`, report the before/after score
and what's still manual (a placeholder security contact, README's Getting Started
section, ARCHITECTURE's boundary table, the first real ADR replacing the seed).

## Rules
- Never overwrite an existing file without `--force`; report what was skipped either
  way.
- Greenfield defaults are a starting point, not a final answer — say so in the
  re-audit output so a placeholder security contact doesn't get mistaken for a real
  one.
- Adapt, don't paste: once a real git remote exists, `{{OWNER_REPO}}` should get
  substituted for real, not left as a token.
- Match the tone the templates already model — see `references/examples.md`.

## Limitations
- Governance-file scaffolding only. Unlike a public-launch OSS tool, this
  deliberately doesn't touch LICENSE, `.gitignore`, CI workflows, or anything
  aimed at going public — these are internal repos.
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
