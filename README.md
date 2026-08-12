# skill_pack

Personal collection of [Claude Agent Skills](https://support.claude.com/en/articles/12512176-what-are-skills) — folders of instructions, scripts, and resources that Claude Code / OMP / Claude.ai load dynamically for specialized tasks. Most skills here are authored in this repo; `notebooklm` is vendored from a third-party package and should never be hand-edited (see [`yt_research_for_cc/README.md`](yt_research_for_cc/README.md)).

Skills are grouped by category folder; see each category's own README for dependencies specific to it.

## Categories

### [`my_loops/`](my_loops) — autonomous repo-maintenance loops

Bounded, unattended "work the backlog" loops for the Rusty-Mill/baileyrd platform repos — assess or triage, check for existing coverage before writing anything, act (issue → implement → PR → green CI → merge → sync), repeat until done.

| Skill | Does |
|---|---|
| [`parity-loop/`](my_loops/parity-loop) | Closes capability gaps against a reference API/spec: assess → check sibling repos for something to port → file issues → implement/port → PR → merge → repeat. |
| [`dedupe-loop/`](my_loops/dedupe-loop) | Finds duplicate/near-duplicate implementations across repos and proposes hoisting the genuine duplicates into a shared platform module. |
| [`sovereignty-loop/`](my_loops/sovereignty-loop) | Audits external dependencies, checks whether the platform ecosystem already covers the same capability, proposes swap-to-internal or a scoped hand-rolled replacement. |
| [`issue-loop/`](my_loops/issue-loop) | Clears a target repo's open GitHub issue backlog end-to-end — triage, reuse-check, implement, PR, merge on green CI, repeat. |
| [`repo-config/`](my_loops/repo-config) | Scans a repo and applies the standard governance file set (PR/issue templates, README, CONTRIBUTING, SECURITY, CHANGELOG, ARCHITECTURE, ADR seed). |

### [`yt_research_for_cc/`](yt_research_for_cc) — YouTube research pipeline

Three skills that chain into an unattended YouTube research pipeline: search, curate, and hand off to NotebookLM for analysis and deliverables.

| Skill | Does |
|---|---|
| [`yt-search/`](yt_research_for_cc/yt-search) | Searches YouTube via `yt-dlp`, returns structured results with an engagement (views/subscribers) ratio. |
| [`notebooklm/`](yt_research_for_cc/notebooklm) | Full programmatic access to Google NotebookLM — notebooks, sources, chat, and every artifact type. Vendored from the third-party `notebooklm-py` package. |
| [`yt-pipeline/`](yt_research_for_cc/yt-pipeline) | Orchestrates the two above: topic → search → auto-select best videos → NotebookLM notebook → analysis → optional deliverable. |

## Versioning

Every authored skill's `SKILL.md` frontmatter carries a `version:` field (semver, bumped by hand on meaningful changes), and a `RELEASE_NOTES.md` next to it logs what changed and why — reverse chronological, one entry per change, modeled on `repo-config`'s original log. `notebooklm` is the one exception: it's vendored from `notebooklm-py`'s own release, carries that package's version instead, and isn't versioned independently here.

## Repo tooling

Three standalone scripts under `scripts/`, each usable on its own or chained — `install_skills.py` and `build_skill_zips.py` both call `restore_exec_bits.py` automatically, so a plain `git add -A && python scripts/install_skills.py` (or `build_skill_zips.py`) is enough day to day.

### `scripts/install_skills.py`

Installs/updates/replaces every skill directly into Claude Code's `~/.claude/skills/<name>/`. OMP's own `claude` discovery provider (priority 80) reads that exact same tree automatically, so this one target covers **Claude Code and OMP together** — no separate OMP step. Mirrors each skill's contents: adds new files, updates changed ones, removes files no longer in the source.

```bash
git add -A
python scripts/install_skills.py [--dry-run] [--target DIR]
```

`claude.ai` and Claude Desktop have no scriptable install path — both only accept a Skill ZIP through their own Settings UI — so they're out of scope for this script; use `build_skill_zips.py`'s output and upload by hand.

### `scripts/build_skill_zips.py`

Packages every skill (any directory containing a `SKILL.md`) into an installable, version-tagged zip under `zip/` at the repo root (e.g. `zip/dedupe-loop-v1.0.0.zip`; `notebooklm.zip` has no version suffix since it isn't versioned here). Each archive's single top-level entry is the skill directory itself, matching the [Skills API upload format](https://platform.claude.com/docs/en/build-with-claude/skills-guide) so an archive can be uploaded as-is to claude.ai / Claude Desktop / the Skills API.

```bash
git add -A
python scripts/build_skill_zips.py
```

`zip/` is generated output and is gitignored, not committed.

### `scripts/restore_exec_bits.py`

This repo runs with `core.fileMode=false` and is worked on from Windows, so `git add` never derives a file's executable bit from the OS — a moved or copied file lands in the index as `100644` even if the identical content was `100755` at `HEAD`. This script re-marks staged files `+x` by matching git blob content (not path) against `HEAD`'s tree, so it survives renames and directory reshuffles. Run standalone with `python scripts/restore_exec_bits.py [--dry-run]`, or let the other two scripts call it automatically.

## Install

- **Claude Code / OMP:** `python scripts/install_skills.py` (see above).
- **claude.ai / Claude Desktop:** build zips with `python scripts/build_skill_zips.py`, then Settings → Skills → upload the relevant `zip/<name>.zip`.
- **Manual:** copy any skill folder to `~/.claude/skills/<name>/` yourself.

## Architecture
See [ARCHITECTURE.md](./ARCHITECTURE.md) for how the repo is organized and why it doesn't use a service-style boundary pattern.

## Contributing
See [CONTRIBUTING.md](./CONTRIBUTING.md).

## Security
See [SECURITY.md](./SECURITY.md) to report a vulnerability.

## License
Internal — not for external distribution.
