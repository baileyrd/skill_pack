---
name: unix-philosophy
description: Applies Unix software design philosophy — do one thing well, compose small pieces, an open parseable format at every boundary, silence on success, mechanism not policy — in two modes. Design mode shapes what's being built: use it when a tool, CLI, service, module, library API, job, or agent tool is being designed, when the question is "extend this or build a second thing that composes with it", or when a decision turns on interface shape, output format, error behavior, or where a boundary goes — it applies even when nobody says "Unix". Audit mode reviews what exists: "review this against Unix principles", "is this doing too much", "why is this so painful to script against", "should this be one tool or two" — it scores eight dimensions Pass/Warn/Fail against cited evidence and ranks findings by present cost. Translates the principles to libraries, services, pipelines, and agent tools rather than quoting pipes at code that has none, and treats each as a default with a cost, not a law.
version: 1.1.1
---

# unix-philosophy

Two modes over one body of material:

- **Design mode** — a design decision is live and the shape of the thing isn't
  fixed yet. Cheap to influence now, expensive later.
- **Audit mode** — the thing exists and someone wants to know where it drifted.
  Produces a report with cited evidence and a ranked backlog.

If the request doesn't clearly signal one, pick by whether the artifact exists
yet. When both apply (auditing a design in order to change it), audit first —
findings with evidence make better design input than opinions do.

**Why this skill exists, specifically**: these principles are widely agreed
with and rarely applied, because the moment of application is always a moment
when violating them is *easier*. Adding a seventh flag to an existing tool is
cheaper than building a second one. Printing a friendly summary is cheaper than
designing an output contract. Swallowing an error is cheaper than deciding what
the caller should do about it. Each of those is locally rational; the cost lands
on whoever tries to compose, script, test, or replace the thing six months
later. The value here is not knowing the principles — it's naming the specific,
present cost at the moment the cheap choice is being made, so the tradeoff gets
made deliberately instead of by default.

The corollary matters just as much: **cite these principles as reasoning, never
as authority.** "Unix says do one thing" persuades nobody and is often wrong for
the case at hand. "These two paths share no state and have separate release
cadences, so bundling them means neither ships independently" is the same
argument with its actual force showing. If a recommendation can't be stated in
terms of a cost someone is paying, it isn't ready to be made.

## The core test

Everything below reduces to one question, asked about whatever is being built:

> **What is the boundary, how small is it, and can something else already read
> it?**

"Do one thing and do it well" is the answer to *how small*. "Text streams as the
universal interface" is the answer to *can something else read it*. The rest —
silence, mechanism-not-policy, transparency, repair — are what keep a small
boundary from leaking back into a large one.

Applying this needs the boundary identified first, and it is different per
surface: a pipe for a CLI, a public API for a library, a wire contract for a
service, a queue for a pipeline, the context window for an agent tool. Read
[`references/beyond-the-cli.md`](references/beyond-the-cli.md) before applying
any of this to something that isn't a command-line program — that translation is
where the material either earns its keep or reads as cargo-culted Unix nostalgia.

## Design mode

Work these in order. Stop as soon as the decision is settled — this is a
checklist for a live question, not a gate every change has to pass.

**1. Run the `and` test on the one-sentence description.** Describe what the
thing does in one sentence. Every `and` joining two *different kinds* of work
marks a candidate seam. "Parses and validates" is one job; "parses and uploads"
is two. When there's a seam, the default is two units that compose, and the
burden of proof sits on bundling — not the other way round.

Reach for the seam hardest when adding to something that already exists. The
question is never "can this feature go in here?" (it always can) but "does this
feature share a *reason to change* with what's already here?" If the answer is
no, the honest cost of bundling is that the two can never ship, be tested, or be
replaced independently again.

**2. Name the boundary and pick its format.** Whatever crosses it should be
readable by a program that wasn't written for this one: a documented schema, a
standard encoding, plain data over framework-bound objects. "Text streams"
translates to **open, documented, parseable** — a stable protobuf schema honors
it, an undocumented pickle doesn't, and a rendered table with no underlying data
path fails it outright.

