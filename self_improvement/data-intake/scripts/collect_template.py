#!/usr/bin/env python3
"""collect_<SOURCE>.py — adapter skeleton (copied by `data-intake scaffold`).

Fill in fetch(). Everything else (landing, dedupe, state, the envelope) is
handled by intake_lib, so an adapter is small on purpose.

Two flavours:
  - Script adapter (direct API or scrape): implement fetch() to return events
    and this script runs standalone (cron / run_intake.py).
  - MCP adapter (Fathom, Slack, Gmail, Notion, Apollo): a pure script cannot
    call an MCP tool. Leave fetch() raising NotImplementedError; the
    data-intake SKILL.md pulls these IN SESSION (it calls the MCP read tool,
    then lands each result with intake_lib.land_raw_event). Keep this file as
    the documented shape + the capture policy.

An "event" is a dict:
  {"event_id": str, "title": str, "body": str,
   "source_ref": str | None, "raw": str | None}

The capture POLICY lives here: filter to signal-dense items, shape the body.
Do not land everything. That is RAG, a different solution.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intake_lib  # noqa: E402

SOURCE = "manual"          # one of intake_lib.FOLDERS or an alias
CAPTURE_POLICY = "TODO"    # name of the policy this adapter applies


def fetch() -> list[dict]:
    """Return the signal-dense events to land. APPLY THE CAPTURE POLICY HERE.

    Script adapter: call the API / read the source, filter, shape, return.
    MCP adapter: leave this raising; the skill fills events in session.
    """
    raise NotImplementedError(
        "Implement fetch() for a script adapter, or pull this source in "
        "session via the data-intake skill (MCP adapters)."
    )


def run(root: str) -> dict:
    try:
        events = fetch()
    except NotImplementedError as exc:
        return {"success": False, "error": str(exc), "new": 0, "skipped": 0, "failed": 0}

    results, failed = [], 0
    for ev in events:
        try:
            results.append(intake_lib.land_raw_event(
                source=SOURCE,
                source_event_id=ev["event_id"],
                title=ev.get("title", "untitled"),
                body=ev.get("body", ""),
                source_ref=ev.get("source_ref"),
                capture_policy=CAPTURE_POLICY,
                raw_sidecar_content=ev.get("raw"),
                root=root,
            ))
        except Exception as exc:
            failed += 1
            print(f"  failed on {ev.get('event_id')}: {exc}", file=sys.stderr)

    out = intake_lib.summary(results)
    out["failed"] = failed
    out["success"] = failed == 0
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=f"{SOURCE} intake adapter.")
    ap.add_argument("--root", default="evidence/intake")
    args = ap.parse_args()
    result = run(args.root)
    print(json.dumps(result, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
