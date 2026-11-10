---
name: data-intake
description: >-
  Envelope and dedupe layer for a self-improvement harvest: validates curated
  events, sorts them to the right source folder, dedupes by source and event
  id, checkpoints state, and lands them read-only in
  evidence/intake/raw-events/ for human-reviewed refinement. Modes - process
  (drain the push dropzone), pull a source (MCP in session or a script
  adapter), plan, scaffold an adapter, pull-all. Use when the user says "run
  intake", "process the intake dropzone", "what landed in intake", "pull from
  a source" on a schedule, "scaffold an adapter for a source", "wire a system
  to push in" or "set up data intake". Not for a one-off look at some data
  (call the MCP tool directly), pulling everything, importance scoring, or
  building a knowledge base / RAG.
compatibility: Requires python3 and PyYAML (pip install pyyaml) for run_intake.py.
metadata:
  version: "1.0.0"
---

# Data Intake

Curate first, then pull. The cleanest intake harvests only the slice that was
already judged worth keeping. Because your sources are already connected,
a scheduled pull is the workhorse: the agent sweeps each source for the flagged
slice and lands it. When a source cannot be pulled, a push, export, or file-drop
into the landing zone does the same job. data-intake is the **envelope and dedupe
layer**. It does not discover importance from a firehose. It makes sure curated
events land in one shape that a downstream review step can read.

Clean line:

> Curate before the door. A human marks what matters with a cheap flag (a Slack
> reaction, a label, a tag, a watched folder); the sweep pulls only what is
> flagged. data-intake validates, dedups, and lands the event. It is plumbing,
> not judgement, and it is read-only.

## Where this sits

```
 improvement-intake-planner   data-intake (this skill)                 human review
 PLAN which sources       ->  PROCESS what arrived: validate, sort, -> (a separate
 carry signal                 dedup -> raw-events/<source>/             step)
```

Upstream: `evidence/intake/harvest-plan.md` and `adapters.yaml` from
`improvement-intake-planner`, plus a capture-policy decision made by the user.
Downstream: whatever reviews `raw-events/` (no capture or routing skill ships in
this pack yet). This skill just fills the folder that step drains.

## Two ways data arrives

Transport is an efficiency choice, not the principle. Curation happens at the
source either way. Pick whichever path reaches the source with least effort.

1. **PULL (the workhorse).** Your sources are already connected,
   so a scheduled pull is usually the least-effort path. The agent sweeps the
   source for the flagged slice and lands it. MCP sources are pulled in session
   or by a scheduled routine (the skill calls the MCP read tool); API sources can
   be a standalone script. The rule: **pull only what is flagged** (a reacted
   thread, a labelled message, a changed record), never raw everything.

2. **PUSH / DROP (flag-triggered, or for sources you cannot pull).** A flag can
   fire a push instead of waiting for a sweep: a no-code workflow (Slack Workflow
   Builder on an emoji-reaction trigger, n8n, Zapier, Make), webhook, export, or
   file-sync drops a curated event into the landing zone
   `evidence/intake/_dropzone/<source>/` the moment it is flagged. Pick it when an
   instant no-code push is simpler than a scheduled pull, or when the source has
   no connector to pull from. Same curation rule: send only what matters. No
   session is needed for the push itself.

Use this skill when intake must be repeatable, deduped, and stateful; for one-offs,
call the MCP tool directly.

## Read these references as needed

- `references/adapter-contract.md` for the envelope, the dedup/state contract,
  and the push-mapping vs pull-adapter shapes.
- `references/capture-policies.md` for what each source should push (or be pulled
  for), signal-dense, plus the intent fork (capture vs RAG).

Scripts run through `python3`; to run one directly, `chmod +x scripts/*.py` first (the skill sync drops the executable bit).

## Modes

### process

Drain the push lane. Process whatever has landed in the dropzone from a source
that pushes rather than pulls:

```bash
python3 <this skill's folder>/scripts/collect_filedrop.py --src evidence/intake/_dropzone/<source> --into <source>
```

It reads the pushed files, normalizes + dedups + lands them in
`raw-events/<source>/`. Schedule it (next to your daily brief) so pushed events
get processed unattended. Or run every registered source at once with `pull-all`
below. Reject malformed or out-of-policy files here; leave interpretation to
the refinement chain.

### pull `<source>` (the workhorse)

For a connected source (the usual case):

- **MCP source (in session):** call the source's MCP read tool (read-only verbs),
  apply the capture policy, and land each result with the helper:
  ```bash
  python3 - <<'PY'
  import sys; sys.path.insert(0, "<this skill's folder>/scripts")
  import intake_lib
  print(intake_lib.land_raw_event(
      source="fathom", source_event_id="call_88213",
      title="Discovery, Acme Corp",
      body="<signal-dense summary + key moments + action items>",
      source_ref="https://fathom.video/calls/88213",
      capture_policy="discovery-objections-v1"))
  PY
  ```
- **API/script source:** run its `collect_<source>.py`.

### plan

