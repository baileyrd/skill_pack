## Hoisting {{CAPABILITY}} into this repo

Duplicated (or converging on the same purpose) across: {{REPOS_LOCAL_NAMES}}.
See `duplication-audit.md` in the originating scan for the full comparison.

**Classification:** {{CLASSIFICATION}}
**Behavioral differences to reconcile:** {{BEHAVIORAL_DIFFERENCES}} <!-- blank if exact/near-duplicate -->

## Design

Mechanism goes here, not policy — per ADR-011's split. Configurable
knobs cover the behavioral differences above rather than this module
picking one consuming repo's opinion silently.

## Linked adoption issues

{{ADOPT_ISSUE_LINKS}} <!-- filled in after each consuming repo's issue exists -->

## Acceptance

- [ ] Public API covers every consuming repo's current usage (checked
      against each repo's local implementation, not assumed)
- [ ] Behavioral differences from the audit are resolved — either unified
      or exposed as an explicit, documented option
- [ ] Tests: happy path + boundary/failure cases
- [ ] Doc-comments on the new public surface
- [ ] `cargo clippy -- -D warnings` and `cargo fmt --check` clean
- [ ] `RELEASE_NOTES.md` entry added (if this repo has one)

<!--
Filed by the dedupe-loop skill from duplication-audit.md, only after the
user approved this cluster. Adoption issues in consuming repos should not
start work until this issue's PR has merged.
-->
