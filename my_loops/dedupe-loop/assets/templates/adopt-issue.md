## Adopting {{CAPABILITY}} from {{HOIST_TARGET}}

This repo's local `{{LOCAL_NAME}}` duplicates (or converges with) the
version being hoisted into {{HOIST_TARGET}}: {{HOIST_ISSUE_LINK}}.

**Do not start this issue until the hoist-target PR above has merged** — see
`dedupe-loop`'s Rules on sequencing.

## Work

- [ ] Pin to {{HOIST_TARGET}}'s new module (existing ADR-011-style
      dependency mechanism — git rev / path dep / internal registry,
      whichever this repo already uses)
- [ ] Replace `{{LOCAL_NAME}}` usage with the hoisted module, keeping only
      whatever thin repo-specific policy layer stays local
- [ ] Delete the now-dead local implementation in this same PR — no
      leftover copy
- [ ] Existing tests still pass; add coverage for anything the swap changes
- [ ] `cargo clippy -- -D warnings` and `cargo fmt --check` clean
- [ ] `RELEASE_NOTES.md` entry added (if this repo has one)

<!--
Filed by the dedupe-loop skill from duplication-audit.md, only after the
user approved this cluster.
-->
