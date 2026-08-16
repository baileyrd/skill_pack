# Applying the principles beyond the command line

The philosophy was written about programs connected by pipes, and it reads that
way. Most code being designed today is not a filter reading `stdin` — it's a
library, an HTTP service, a module inside a monolith, a background job, or an
agent tool. The principles still apply, but the *translation* is where the value
is; quoting McIlroy at a REST API is how this material earns an eye-roll.

Read the section matching the surface being designed or audited. The pattern is
the same each time: identify what plays the role of the **pipe** (the boundary
the thing is composed across), then apply the principles to *that*.

## Libraries and modules

The pipe is the **public API surface**. Composition happens through function
signatures and types rather than byte streams.

| Principle | Translation |
|---|---|
| Do one thing | One module, one reason to change. The `and` test runs on the module docstring. |
| Composability | Return values callers can feed elsewhere — plain data types over framework-bound objects. Accept interfaces, return structs. |
| Text streams | An open, documented type contract: no leaking internal types, no requiring a caller to construct a private builder. Serialization at the edge, not through the core. |
| Silence | No printing or logging from library code — return or raise, let the caller decide what to say. A library that writes to `stdout` has stolen a channel that isn't its. |
| Mechanism, not policy | Take config as parameters; don't read env vars from inside the engine. No implicit retries, no ambient timeouts the caller can't set. |
| Everything is a file | One uniform abstraction over the variants (one `Store` trait over memory/disk/S3) rather than three near-identical APIs. |

**The tell**: a library that can't be used from a test without a running
service, a config file, or a network has policy baked into mechanism.

## HTTP and RPC services

The pipe is the **wire contract** — routes, payloads, status codes.

| Principle | Translation |
|---|---|
| Do one thing | A service owns one bounded capability. The `and` test runs on the service name; endpoints that share only a deployment are a seam. |
| Composability | Predictable resource-shaped endpoints, stable pagination, no operation reachable only through a bespoke multi-step dance. |
| Text streams | A published schema (OpenAPI, protobuf) that is actually generated from the code, not maintained beside it and drifting. |
| Silence | The response body is the output. No debug fields in production payloads; logs go to the log sink, not the response. |
| Least surprise | HTTP semantics as everyone else uses them: correct verbs, real status codes. `200 {"error": ...}` is the canonical violation — it forces every client to parse the body to know if it worked. |
| Repair | Reject invalid requests at the boundary with a specific `4xx` and a field-level reason, not a `500` from three layers in. |

## Background jobs and pipelines

The pipe is **the queue, the file drop, or the table** between stages.

| Principle | Translation |
|---|---|
| Do one thing | One job, one stage. A job that extracts, transforms, loads, *and* alerts can't be retried at the granularity of its actual failure. |
| Composability | Each stage's output is durable and inspectable — someone can run stage 3 alone on stage 2's output when debugging at 2am. |
| Transparency | Intermediate state is stored, not held in memory across a whole run. |
| Repair | A failed stage fails the run visibly. Partial success reported as success is the failure mode that eats data silently. |
| Silence | Per-item logging on a million-row job is noise. Log stage boundaries, counts, and failures. |

## CLIs

Closest to the original context, so the principles apply nearly literally.
Concretely: results to `stdout` and diagnostics to `stderr`; a `--json` or
otherwise machine-readable mode alongside the human-readable default; a
non-interactive path for every interactive prompt; meaningful exit codes; no
colour or progress bars when `stdout` isn't a TTY; subcommands that each do one
thing rather than one command with mutually-exclusive mode flags.

## Agent tools and skills

The pipe is **the model's context window**, and the same economics apply — this
is the newest surface, and the least often reasoned about this way.

| Principle | Translation |
|---|---|
| Do one thing | A tool with one clear job triggers reliably. A tool that does six things is described vaguely and therefore fires unpredictably. |
| Composability | Return structured data the model can pass to another tool, not a rendered paragraph it has to re-parse. |
| Silence | Don't flood context with output the caller didn't ask for. Verbose success output is a direct, measurable cost here. |
| Mechanism, not policy | Expose capability; let the calling model decide the workflow. A tool that hardcodes a five-step sequence can't be used for step three alone. |
| Repair | Fail with an actionable message — the model is the one reading it and deciding what to do next. |

## Distributed systems: the one place the analogy breaks

`Do one thing` at process granularity across a network buys independent scaling
and deployment, and pays for it in latency, partial failure, and distributed
transactions — costs the original context never had, because pipes are local,
ordered, and fail as a unit.

`Parsimony` cuts *against* decomposition here: write a big program only when
nothing else will do, but also don't split into services when a module boundary
would have done. The relevant version of "small and sharp" for distributed
systems is usually **small modules inside one deployable**, not small
deployables. If a design argument is reaching for "Unix philosophy says
microservices," that's the reasoning to challenge — a modular monolith is the
more faithful reading.
