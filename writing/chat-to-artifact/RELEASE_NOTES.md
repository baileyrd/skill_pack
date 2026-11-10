# Release Notes

Reverse chronological, one entry per meaningful change.

---

## v1.0.0 — Initial skill
**2026-11-10**

- **New:** turns a chat (the live conversation or a pasted/exported
  transcript) into one self-contained document for a reader who was not
  there. Harvest buckets, five shapes in `references/shapes.md`.
- **Claude Docs format, every element, any agent:** the default output is
  one HTML file from `assets/template.html` that holds everything a Claude
  Doc can (dated byline with date and mention chips, lead, tables, tasks,
  bold-led bullets, inline SVG diagrams and charts, embedded images,
  callouts, code). `references/claude-doc-format.md` maps each Claude Docs
  element to its HTML and Markdown form, so Codex, Gemini CLI or Cursor
  produce the same document Claude does. The element set was taken from a
  real Claude Doc; it is a format, not a document type. The Claude Docs
  connector, when present, gets the same content as a live doc; Markdown
  (Mermaid for diagrams, image files beside it) is for repos and PRs.
- **`scripts/embed_images.py`:** inlines local images as data URIs so the
  page is one file that opens offline; refuses missing, non-image or
  over-5 MB files and writes nothing on any error.
- **"Assumptions to check"** gives inferences a marked home, which is what
  stopped the invented reasons the evals caught (below).
- **`scripts/check_doc.py`:** fails on leftover placeholders, a missing
  title or dated byline, remote resources or un-inlined images that break
  the page on its own, missing image files beside a Markdown doc, and
  strings shaped like credentials. A key pasted into a chat is the likeliest way a secret
  reaches a shared document, so the check is mechanical rather than left to
  a reread.
- **Wrap-up retro** scoped to runs with a correction round; a short,
  accepted-as-is run only offers it, since a retro would outweigh the work.
- **Evals:** 4-case Eval-Kit suite (decision reversal + pasted key + a shared chart image, a
  name settled after two rejections, a pasted debugging chat, a plan whose
  step order must be drawn).
  Final run, 4 cases, 2 samples each: skill 7/8 vs no-skill control 0/8
  (+88%, 95% interval +62% to +100%). The control never writes the dated
  byline, never embeds the shared image, and never draws the step order as
  a diagram; it also adds reasons the chat never gave. A first run of this
  version missed the Markdown case because the skill did not load for "write
  up ... as a markdown doc"; the description now names that phrasing.
  Earlier rounds caught the file being written inside the skill folder and
  invented reasons, roles and lessons.
