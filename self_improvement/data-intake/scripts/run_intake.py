#!/usr/bin/env python3
"""run_intake.py — run the enabled script adapters from the registry.

Reads evidence/intake/adapters.yaml, runs every enabled adapter that has a
`script`, and aggregates the new / skipped / failed counts. Adapters that are
MCP-only (a `mcp_tool` and no `script`) are listed as "pull in session",
because a standalone process cannot call an MCP tool; the data-intake skill
pulls those itself.

Schedule this next to your daily brief. It is idempotent (intake_lib dedupes).

Usage:
  python3 run_intake.py [--registry evidence/intake/adapters.yaml]
                        [--root evidence/intake] [--only <source>]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import shlex
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def load_registry(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        import yaml  # available in the repo env
        data = yaml.safe_load(path.read_text()) or {}
        return data.get("adapters", [])
    except ImportError:
        print("pyyaml not available; cannot read the registry.", file=sys.stderr)
        return []


def run_one(adapter: dict, root: str) -> dict:
    name = adapter.get("source", "?")
    script = adapter.get("script")
    if not script:
        return {"source": name, "status": "in-session",
                "note": f"MCP adapter ({adapter.get('mcp_tool', 'mcp')}); pull via the data-intake skill"}
    script_path = SCRIPT_DIR / script
    if not script_path.exists():
        return {"source": name, "status": "error", "note": f"script not found: {script}"}

    extra = shlex.split(adapter.get("args", ""))
    cmd = [sys.executable, str(script_path), *extra, "--root", root]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except Exception as exc:
        return {"source": name, "status": "error", "note": str(exc)}
    try:
        out = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"source": name, "status": "error",
                "note": (proc.stderr or proc.stdout or "no output").strip()[:200]}
    return {"source": name, "status": "ran",
            "new": out.get("new", 0), "skipped": out.get("skipped", 0),
            "failed": out.get("failed", 0), "success": out.get("success", False)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Run enabled data-intake adapters.")
    ap.add_argument("--registry", default="evidence/intake/adapters.yaml")
    ap.add_argument("--root", default="evidence/intake")
    ap.add_argument("--only", default=None, help="run only this source")
    args = ap.parse_args()

    adapters = load_registry(Path(args.registry))
    if not adapters:
        print("no adapters registered (evidence/intake/adapters.yaml).")
        return 0

    results = []
    for a in adapters:
        if not a.get("enabled", False):
            continue
        if args.only and a.get("source") != args.only:
            continue
        results.append(run_one(a, args.root))

    total_new = sum(r.get("new", 0) for r in results)
    total_skip = sum(r.get("skipped", 0) for r in results)
    total_fail = sum(r.get("failed", 0) for r in results)
    in_session = [r["source"] for r in results if r.get("status") == "in-session"]

    print(json.dumps({
        "ran": [r for r in results if r.get("status") == "ran"],
        "errors": [r for r in results if r.get("status") == "error"],
        "pull_in_session": in_session,
        "totals": {"new": total_new, "skipped": total_skip, "failed": total_fail},
    }, indent=2))
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
