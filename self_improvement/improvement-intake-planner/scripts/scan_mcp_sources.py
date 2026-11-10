"""Decide which connected MCP sources are worth harvesting for the
self-improvement loop. data-intake (explicitly not an importance scorer)
does not make this judgment.

Deterministic and conservative: it maps KNOWN MCP families to the kind of
self-improvement signal they carry, and says nothing about servers it does not
recognise. The skill's LLM step refines this into the final plan; this script
is the grounded floor so the plan is never hallucinated from an empty list.
"""
from __future__ import annotations

import json
import re
import sys

# family regex -> (signal_kind, why, read_only). Only families that plausibly
# carry drift / correction / demand signal for a solo AIOS. Conservative on
# purpose: unknown servers are not invented as candidates.
_FAMILIES = [
    (r"youtube", "performance-drift",
     "video CTR/retention vs your own median surfaces which content bets decayed", True),
    (r"notion", "decision-and-doc-change",
     "edited docs and status changes are corrections and decisions worth capturing", True),
    (r"gmail|mail", "recurring-request",
     "repeated inbound questions are unmet-demand and support signal", True),
    (r"slack", "correction-and-thread",
     "flagged threads carry corrections and 'do it this way' feedback", True),
    (r"fathom|fireflies|otter", "call-lesson",
     "call summaries carry objections, promises, and decisions with reasons", True),
    (r"linear|jira|github", "failure-and-issue",
     "recurring issues and closed-with-reason tickets are failure signal", True),
    (r"kit|beehiiv|convertkit", "funnel-drift",
     "open/click decay flags messaging that stopped landing", True),
]


def candidate_sources(connected: list[str], datamap_path: str | None = None) -> list[dict]:
    """Map connected MCP server names to harvest candidates. Unknown servers
    yield nothing — the planner never invents a source it cannot justify.

    `datamap_path` is accepted for callers that hold a data-source inventory,
    but this floor does not depend on it: the candidate set is derived from
    the connected-server names alone.
    """
    out: list[dict] = []
    seen: set[str] = set()
    for name in connected:
        low = (name or "").lower()
        for pat, kind, why, read_only in _FAMILIES:
            if re.search(pat, low) and name not in seen:
                seen.add(name)
                out.append({
                    "source": name,
                    "mcp_family": pat.split("|")[0],
                    "signal_kind": kind,
                    "why": why,
                    "suggested_cadence": "weekly",
                    "read_only": read_only,
                })
                break
    return out


def main(argv: list[str]) -> int:
    """CLI: server names as arguments -> candidate list as JSON on stdout."""
    if not argv:
        print("usage: python3 scan_mcp_sources.py <server> [<server> ...]", file=sys.stderr)
        return 2
    print(json.dumps(candidate_sources(argv), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
