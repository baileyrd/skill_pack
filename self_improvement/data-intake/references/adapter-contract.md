# Adapter Contract

**Contents:** Five parts every adapter needs · The envelope · Intake folders · Read-only verb allowlist · Push mapping vs pull adapter · What this is not

---

An adapter is a documented contract plus one thin script. It gets already-curated
events from one source into `evidence/intake/raw-events/<folder>/` in one
shape a downstream review step can read unchanged. Adapters never write
to a skill, a context file, or a database. They only land curated raw events.

## The five parts (every adapter, every tier)

1. **Input.** Exactly one read source: an MCP read tool, a direct API call, a
   scrape, or a webhook payload. Read-only verbs only (see the allowlist below).
2. **Capture policy then file.** Enforce the source's already-approved capture
   policy (narrow filter, expected grain, body shape), then write the markdown
   envelope via `intake_lib.land_raw_event`. Optionally keep the raw original as
   a sidecar.
3. **Dedupe key.** `(source, source_event_id)`. `land_raw_event` checks the
   state before writing; an already-seen event is skipped. Pick a stable
   `source_event_id` from the origin system (a call id, a message ts, a thread
   id, a record id, or a content hash).
4. **State / checkpoint.** `evidence/intake/.state/<source>.json` holds
   `last_pulled_at` and `seen_event_ids`. Re-running an adapter never duplicates.
5. **Fail safe.** On any error, write nothing for that item and report it.
   Never half-write. `land_raw_event` writes the sidecar before the envelope, so
   an interrupted write does not leave a dangling envelope.

## The envelope (what gets written)

One markdown file per event, in the source's intake folder, named
`<YYYY-MM-DD>-<slug>.md` (a short hash is appended only on a filename clash):

```yaml
---
source_system: fathom            # the source label (maps to the intake folder)
source_event_id: "call_88213"    # stable id from the origin system (dedupe key)
capture_policy: "discovery-objections-v1"
pulled_at: "2026-06-09T14:00:00Z"
source_ref: "https://fathom.video/calls/88213"
raw_sidecar: "2026-06-09-acme-discovery.raw.json"   # optional, omitted if none
title: "Discovery, Acme Corp"
---
the signal-dense, normalized body
```

The frontmatter is a subset of an evidence-card schema, so a downstream step
can lift it cleanly instead of re-parsing.

## The intake folders

Land into one of the nine curated folders where one fits:

`fathom`, `drafts`, `sessions`, `support`, `evals`, `notion`, `slack`, `crm`,
`manual`.

`intake_lib` also accepts common aliases and maps them to a folder, for example
`gmail` and `email` to `support`, `apollo`/`hubspot`/`salesforce` to `crm`,
`zoom`/`fireflies` to `fathom`, `docs`/`drive` to `notion`. Any other label
gets its own slugified folder.

## Read-only verb allowlist

Adapters may only READ. Allowed verbs: list,
search, get, read, fetch, export, query. Never create, update, delete, send,
move, or post. An adapter that needs a write verb is not an adapter.

## Push mapping (primary) vs pull adapter (fallback)

- **Push/drop mapping (primary).** A human flag, no-code automation (n8n,
  Zapier, Make), webhook, export, or file-sync writes a curated event into
  `evidence/intake/_dropzone/<source>/`. Nothing in this repo runs the push; the
  mapping lives in the source or automation tool, and the source-side rule is
  send only what matters. On arrival, `collect_filedrop.py` validates, sorts,
  dedups, and lands it.
- **Pull adapter (fallback).** For a source that cannot push:
  - **API or scrape:** implement `fetch()` in `collect_<source>.py`; it runs
    standalone via cron or `run_intake.py`.
  - **MCP:** a standalone process cannot call an MCP tool, so it is pulled IN
    SESSION. The data-intake skill calls the MCP read tool, applies the policy, and
    lands each result with `intake_lib.land_raw_event`. The `collect_<source>.py`
    keeps the documented shape plus the policy, with `fetch()` left raising.

## What this is not

Not RAG, not a watcher framework, and not an importance scorer. An adapter lands
signal-dense, curated events for refinement and context. If you want to capture
everything to query later, that is a different solution (a knowledge base on a
vector store), out of scope here.
