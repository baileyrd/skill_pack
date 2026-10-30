# Step 1: the three assessment paths

Read this in step 1 for the path step 0 chose. Each produces a *candidate*
list; the judgment pass in `SKILL.md` step 1 applies to all three.

- **Roadmap-defined scope**: audit the roadmap's stated items against the
  target's current implementation — done / partial / not started. A partial
  item gets the same judgment pass as below (does finishing it stay additive,
  or does it touch an existing signature).
- **Comparable reference surface exists** (a crate/package shaped enough like
  the target to diff — e.g. `libc` against a from-scratch libc reimplementation
  that's far enough along to have a real public surface): `cargo public-api`
  against the pinned reference version and the target (`cargo install
  cargo-public-api` if missing — check `cargo public-api --help` for current
  flags), diffed by symbol name (ignore module path). This is a *candidate*
  list, not a final one — expect noise from platform-`cfg`'d items and
  type/const-only entries. Only use this path when step 0 didn't already
  settle scope from a roadmap; a diff is a way to *discover* candidates, not
  to override an already-defined scope.
- **No comparable surface to diff, and no roadmap** (a spec, man pages, or a
  target too early-stage to have anything a tool can diff against): extract
  required capabilities by reading the reference directly. This is a
  documentation-driven judgment pass, not a fallback to apologize for — it's
  the normal path whenever there's nothing structurally comparable to run
  `cargo public-api` against.
