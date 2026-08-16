# Audit rubric

Per-dimension criteria for audit mode (`SKILL.md` → "Audit mode"), plus the
report template. Eight dimensions, each scored **Pass / Warn / Fail** against
observed evidence, never against a general impression.

**Contents**

- [Scoring discipline](#scoring-discipline)
- [D1 — Single purpose](#d1--single-purpose)
- [D2 — Composability](#d2--composability)
- [D3 — Interface format](#d3--interface-format)
- [D4 — Output discipline](#d4--output-discipline)
- [D5 — Mechanism vs policy](#d5--mechanism-vs-policy)
- [D6 — Failure behavior](#d6--failure-behavior)
- [D7 — Transparency](#d7--transparency)
- [D8 — Simplicity and replaceability](#d8--simplicity-and-replaceability)
- [Severity ranking](#severity-ranking)
- [Report template](#report-template)

## Scoring discipline

A verdict needs a citation — `path/to/file.rs:120-146`, a CLI invocation and its
actual output, a route handler, a function signature. "Feels bloated" is not a
finding; "`sync()` at `cmd/sync.go:88` performs fetch, transform, write, *and*
Slack notification, and the notification cannot be disabled" is.

- **Pass** — the dimension holds, or deviates for a reason the code itself makes
  evident (a comment, an ADR, a documented constraint).
- **Warn** — a real deviation whose cost is currently absorbed, but which
  compounds: it will bite when the next caller, format, or platform arrives.
- **Fail** — the deviation is already costing something observable today:
  callers work around it, tests can't reach it, a feature is blocked on it.

Do not grade on a curve. Eight Passes is a legitimate outcome for
well-designed code, and so is one dimension failing while seven pass — the
rubric is a checklist, not a distribution to fill.

When a dimension genuinely does not apply (D3's stream format for a pure
in-process library with no serialization boundary, say), mark it **N/A** with
one line on why. Do not stretch a dimension to produce a verdict.

## D1 — Single purpose

*Does the unit do one thing?*

| Signal | Look for |
|---|---|
| The "and" test | Describe the unit in one sentence. Every `and` that joins two *different kinds* of work is a candidate seam. "Parses and validates" is one thing; "parses and uploads" is two. |
| Flag-mode branching | A CLI flag that switches the tool into a materially different job (`--serve` on a tool that otherwise transforms a file) is a second tool wearing a trench coat. |
| Divergent change | Does one file get edited for unrelated reasons by unrelated people? Coupled release cadences are the practical cost. |
| Unreachable-together code | Two branches whose code paths share nothing but the entry point. |

**Fail** when a caller must pull in, configure, or tolerate capability B to use
capability A. **Warn** when the seam is visible but nothing has yet paid for it.

## D2 — Composability

*Can this be combined with things its author never anticipated?*

| Signal | Look for |
|---|---|
| Terminal-only output | Results that exist only as rendered text, a TUI, or a chart, with no path to the underlying data. |
| Missing programmatic entry | A CLI with no library form, or a library whose logic is only reachable through a framework-bound handler. |
| Interactive-only paths | Prompts with no non-interactive equivalent, blocking automation. |
| Hidden global state | Env vars, singletons, or ambient config that make two instances in one process impossible. |
| Piping honesty | Does it detect a pipe and behave sanely, or emit colour codes and progress bars into `stdout`? |

**Fail** when the only way to consume the result is a human reading it.

## D3 — Interface format

*Is the boundary format something else can already read?*

| Signal | Look for |
|---|---|
| Bespoke serialization | A hand-rolled format where a standard one (JSON/CSV/NDJSON/protobuf) exists. |
| Prose-encoded data | Data recoverable only by regexing human-formatted sentences. |
| No stable contract | Field names, ordering, or types that shift with cosmetic changes, with no versioning. |
| Lossy defaults | Truncation, rounding, or column-eliding applied to *machine* output, not just the human view. |

Modern read: "text streams" means **an open, documented, parseable boundary
format** — not literally ASCII. A stable protobuf schema passes; an
undocumented pickle blob fails. Binary is a Warn only when it's *also* opaque
or undocumented; a justified binary format with a published schema is a Pass.

## D4 — Output discipline

*Does it stay quiet, and split its channels?*

| Signal | Look for |
|---|---|
| Chatty success | Progress chatter, banners, or "Done!" on the success path of a non-interactive tool. |
| Channel confusion | Diagnostics on `stdout`, results on `stderr`, or logs interleaved into structured output — the single most common cause of "unparseable" output. |
| Exit codes | Always `0`? Distinct codes for distinct failure classes, or one catch-all? |
| No quiet mode | No `--quiet`/`-q` on a tool with an unavoidably verbose default. |

Judge against the *primary* consumer. A tool humans run interactively earns
more output than one that lives in a pipeline — the failure is emitting the
human-facing version when the consumer is a program, with no way to suppress it.

## D5 — Mechanism vs policy

*Is a workflow baked into something that should just provide capability?*

| Signal | Look for |
|---|---|
| Hardcoded destinations | Paths, endpoints, table names, or channels burned into the engine rather than passed in. |
| Non-overridable defaults | A default is fine and good; a default with no override is policy. |
| Presumed workflow | A library that assumes it's called from a CLI, a web request, or a specific ordering of steps. |
| Engine/interface tangle | Business logic reachable only through the presentation layer (an HTTP handler that *is* the algorithm). |

**Fail** when a legitimate second use case is blocked by an assumption the code
had no reason to make.

## D6 — Failure behavior

*Does it fail loudly, early, and at the right layer?* (Raymond's **Repair**.)

| Signal | Look for |
|---|---|
| Swallowed errors | `catch {}`, `except: pass`, `let _ =`, ignored return codes. |
| Deferred detection | Invalid input accepted at the boundary and detonating three layers deep with no context. |
| Silent coercion | Malformed input quietly defaulted, clamped, or dropped instead of rejected. |
| Context-free propagation | An error surfaced with no indication of which input or stage produced it. |
| Partial-write hazard | Failure mid-operation leaving output half-written with a success exit code. |

**Fail** on any silently swallowed error on a path where the caller could have
acted on it. This dimension usually produces the highest-severity findings —
it's the one whose violations are invisible until they've already caused damage.

## D7 — Transparency

*Can someone see what it's doing without a debugger?*

| Signal | Look for |
|---|---|
| Clever over clear | Density that saves lines and costs comprehension. |
| Logic where data belongs | Long `if`/`switch` chains encoding knowledge that could be a table (Raymond's **Representation**: fold knowledge into data so the logic can be dumb). |
| Opaque intermediate state | Multi-stage pipelines with no way to inspect between stages. |
| Untestable seams | Logic reachable only through I/O, network, or a live clock. |
| Magic | Reflection, metaprogramming, or implicit registration where an explicit list would do. |

## D8 — Simplicity and replaceability

*Is the complexity earned, and can a part be swapped out?*

| Signal | Look for |
|---|---|
| Speculative generality | Abstractions, plugin points, or config with exactly one implementation and no second on the horizon. |
| Wide interfaces | A module exposing 40 public methods where callers use 4 — the practical measure of "narrow interface." |
| Dependency depth | A heavy dependency pulled in for one function. |
| Swap cost | Pick one component: how many files change to replace it? |
| Premature optimization | Caching, pooling, or hand-tuning with no profile behind it (Raymond's **Optimization**). |

Both directions are findings here. Under-abstraction (copy-paste, no seam) and
over-abstraction (a factory producing one product) are the same failure of
`parsimony`, and over-abstraction is the more common one in practice.

## Severity ranking

Rank the backlog by **cost already being paid**, not by how far the code sits
from the ideal:

- **High** — blocking a real use case today, or a correctness/data-integrity
  hazard (most D6 failures land here).
- **Medium** — imposing a recurring workaround on callers, or blocking a
  concretely-anticipated near-term use case.
- **Low** — a deviation with no current cost; worth noting at the next natural
  edit, not worth a dedicated change.

A finding with no articulable cost is a **Low** at best, and possibly not a
finding at all. Say so rather than inflating it.

## Report template

Use this exact structure:

```markdown
# Unix philosophy audit — <target>

**Scope:** <what was read — paths, entry points, commits>
**Not covered:** <what was out of scope and why>

## Verdicts

| # | Dimension | Verdict | One-line basis |
|---|---|---|---|
| D1 | Single purpose | Pass/Warn/Fail/N/A | |
| D2 | Composability | | |
| D3 | Interface format | | |
| D4 | Output discipline | | |
| D5 | Mechanism vs policy | | |
| D6 | Failure behavior | | |
| D7 | Transparency | | |
| D8 | Simplicity & replaceability | | |

## Findings

### F1 — <short title> (D<n>, High/Medium/Low)
**Evidence:** `path:line` — what's there.
**Cost:** what this is preventing or making expensive *today*.
**Change:** the smallest change that removes the cost.
**Cost of the change:** what it breaks, who has to migrate, what it's worth.

## What's already right
<Two or three specifics worth preserving — named, with citations. This is not
padding: an audit that only lists faults invites a rewrite of things that were
load-bearing and correct.>

## Prioritized backlog
1. F<n> — <title> (High) — <one line>
2. ...
```

Order findings by severity, not by dimension number. If nothing reaches High,
say that plainly at the top rather than promoting the worst Medium to fill the
slot.