The check: *if someone wanted to consume this from a language you didn't
anticipate, what would they have to do?* If the answer involves regexing prose
or reading source, the boundary isn't designed yet.

**3. Decide what it says on success — and default to nothing.** Establish who
the primary consumer is. A program consumer means results on the results channel
(`stdout`), diagnostics elsewhere (`stderr`), and no chatter on the success path.
A human consumer earns more, but keep the machine-readable path available and
suppressible rather than emitting the human version into a pipeline.

**4. Separate mechanism from policy.** Take destinations, endpoints, timeouts,
and retry behavior as parameters. Defaults are good; defaults with no override
are policy. The test: *is there a legitimate second use case blocked by an
assumption this code had no reason to make?*

**5. Decide the failure behavior explicitly.** Reject bad input at the boundary,
where the context to explain it still exists, rather than three layers deep.
Never swallow an error the caller could have acted on. Failure mid-operation
shouldn't leave a half-written output reported as success. This is the one
principle whose violations stay invisible until they've already cost something,
so it's worth deciding rather than discovering.

**6. Check the complexity is earned — in both directions.** Speculative
abstraction (a plugin system with one plugin, an interface with one
implementation) is the same failure as no abstraction at all, and it's the more
common one. Add complexity when something demonstrably needs it now.

**7. State the tradeoff out loud in the recommendation.** Every one of these has
a cost — coordination overhead, parsing ambiguity, discoverability,
onboarding friction. Naming the cost is what makes the advice usable; hiding it
is what makes people ignore the whole framework the first time it's wrong.
[`references/philosophy.md`](references/philosophy.md) ends with the cost of each
principle if a specific one is needed.

## Audit mode

**1. Establish scope and read before judging.** Identify the unit under audit
and its boundary. Read entry points, the public surface, the error paths, and —
if it's a CLI — actually run `--help` and inspect real output rather than
inferring it from argument-parser source. Note what wasn't covered; a scoped
audit that says what it skipped beats a vague one claiming completeness.

**2. Score the eight dimensions** from
[`references/audit-rubric.md`](references/audit-rubric.md), which carries the
signal tables, the Pass/Warn/Fail criteria, the severity definitions, and the
report template. Read it before scoring — the dimensions are D1 single purpose,
D2 composability, D3 interface format, D4 output discipline, D5 mechanism vs
policy, D6 failure behavior, D7 transparency, D8 simplicity and replaceability.

Every verdict needs a citation — a file and line, an invocation and its actual
output, a signature. A finding without evidence is an impression, and it's what
makes an audit easy to dismiss wholesale. Mark a dimension **N/A** with one line
of reasoning rather than stretching it to produce a verdict.

**3. Rank findings by the cost already being paid**, not by distance from the
ideal. High = blocking a real use case today or risking data integrity. Medium =
a recurring workaround, or a concretely-anticipated near-term use case. Low = a
deviation with no current cost. A finding with no articulable cost is Low at
best, and possibly isn't a finding — say so rather than inflating it to fill out
the report.

**4. Say what's already right, specifically.** Name two or three things worth
preserving, with citations. This isn't diplomacy: an audit that lists only faults
invites a rewrite that discards the parts that were load-bearing and correct,
and that outcome is worse than the drift being audited.

**5. Report using the rubric's template**, findings ordered by severity rather
than by dimension. Then stop. Fixing findings is a separate, explicitly-approved
piece of work — an audit that starts refactoring what it found has itself
violated `do one thing`, and it removes the user's chance to rule on the
tradeoffs before code moves.

## When not to apply this

Raymond's own **Diversity** rule — *distrust all claims of "one true way"* — is
on the list deliberately and applies to the list. Back off when:

- **The surrounding code has a different, coherent convention.** Matching the
  codebase beats importing a philosophy into one corner of it. A lone
  Unix-idiomatic module in a framework-idiomatic codebase is worse than either
  done consistently.
- **The user asked for something specific and this is a tangent.** Design
  guidance during an unrelated task is scope creep. Raise it in a sentence,
  don't redesign uninvited.
