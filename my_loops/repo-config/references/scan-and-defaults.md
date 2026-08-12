# Scan signals, Q&A, and greenfield defaults

## Scan signals → what they answer

| Signal | Source | Answers |
| --- | --- | --- |
| `git remote get-url origin` | git | `{{OWNER_REPO}}`, and `{{SECURITY_CONTACT}}` (defaults to the repo owner) |
| `Cargo.toml` / `pyproject.toml` / `package.json` present | filesystem | language, likely test/build command for README |
| Existing `.github/`, README, etc. | `audit.sh` | what's already covered — never regenerate these without `--force` |
| Commit count / repo age | git | a rough greenfield signal alongside "no manifest, no standard files" |

## Greenfield check

A repo counts as greenfield when **all** of these hold:
- No stack manifest (`Cargo.toml`, `pyproject.toml`, `package.json`, etc.)
- None of the 10 standard items from `audit.sh` already present
- No `git remote origin` configured yet

When greenfield, skip the Q&A round in step 2 entirely — there's nothing to ask
about yet that the person would have a real answer for — and generate straight from
these defaults:

Before applying the architecture default or boundary pattern below, check
`references/development-standards.md` — the two external standards repos it
covers take precedence over these generic fallbacks whenever they specify
something more concrete for the target's stack.

| Field | Greenfield default |
| --- | --- |
| License line (README) | `Internal — not for external distribution` |
| Architecture default | Modular monolith. Extract a separate service only for a concrete forcing function — independent scaling, a team/language boundary, or hard fault isolation. (Fallback only — see `references/development-standards.md` first.) |
| Boundary pattern | Ports-and-adapters — domain logic stays free of I/O and framework details. (Fallback only — see `references/development-standards.md` first.) |
| `{{OWNER_REPO}}` | `<fill in once a git remote is set>` |
| `{{SECURITY_CONTACT}}` | `<fill in — no git remote yet to derive an owner from>` |
| PR templates | All four: feature, bug_fix, docs, chore |
| Issue templates | Both: bug_report, feature_request (+ config.yml) |
| ADR log | Seed `0001-template.md` as-is — first real decision replaces it |
| README Getting Started | Left as a placeholder — nothing to show yet |

These defaults exist so a brand-new repo isn't blocked on questions nobody can
answer yet. Say so explicitly in the re-audit output (step 4) — a greenfield repo
should come back to `{{OWNER_REPO}}` and the security contact once they're real,
not treat the defaults as final.

## Non-greenfield: what to actually ask

Once there's *something* to scan, ask only what the scan left unanswered — batch
into one round, skip anything already inferred:

- One-line project description for README — the scan can suggest a stack-based
  guess but shouldn't assert one
- A non-standard test/build command, if the manifest's scripts don't make it obvious

Security contact is never asked here — it defaults to the repo owner resolved
from `{{OWNER_REPO}}`'s `git remote`. Only surface it as a question if the
user explicitly wants a different contact (a team alias instead of the
owner, for instance).

Don't ask about license, architecture pattern, or template selection — those follow
the greenfield defaults unless the person says otherwise, even in a non-greenfield
repo, since they're standing engineering principles rather than per-repo choices.
