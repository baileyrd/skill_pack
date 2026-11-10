---
name: chat-to-artifact
description: >-
  Turns a chat discussion into one polished, self-contained document in the
  Claude Docs format that someone who missed the conversation can read cold.
  Harvests decisions with their reasons, outcomes, rejected options, open
  questions and action items, keeps only what the chat settled, strips
  secrets, then writes one HTML file holding every Claude Docs element
  (dated byline, tables, tasks, chips, inline SVG diagrams and charts,
  embedded images), a live Claude Doc via the connector, or Markdown for a
  repo. Agent-neutral: works in any agent that loads Agent Skills. Use when
  the user asks to "turn this chat into a doc", "write this up", "write up
  the discussion as markdown", "make notes of what we decided", "make an
  artifact of this conversation", "make this shareable", or gives a chat
  transcript and wants a document from it, in any format. Not for diagrams
  of code or branches (that is visual) or for a pack an agent will consult
  later (that is project-expert).
compatibility: >-
  Any agent that reads SKILL.md (Claude Code, claude.ai, Codex, Gemini CLI,
  Cursor and others). The check script needs Python 3, standard library only.
metadata:
  version: "1.0.0"
---

# Chat to artifact

The reader was not in the chat. Everything below follows from that: the
document has to stand alone, say what was decided and why, and leave out the
path the conversation took to get there unless that path explains a decision.

The output format is the Claude Docs format, whatever agent or model is
running this skill: a fixed head (title, dated byline, a lead that answers),
sections, tables, tasks, drawn diagrams and charts, embedded images and a
plain house style. [`references/claude-doc-format.md`](references/claude-doc-format.md)
maps each Claude Docs element to the file you write, with an example; read
it before step 4. Nothing here assumes a particular agent's tools: where a
step names a tool, it says what to do when that tool is absent.

## Rules that hold every run

- **Only what the chat settled.** A decision is something a participant
  agreed to or stated as final. A suggestion nobody took up is not one. Never
  invent owners, dates, numbers, names, roles or reasons; write
  "unassigned", put the item under open questions, or leave a decision's why
  out when the chat never gave one. A plausible reason you inferred is still
  invented; so is a "why" column for follow-ups nobody justified, a lessons
  section the chat never drew, or a job title ("the on-call engineer") for a
  speaker the chat never described. An inference the reader needs goes under
  `## Assumptions to check`, marked as yours.
- **Latest word wins.** When the chat changed its mind, record the final
  position; the earlier one goes under rejected options with the reason it
  lost, and only if the reason is useful to the reader.
- **Self-contained.** No "as discussed above", "the second option", "your
  idea". Name things; define project jargon once; quote short phrases the
  user used when the wording matters.
- **No secrets.** Drop API keys, tokens, passwords, private URLs with
  credentials and personal contact details, even if they were pasted into
  the chat. Say "(credential redacted)" only if the reader needs to know one
  exists.
- **Don't ask what you can infer.** Pick the scope, audience and format from
  the request; ask one question only when two readings would produce
  different documents (for example, two unrelated topics in one chat and no
  hint which one is wanted).

## Procedure

1. **Scope.** The whole conversation by default; "since X" or "the part
   about Y" narrows it. A pasted or attached transcript is the source when
   one is given. Exclude the request to make the document itself.
2. **Harvest** into these buckets, keeping the speaker and the reason for
   each item:
   - context (the problem, constraints, who it is for)
   - decisions (each with its why)
   - outcomes (what was built, run, measured, merged, with links or paths)
   - rejected options (with why), open questions, action items (owner only
     if named)
3. **Pick the shape** from what the harvest holds, not from habit. Read
   [`references/shapes.md`](references/shapes.md) for the section order of
   each: decision record (default), plan or spec, explainer, incident or
   debugging write-up, meeting-style notes. Drop any empty section rather
   than writing "None".
4. **Write** in the Claude Docs format: a title that names the subject
   (not "Chat summary"); the byline `<as-of date> · <author>` (the person
   who asked, by the name the chat uses; no name, the date alone); a lead of
   one to three sentences whose first sentence is the outcome; then the
   sections. Tables for items compared on the same attributes, tasks for
   action items, a drawn diagram or chart for anything with a shape (order,
   dependencies, a timeline, numbers across items), the chat's images where
   they are discussed, and "Assumptions to check" last when you inferred
   anything (inferences go there, nowhere else). Keep it shorter than the
   chat.
5. **Render.** Choose the output in this order:
   1. The user named a format or file name: use it.
   2. A Claude Docs connector is available: create the doc there, following
      the connector's own instructions (outline first, then one section per
      update; chips for the byline, its drawn widgets for diagrams and
      charts, uploads for images).
   3. Otherwise, the default: one HTML file from
      [`assets/template.html`](assets/template.html), named after the title
      in kebab-case (`auth-token-rotation.html`), in the user's working
      directory, never inside this skill's folder. Fill `{{TITLE}}`,
      `{{DATE}}`, `{{AUTHOR}}`, `{{LEAD}}` and `{{BODY}}` with the building
      blocks listed in its header comment, then delete that comment.
      Diagrams and charts are inline SVG; images go in by relative path,
      then `python3 <skill-folder>/scripts/embed_images.py <file>` inlines
      them so the page is one file that opens offline anywhere.
   4. Markdown when the destination is a repo, PR or wiki: same head,
      sections and order, per the format reference's fallback column
      (Mermaid for diagrams, image files beside the document).
6. **Check.** For a file, run
   `python3 <skill-folder>/scripts/check_doc.py <file>` from the user's
   working directory (the sync drops the executable bit, so to run it
   directly first `chmod +x scripts/*.py 2>/dev/null || true` in the skill
   folder). It fails on a leftover `{{placeholder}}`, a missing title or
   dated byline, remote scripts, styles or images, local images not yet
   inlined (or, in Markdown, missing beside the file), and strings shaped
   like keys or tokens. Fix every finding and run it again; deliver only on
   a clean pass. If the agent can't run scripts, or running it is refused,
   check those by eye and say the script did not run. Then reread once as the cold reader: does each
   decision carry the why the chat gave, and is any reference meaningful only
   inside the chat?
7. **Deliver.** Give the path or link and a two-line summary of what the
   document covers. Don't paste the whole document back into the chat.

## Wrap-up retro

When the user accepts the document, or after their first round of
corrections, run a `meta/skill-retro` pass on this skill grounded in the
run: did the harvest miss a decision or keep a superseded one, did the shape
from `references/shapes.md` fit or need reordering, did `check_doc.py` flag
something real or miss something the user caught? Skip it for a document
the user took without comment in a short chat; offer it instead. Reporting
is automatic and safe to run unattended; applying any finding is a separate,
approved change.
