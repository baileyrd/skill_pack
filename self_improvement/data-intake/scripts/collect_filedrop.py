#!/usr/bin/env python3
"""collect_filedrop.py — a runnable file-drop adapter.

The simplest real adapter: watch a folder (a synced Drive/Dropbox folder, an
email-to-folder export, or a manual drop dir) and land each file as a curated
intake event. This is the Tier 0 (manual) and Tier 2c (file-sync) lane, and it
needs no API and no MCP, so it runs from cron or by hand.

It also doubles as the reference implementation of the adapter contract:
fetch -> apply policy -> intake_lib.land_raw_event (which dedupes + checkpoints).

Usage:
  python3 collect_filedrop.py --src <folder> [--into manual] [--policy name]
                              [--root evidence/intake] [--glob '*.md']
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intake_lib  # noqa: E402


def collect(src: Path, into: str, policy: str | None, root: str, pattern: str) -> dict:
    if not src.exists():
        return {"success": False, "error": f"src folder not found: {src}",
                "new": 0, "skipped": 0, "failed": 0}

    results = []
    failed = 0
    for path in sorted(src.rglob(pattern)):
        if not path.is_file() or path.name.startswith("."):
            continue
        try:
            content = path.read_text(errors="ignore")
            # event id is stable across re-runs unless the file content changes
            rel = path.relative_to(src).as_posix()
            event_id = f"{rel}:" + hashlib.sha1(content.encode()).hexdigest()[:12]
            results.append(intake_lib.land_raw_event(
                source=into,
                source_event_id=event_id,
                title=path.stem,
                body=content,
                source_ref=str(path),
                capture_policy=policy,
                root=root,
            ))
        except Exception as exc:  # never half-process the batch
            failed += 1
            print(f"  failed on {path}: {exc}", file=sys.stderr)

    out = intake_lib.summary(results)
    out["failed"] = failed
    out["success"] = failed == 0
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="File-drop intake adapter.")
    ap.add_argument("--src", required=True, help="folder to read events from")
    ap.add_argument("--into", default="manual", help="intake folder/source (default: manual)")
    ap.add_argument("--policy", default="filedrop-all", help="capture_policy label")
    ap.add_argument("--root", default="evidence/intake", help="intake root")
    ap.add_argument("--glob", dest="pattern", default="*", help="file glob (default: *)")
    args = ap.parse_args()

    result = collect(Path(args.src), args.into, args.policy, args.root, args.pattern)
    print(json.dumps(result, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
