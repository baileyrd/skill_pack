# The Claude Docs format

Read this before writing (step 4). It is the shape of a Claude Docs
document, taken from a real one (a development roadmap: title, date and
author byline, a lead, a drawn roadmap, one table per workstream, bold-led
bullets, an "Assumptions to check" close), written down so any agent can
produce it as plain Markdown. A file in this format renders anywhere
Markdown does and goes into Claude Docs without rework.

## Contents

- The head
- The body
- House style
- What to leave out
- Example
- With the Claude Docs connector

## The head

Exactly three parts, in this order, each separated by a blank line:

1. `# Title`: names the subject ("Pricing API: FX-rate caching"), never
   "Summary" or "Chat notes".
2. The byline: `<as-of date> · <author>`, for example `2026-11-10 · Priya`.
   The date is when the document was written (ISO, `YYYY-MM-DD`). The
   author is the person who asked for the document, by the name the chat
   uses. No name known: the date alone. Nothing else goes on this line: no
   status, scope, sources or caveats.
3. The lead: one to three sentences. The first sentence is the point (the
   decision, result or answer, with its number or date). Never "This
   document outlines...".

## The body

- `## ` sections, each opening with its own point in the first sentence.
- Pipe tables for items compared on the same attributes (options, action
  items with owners, rejected alternatives). Units in the header. A column
  you can't fill is left out, never "n/a".
- `- [ ]` tasks for action items people will tick off; `- [x]` only for
  items the chat says are done.
- Numbered lists for steps in a straight run; bullets only for parallel
  items. A bullet that makes a point leads with it in bold, then one
  sentence of support: `- **L3 is the longest item.** It needs your time.`
- A shape (a flow, dependencies, a timeline of phases) is drawn, not
  described: a Claude Docs diagram when the connector is present, otherwise a
  ```` ```mermaid ```` block, with one sentence under it saying how to read
  it.
- When the document states something the chat implied but never said, it
  goes in a last `## Assumptions to check` section as bullets, so the reader
  sees what to verify. Nothing inferred appears anywhere else unmarked.
- Code blocks only for code or commands the reader will run.
- Links as `[text](url)`. When the chat cited pages, a `## Sources` list
  goes last.
- A missing fact is a one-line open question, not a guess.

## House style

- Sentences under 25 words; paragraphs of at most three sentences.
- Specifics over adjectives: numbers with units, names, dates.
- Plain words, the user's language, no emoji.
- Sized to the ask: a topic the ask didn't name (background, next steps)
  gets at most a sentence, not its own section.

## What to leave out

- An introduction, a recap or a "key takeaways" section.
- Raw HTML in the Markdown, and front matter.
- Template placeholders: `check_doc.py` fails on any `{{NAME}}` left in.

## Example

```markdown
# Pricing API: FX-rate caching

2026-11-10 · Priya

FX rates for `/quote` are now cached in Redis for 300 seconds, which took
p95 latency from 1.8 s to 240 ms in a local load test.

## Decisions

**Cache FX rates in the existing Redis.** It is already run for sessions, so
it adds no new dependency and gives one warm cache across all 12 pods.

**TTL of 300 seconds.** Finance accepts quotes up to 5 minutes stale.

## Rejected options

| Option | Why not |
| --- | --- |
| In-process LRU per pod | Each of the 12 pods warms separately |
| 60 s TTL | Finance allows 5 minutes, and 300 s cuts provider calls |

## Open questions and action items

- Should a Redis outage page someone, or only log a warning?
- [ ] Marco reviews PR #412 before Friday

## Assumptions to check

- The 240 ms figure is from a local load test; production may differ.
```

## With the Claude Docs connector

When the agent has the Claude Docs tools, the same content is created as a
live doc instead of a file. Follow the connector's own instructions: it
creates the outline first (title, byline, a pending block per section) and
fills one section per update. The byline becomes its date chip and the
author's mention chip; everything else is the Markdown above.
