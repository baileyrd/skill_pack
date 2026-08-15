# docs-audit.md format

Written at the end of step 3, before a single doc edit lands. One table, one
row per finding — not per doc file, since a README typically produces several
findings of different classifications and collapsing them loses the ones that
need a human.

| Doc | Where | Claim | Classification | Ground truth | Fix | Size |
| --- | --- | --- | --- | --- | --- | --- |
| README.md | `Repo tooling`, L62 | "Three standalone scripts under `scripts/`" | stale | `git ls-files scripts/` → 4 scripts; `render_index.py` added in #71 | Update the count and add the row to the table below it | S |
| README.md | `Categories`, L46 | — | missing | `web_dev/datastar-pro/` exists and is versioned | Add the category section + skill row, matching the existing sections' shape | S |
| ARCHITECTURE.md | `Structure`, L19 | "Four category folders" | stale | Five on disk (`my_loops`, `yt_research_for_cc`, `meta`, `web_dev`, `need_to_productize`) | Update the count; `need_to_productize` needs a sentence saying what it is | S |
| CONTRIBUTING.md | `Testing`, L28 | "`pytest` runs the suite" | orphaned | No `pyproject.toml`, no tests dir, CI runs no pytest job | Cut the section, or replace with the real check (`build_skill_zips.py`) — needs a pick | S |
| README.md | `Install`, L92 | "OMP's `claude` provider (priority 80)" | unverifiable | Nothing in this repo defines OMP's provider priority | Leave as-is; flagged so a re-run doesn't re-open it | — |
| docs/adr/0002 | `Decision` | "Skills will share a common `lib/`" | aspirational | No `lib/`; ARCHITECTURE's Non-goals says the opposite | Stop-and-ask: ADR vs. ARCHITECTURE genuinely disagree, and one of them is wrong | M |
| SECURITY.md | whole file | "Report to the address below" | accurate | Matches the repo owner resolved from `git remote` | None | — |

Columns:
- **Doc** — repo-relative path.
- **Where** — section heading plus line number. Line numbers alone go stale
  between the audit and the fix; the heading is what survives an edit.
- **Claim** — quote the actual sentence or fragment being judged, trimmed.
  Paraphrasing here is how a wrong verdict slips through review. Empty for
  `missing` rows, since the point is that nothing says it.
- **Classification** — exactly one of `stale` / `missing` / `orphaned` /
  `aspirational` / `unverifiable` / `accurate` (definitions in SKILL.md step
  3). If a row seems to be two at once, it's usually two rows.
- **Ground truth** — *the specific artifact that settles it*: a command and
  its output, a manifest line, a file path, a workflow step. Not "the code"
  and not "I checked" — a reviewer has to be able to re-run this column.
  This is the column that makes the audit auditable.
- **Fix** — what the edit will be, concretely enough to review before it's
  written. For a stop-and-ask row, say what the question is instead.
- **Size** — S/M/L, a rough gut call for batching PRs (step 4 groups by doc
  file or theme), not a commitment. `—` for rows with no edit.

## Reporting alongside the table

- **Counts by classification**, before and after, so a re-run shows movement.
- **Which rows are auto-eligible** under `LOOP_HARNESS_MODE=auto` and which
  always wait — spell this out rather than leaving the user to derive it
  from SKILL.md's "Harness mode" section.
- **Rows where the code is the suspect party**, called out separately from
  the table. These are the highest-value output of a docs review and they
  get lost in a 40-row table. Each one names the doc's claim, what the code
  does instead, and why the doc's version looks like the intended behavior.
- **Scope**, if step 0 narrowed it — an audit of six PRs' worth of docs must
  not read as a whole-repo clean bill of health.

## Persistence

`accurate` and `unverifiable` rows stay in the table. They're logged
decisions, not absences: dropping them means the next run re-litigates every
claim someone already settled, and the run after that does it again. Keep
`docs-audit.md` in the target repo (or hand it back with the report if the
user would rather not commit it) so the next run starts from the last one's
verdicts instead of from scratch.
