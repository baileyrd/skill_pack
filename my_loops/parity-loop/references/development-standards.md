# Development standards sources

Two external repos are the normative source for *development/architecture*
standards, consulted before writing new code — separate from governance
process (branching, PR mechanics, RELEASE_NOTES), which is `repo-config`'s
domain, not this skill's.

- **`Rusty-Mill/rusty_foundation_akb`** — the RustyMill org's architecture
  knowledge base: project charter, capability model, architecture
  principles, ecosystem/repository-strategy docs. Currently in "foundation /
  specification" phase — read for intent and vocabulary, not a finished
  pattern catalog.
- **`baileyrd/Atlas_Engineering_Standards_Library`** — a personal normative
  standards library, numbered `ATLAS-###` requirements with RFC-style
  `MUST`/`SHOULD`/`MAY` language (foundation, architecture, versioning, Rust
  workspace/Cargo, SDK, security, toolchain, plugin/extension, ecosystem,
  reference architectures). Most volumes are still `Seed`/`Draft 0.1` as of
  when this was written — a gap means "not yet specified," not "anything
  goes."

## When to consult them

Before implementing (after triage/classification and the reuse check, before
writing code): check whether either repo already has an applicable
requirement or architectural constraint for the area being touched. If one
exists, it governs the implementation — conform to it and cite the
requirement ID (`ATLAS-###`) or doc section in the commit message / PR
description. If neither speaks to the situation, fall back to this repo's
own conventions (`Result`+`?`, no `unwrap()`/`expect()` outside tests,
doc-comments, tests for happy path + boundary/failure), same as the sibling
loop skills already require.

## Caveats

- Don't quote large blocks of either repo verbatim — cite the requirement
  ID/section and summarize in this repo's own words.
- A standards gap doesn't license inventing a requirement — it means the
  fallback convention applies, worth noting as such rather than presented
  as if a real standard specified it.
- Neither repo governs process — that stays `repo-config`'s and this
  skill's own domain (branch/PR/merge mechanics, issue triage).
- **The Rust standard library (`std`, `core`, `alloc`) is never a
  hand-roll or sovereignty-swap target.** It isn't an external dependency
  in the sense either standard is concerned with — it ships with the
  toolchain, carries none of the supply-chain trust/re-verification cost a
  crates.io dependency does, and using it directly is always in scope.
  None of the loop skills should flag `std` usage as a gap to fill, a
  dependency to audit for internal coverage, or something to
  consolidate/hoist.
