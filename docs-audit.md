# docs-audit.md

**Run:** 2026-08-15 against `462d704` · **Scope:** whole repo (95 tracked docs)
**Counts:** 3 stale · 1 missing · 1 orphaned · 3 aspirational · 0 unverifiable · 4 accurate

## Findings

| Doc | Where | Claim | Classification | Ground truth | Fix | Size |
| --- | --- | --- | --- | --- | --- | --- |
| README.md | intro, L5 | "see each category's own README for dependencies specific to it" | stale | `meta/` and `web_dev/` have no README; `my_loops/README.md` is a 1-line stub. Only `yt_research_for_cc/README.md` (72 lines) delivers | Name the one category that has one, or write the two missing | S |
| my_loops/README.md | whole file | `# skill_pack` | orphaned | It's a category folder, but the file contains the *root repo's* title and nothing else — a copy-paste stub never filled in | Write a real category README, or delete it | S |
| README.md | Repo tooling, L78 | "e.g. `zip/dedupe-loop-v1.0.0.zip`" | stale | dedupe-loop is v1.1.1; `build_skill_zips.py` now emits `dedupe-loop-v1.1.1.zip` | Drop the version from the example so it can't rot again | S |
| ARCHITECTURE.md | Structure, L19 | "Four category folders (…), plus repo-wide tooling under `scripts/`" | missing | Accurate as far as it goes, but `need_to_productize/` (4 `.skill` archives) and `trying/` (3) are tracked top-level dirs named in **no doc at all** — `grep` across README/ARCHITECTURE/CONTRIBUTING/docs returns nothing | One sentence saying what they are and why they're not categories | S |
| CONTRIBUTING.md | Review, L28 | "CI must be green before merge" | aspirational | No `.github/workflows/` exists. No manifest, so `repo-config` deliberately added none. Six PRs merged today with no CI at all | Stop-and-ask: add CI, or say this repo has none | S |
| CONTRIBUTING.md | Standards, L13 | "Add tests for non-trivial logic — happy path and at least one failure/boundary case" | aspirational | No test directory, no runner, no test file anywhere in the tree | Stop-and-ask: same shape as above | S |
| ARCHITECTURE.md | Key decisions, L25 | "See `docs/adr/` for the record of individual decisions and their tradeoffs" | aspirational | `docs/adr/` holds exactly one file: `0001-template.md`, an unfilled seed (`# ADR-0001: <Title>`). No decision is recorded | Stop-and-ask: several real decisions were made today that would be ADR-0002 | M |
| README.md | Categories tables | all 14 skills listed | accurate | 14 `SKILL.md` files, 14 table rows, names match | none | — |
| README.md | Repo tooling, L63 | "Three standalone scripts under `scripts/`" | accurate | Exactly 3: `build_skill_zips.py`, `install_skills.py`, `restore_exec_bits.py` | none | — |
| README.md | Versioning, L58 | notebooklm is the one unversioned exception | accurate | It's the only skill with no `version:` and no `RELEASE_NOTES.md` | none | — |
| 5 × `check_references` broken rows | — | — | accurate (non-findings) | Each names a *different* component's or repo's path — the structural false-positive class docs-loop's Limitations already documents | none | — |

## Auto-eligible vs. always-waits

Under `LOOP_HARNESS_MODE=auto`, rows 1, 3 and 4 (the two stale facts and the
missing-directories sentence) would proceed unattended — each is transcription
from a verifiable source. Rows 2, 5, 6 and 7 always wait in either mode:
deleting a doc file, and three `aspirational` rows where the question is
whether to build the thing or document its absence.

`LOOP_HARNESS_MODE` is unset for this run, so **nothing proceeds without a pick.**

## Where the code is the suspect party

One row, reported rather than fixed, per docs-loop's rule that this loop never
edits code:

- **`scripts/build_skill_zips.py` ignores `--help`** and builds all 14 zips
  instead of printing usage. Its two siblings both handle it correctly
  (`install_skills.py` has argparse, `restore_exec_bits.py` takes `--dry-run`).
  No doc claims otherwise, so this is not documentation drift — it's a
  papercut found by reading, and the fix belongs in a code PR.

## Notes on this run

- **The auditor was already anchored.** I had read `README.md` and
  `ARCHITECTURE.md` earlier in this session before building ground truth, which
  is precisely the confirmation-reading failure docs-loop's step order exists to
  prevent. Mitigated by re-deriving every claim from `git ls-files` and the
  `SKILL.md` frontmatter rather than trusting recall, but a first run from a
  clean context would be a stronger test of the skill.
- Three of the seven real findings are `aspirational` — claims that were never
  true rather than claims that rotted. For a repo of this age that's the
  interesting result: the docs describe an intended engineering practice (CI,
  tests, recorded decisions) that hasn't been built.
