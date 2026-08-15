#!/usr/bin/env python3
"""PostToolUse hook: remind that a skill carries a wrap-up skill-retro step.

Twelve skills in this repo end with "run a `meta/skill-retro` pass on
yourself." Measured across this repo's own use, that step fired **zero** times
out of two opportunities — the reader (me) simply forgot, twice, and the user
had to ask both times. Instructions that reliably don't happen are the
aspirational-claim problem in a different costume, so ADR-0002's sibling
argument applies: wire it, or stop claiming it.

This is the wiring. Reads the PostToolUse payload on stdin, and if the skill
just invoked carries a retro step, injects a one-line reminder into context.

Deliberately narrow:
  - Silent for skills with no retro step (most Skill calls print nothing).
  - Silent for `skill-retro` itself — its own step 6 handles the self-retro,
    and reminding it to retro itself is the recursion its guard exists to stop.
  - Reminds that the retro fires when the RUN ends, not per invocation. A
    reminder after every Skill call would be noise, and docs-loop v1.3.0
    already had to define "ended" for exactly this reason.

A hook can't make the retro happen; it can remove "I forgot" as a failure
mode, which is the one that actually occurred. Exits 0 and prints nothing on
any error — a broken reminder must never break a skill invocation.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKER = "skill-retro"


def find_skill_md(skill: str) -> Path | None:
    """This repo's copy first, then the installed tree. The repo copy is the
    source of truth when working here; the installed one covers a skill used
    from this repo that lives only under ~/.claude/skills/."""
    for candidate in sorted(REPO_ROOT.glob(f"*/{skill}/SKILL.md")):
        return candidate
    installed = Path.home() / ".claude" / "skills" / skill / "SKILL.md"
    return installed if installed.is_file() else None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    skill = (payload.get("tool_input") or {}).get("skill") or ""
    skill = skill.strip().split(":")[-1]  # plugin:skill → skill
    if not skill or skill == "skill-retro":
        return 0

    path = find_skill_md(skill)
    if path is None:
        return 0
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    if MARKER not in text:
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                f"`{skill}` carries a wrap-up skill-retro step. Run it when this "
                f"run of {skill} ENDS — not after each PR or each approved row — "
                f"and don't wait to be asked. If the run is still going, ignore "
                f"this."
            ),
        },
        "suppressOutput": True,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
