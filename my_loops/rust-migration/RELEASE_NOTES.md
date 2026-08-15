# Release Notes

rust-migration lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/rust-migration) —
this log tracks commits against `main`, same convention as
[parity-loop's RELEASE_NOTES.md](../parity-loop/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.1.1 — Declare jq and ripgrep
**2026-08-15**

- **Fixed:** the Scripts note said "shell out to `gh`/`git` (or plain text
  parsing for the coverage check) only — no extra dependencies."
  `next_capability.sh:26` requires **`jq`**; `scan_platform_repos.sh:56`
  uses **`ripgrep`** when present, `grep` otherwise.
- Found by `docs-loop` row 5.

## v1.1.0 — Wire skill-retro into step 4's wrap-up
**2026-08-13**

- **Added:** step 4 now runs a `meta/skill-retro` pass on `rust-migration`
  itself, evidence-grounded in the run that just finished, right after the
  coverage-gated wrap-up report — regardless of whether the run ended in a
  full migration, a partial one, or a stop. Read-only, runs unattended in
  either harness mode; applying anything it finds is still its own
  separate, explicitly-approved change, never bundled into finishing a
  migration.
- This is the first real instance of the wiring both `skill-retro` and
  `learn-it`'s "Limitations" sections named as a deliberate follow-up
  rather than something either meta-skill sets up on its own — a one-line
  addition to a target skill's own "Wrap up" step, not a `settings.json`
  hook.

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
