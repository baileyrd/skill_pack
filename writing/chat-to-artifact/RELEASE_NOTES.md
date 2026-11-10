# Release Notes

Reverse chronological, one entry per meaningful change.

---

## v1.0.0 — Initial skill
**2026-11-10**

- **New:** turns a chat (the live conversation or a pasted/exported
  transcript) into one self-contained document for a reader who was not
  there. Harvest buckets, five shapes in `references/shapes.md`.
- **Claude Docs format by default, any agent:** `references/claude-doc-format.md`
  spells out the format from a real Claude Doc (title, as-of byline, a lead
  that answers, tables, tasks, bold-led bullets, a drawn shape, "Assumptions
  to check") as plain Markdown, so Codex, Gemini CLI or Cursor produce the
  same document Claude does. The Claude Docs connector, when present, takes
  the same content; HTML from `assets/template.html` only on request.
- **"Assumptions to check"** gives inferences a marked home, which is what
  stopped the invented reasons the evals caught (below).
- **`scripts/check_doc.py`:** fails on leftover placeholders, a missing
  title or byline, external resources that break the page offline, and strings shaped
  like credentials. A key pasted into a chat is the likeliest way a secret
  reaches a shared document, so the check is mechanical rather than left to
  a reread.
- **Wrap-up retro** scoped to runs with a correction round; a short,
  accepted-as-is run only offers it, since a retro would outweigh the work.
- **Evals:** 3-case Eval-Kit suite (decision reversal + pasted key, a
  name settled after two rejections, a pasted debugging chat).
  Five iterations, 2 samples each. Final: skill 6/6 vs no-skill control
  2/6 (+67%, 95% interval 0 to +100%). Part of that gap is the format
  itself (the control never writes the as-of byline); the rest is
  invention: the control added reasons and "lessons" the chat never gave,
  the skill put its inferences under "Assumptions to check". Earlier rounds
  also caught the file being written inside the skill folder.
