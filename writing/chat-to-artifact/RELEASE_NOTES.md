# Release Notes

Reverse chronological, one entry per meaningful change.

---

## v1.0.0 — Initial skill
**2026-11-10**

- **New:** turns a chat (the live conversation or a pasted/exported
  transcript) into one self-contained document for a reader who was not
  there. Harvest buckets, five shapes in `references/shapes.md`, a
  dependency-free HTML template (light/dark, print) and a Markdown path.
- **`scripts/check_doc.py`:** fails on leftover placeholders, an empty
  title, external resources that break the page offline, and strings shaped
  like credentials. A key pasted into a chat is the likeliest way a secret
  reaches a shared document, so the check is mechanical rather than left to
  a reread.
- **Render order** prefers a named format, then the environment's native
  artifact or document tool, then the HTML file, so the same skill works in
  claude.ai, Claude Code and cloud sessions.
- **Wrap-up retro** scoped to runs with a correction round; a short,
  accepted-as-is run only offers it, since a retro would outweigh the work.
- **Evals:** 3-case Eval-Kit suite (decision reversal + pasted key, a
  name settled after two rejections, a pasted debugging chat).
