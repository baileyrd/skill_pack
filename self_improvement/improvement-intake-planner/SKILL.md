---
name: improvement-intake-planner
description: >-
  Setup-time planner for a self-improvement harvest: scaffolds the evidence/
  workspace, scans the connected MCP servers, keeps only sources that carry
  recurring drift, correction or demand signal, and writes a harvest plan plus
  disabled adapter stanzas for data-intake to execute. Use when the user says
  "plan my harvest", "what should I pull for self-improvement", "scan my MCP
  for improvement signal", "set up intake harvesting", "which of my connected
  tools have signal" or "build my harvest plan". Run once at setup and again
  when connected tools change. Does not pull data (that is data-intake) and
  never enables an adapter.
compatibility: Requires python3 and PyYAML (pip install pyyaml).
metadata:
  version: "1.0.0"
---

# Improvement Intake Planner

The one judgment `data-intake` doesn't make: **of everything you have
connected, which sources produce recurring signal worth feeding the
self-improvement loop, and what should be pulled from each.**

Clean line:

> This says what's worth learning from. Then data-intake pulls it.

## Load-bearing rules

- **The planner never pulls data.** It only writes the plan. Pulling is
  data-intake's job. This keeps this skill's responsibility single and
  preserves data-intake's "not an importance scorer" contract.
- **The planner never enables an adapter.** Every stanza it writes ships
  `enabled: false`. A human enables one once it points at something real
  (a working `mcp_tool` name, the right capture policy). Proposing is safe;
  enabling is a decision.
- **The planner never invents a source it cannot justify.** The deterministic
  floor (`scan_mcp_sources.py`) only recognises MCP families that plausibly
  carry drift/correction/demand signal. Unknown servers yield nothing. The LLM
  step may drop candidates but must not add unrecognised ones.
- **Weekly, read-only, by default.** External pulls are metered, so the default
  cadence is weekly (never real-time — that is a different, reactive system).
  Prefer read-only sources; a write-capable server is a candidate only for its
  read surface.

Scripts run through `python3`; to run one directly, `chmod +x scripts/*.py` first (the skill sync drops the executable bit).

## Workflow

### 1. Determine the connected MCP servers

Use the servers available in this session (the `mcp__<server>__*` tools you can
see), or a list the user passes. You do not need every tool — just the server
names, e.g. `youtube-analytics`, `Notion`, `Gmail`, `Slack`, `Fathom`.

If an inventory of the user's data sources already exists, read it for richer
context — but do not require it.

### 2. Run the deterministic candidate floor

```bash
python3 <this skill's folder>/scripts/scan_mcp_sources.py
```

(or import `candidate_sources(connected, datamap_path=None)` and pass the list).
This returns the grounded candidate set — the floor the plan is built on, so it
is never hallucinated from nothing.

### 3. Refine (the judgment step)

For each candidate, decide:

- **Keep or drop.** Drop write-heavy, low-signal, or noisy sources. A source
  earns its place only if a *recurring* pattern from it would change how a
  skill, a piece of context, or a decision works.
- **Name the read tool.** Replace the `<the read tool for …>` placeholder with
  the actual MCP read tool (e.g. `mcp__youtube-analytics__get_top_videos`,
  `mcp__Notion__notion-search`). Read tools only.
- **Confirm cadence.** Weekly unless the user has a specific reason otherwise.
- **What to pull.** One line: the specific slice that carries signal (e.g.
  "videos whose 28-day CTR fell below the channel median", not "all analytics").

Cut ruthlessly. A five-source plan that gets run beats a fifteen-source plan
that overwhelms the intake and never gets reviewed.

### 4. Write the plan

```bash
python3 <this skill's folder>/scripts/write_plan.py
```

(or import `write_plan(candidates, root)`.) This writes:

- `evidence/intake/harvest-plan.md` — the human-readable plan.
- disabled adapter stanzas appended to `evidence/intake/adapters.yaml` — what
  `run_intake.py` and the data-intake skill consume. Existing sources are never
  duplicated.

### 5. Hand off

Report the plan. Tell the user:

> Everything is proposed disabled. To turn one on: open
> `evidence/intake/adapters.yaml`, set `enabled: true` on the source you want,
> confirm its `mcp_tool` is the real read tool, then run **data-intake** (weekly)
> to pull it into `evidence/intake/raw-events/`. What lands there is raw
> material for a human-reviewed step, never a change applied straight to the
> setup.

### 6. Wrap-up retro

Run a `meta/skill-retro` pass on this skill grounded in the run: which
candidates `scan_mcp_sources.py` missed or mis-recognised, which you dropped
in step 3 and why, whether the read-tool names held up. Reporting is
automatic and safe; applying any finding is a separate, approved change.

## What this is not

- Not a data audit of everything connected.
- Not a puller — that's `data-intake` (`run_intake.py` + the skill's in-session MCP pulls).
- Not a capturer or router of evidence; that downstream step is not in this pack.
- Not a real-time system — external harvest is weekly on purpose.

## Setup helper

First-time setup of the whole evidence workspace (idempotent, runs standalone
with no dashboard, so Cowork and VS Code get the identical folder contract):

```bash
python3 <this skill's folder>/scripts/scaffold_evidence.py --root evidence
```

Schedule the weekly pull with cron, a desktop scheduled task or a cloud
trigger running `data-intake`.
