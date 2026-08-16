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
- None of the 11 standard items from `audit.sh` already present
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

## Multi-product repos

A monorepo or a merged workspace can already carry the standard set *below* the
root. `audit.sh` only looks at the root, so it reports those files as missing
and the natural next move — seed them — silently creates a competing second
(or third) series.

Observed in `baileyrd/rusty_recall`, which merged two previously separate repos
(`rusty_remind_me`, `rusty_dbs`) keeping each half under its own prefix:

| Found | Consequence of seeding the root blind |
|---|---|
| `remind_me/docs/adr/` and `dbs/docs/adr/`, **each numbered from 0001** | a *third* ADR series, also `0001-…`, with nothing saying which of the three a reader should look in |
| `remind_me/RELEASE_NOTES.md`, `dbs/RELEASE_NOTES.md` | a root notes file with no stated relationship to the two below it |
| `dbs/CHANGELOG.md` | same, for changes |

**Ask, don't assume** — these are the questions the scan can't answer:

1. Should there be a root ADR series at all, given the per-product ones exist?
2. If yes, what is its **remit**, so a reader knows which series a decision
   belongs in? The workable answer there was "decisions belonging to the
   repository rather than to either product," seeded with the merge ADR itself.
3. Do root `RELEASE_NOTES.md` / `CHANGELOG.md` track the **repository**, the
   **products**, or both — and does the root supersede the per-product files or
   sit alongside them?

Whatever is decided, **write the scope down in the file itself** rather than
leaving it to be inferred: a remit line in the root ADR series, and an explicit
pointer in each root notes file to the per-product ones. Two files that don't
say which is authoritative are worse than one.

On numbering: if per-product ADR series already start at 0001, a root series
starting at 0001 too is legal but reads as a collision. Either give the root
series an explicit remit line at the top, or start it at a distinct offset —
state the choice rather than letting the next reader reverse-engineer it.

Note the audit scores 11/11 either way. Nothing in the number distinguishes a
thoughtful placement from files that contradict the ones a level down, which is
why this is a step 2 question rather than something to infer from the score.
