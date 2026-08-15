# Ground-truth sources

docs-loop step 1 builds its picture of the repo from these, **before** opening
any prose doc. The ordering principle throughout: *an artifact you can execute
or parse beats an artifact you have to believe.*

## Repo-wide, any stack

| Question the docs answer | Authoritative source |
| --- | --- |
| What is this project called, what version is it | Manifest (`Cargo.toml`, `pyproject.toml`, `package.json`, `go.mod`) — not the README heading |
| What does it depend on | The manifest's dependency tables, plus the lockfile for what's actually resolved |
| What's the directory layout | `git ls-files` / the real tree — never a hand-drawn tree block in a README, which is the single most reliably stale thing in any repo |
| What commands exist for developers | `scripts/`, `Makefile`/`justfile` targets, manifest script sections, and `.github/workflows/*` — CI is the honest answer to "how do you test this", since it's the version that has to keep working |
| What CI actually enforces | `.github/workflows/*.yml` job steps, plus which checks are required in branch protection |
| What the entry points are | Manifest `[[bin]]`/`[project.scripts]`/`"bin"`, `main.rs`/`__main__.py`/`index.ts` |
| What flags/subcommands exist | `--help` output from an actual run; the arg-parser definition if running isn't possible |
| What env vars are read | A grep for the env-reading call (`std::env::var`, `os.environ`, `process.env`) — env vars are chronically under-documented and this catches the whole set |
| What decisions were made and why | `docs/adr/` — authoritative for *decisions*, see the caveat below |
| What changed recently | `git log` since the doc's last change, merged PR titles, `CHANGELOG.md`/`RELEASE_NOTES.md` newest entries |

## Per stack

- **Rust** — `cargo metadata --no-deps` for the parsed manifest; `cargo
  doc`/the `///` and `//!` comments for the public API surface; `pub` items
  in `lib.rs`/`mod.rs` for what's actually exported (a doc describing a
  module that isn't `pub` is documenting something no caller can reach);
  feature flags in `[features]`, which READMEs routinely list wrong.
- **Python** — `pyproject.toml` for name/version/entry points/optional
  extras; `__all__` and module docstrings for the public surface; the
  installed console-script names, not the ones the README claims.
- **Node/TS** — `package.json` `scripts`, `exports`, `bin`, and `engines`
  (documented Node version requirements drift constantly); `tsconfig.json`
  for what's actually compiled.
- **Shell-script repos (this one included)** — the scripts' own `--help`
  block and argument parsing are the contract; a usage line in a README is
  a copy, and copies rot.

## The ADR caveat

The ADR log is ground truth for **decisions**, not for **current behavior**.
Three distinct situations that look identical if you don't check both:

1. ADR accepted, implemented, docs match → accurate.
2. ADR accepted, never implemented, docs describe it in the present tense →
   **aspirational**, not accurate. The docs need a tense/status fix; whether
   to build the thing is a separate, human decision.
3. ADR superseded by later work, docs still describe the old decision →
   **stale**. Fix the docs, and note that the ADR log needs a superseding
   entry — never edit the original ADR (docs-loop Rules).

## What is not ground truth

- Another doc. Chasing README → CONTRIBUTING → ARCHITECTURE in a circle
  confirms only that they agree with each other, which stale docs reliably
  do.
- Commit messages and PR descriptions. Good evidence of *intent* and useful
  for finding what changed; not evidence the merged code does it.
- Comments near the code, other than doc-comments on the public surface —
  they're prose too, and they drift the same way. Useful as a lead, checked
  against the code like anything else.
- This skill's own memory of the repo from earlier in the session. Re-read
  when in doubt; the cost of a second look is far below the cost of writing
  a confident wrong sentence into a README.
