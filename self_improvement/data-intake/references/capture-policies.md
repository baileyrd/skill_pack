# Capture Policies

**Contents:** Set the intent first · Who curates? · Per-source menu · When not to use data-intake · How a policy lives in code

---

A capture policy is the curation. For one source it answers three things: what
crosses the door (the filter), in what form (the grain), and how it gets curated.
The default everywhere is signal-dense: only the high-signal layer comes in, with
the raw original kept as an optional sidecar, never vacuum everything.

Importance is decided before the event reaches the door, not by scoring a
firehose after. At the **source**, the pull query (or the push/export) is
configured to send only what matters: a summarised call, a processed change, a
flagged message. On **arrival**,
data-intake validates, sorts, dedups, and checkpoints. It may reject malformed
or obviously out-of-policy files, but it is not an importance scorer for a
firehose. The policy is the gate.

This is the part a consultant tailors per client. The table below is the
starting menu, not the answer. The value is knowing which of these signals
matter for a specific business.

## Set the intent first

Before any policy, decide why you are pulling this data:

- **Refinement and context** (what this skill is for): selective, signal-first.
  Lessons and changed facts that refine skills and update context. Low volume.
- **RAG / chat-with-your-data**: comprehensive, embedded, retrievable. The
  opposite philosophy (capture everything). A different solution, out of scope.

If you find yourself wanting to pull every message, you are building RAG.

## Who curates? (the layered answer)

Nobody hand-sifts everything. Curation is spread across cheap layers, and the
policy writes it down:

1. **Scoping.** Decide once which channels, labels, databases, or call types you
   even look at. Biggest lever, lowest effort.
2. **Source AI first pass.** Let the tool's own AI distill (a Fathom summary),
   then capture that.
3. **In-flow flagging.** React, label, or tag as you work (an emoji that means
   "capture this"). Near-zero effort, high signal.
4. **AI proposes, human approves.** A narrow pull can surface candidates, but the
   evidence pipeline's existing human gate confirms downstream.
5. **Consultant configured.** Set the policy with the client per engagement.

## The per-source menu

| Source | What to capture (filter) | Form / grain | Curation lever |
| --- | --- | --- | --- |
| **Fathom calls** | Discovery / support / review calls; within them: objections, new requirements, budget reactions, competitor mentions, scope changes, voice corrections | AI summary + key moments + action items (full transcript as optional sidecar) | Source AI summary; filter by call type; consultant picks the signal types |
| **Slack** | Watched channels only (feedback, support, cs, wins, decisions) OR reaction-flagged messages OR forwarded threads. Never every conversation. | The flagged message/thread + minimal context | In-flow reaction flagging; channel scoping set once |
| **Gmail** | Labeled threads only (support, feedback, client-deliverable); or replies from key-client domains; or intent matches (complaint, feature request, cancellation, testimonial) | The thread body | Curation by labeling while triaging; or a classifier on a watched label |
| **CRM / Apollo** | State changes only: deal-stage moves, closed-lost reasons, won-deal attributes, new-requirement notes | Changed field + record context | Change detection; reps log reasons in structured fields |
| **Notion / docs** | Edits to watched databases only (ICP doc, SOPs, client pages) | The changed page / diff | DB scoping + last_edited |
| **Support tickets** | Escalated / low-CSAT / recurring-theme tickets | Ticket summary + resolution | Tag/category scoping; recurring-theme detection |
| **AI sessions** | Sessions where you corrected the AI more than once for the same thing | The correction + context | Auto-flag on the repeated-correction pattern |
| **File-drop** | Whatever lands in a watched/synced folder (the manual and file-sync lane) | The file as-is | You decide what goes in the folder |

## When not to use data-intake

Skip the adapter when:

- the source already writes safely to the final destination
- the event is a one-off you can review directly
- you cannot define a narrow policy and are tempted to import everything
- the source would require a perpetual watcher for low-value events

The default for most users is one manual/file-drop source, then one or two
narrow pulls or labels once the value is obvious.

## How a policy lives in code

The capture policy has two homes:

- A **name** in the adapter registry (`capture_policy:`) and stamped into every
  envelope it produces, so you can trace which policy landed a card.
- The **filter + grain logic** inside the adapter's `fetch()` (script adapters)
  or the skill's in-session pull step (MCP adapters). That logic is where you
  encode "only flagged Slack messages" or "Fathom summaries, not transcripts".

Version the name (`discovery-objections-v1`) so a policy change is visible and
reversible.
