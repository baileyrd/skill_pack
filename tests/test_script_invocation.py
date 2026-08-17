#!/usr/bin/env python3
"""Guard: a skill that ships executable scripts must say how to restore the
executable bit the sync drops.

The bug this would have caught (issue #1): the sync that delivers a skill to a
session does not preserve mode bits. Every shebanged script in every skill
arrives as 0644 — measured at 31 of 31 in a live session. A SKILL.md step that
reads

    10. `scripts/watch_and_merge.sh <pr-number>`: waits for CI, and on green...

is an instruction to execute that path, and executing it fails with
`permission denied`.

This check is deliberately blunt: it asks whether the skill documents the
recovery, not whether its current prose phrases invocations safely. An earlier
draft tried the sharper question — flag only the skills whose instructions
invoke a script *bare* — and got it wrong twice in a row. It first read
``enforced by `scripts/check_repo.py`'s `manifests` check`` as a command,
because a substring scan cannot see where a code span ends. Then, scanning line
by line, it missed sovereignty-loop's genuine invocation at line 48, whose code
span wraps across a newline.

Both misses share a cause: the safe/unsafe distinction lives in prose, so any
test of it is a prose parser, and a prose parser is a thing to get wrong. The
property that actually holds is simpler and needs no parsing — the bit is lost
for every script in every skill, so every skill that ships one needs the
recovery documented. Phrasing can then change freely without silently
reintroducing the breakage.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The convention marker: a documented way to put the bit back.
RECOVERY = re.compile(r"chmod\s+\+x\s+[^\n]*scripts/")


def skills_shipping_executables():
    """Skills with at least one shebanged file under scripts/."""
    for skill_md in sorted(REPO_ROOT.glob("*/*/SKILL.md")):
        scripts = skill_md.parent / "scripts"
        if not scripts.is_dir():
            continue
        for script in scripts.iterdir():
            if not script.is_file():
                continue
            try:
                if script.read_bytes()[:2] == b"#!":
                    yield skill_md
                    break
            except OSError:
                continue


class TestScriptInvocation(unittest.TestCase):
    def test_population_is_non_empty(self):
        """Guard the guard: if the glob or the shebang probe stops matching,
        every assertion below passes vacuously."""
        found = list(skills_shipping_executables())
        self.assertTrue(
            found, "no */*/SKILL.md ships a shebanged script — the probe is wrong"
        )

    def test_every_skill_with_scripts_documents_the_recovery(self):
        offenders = [
            str(skill_md.relative_to(REPO_ROOT))
            for skill_md in skills_shipping_executables()
            if not RECOVERY.search(skill_md.read_text())
        ]
        self.assertEqual(
            [], sorted(offenders),
            "the sync delivers every script as 0644, so a bare "
            "`scripts/x.sh` invocation fails with permission denied (issue #1). "
            "These skills ship executable scripts but never say how to restore "
            "the bit — document `chmod +x scripts/...`:\n  "
            + "\n  ".join(sorted(offenders)),
        )


if __name__ == "__main__":
    unittest.main()
