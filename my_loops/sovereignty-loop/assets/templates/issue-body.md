## Dependency

`{{DEPENDENCY}}` — {{PURPOSE}}

**Classification:** {{CLASSIFICATION}} <!-- covered / partial / hand-roll candidate -->
**Internal candidate:** {{INTERNAL_CANDIDATE}} <!-- blank for hand-roll -->
**Action:** {{ACTION}} <!-- swap-to-internal / extend-and-swap / hand-roll -->

## Why

{{NOTES}}

## Acceptance

- [ ] External import/usage of `{{DEPENDENCY}}` replaced (fully, or per the
      partial-coverage scope noted above)
- [ ] Existing test suite still passes; new tests added for anything new
      (happy path + boundary/failure cases)
- [ ] Doc-comment on any new public surface
- [ ] `cargo clippy -- -D warnings` and `cargo fmt --check` clean
- [ ] Manifest updated — dependency removed or narrowed, not just unused
- [ ] `RELEASE_NOTES.md` entry added (if the repo has one)

<!--
Filed by the sovereignty-loop skill from dependency-audit.md, only after the
user approved this row. Not auto-generated from classification alone.
-->
