# Development standards sources

Two external repos are the normative source for *development/architecture*
standards — including whatever they specify about documentation itself
(required sections, doc-comment expectations, ADR conventions, versioning
language). Governance *process* (branching, PR mechanics, RELEASE_NOTES
format) is `repo-config`'s domain, not this skill's.

- **`Rusty-Mill/rusty_foundation_akb`** — the RustyMill org's architecture
  knowledge base: project charter, capability model, architecture
  principles, ecosystem/repository-strategy docs. Currently in "foundation /
  specification" phase — read for intent and vocabulary, not a finished
  pattern catalog. Useful here mainly as the source of the *right words* for
  a capability an ARCHITECTURE.md is describing loosely.
- **`baileyrd/Atlas_Engineering_Standards_Library`** — a personal normative
  standards library, numbered `ATLAS-###` requirements with RFC-style
  `MUST`/`SHOULD`/`MAY` language (foundation, architecture, versioning, Rust
  workspace/Cargo, SDK, security, toolchain, plugin/extension, ecosystem,
  reference architectures). Most volumes are still `Seed`/`Draft 0.1` as of
  when this was written — a gap means "not yet specified," not "anything
  goes."

## When to consult them

Twice in a docs-loop run, for different reasons:

1. **Step 3, classifying** — before marking a doc *stale* for saying
   something a standard actually requires. If ARCHITECTURE.md asserts a
   constraint the code doesn't yet honor, and `ATLAS-###` requires that
   constraint, the finding is "code doesn't meet the standard yet" (a
   stop-and-ask, handed back), not "doc is wrong, correct it downward."
   Quietly relaxing a documented requirement to match non-conforming code is
   the worst outcome this loop can produce.
2. **Step 4, writing** — before asserting a documentation requirement as
   this skill's own opinion. If either repo specifies the shape of the thing
   being written, conform and cite the requirement ID (`ATLAS-###`) or doc
   section, the same way `repo-config` cites rather than asserts in
   ARCHITECTURE.md.

If neither repo speaks to the situation, fall back to this repo's own
conventions — terse, reasoning included, honest about limitations — same as
the sibling loop skills already require.

## Caveats

- Don't quote large blocks of either repo verbatim into a target repo's
  docs — cite the requirement ID/section and summarize in the target's own
  words.
- A standards gap doesn't license inventing a requirement, and it especially
  doesn't license *documenting* one. "Not yet specified" written into a
  README reads to every future reader as settled policy.
- Neither repo governs process — that stays `repo-config`'s domain
  (branch/PR/merge mechanics, the governance file set itself).
- A standard describes what the code *should* do. Documentation describes
  what it *does*. When those differ, docs-loop reports the gap; it never
  closes it by writing the aspirational version in the present tense.
