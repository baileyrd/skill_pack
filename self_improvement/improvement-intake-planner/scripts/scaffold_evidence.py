"""One-time setup for the self-improvement loop's evidence workspace.

Idempotent and standalone (no server), so every surface gets the same folder
contract.
"""
from __future__ import annotations

import argparse
from pathlib import Path

_TREE = [
    "intake/raw-events", "intake/_dropzone",
    "inbox", "proposals", "weekly-digests",
    "routed/skill", "routed/context", "routed/memory", "routed/knowledge",
    "routed/eval", "routed/state", "routed/digest", "routed/no-op",
]

_ADAPTERS_HEADER = ("# data-intake adapter registry. Everything ships disabled;\n"
                    "# enable one once it points at something real.\nadapters: []\n")


def scaffold(root: str) -> dict:
    root_p = Path(root)
    created, existed = [], []
    for sub in _TREE:
        d = root_p / sub
        (existed if d.is_dir() else created).append(sub)
        d.mkdir(parents=True, exist_ok=True)
    adapters = root_p / "intake" / "adapters.yaml"
    if not adapters.exists():
        adapters.write_text(_ADAPTERS_HEADER)
        created.append("intake/adapters.yaml")
    return {"created": created, "existed": existed}


def main() -> int:
    p = argparse.ArgumentParser(description="Scaffold the evidence workspace.")
    p.add_argument("--root", default="evidence")
    args = p.parse_args()
    res = scaffold(args.root)
    print(f"created {len(res['created'])}, existed {len(res['existed'])}")
    if res["created"]:
        for c in res["created"]:
            print(f"  + {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
