# Document shapes

Read this at step 3 to pick a section order. Every shape opens with the
Claude Docs head (title, byline, lead; see `claude-doc-format.md`). Drop
empty sections; rename a heading when the subject has a better word for it.

## Decision record (default)

For a chat that weighed options and settled something.

1. Context: the problem and constraints, in a short paragraph.
2. Decisions: one entry each, the decision in bold and, beneath it, the
   why the chat gave (none given: no why line).
   Use the `decision` class in HTML.
3. Outcomes: what now exists (PRs, files, measurements), with links.
4. Rejected options: a pipe table of option, why not.
5. Open questions and action items: open questions as bullets; action items as `- [ ]` tasks with the owner
   when one was named.

## Plan or spec

For a chat that designed something not yet built.

1. Goal and non-goals.
2. Design: components, interfaces, data, in the order a builder needs them.
3. Decisions taken while designing, each with its why.
4. Risks and open questions.
5. Next steps, in order.

## Explainer

For a chat where the user learned how something works.

1. The question, in one sentence.
2. The answer, short, first.
3. How it works: build from the simplest correct model to the details.
4. Examples or commands the reader can try.
5. Pitfalls and where to read more.

## Incident or debugging write-up

For a chat that chased a failure.

1. Symptom and impact.
2. Root cause, stated plainly.
3. Fix and how it was verified, without adding a rationale nobody stated.
4. Timeline, only if order matters to the cause.
5. Follow-ups that stop a repeat.

Leave out hypotheses that were ruled out unless the ruling-out is evidence a
future debugger would otherwise repeat.

## Meeting-style notes

For a broad chat touching several topics with no single thread.

1. One heading per topic, each with its own short decisions and open points.
2. A combined `- [ ]` action-item list at the end.
