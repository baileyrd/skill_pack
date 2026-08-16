# Release Notes

docs-loop lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/docs-loop) —
this log tracks commits against `main`, the same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md): reverse
chronological, one entry per meaningful change, honest about what's still
open.

---

## v1.3.2 — `where` paths are forward-slashed on every platform
**2026-08-16**

- **Fixed ([#49](https://github.com/baileyrd/skill_pack/issues/49)):**
  `check_references.py` built each row's `where` field by stringifying a
  `Path`. On Windows that yields `meta\\skill-retro\\...` while
  `docs-refs-baseline.tsv` stores `meta/skill-retro/...`. Since `baseline_key`
  is kind+where+detail, **no baselined row ever matched on a Windows
  checkout** — every accepted finding resurfaced as `NEW`.
- **The cost was masking, not noise.** During PR #44 the local run showed three
  `NEW` findings, all false; the reporter concluded `doc-refs` was
  pre-existing-red and moved on. CI on Linux then showed a single, different,
  genuine finding in a file they had just written. A check whose output depends
  on the platform teaches you to ignore it, and then you miss the real one.
- **Changed:** path relativization is now `rel_where()`, a small pure function
  returning `.as_posix()`. It was split out specifically so the Windows
  behaviour is testable from Linux by passing `PureWindowsPath` — the first
  version of the test asserted "no backslash" against real `Path`s, **passed
  with the fix reverted**, and would have shipped unable to fail. Two of the
  five new tests in `tests/test_check_references.py` fail when `.as_posix()` is
  dropped; verified by reverting and restoring, per ADR-0002.
- The command-line `missing-doc` row got the same treatment — it is a `where`
  field too, and had the identical bug on a path the user typed.

---

## v1.3.1 — Description under claude.ai's upload limit
**2026-08-16**

- **Fixed:** the `description` was 1274 characters, over the 1024-character
  limit claude.ai enforces on skill upload, so the zip was rejected outright.
  Trimmed to 979 (45 characters of headroom) with every trigger phrase kept —
  the cuts are the doc-comment scope note and the long repo-config comparison,
  now a single clause. Nothing about what the skill does changed.
- **Context:** five skills here shipped over the limit at once, and none of the
  local tooling noticed: `install_skills.py` copies frontmatter without reading
  it, `build_skill_zips.py` zips it the same way, and Claude Code itself loads
  an over-length description fine. Only claude.ai rejects it, at upload, one
  file at a time. `check_repo.py`'s `manifests` check now enforces the limit so
  this fails locally and in CI instead.

## v1.3.0 — Six findings from the first skill-retro
**2026-08-15**

Applied from a `meta/skill-retro` pass grounded in this skill's own first
real run against `skill_pack` — the audit, the rows 1–3 pass, the row 5
pass, and the `my_loops/README.md` deletion. All six findings had a concrete
incident behind them; none were speculative.

- **Added (the one that matters):** step 4 now stops and re-reports when an
  approved row turns out bigger than the row. **Row 5 was approved as "declare
  PyYAML — one line in that skill's Scripts section" and delivered as edits to
  six skills.** The checkpoint is this loop's core safety mechanism and it
  widened silently, because nothing said not to. An approval is for the row as
  written, not for what the row turns out to imply — and this failure is
  invisible from inside the fix, since the work feels like finishing the
  approved row right up until it isn't. Applies in auto mode too, regardless
  of classification.
- **Changed:** doc-comments are no longer default scope. Step 0 claimed them
  (`///`, docstrings, JSDoc) while the loop provides no extraction pass for
  any language — so the run audited **zero** of them and still reported
  whole-repo coverage. That's the same nearly-true claim this skill exists to
  catch, made by the skill about itself. Now opt-in, with a requirement to
  report which languages were covered; Limitations updated to match instead
  of contradicting it.
- **Added:** step 1 now requires declaring prior exposure. This run had read
  `README.md` and `ARCHITECTURE.md` hours before building ground truth —
  exactly the confirmation-reading failure the step order exists to prevent.
  It got flagged, but by improvisation, not instruction. The auditor is the
  last person able to notice it happening, so the disclosure has to be a rule.
- **Changed:** the per-run tracking issue is now conditional on auditing and
  fixing being split across people or sessions. None was filed this run and
  nothing suffered — a committed `docs-audit.md` already *is* the
  traceability when the same run does both.
- **Fixed:** step 5 asked for a re-run of *both* step 2 scripts. Only
  `check_references.py` was re-run, correctly: `inventory_docs.sh` ranks by
  commit recency, which your own edits perturb without saying anything about
  correctness.
- **Fixed:** step 6 said to retro "regardless of how the run ended" without
  defining *ended*. In an interactive run where the user keeps picking rows,
  it never fired — the user had to ask, four turns later. Now: once, when the
  last approved row is merged and none remain picked, or when the user stops
  the loop. Never per-PR.
- **Logged as a candidate, not acted on:** `inventory_docs.sh` contributed
  nothing this run — 38 of 98 docs share one bulk-commit date, so the top of
  its ranking was a flat tie. One run isn't enough to call a step dead.
- **Validated, not changed:** step 4's "every claim you write must be
  checkable against something in the tree" caught two false sentences before
  they landed. That rule earned its place twice in one day.

## v1.2.1 — docs-audit.md counts as a historical log
**2026-08-15**

- **Fixed:** a run that deletes a file, then records the deletion in its own
  `docs-audit.md`, made the next run report that record as new broken
  breakage — and with the checker wired into CI, that turns a completed,
  correct fix into a red build. Hit for real the moment
  `my_loops/README.md` was deleted from this repo.
- `docs-audit` joins `CHANGELOG`/`RELEASE_NOTES` in the historical set. Its
  rows persist across runs by design (`references/docs-audit-format.md`), so
  it necessarily accumulates references to things a run deliberately removed.
  A row saying "this stub was deleted" is the report working, not drift.
- Scoped, not a blanket mute: only the `docs-audit` stem is affected, and
  those rows are still reported — as `historical-*`, which the legend already
  labels "never fix one."

## v1.2.0 — --baseline, so the checker can gate CI
**2026-08-15**

- **Added:** `--baseline FILE` to `check_references.py`. Without it, wiring
  the checker into CI makes the build red on day one for any repo with the
  structural false-positive class this skill's own Limitations describe —
  and an always-red check gets ignored, which is worse than no check.
- Baseline entries are keyed on `kind + doc + detail`, deliberately
  **without** the line number: an accepted row must not come back as "new"
  because someone added a paragraph above it. Entries that stop matching are
  reported as stale so they can be deleted, but never fail the run — a
  forgotten baseline line isn't a reason to block a merge.
- Proven against this repo: 3 accepted rows, and a genuinely new broken
  reference still fails the run.

## v1.1.0 — Cut check_references.py's false positives 26 → 6
**2026-08-15**

Three fixes to what the checker treats as a claim about the tree. Measured
against `skill_pack` itself, whole-repo: **26 `broken` rows → 6**, including
**3 broken anchors → 0**. No real finding was lost — the two genuine ones
from v1.0.0's run were already fixed in #18, and re-running against that
state reproduces them when reverted.

- **Added:** component-relative resolution. Paths now resolve against three
  bases, nearest first — the doc's own directory, its nearest enclosing
  component (a directory holding a `SKILL.md` or a language manifest), and
  the repo root. A skill's `references/foo.md` saying `scripts/run.sh` means
  its own sibling `scripts/`, which is how a reader reads it and how the
  checker now reads it too. This alone cleared the four
  `platform-directory.md` rows and 23 → 18 inline-path rows.
- **Fixed:** markdown link syntax quoted inside backticks was parsed as a
  real link. A release note saying "the TOC linked
  `` `[Operators](#operators)` ``" is *describing* a link, not making one —
  so every note documenting a broken link re-reported that broken link
  forever. Exactly the trap a docs checker shouldn't walk into, and it was
  this skill's own release notes that walked into it. Code spans are now
  masked before link extraction (length-preserving, so columns still line
  up); path candidates still come from the code spans themselves. Same line,
  two readings. 3 broken anchors → 0.
- **Fixed:** code spans delimited by a run of backticks (``` ``a `b` c`` ```)
  were only matched at length one, leaving the inner content exposed to the
  link and path scanners. Caught by writing the entry above: quoting the
  quoted-link example needed double backticks, which promptly produced a
  seventh false positive in this very file.
- **Added:** `historical-*` verdicts. A non-resolving path in a
  `CHANGELOG`/`RELEASE_NOTES` is usually *correct history* — the entry
  recording that a file was removed is doing its job — and this skill's own
  Rules already forbid rewriting past entries. Reporting those as `broken`
  sent an auditor to rows they're not allowed to touch. They're now
  `unresolved` with a self-labelling kind, still visible, no longer an
  action item. 55 rows moved.
- **Unchanged, deliberately:** the remaining 6. Each is a doc describing a
  *different* component or repo (`docs-loop`'s own SKILL.md citing a target
  repo's `.github/workflows/`, `skill-retro`'s format example, dedupe-loop
  citing repo-config's `scripts/audit.sh`), or build-state-dependent
  (`README.md`'s `zip/` example). That class is structural — no resolution
  rule fixes it without also hiding real findings.

## v1.0.0 — Initial release
**2026-08-15**

- **Added:** `docs-loop` — a bounded documentation review/update loop for a
  target repo: ground truth from the code first, doc-surface inventory
  second, a classified `docs-audit.md` checkpoint third, then per-doc PRs
  through the same CI-gated merge-commit mechanics as the sibling
  `my_loops` skills, a verification pass, and a `meta/skill-retro` wrap-up.
- **Added:** six-way finding classification (`stale` / `missing` /
  `orphaned` / `aspirational` / `unverifiable` / `accurate`). The last two
  are logged decisions that persist across runs so a re-audit doesn't
  re-litigate claims someone already settled; `aspirational` exists because
  "described in the present tense but never shipped" is a different defect
  from "used to be true," and only the first is a product question.
- **Added:** `scripts/inventory_docs.sh` — drift signal per tracked doc
  (last changed, plus commits to non-doc files since). Ranks where to look;
  deliberately not a verdict, since commit recency isn't semantics.
- **Added:** `scripts/check_references.py` — resolves relative links,
  heading anchors, backticked repo paths, and shell-block paths against the
  working tree. Stdlib only. Covers the checkable half of drift; a clean run
  is explicitly *not* evidence the docs are true.
- **Added:** `references/ground-truth-sources.md` (what's authoritative per
  stack, including the three-way ADR caveat and a "what is not ground truth"
  list), `references/docs-audit-format.md` (report table, with a
  re-runnable `Ground truth` column), and `references/development-standards.md`
  (adapted from the sibling copies for the docs case — a doc asserting a
  standard the code doesn't meet is a code finding, not a doc to relax).
- **Added:** `LOOP_HARNESS_MODE=auto` support on the same split as
  `sovereignty-loop`/`dedupe-loop` — transcription-from-a-verifiable-source
  rows (stale facts, orphaned pointers, broken references) proceed
  unattended; anything where the code looks wrong rather than the doc always
  waits, in both modes.
- **Known limitations, stated rather than glossed:** prose accuracy is
  judgment and no script here touches it; doc-comment review defaults to the
  public API surface only; generated API reference output (rustdoc/Sphinx
  builds) is out of scope; claims about anything outside the repo stay
  `unverifiable` permanently.
