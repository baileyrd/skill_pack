# Release Notes

rust-migration lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/rust-migration) —
this log tracks commits against `main`, same convention as
[parity-loop's RELEASE_NOTES.md](../parity-loop/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.0.0 — Initial release
**2026-08-13**

- **Added:** first cut of the skill. Built to close a recurring failure
  mode observed across prior repo/application-to-Rust migrations: a
  capability of the source repo gets quietly treated as optional — dropped,
  stubbed, or deferred — instead of being carried over, and the migration
  gets reported done anyway.
- **Core mechanism:** the boundary contract — every capability discovered in
  step 1 defaults to `REQUIRED` in `capability-manifest.md`; the only path
  to `OUT-OF-SCOPE` is an explicit, written, user-attributed line, never
  inferred by Claude. `scripts/check_manifest_coverage.sh` makes this a
  mechanical gate rather than an honor system: it fails loudly if any row
  isn't `DONE` (with evidence) or `OUT-OF-SCOPE` (with a reason), and
  step 4 refuses to report the migration finished while it fails.
- Loop mechanics (issue → branch → implement → PR → watch → merge → sync),
  platform-sibling reuse check, and development-standards lookup are
  adapted from `parity-loop`/`issue-loop` — same companion family, same
  PR/CI/merge conventions.
- `references/source-extraction-playbook.md` is new to this skill family: a
  per-source-language checklist (Python, Node, Go, JVM, Ruby) for
  extracting the interface/config/behavior surface that migrations from
  non-Rust codebases need but the existing loop skills (which mostly
  operate within already-Rust platform repos) never had to cover.
