## Capability

**{{CAPABILITY_ID}}**: {{CAPABILITY}}

**Category:** {{CATEGORY}} <!-- interface / config / behavior -->
**Source:** {{SOURCE}} <!-- interface / code / test / docs / combination, from capability-manifest.md -->
**Existing RustyMill impl:** {{RUSTYMILL_IMPL}} <!-- sibling repo, or "none found" -->

## Why this is required

This capability is present in the source repo and defaults to **REQUIRED**
under the migration's boundary contract — it does not get dropped, stubbed,
or simplified without an explicit, user-attributed line in
`capability-manifest.md` moving it to `OUT-OF-SCOPE`. If closing this issue
without full parity seems tempting for any reason, that's a stop-and-ask,
not a call to make unilaterally.

## Source reference

{{SOURCE_LOCATION}} <!-- file/line, route, test name, or doc section in the source repo -->

## Acceptance

- [ ] Implemented — ported and adapted from the RustyMill sibling above if
      one was found, otherwise written fresh — preserving the source's
      behavior for this capability (idiomatic Rust is the *how*, not
      license to change the *what*)
- [ ] Parity test written, demonstrating this specific capability matches
      the source repo's behavior (ported from the source's own test if one
      exists, else written from the behavior spec)
- [ ] Doc-comment on the new public surface
- [ ] `cargo clippy -- -D warnings` and `cargo fmt --check` clean
- [ ] `RELEASE_NOTES.md` entry added (if the repo has one)
- [ ] `capability-manifest.md` row {{CAPABILITY_ID}} updated to `DONE` with
      this PR and the parity test name in the Evidence column

<!--
Filed by the rust-migration skill from capability-manifest.md. This issue
does not close on "it compiles" — the parity test is the acceptance bar.
If completing this turns out to require a breaking change to the target's
already-shipped public surface, or a new dependency, that's a stop-and-ask,
not an auto-implement. If RUSTYMILL_IMPL names a repo, copying the code in
is fine unattended; *depending on* that repo as a crate is its own
stop-and-ask, same as any new dependency.
-->
