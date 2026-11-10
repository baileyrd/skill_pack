"""Turn harvest candidates into (a) a human-readable harvest-plan.md and
(b) disabled adapter stanzas in adapters.yaml that run_intake.py understands.

Never enables an adapter and never duplicates one. Enabling is a human act
(point it at something real first); the planner only proposes.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def _existing_sources(reg: dict) -> set[str]:
    return {a.get("source") for a in (reg.get("adapters") or []) if a.get("source")}


def write_plan(candidates: list[dict], root: str) -> dict:
    root_p = Path(root)
    root_p.mkdir(parents=True, exist_ok=True)
    reg_path = root_p / "adapters.yaml"
    reg: dict = {}
    if reg_path.exists():
        reg = yaml.safe_load(reg_path.read_text()) or {}
    reg.setdefault("adapters", [])
    have = _existing_sources(reg)

    added, skipped = 0, 0
    for c in candidates:
        if c["source"] in have:
            skipped += 1
            continue
        reg["adapters"].append({
            "source": c["source"],
            "mode": "pull",
            "tier": "T1a",
            "mcp_tool": c.get("mcp_tool") or f"<the read tool for {c['source']}>",
            "capture_policy": "self-improvement-v1",
            "schedule": c.get("suggested_cadence", "weekly"),
            "enabled": False,
            "note": f"{c['signal_kind']}: {c['why']}",
        })
        have.add(c["source"])
        added += 1

    # Write registry, preserving any human header comment lines that were there.
    header = ""
    if reg_path.exists():
        text = reg_path.read_text()
        if text.lstrip().startswith("#"):
            header = "\n".join(l for l in text.splitlines() if l.startswith("#")) + "\n\n"
    reg_path.write_text(header + yaml.safe_dump(reg, sort_keys=False))

    # Write the human plan.
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"# Harvest plan ({ts})", "",
             "What external signal the self-improvement loop pulls, and why.",
             "Everything is proposed disabled — enable one once it points at something real.", ""]
    for c in candidates:
        lines += [f"## {c['source']}  ·  {c['signal_kind']}",
                  f"- **why:** {c['why']}",
                  *([f"- **pull:** {c['pull']}"] if c.get("pull") else []),
                  f"- **cadence:** {c.get('suggested_cadence', 'weekly')}",
                  f"- **read-only:** {c.get('read_only', True)}", ""]
    plan_path = root_p / "harvest-plan.md"
    plan_path.write_text("\n".join(lines))

    return {"plan_path": str(plan_path), "adapters_added": added, "adapters_skipped": skipped}


def main() -> int:
    """CLI: refined candidates JSON (file or '-' for stdin) -> plan + registry."""
    ap = argparse.ArgumentParser(description="Write harvest-plan.md and disabled adapter stanzas.")
    ap.add_argument("--candidates", required=True,
                    help="JSON list from scan_mcp_sources.py, refined (optional keys: mcp_tool, pull); '-' = stdin")
    ap.add_argument("--root", default="evidence/intake")
    args = ap.parse_args()
    src = sys.stdin.read() if args.candidates == "-" else Path(args.candidates).read_text()
    print(json.dumps(write_plan(json.loads(src), args.root), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
