#!/usr/bin/env python3
"""intake_lib.py — the deterministic core of the data-intake skill.

This is the shared helper older source-specific scripts never had:
it lands a raw external event as a curated markdown envelope in
evidence/intake/raw-events/<folder>/, and it dedupes + checkpoints so
re-running an adapter never produces duplicate files.

Every adapter (manual, scheduled pull, webhook) calls these functions, so
the "land + dedupe + state" contract is enforced in exactly one place.

Stdlib only. The actual fetch from a source (MCP tool, API, scrape) happens
in the adapter or in the skill session; this module never reaches the network.
"""
from __future__ import annotations

import json
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# The nine curated intake folders. Unknown sources get their own slugified
# folder (see resolve_folder).
FOLDERS = {
    "fathom", "drafts", "sessions", "support",
    "evals", "notion", "slack", "crm", "manual",
}

# Convenience aliases: a source_system label -> the intake folder it lands in.
# Adapters can pass an alias and it resolves to the right folder.
ALIASES = {
    "gmail": "support", "email": "support",
    "apollo": "crm", "hubspot": "crm", "salesforce": "crm",
    "fireflies": "fathom", "zoom": "fathom", "call": "fathom",
    "zendesk": "support", "intercom": "support",
    "docs": "notion", "drive": "notion",
    "filedrop": "manual", "folder": "manual",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def slugify(text: str, max_len: int = 48) -> str:
    """Lowercase kebab slug, trimmed to max_len, safe for a filename."""
    text = (text or "untitled").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if len(text) > max_len:
        text = text[:max_len].rstrip("-")
    return text or "untitled"


def resolve_folder(source: str) -> str:
    """Resolve a source label to an intake folder under raw-events/.

    Known folders and aliases map to the curated nine. Anything else — a
    harvest source the improvement-intake-planner proposed, e.g.
    'youtube-analytics' — lands in its own slugified folder, since the
    planner produces arbitrary MCP source names by design.
    """
    s = (source or "").lower().strip()
    if s in FOLDERS:
        return s
    if s in ALIASES:
        return ALIASES[s]
    return slugify(s)


def _state_path(root: Path, source: str) -> Path:
    return root / ".state" / f"{source}.json"


def load_state(root: str | Path, source: str) -> dict:
    p = _state_path(Path(root), source)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            pass
    return {"last_pulled_at": None, "seen_event_ids": []}


def is_seen(root: str | Path, source: str, event_id: str) -> bool:
    return event_id in set(load_state(root, source).get("seen_event_ids", []))


def mark_seen(root: str | Path, source: str, event_id: str) -> None:
    root = Path(root)
    state = load_state(root, source)
    seen = state.get("seen_event_ids", [])
    if event_id not in seen:
        seen.append(event_id)
    # keep the state file bounded; the last 5000 ids is plenty for dedupe
    state["seen_event_ids"] = seen[-5000:]
    state["last_pulled_at"] = _now_iso()
    p = _state_path(root, source)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2))


def _envelope(meta: dict, body: str) -> str:
    lines = ["---"]
    for k, v in meta.items():
        if v is None:
            continue
        # quote strings that could confuse a naive YAML reader
        if isinstance(v, str) and (":" in v or v.startswith(("@", "#", "[", "{"))):
            lines.append(f'{k}: "{v}"')
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append("")
    lines.append(body.rstrip())
    lines.append("")
    return "\n".join(lines)


def land_raw_event(
    source: str,
    source_event_id: str,
    title: str,
    body: str,
    *,
    source_ref: str | None = None,
    capture_policy: str | None = None,
    raw_sidecar_content: str | None = None,
    raw_sidecar_ext: str = "raw.txt",
    root: str | Path = "evidence/intake",
    date: str | None = None,
) -> dict:
    """Land one external event as a curated markdown envelope.

    Returns {"status": "landed"|"skipped", "path": str|None, "event_id": str}.
    Idempotent: if (source, source_event_id) was already landed, it is skipped.
    Never half-writes: the sidecar is written before the envelope.
    """
    folder = resolve_folder(source)
    root = Path(root)
    event_id = str(source_event_id)

    if is_seen(root, folder, event_id):
        return {"status": "skipped", "path": None, "event_id": event_id}

    day = date or _today()
    slug = slugify(title)
    out_dir = root / "raw-events" / folder
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = f"{day}-{slug}"
    md_path = out_dir / f"{stem}.md"
    # avoid clobbering an unrelated file that happens to share date+slug
    if md_path.exists():
        h = hashlib.sha1(event_id.encode()).hexdigest()[:6]
        stem = f"{day}-{slug}-{h}"
        md_path = out_dir / f"{stem}.md"

    sidecar_name = None
    if raw_sidecar_content is not None:
        sidecar_name = f"{stem}.{raw_sidecar_ext}"
        (out_dir / sidecar_name).write_text(raw_sidecar_content)

    meta = {
        "source_system": folder if source.lower() in FOLDERS else source.lower(),
        "source_event_id": event_id,
        "capture_policy": capture_policy,
        "pulled_at": _now_iso(),
        "source_ref": source_ref,
        "raw_sidecar": sidecar_name,
        "title": title,
    }
    md_path.write_text(_envelope(meta, body))
    mark_seen(root, folder, event_id)
    return {"status": "landed", "path": str(md_path), "event_id": event_id}


def summary(results: list[dict]) -> dict:
    landed = [r for r in results if r.get("status") == "landed"]
    skipped = [r for r in results if r.get("status") == "skipped"]
    return {
        "success": True,
        "new": len(landed),
        "skipped": len(skipped),
        "failed": 0,
        "landed_paths": [r["path"] for r in landed],
    }


if __name__ == "__main__":
    # tiny self-check: land a sample event twice, prove dedupe
    import tempfile, sys
    with tempfile.TemporaryDirectory() as d:
        r1 = land_raw_event("manual", "evt-1", "Self check note",
                            "body of the note", root=d, capture_policy="selfcheck")
        r2 = land_raw_event("manual", "evt-1", "Self check note",
                            "body of the note", root=d, capture_policy="selfcheck")
        ok = r1["status"] == "landed" and r2["status"] == "skipped"
        print(json.dumps({"selfcheck_pass": ok, "first": r1["status"], "second": r2["status"]}))
        sys.exit(0 if ok else 1)
