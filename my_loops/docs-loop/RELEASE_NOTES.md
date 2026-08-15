# Release Notes

docs-loop lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/docs-loop) —
this log tracks commits against `main`, the same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md): reverse
chronological, one entry per meaningful change, honest about what's still
open.

---

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
