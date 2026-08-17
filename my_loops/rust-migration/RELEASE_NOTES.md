# Release Notes

rust-migration lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/rust-migration) —
this log tracks commits against `main`, same convention as
[parity-loop's RELEASE_NOTES.md](../parity-loop/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.3.0 — Don't depend on an executable bit the sync drops
**2026-08-17**

- **Added:** a first item in step 0's tooling preflight documenting how to restore the executable bit —
  `chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true`, with naming the
  interpreter (`bash scripts/x.sh`) as the fallback where the skill directory
  is read-only.
- **Why ([#1](https://github.com/baileyrd/skill_pack/issues/1)):** the sync
  that delivers a skill to a session doesn't preserve mode bits. Measured in a
  live session: **31 of 31 shebanged scripts across all ten skills arrive as
  `0644`**, so any step written `scripts/x.sh` fails with `permission denied`.
  The issue had recorded this as an occasional symptom; it is universal.
- **Scope note:** this documents a recovery rather than fixing the sync, which
  lives outside this repo. #1 stays open.

---

## v1.2.0 — Tooling preflight and an infrastructure stop condition
**2026-08-16**

- **Added:** a **tooling preflight** as the first bullet of step 0 — `command
  -v gh`, one cheap API read, and a note on which CI-status mechanism the
  target uses. The bullets it sits above all validate the *target*; this one
  validates the loop's own execution environment, which is what actually fails
  first when it fails.
- **Added:** an **infrastructure stop condition** — an unreachable or
  rate-limited GitHub API halts cleanly and reports three lists (completed, in
  flight with branch and PR named, never started) plus the retry path. Every
  other stop condition in this skill is about work state; this is the one where
  partial state exists and something can be stranded unnamed.
- **Added:** the preflight names the two CI-status traps by their symptom:
  a repo reporting via Actions checks returns `total_count: 0` from the
  commit-status endpoint (not evidence CI is missing), and runs associate to
  PRs by *branch*, so a stale run from an earlier PR on a reused branch can
  read as a pass for code it never ran against. Match by `head_sha`.
- **Documented:** which scripts require `gh`, in both the Scripts section and
  Limitations. Three of the four (`next_capability.sh`, `watch_and_merge.sh`,
  `scan_platform_repos.sh`) do; `check_manifest_coverage.sh` doesn't and keeps
  working without it.

**Evidence, stated honestly:** only `issue-loop` actually failed this way in a
live run — `gh` absent in a web session, so its scripts couldn't run and the
loop had to be re-derived mid-flight. The gap here was confirmed structurally
by reading this skill, not by a failing run of it. The change is documentation
only — no behavior changes and no scripts touched — so the cost of being wrong
is low, but it isn't the same grade of evidence
([#61](https://github.com/baileyrd/skill_pack/issues/61)).

---

## v1.1.2 — Description under claude.ai's upload limit
**2026-08-16**

- **Fixed:** the `description` was 1354 characters, over the 1024-character
  limit claude.ai enforces on skill upload, so the zip was rejected outright.
  Trimmed to 994 (30 characters of headroom) with every trigger phrase kept —
  the cuts are the capability-type list, and the sibling-skill/repo-config
  cross-reference already stated in the body. Nothing about what the skill
  does changed.
- **Context:** five skills here shipped over the limit at once, and none of the
  local tooling noticed: `install_skills.py` copies frontmatter without reading
  it, `build_skill_zips.py` zips it the same way, and Claude Code itself loads
  an over-length description fine. Only claude.ai rejects it, at upload, one
  file at a time. `check_repo.py`'s `manifests` check now enforces the limit so
  this fails locally and in CI instead.

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
