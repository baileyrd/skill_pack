# The Claude Docs format

Read this before writing (step 4). It lists the elements a Claude Docs
document can hold, taken from a real one: title, date and author byline,
lead, drawn diagrams and charts, images, tables, tasks, bold-led bullets,
numbered steps, chips and links to other docs. It describes a format, not a
kind of document: which sections a document has comes from
`references/shapes.md` and from the chat, and most documents use only a few
of these elements. It is written down so any agent, not only Claude,
produces the same document.

## Contents

- Where each element goes
- The head
- The body
- Diagrams and charts
- Images
- House style
- Example (HTML body)
- Markdown fallback
- With the Claude Docs connector

## Where each element goes

The default file is HTML from `assets/template.html`: it is the one plain
format that holds every Claude Docs element in a single file any browser
opens. Markdown is the fallback for repos and PRs.

| Claude Docs element | HTML file (default) | Markdown fallback |
| --- | --- | --- |
| Title | `<h1>` and `<title>` | `# Title` |
| Byline: date chip · author mention | `<p class="byline">` with `.chip` and `.chip.mention` | `2026-11-10 · Priya` |
| Lead | `<p class="lead">` | first paragraph |
| Section, subsection | `<h2>`, `<h3>` | `##`, `###` |
| Bold, link, link to another doc | `<strong>`, `<a href>` | `**`, `[text](url)` |
| Bullets, numbered steps | `<ul>`, `<ol>` | `-`, `1.` |
| Tasks | `<ul class="tasks">` with disabled checkboxes | `- [ ]`, `- [x]` |
| Table | `<div class="table-wrap"><table>` with `<thead>` | pipe table |
| Date or person in text | `<span class="chip">`, `<span class="chip mention">` | plain text |
| Status in a cell | `<span class="tag">` | plain word |
| Diagram or chart | `<figure>` with inline `<svg>` and `<figcaption>` | ```` ```mermaid ```` block, or an image |
| Image | `<figure><img>` inlined by `embed_images.py` | `![alt](images/x.png)` next to the file |
| Callout | `<div class="callout">` | `> ` quote |
| Code | `<pre><code>` | fenced block |

## The head

Exactly three parts, in this order:

1. Title: names the subject ("Pricing API: FX-rate caching"), never
   "Summary" or "Chat notes".
2. Byline: `<as-of date> · <author>`. The date is when the document was
   written (`YYYY-MM-DD`). The author is the person who asked for it, by the
   name the chat uses; no name known, the date alone. Nothing else goes on
   this line: no status, scope, sources or caveats.
3. Lead: one to three sentences. The first is the point (the decision,
   result or answer, with its number or date). Never "This document
   outlines...".

## The body

- Sections each open with their own point in the first sentence.
- Tables for items compared on the same attributes (options, milestones,
  action items with owners, rejected alternatives). Units in the header. A
  column you can't fill is left out, never "n/a". Several groups of the same
  kind (one per workstream) get one table each, under their own heading,
  with identical columns.
- Tasks for action items people will tick off; ticked only when the chat
  says they are done.
- Numbered lists for steps in a straight run; bullets only for parallel
  items. A bullet that makes a point leads with it in bold, then one
  sentence of support: "**L3 is the longest item.** It needs your time."
- When the document states something the chat implied but never said, it
  goes in a last "Assumptions to check" section as bullets, so the reader
  sees what to verify. Nothing inferred appears anywhere else unmarked.
- Links to pages and other docs the chat cited go inline; a "Sources" list
  goes last when there are several.
- A missing fact is a one-line open question, not a guess.

## Diagrams and charts

A shape is drawn, not described: phases in order, dependencies, a flow that
branches, parts of a whole, a timeline, five or more numbers over time or
across items. Draw it as inline SVG inside a `<figure>`:

- `viewBox` sized to the content, `role="img"` and an `aria-label` that
  says what it shows; text as `<text>`, never as a picture of text.
- Edges that mean order or dependency carry arrowheads (one `<marker>` in
  `<defs>`, used as `marker-end`), so direction reads without the caption.
- Colors from the template's variables (`var(--fg)`, `var(--muted)`,
  `var(--line)`, `var(--accent)`, `var(--ok)`) or `currentColor`, so it
  reads in light and dark mode.
- A `<figcaption>` in the Claude Docs style: what it is, then its counts
  ("rollout · 3 steps", "p95 latency · 4 weeks").
- One sentence under the figure saying how to read it.
- A chart shows numbers the chat gave; it never invents data points.

## Images

An image the chat shared (a screenshot, an exported chart, a photo of a
whiteboard) goes in where it is discussed: `<figure><img src="relative/path"
alt="what it shows"><figcaption>...</figcaption></figure>`. Then run
`python3 <skill-folder>/scripts/embed_images.py <doc.html>`, which replaces
each local path with the image itself so the page travels as one file.
Images over 5 MB are refused; resize first. Never link a remote image: the
page would break offline.

## House style

- Sentences under 25 words; paragraphs of at most three sentences.
- Specifics over adjectives: numbers with units, names, dates.
- Plain words, the user's language, no emoji.
- Sized to the ask: a topic the ask didn't name gets at most a sentence.
- No introduction, recap or "key takeaways"; no scripts or remote URLs.

## Example (HTML body)

What goes in place of `{{BODY}}` for a short decision record; the head comes
from the template's `{{TITLE}}`, `{{DATE}}`, `{{AUTHOR}}` and `{{LEAD}}`.

```html
<h2>Decisions</h2>
<ul>
  <li><strong>Cache FX rates in the existing Redis.</strong> It already runs
    for sessions, so all 12 pods share one warm cache.</li>
  <li><strong>TTL of 300 seconds.</strong> Finance accepts quotes up to 5 minutes stale.</li>
