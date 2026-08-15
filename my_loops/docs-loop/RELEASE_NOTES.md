# Release Notes

docs-loop lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/docs-loop) —
this log tracks commits against `main`, the same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md): reverse
chronological, one entry per meaningful change, honest about what's still
open.

---

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
