# Architecture

## Overview
skill_pack is a personal collection of [Claude Agent Skills](https://support.claude.com/en/articles/12512176-what-are-skills) — self-contained directories of instructions (`SKILL.md`), scripts, and reference material that Claude Code, OMP, and claude.ai load dynamically for specialized tasks. It is not a running service: nothing in this repo executes on its own between invocations; a skill only does something when an external harness reads and loads it.

What it's not: a shared library that skills import from one another, or a single deployable artifact. Each skill is designed to be copied or zipped and consumed independently — into Claude Code's `~/.claude/skills/<name>/` tree, OMP's `claude` discovery provider, or a claude.ai/Desktop Skill ZIP upload.

## Boundaries
Skills here don't depend on each other across a process, service, or crate boundary, so `ATLAS-100` (Architecture)'s own trigger clause hasn't fired: *"When Atlas has two or more real components that must depend on each other ... forcing an actual choice about layering and dependency direction ... Until then, [ATLAS-001 Part IV's] general principles already govern; this volume would only restate them speculatively."* Falling back to a generic ports-and-adapters split here would itself violate `ATLAS-PHIL-0102` (Justified Complexity: *"New process, tooling, or abstraction MUST be justified by a demonstrated, current need"*) — there's no I/O boundary to abstract, since a skill's only "input" is the harness reading its files off disk.

The real, checkable contract is between each skill directory and the harnesses that consume it:

| Port | Adapter(s) | Notes |
| ---- | ---------- | ----- |
| Skill manifest (`SKILL.md` frontmatter: `name`, `description`, `version`) | Claude Code discovery, OMP's `claude` provider (priority 80), claude.ai/Desktop Skill ZIP upload | One manifest format serves three independent consumers — see `scripts/install_skills.py` and `scripts/build_skill_zips.py` for how each target is produced |
| Skill implementation (`scripts/`, `references/`, `assets/`) | Whatever that skill needs — shell/Python scripts, markdown references, template payloads | No shared runtime; a skill's own `scripts/` never imports from a sibling skill |

## Structure
Two category folders (`my_loops/`, `yt_research_for_cc/`), each holding independently-versioned skill directories, plus repo-wide tooling under `scripts/`. There is no modular-monolith-vs-service question to answer yet — see Boundaries above for why the generic architecture default doesn't apply as written here; it would apply the moment two skills need to share code across a real dependency edge, at which point `ATLAS-100` becomes the reference to consult, not this repo's own opinion.

## Data flow
No request/event flow at repo level — this is a static, versioned file tree consumed on demand by an external harness. `scripts/install_skills.py` mirrors it into `~/.claude/skills/`; `scripts/build_skill_zips.py` packages it for the claude.ai/Desktop upload path. See the root README's "Repo tooling" section for the full walkthrough.

## Key decisions
See [docs/adr/](./docs/adr/) for the record of individual decisions and their tradeoffs.

## Non-goals
- Not a shared code library — skills intentionally don't import from one another, so there is no cross-skill API surface to keep stable.
- Not a deployable service — nothing here runs continuously; `scripts/*.py` are one-shot tooling invoked by hand.
- `notebooklm` is excluded from this repo's own versioning/authoring conventions — it's vendored from the third-party `notebooklm-py` package and should never be hand-edited (see [`yt_research_for_cc/README.md`](yt_research_for_cc/README.md)).
