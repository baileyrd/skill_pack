# Development standards sources

Two external repos are the normative source for *development/architecture*
standards — separate from this skill's own *governance-process* scaffolding
(PR/issue templates, branch/merge workflow, RELEASE_NOTES convention), which
stays exactly as documented in SKILL.md. Don't conflate the two: repo-config
generates the governance files itself; these repos inform what goes in
ARCHITECTURE.md's content and the greenfield architecture defaults.

- **`Rusty-Mill/rusty_foundation_akb`** — the RustyMill org's architecture
  knowledge base: project charter, capability model, architecture principles,
  ecosystem/repository-strategy docs. Currently in "foundation / specification"
  phase — read it for intent and vocabulary, not for a finished pattern
  catalog.
- **`baileyrd/Atlas_Engineering_Standards_Library`** — a personal normative
  standards library, numbered `ATLAS-###` requirements with RFC-style
  `MUST`/`SHOULD`/`MAY` language, organized in volumes (foundation,
  architecture, versioning, Rust workspace/Cargo, SDK, security, toolchain,
  plugin/extension, ecosystem, reference architectures). Most volumes are
  still `Seed` or `Draft 0.1` status as of when this was written — treat
  absence of a requirement as "not yet specified," not as "anything goes."

## When to consult them

- **Step 2 (architecture default / boundary pattern)** — before falling back
  to the greenfield defaults in `scan-and-defaults.md` (modular monolith,
  ports-and-adapters), check whether either standards repo already has a
  more specific applicable requirement for the target repo's stack (e.g. an
  `ATLAS-300`-series Cargo/workspace rule, or a `rusty_foundation_akb`
  capability-model constraint). A specific standard wins over the generic
  default; the generic default is the fallback when neither repo speaks to
  the situation.
- **ARCHITECTURE.md generation** — the boundary-table guidance
  (`references/examples.md`) should note the governing `ATLAS-###`
  requirement ID(s) or `rusty_foundation_akb` doc section where one applies,
  so the file stays traceable to its source rather than reading as an
  opinion this skill invented.
- **Loop-skill implementation work** (parity-loop / sovereignty-loop /
  dedupe-loop / issue-loop) — these consult the same two repos before writing
  new code; this file is the shared description of what's in each, so it
  isn't re-explained four times.

## Caveats

- Both repos are early-stage (spec-only / draft volumes) — expect gaps.
  A gap here is not license to invent a standard; it means the fallback
  default applies and is worth flagging as such rather than silently
  treated as a confirmed standard.
- Don't quote large blocks of either repo verbatim into a generated file —
  cite the requirement ID or doc section and summarize in this repo's own
  words, same as any other external source.
- Neither repo governs process (branching, PR/merge mechanics, issue
  templates) — that's this skill's own domain, untouched by either.
- **The Rust standard library (`std`, `core`, `alloc`) is never a
  hand-roll or sovereignty-swap target for the loop skills that consult
  this file.** It isn't an external dependency in the sense either
  standard is concerned with — it ships with the toolchain and using it
  directly is always in scope. Worth stating here since this file is their
  shared reference point.
