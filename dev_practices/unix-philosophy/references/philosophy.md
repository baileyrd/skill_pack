# Unix Software Design Philosophy

The source reference material behind this skill. `SKILL.md` distills it into
decision rules and audit criteria; this file is the *why* — read it when a
design decision turns on the reasoning rather than the rule, or when a
recommendation needs to be justified to someone who hasn't bought in yet.

> "Write programs that do one thing and do it well. Write programs to work
> together. Write programs to handle text streams, because that is a universal
> interface."
> — Doug McIlroy

## Core Tenet

**Do one thing and do it well.** A tool should have a single, focused purpose and
excel at it. Feature accumulation is a design smell — new capability belongs in a
new tool, composed with the old ones.

## Foundational Principles

### Composability
Write programs that work together. Small, orthogonal tools chain into pipelines
to solve problems no single tool anticipated:

```sh
grep ERROR app.log | cut -d' ' -f3 | sort | uniq -c | sort -rn
```

The pipeline is composition made executable. The value of a tool is multiplied by
every other tool it can combine with.

### Text Streams as the Universal Interface
Programs should read and write plain text. Text is the one format every other
program, language, and human can consume. Binary and bespoke formats create
coupling; text creates leverage.

### Silence Is Golden
Succeed quietly. Only produce output when there is something to report —
requested results or an error. Chatty programs break pipelines and bury signal in
noise.

### Mechanism, Not Policy
Provide capability; let the user decide how to apply it. Don't hardcode workflows
or assume you know the user's intent better than they do.

### Everything Is a File
Devices, sockets, processes — expose them through one uniform abstraction so the
same small tools operate on all of them. Uniform interfaces are what make
composition possible at the OS level.

## Raymond's Rules (The Art of Unix Programming, distilled)

| Rule | Meaning |
|---|---|
| Modularity | Simple parts, clean interfaces |
| Clarity | Clarity beats cleverness |
| Composition | Design programs to be connected to other programs |
| Separation | Separate policy from mechanism; interfaces from engines |
| Simplicity | Add complexity only where you must |
| Parsimony | Write a big program only when nothing else will do |
| Transparency | Design for visibility — make inspection and debugging easy |
| Robustness | Robustness is the child of transparency and simplicity |
| Representation | Fold knowledge into data so program logic can be dumb |
| Least Surprise | Do the least surprising thing |
| Silence | When a program has nothing surprising to say, say nothing |
| Repair | Fail loudly, and as soon as possible |
| Economy | Programmer time is expensive; conserve it over machine time |
| Generation | Write programs to write programs when you can |
| Optimization | Prototype before polishing; get it working before optimizing |
| Diversity | Distrust all claims of "one true way" |
| Extensibility | Design for the future — it arrives sooner than you think |

## Why It Endures

Small, sharp tools with narrow, explicit interfaces beat monolithic applications
because they are:

- **Testable** — a single-purpose tool has a small behavioral surface
- **Replaceable** — narrow interfaces make swapping implementations cheap
- **Recombinable** — utility compounds as the toolset grows
- **Comprehensible** — each piece fits in one head

The same instincts show up in modern practice as composition over inheritance,
ports-and-adapters, KISS, and modular boundaries with explicit contracts. Unix
simply proved them at operating-system scale, fifty years early.

## The rule that governs the other sixteen

**Diversity** — *distrust all claims of "one true way"* — is on the list
deliberately, and it applies to this list. Every principle above is a default
with a cost, not a law:

- **Text streams** cost parsing ambiguity and throughput. A columnar format for
  a hundred-million-row dataset is not a philosophy violation; refusing to emit
  *anything* another program can read is.
- **Do one thing** cost coordination. Ten processes where one function would do
  is `parsimony` violated in the other direction — the rule says write a big
  program only when nothing else will do, not "never write a big program."
- **Silence** costs discoverability for interactive users. `git` prints on
  success because a human is the primary consumer; `grep` doesn't because a
  pipeline is.
- **Mechanism, not policy** costs onboarding. A tool with no defaults at all is
  mechanism-pure and unusable.

Cite these principles as reasoning, not authority. "This should be two tools
because Unix says so" is a worse argument than "this should be two tools because
the export path and the render path have no shared state and separate release
cadences, so bundling them means one can't ship without the other."