- **The cost genuinely runs the other way.** Ten processes where one function
  would do violates `parsimony` just as much as a monolith does. Distributed
  systems in particular are where "small and sharp" most often gets misread as
  "microservices" — see the closing section of
  [`references/beyond-the-cli.md`](references/beyond-the-cli.md).
- **It's a prototype and the point is to learn something.** `Optimization` says
  prototype before polishing; boundary design on code that may be deleted next
  week is premature.

## Rules

- Cite a **present cost**, not the principle, whenever recommending a change. A
  recommendation that can't name what it's costing someone isn't ready.
- Read [`references/beyond-the-cli.md`](references/beyond-the-cli.md) before
  applying any of this to a non-CLI surface. Applying pipe-shaped advice to a
  library or service unmodified is the main way this material goes wrong.
- Every audit verdict carries a citation; no verdict rests on general impression.
- Audit mode reports and stops. Fixing findings is separate work needing explicit
  approval — never bundled into the audit that found them.
- Match the surrounding codebase's conventions over these defaults when the two
  conflict and the existing convention is coherent.
- State the cost of following each principle alongside the recommendation. These
  are defaults with tradeoffs, not laws.
- Both over- and under-abstraction are findings. Don't only flag missing seams.

## Limitations

- Design and audit judgment here is qualitative. The rubric makes verdicts
  consistent and citable; it doesn't make them objective, and two careful
  reviewers can reasonably split Warn/Fail on the same evidence.
- The eight dimensions cover *design shape*. They say nothing about correctness,
  security, performance, or test coverage — a codebase can pass all eight and
  still be wrong. Pair with a real code review rather than treating an all-Pass
  audit as a clean bill of health.
- Audit scope is whatever was actually read. On a large codebase this is a
  sampled view; step 1's "not covered" line is doing real work and shouldn't be
  dropped.
- The principles predate distributed systems, managed platforms, and
  agent-driven tooling. `references/beyond-the-cli.md` translates them, but the
  translation is interpretation, not doctrine — where it conflicts with a
  concrete, measured constraint, the constraint wins.

## Reference files

| File | Read it when |
|---|---|
| [`references/philosophy.md`](references/philosophy.md) | A decision turns on *why* a principle exists, or a recommendation needs justifying to someone unconvinced. Holds the source material, Raymond's seventeen rules, and the cost of each principle. |
| [`references/audit-rubric.md`](references/audit-rubric.md) | Any time audit mode runs — the eight dimensions' signal tables, Pass/Warn/Fail criteria, severity definitions, and the report template. |
| [`references/beyond-the-cli.md`](references/beyond-the-cli.md) | Before applying this to a library, service, background pipeline, agent tool, or distributed system — i.e. almost always. |

## Wrap-up retro — audit mode only

**After an audit report lands**, run a
[`meta/skill-retro`](../../meta/skill-retro) pass on **this skill**, grounded in
what just happened: did the rubric's eight dimensions fit the surface under
audit or did one have to be stretched into an N/A, did
[`beyond-the-cli.md`](references/beyond-the-cli.md) cover this surface or was a
translation improvised on the spot, was a verdict recorded without a citation
because the evidence bar was awkward to meet here, did the severity definitions
sort these particular findings or did everything pile into one band?

Running and reporting the retro is automatic and safe unattended — `skill-retro`
never edits this skill's files on its own. *Applying* anything it finds is a
separate, explicitly-approved follow-up through this repo's normal PR workflow,
never bundled into the run that triggered it.

**Design mode does not trigger a retro.** The sibling skills that carry a
wrap-up retro are long-running loops that file issues and merge PRs, where a
retrospective is small next to the work it reflects on. A design-mode
consultation is often a few paragraphs answering one question — appending a
retrospective on this skill's own instructions to that is disproportionate, and
it fires in contexts that can't support it (a read-only sandbox, no subagents,
an ephemeral session), where the honest outcome is a run that reports skipping
its own final step. An audit is the substantial, artifact-producing invocation
where the retro earns its cost.

If a design-mode conversation does turn into substantial work — several rounds,
a boundary reconsidered, a reference that didn't cover the surface — that's
worth a retro, but as an explicit request rather than an automatic step. Say so
in a sentence and let the user decide.
