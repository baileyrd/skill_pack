# docs-audit.md

**Run:** 2026-08-15 against `462d704` · **Scope:** whole repo (95 tracked docs)
**Counts at audit:** 3 stale · 1 missing · 1 orphaned · 3 aspirational · 0 unverifiable · 4 accurate
**Status:** rows 1, 3, 4 and the new PyYAML row fixed; the `my_loops/README.md` stub deleted; `CONTRIBUTING.md`'s CI claim resolved by actually adding CI. **Two rows still open:** the test-harness question and the empty ADR log.

## Findings

| Doc | Where | Claim | Classification | Ground truth | Fix | Size |
| --- | --- | --- | --- | --- | --- | --- |
| README.md | intro, L5 | "see each category's own README for dependencies specific to it" | stale | `meta/` and `web_dev/` have no README; `my_loops/README.md` is a 1-line stub. Only `yt_research_for_cc/README.md` (72 lines) delivers | Name the one category that has one, or write the two missing | S |
| my_loops/README.md | whole file | `# skill_pack` | ~~orphaned~~ **resolved — deleted** | Contained the *root repo's* title and nothing else, a copy-paste stub never filled in. Deleted on the repo owner's decision after the stop-and-ask; `my_loops/` now matches `meta/` and `web_dev/`, which have no category README either. No doc linked to it | done | S |
| README.md | Repo tooling, L78 | "e.g. `zip/dedupe-loop-v1.0.0.zip`" | stale | dedupe-loop is v1.1.1; `build_skill_zips.py` now emits `dedupe-loop-v1.1.1.zip` | Drop the version from the example so it can't rot again | S |
| ARCHITECTURE.md | Structure, L19 | "Four category folders (…), plus repo-wide tooling under `scripts/`" | missing | Accurate as far as it goes, but `need_to_productize/` (4 `.skill` archives) and `trying/` (3) are tracked top-level dirs named in **no doc at all** — `grep` across README/ARCHITECTURE/CONTRIBUTING/docs returns nothing | One sentence saying what they are and why they're not categories | S |
| CONTRIBUTING.md | Review, L28 | "CI must be green before merge" | ~~aspirational~~ **resolved** | Was: no `.github/workflows/` at all. Now: `ci.yml` runs `scripts/check_repo.py` on every PR. The claim is true, with a caveat now stated in CONTRIBUTING — it only *reports* until set as a required status check in branch protection | done | S |
| CONTRIBUTING.md | Standards, L13 | "Add tests for non-trivial logic — happy path and at least one failure/boundary case" | aspirational **(still open)** | No test directory, no runner, no test file anywhere. Adding CI did **not** resolve this: the five checks are lint over repo structure, not behavior | CONTRIBUTING now says plainly that no harness exists rather than implying one does — but the underlying question (build one, or drop the requirement) is unanswered | S |
| ARCHITECTURE.md | Key decisions, L25 | "See `docs/adr/` for the record of individual decisions and their tradeoffs" | aspirational | `docs/adr/` holds exactly one file: `0001-template.md`, an unfilled seed (`# ADR-0001: <Title>`). No decision is recorded | Stop-and-ask: several real decisions were made today that would be ADR-0002 | M |
| README.md | Categories tables | all 14 skills listed | accurate | 14 `SKILL.md` files, 14 table rows, names match | none | — |
| README.md | Repo tooling, L63 | "Three standalone scripts under `scripts/`" | accurate | Exactly 3: `build_skill_zips.py`, `install_skills.py`, `restore_exec_bits.py` | none | — |
| README.md | Versioning, L58 | notebooklm is the one unversioned exception | accurate | It's the only skill with no `version:` and no `RELEASE_NOTES.md` | none | — |
| 5 × `check_references` broken rows | — | — | accurate (non-findings) | Each names a *different* component's or repo's path — the structural false-positive class docs-loop's Limitations already documents | none | — |
| meta/my-skill-creator/SKILL.md | whole file | — | missing *(new — found while fixing row 1)* | `meta/my-skill-creator/scripts/quick_validate.py:8` does `import yaml` (PyYAML, third-party). The SKILL.md declares no dependency, and unlike its siblings makes no "stdlib only" claim either — so nothing is contradicted, but a real runtime requirement is undocumented. `jq` and `rg` are likewise invoked by `my_loops` shell scripts | Declare it — one line in that skill's Scripts section | S |

**Rows 1, 3 and 4 are fixed** (`README.md` intro, `README.md` zip example,
`ARCHITECTURE.md` Structure). Struck through above only in this note rather
than removed, so the next run sees them as settled.

**The PyYAML row is fixed too, and it was six times bigger than logged.**
Verifying it before writing turned one undeclared import into a
dependency-declaration audit across every skill with scripts:

| Skill | Was documented | Actually true |
| --- | --- | --- |
| `meta/my-skill-creator` | nothing | requires **PyYAML** (`quick_validate.py:8`, unguarded import) |
| `my_loops/dedupe-loop` | "gh/git/**ripgrep** only" | requires **jq** (`next_issue.sh:33`); uses **no ripgrep at all** — that claim was inherited from a sibling |
| `my_loops/issue-loop` | "gh/git only — no extra dependencies" | requires **jq**; **ripgrep** optional (`command -v rg`, falls back to `grep`) |
| `my_loops/parity-loop` | "gh and git only — no extra dependencies" | same |
| `my_loops/rust-migration` | "gh/git … only — no extra dependencies" | same |
| `my_loops/sovereignty-loop` | "gh/git/ripgrep only — no extra dependencies" | **jq** missing from the list; ripgrep is optional, not required |

Note the direction varies: five skills *understated* their dependencies, and
one (`dedupe-loop`) *overstated* — documenting a `ripgrep` requirement that
no script has. A one-line "declare PyYAML" fix would have left all of that
in place.

Two near-misses worth recording, both caught by checking before writing:
`jq` appears in every `watch_and_merge.sh` as `gh --jq`, which is gh's own
built-in flag and needs no `jq` binary — counting those would have invented
a dependency for `docs-loop`, which has none. And a draft sentence calling
PyYAML "the only third-party dependency anywhere" ignored `yt-dlp`, which
`yt_research_for_cc` genuinely needs as an external binary.

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
- **The fix pass caught its own bad sentence.** The first replacement written
  for row 1 asserted that the categories without a README needed "nothing
  beyond `git`, `gh`, and the Python standard library." Checking it before
  committing — per the rule that every written claim must point at something
  in the tree — showed it was false: `quick_validate.py` imports PyYAML and
  the loop scripts shell out to `jq`/`rg`. The claim was replaced with one
  that doesn't assert what it can't show, and the false premise became the
  new `missing` row above. A confident, plausible, wrong sentence is exactly
  what this loop is supposed to keep out of a README, and it nearly wrote one.
- `trying/` is described in `ARCHITECTURE.md` only by what's checkable — that
  it holds `.skill` archives and is skipped by the tooling. Its *purpose*,
  as distinct from `need_to_productize/`, is recorded nowhere in the repo;
  the folder name is the only evidence, and a name is not ground truth. Worth
  a sentence from whoever knows, rather than an inferred one.
