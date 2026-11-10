---
name: chat-to-artifact
description: >-
  Turns a chat discussion into one polished, self-contained artifact document
  that someone who missed the conversation can read cold, in Claude's
  artifact style. Harvests decisions with their reasons, context, outcomes,
  rejected options, open questions and action items, keeps only what the chat
  actually settled, strips secrets, then renders a single HTML page (inline
  CSS, no CDN, light and dark, prints cleanly) or Markdown, and checks it with
  scripts/check_doc.py. Use when the user asks to "turn this chat into a doc",
  "write this up", "make an artifact of this conversation", "summarize what we
  decided", "make this shareable for my team", or pastes a transcript and
  wants a clean document out of it. Not for diagrams of code or branches
  (that is visual) or for a pack an agent will consult later (that is
  project-expert).
compatibility: Python 3 (stdlib only) for the optional check script.
metadata:
  version: "1.0.0"
---

# Chat to artifact

The reader was not in the chat. Everything below follows from that: the
document has to stand alone, say what was decided and why, and leave out the
path the conversation took to get there unless that path explains a decision.

## Rules that hold every run

- **Only what the chat settled.** A decision is something a participant
  agreed to or stated as final. A suggestion nobody took up is not one. Never
  invent owners, dates, numbers, names, roles or reasons; write
  "unassigned", put the item under open questions, or leave a decision's why
  out when the chat never gave one. A plausible reason you inferred is still
  invented; so is a "why" column for follow-ups nobody justified, a lessons
  section the chat never drew, or a job title ("the on-call engineer") for a
  speaker the chat never described.
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
4. **Write.** Title that names the subject, not "Chat summary". One-line
   subtitle with the date and audience. A TL;DR of two to four sentences that
   leads with the outcome. Then the sections. Tables for anything compared on
   the same attributes; code blocks only for code or commands the reader will
   run. Keep it shorter than the chat.
5. **Render.** Choose the output in this order:
   1. The user named a format or file name: use it.
   2. The environment has a native artifact or document tool (a claude.ai
      artifact, a Docs or artifact-publishing connector): create the
      document there with the same content.
   3. Otherwise write one HTML file from
      [`assets/template.html`](assets/template.html): replace `{{TITLE}}`,
      `{{SUBTITLE}}`, `{{BODY}}` and `{{FOOTER}}` (source and date only:
      "Written up from a chat on 2026-11-10"), using the classes listed
      in the template's header comment. Name it after the title in
      kebab-case (`auth-token-rotation.html`) and write it in the user's
      working directory, never inside this skill's folder.
   4. Markdown instead when the destination is a repo, PR, wiki or chat
      paste: same sections, `# Title` first, no HTML.
6. **Check.** For a file, run
   `python3 <skill-folder>/scripts/check_doc.py <file>` from the user's
   working directory (the sync drops the executable bit, so to run it
   directly first `chmod +x scripts/*.py 2>/dev/null || true` in the skill
   folder). It fails on a leftover `{{placeholder}}`, an empty title,
   external scripts, styles, fonts or images, and strings shaped like keys
   or tokens. Fix every finding and run it again; deliver only on a clean
   pass. If running it is refused, check those four by eye and say the
   script did not run. Then reread once as the cold reader: does each
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