Read `evidence/intake/harvest-plan.md` if it exists, then walk each source
through this checklist:

```
For each source:
[ ] 1. Is this source connected and in the harvest plan?  N → run improvement-intake-planner first
[ ] 2. Does this event repeat often enough to warrant dedup + state?
        N → one-off, skip: call the MCP tool directly
[ ] 3. Can we pull it? (already connected via MCP, or has a clean API)
        Y → MCP pull in session or by routine; API → script adapter (collect_<source>.py)
        N → Can the source push / export / file-sync? Y → push/file-drop into _dropzone/
[ ] 4. Is a narrow policy definable? (filter, grain, body shape)
        N → do NOT proceed; pushing a firehose is not data-intake
[ ] 5. Name the capture policy (e.g. discovery-objections-v1). Version it.
[ ] 6. Rank by value-over-effort alongside other pending adapters.
```

Present the ranked list and chosen routes for approval before wiring anything.
See `references/capture-policies.md` for the per-source policy menu.

### scaffold `<source>`

Register a source. For a **push** source: add a registry row with the landing
folder and policy, and document the no-code/webhook mapping (the automation that
drops curated events into `_dropzone/<source>/`). For a **pull** source: copy
`scripts/collect_template.py` to `scripts/collect_<source>.py`, implement
`fetch()` (or leave it raising for an MCP source pulled in session), and add the
row.

### pull-all / process-all

`python3 <this skill's folder>/scripts/run_intake.py` runs every enabled adapter in
`evidence/intake/adapters.yaml` and aggregates the counts. Script adapters and
dropzone processors run directly; MCP sources are listed as "pull in session".

## The landing zone vs the read folder

- `evidence/intake/_dropzone/<source>/` is the **push inbox**: raw, unprocessed,
  written by automations or webhooks. Nothing downstream reads it.
- `evidence/intake/raw-events/<source>/` is the **processed intake**: validated,
  sorted, deduped, signal-dense. Downstream review reads only this.

`process` moves events from the first to the second. The processor is
non-destructive (it does not delete dropzone files), and dedup means
re-processing the same dropzone is safe.

## What is deterministic vs in-session

`intake_lib.py` (validate, sort, dedup, state, land), `collect_filedrop.py` (the
dropzone processor), and `run_intake.py` are plain scripts. The MCP pull path
(calling Fathom / Slack / Gmail and shaping the result) is Claude-orchestrated,
because MCP tools live in the session.

## What this skill does NOT do

- Does not process the files it lands into evidence cards (a separate downstream step).
- Does not pull everything (curate at the source; harvest only what is flagged).
- Does not score importance from a firehose. Importance is decided at the source
  by a cheap flag: a Slack reaction or channel, a Gmail star or label, a CRM
  stage or tag, a watched folder, an event type, or an explicit capture policy.
- Does not commit to authoritative context on its own. It lands read-only events;
  a human signs off downstream before anything authoritative or client-facing.
- Does not build a queryable knowledge base (that is a separate solution).
- Is not part of the skill-refinement chain.
- Never uses write verbs on a source. Read-only, always.

## When NOT to use

- One-off pull ("show me my last Fathom call"): call the MCP tool directly.
- The source already writes safely to the final destination without a session.
- You cannot define a narrow capture policy — importing everything is RAG, not intake.
- The source would require a perpetual watcher for low-value events.

## Common mistakes

1. **Pushing the raw firehose.** Sending every call, every Slack message, every email
   to the landing zone. The curation happens at the source (filter, summarise, flag)
   before the door — not inside data-intake.

2. **Write verbs in adapters.** An adapter that needs to create, update, delete, send,
   or move anything is not an adapter. `references/adapter-contract.md` enforces a
   strict read-only verb allowlist.

3. **Inventing a folder for a known source.** Nine curated folders exist (`fathom`,
   `drafts`, `sessions`, `support`, `evals`, `notion`, `slack`, `crm`, `manual`),
   plus aliases (`gmail` → `support`, `hubspot` → `crm`, …). Pass the canonical
   label or an alias; `intake_lib.resolve_folder` slugifies anything else into its
   own folder, so `Gmail-inbox` would quietly split one source in two.

4. **Unversioned capture policy names.** Using `capture_policy: fathom-calls` instead
   of `capture_policy: discovery-objections-v1` makes policy changes invisible in the
   envelope. Always version the name so a change is auditable and reversible.

5. **Using this skill for one-offs.** If the event will never repeat, data-intake adds
   dedupe overhead and state for zero benefit. Call the MCP tool, land the result once
   by hand or with a direct `intake_lib.land_raw_event` call.

## Wrap-up retro — plan and scaffold modes only

After a `plan` or `scaffold` run, run a `meta/skill-retro` pass on this skill
grounded in that run: did the checklist route each source correctly, did the
adapter template fit, did any source need a write verb or a firehose? Skip it
for `process`, `pull` and `pull-all`: those are routine, often scheduled runs
where a retro is out of proportion; run one there only if the user asks.
Reporting is automatic and safe; applying any finding is a separate, approved
change.