</ul>
<h2>Rollout</h2>
<figure>
  <svg viewBox="0 0 600 70" role="img" aria-label="Three steps: cache, fallback, review">
    <g font-size="13" fill="var(--fg)">
      <rect x="1" y="15" width="170" height="40" rx="6" fill="none" stroke="var(--accent)"/>
      <text x="86" y="40" text-anchor="middle">Redis cache (done)</text>
      <rect x="215" y="15" width="170" height="40" rx="6" fill="none" stroke="var(--line)"/>
      <text x="300" y="40" text-anchor="middle">Provider fallback</text>
      <rect x="429" y="15" width="170" height="40" rx="6" fill="none" stroke="var(--line)"/>
      <text x="514" y="40" text-anchor="middle">Review PR #412</text>
      <path d="M171 35h44M385 35h44" stroke="var(--muted)"/>
    </g>
  </svg>
  <figcaption>rollout · 3 steps</figcaption>
</figure>
<p>Left to right; the outlined step is done.</p>
<h2>Rejected options</h2>
<div class="table-wrap"><table>
  <thead><tr><th>Option</th><th>Why not</th></tr></thead>
  <tbody><tr><td>In-process LRU per pod</td><td>Each of the 12 pods warms separately</td></tr></tbody>
</table></div>
<h2>Open questions and action items</h2>
<ul class="tasks"><li><input type="checkbox" disabled> <span class="chip mention">Marco</span> reviews PR #412 before Friday</li></ul>
<h2>Assumptions to check</h2>
<ul><li>The 240 ms figure is from a local load test; production may differ.</li></ul>
```

## Markdown fallback

Same head, sections and order, using the right-hand column of the element
map. Images stay as files beside the document (`check_doc.py` fails if one
is missing); diagrams become ```` ```mermaid ```` blocks, which GitHub and
most editors draw. A chart becomes an image or, if none can be made, a
table of the numbers.

## With the Claude Docs connector

When the agent has the Claude Docs tools, create a live doc instead of a
file, following the connector's own instructions: outline first (title,
byline, a pending block per section), then one section per update. The
byline becomes its date and mention chips, diagrams and charts its drawn
widgets, images its uploads. The content and order stay as above.
