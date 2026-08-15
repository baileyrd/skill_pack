#!/usr/bin/env python3
"""Tests for scripts/retro_reminder.py, the PostToolUse wrap-up-retro hook.

This one runs after *every* Skill invocation, so its failure modes are
asymmetric: a crash or a stray message degrades every skill call in the
session. Each test names the specific way that could happen.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts/retro_reminder.py"


def run(payload: str):
    """Invoke exactly as the hook does — a subprocess fed JSON on stdin."""
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=payload, capture_output=True, text=True,
    )


class TestFires(unittest.TestCase):
    def test_reminds_for_a_skill_carrying_a_retro_step(self):
        result = run('{"tool_input":{"skill":"docs-loop"}}')
        self.assertEqual(result.returncode, 0)
        out = json.loads(result.stdout)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PostToolUse")
        self.assertIn("docs-loop", out["hookSpecificOutput"]["additionalContext"])

    def test_reminder_says_when_not_just_that(self):
        """The reminder must say the retro fires when the RUN ends. Without
        that, a hook on every Skill call trains the reader to ignore it —
        and docs-loop v1.3.0 had to define "ended" for the same reason."""
        out = json.loads(run('{"tool_input":{"skill":"docs-loop"}}').stdout)
        self.assertIn("ENDS", out["hookSpecificOutput"]["additionalContext"])

    def test_strips_a_plugin_prefix(self):
        """Skill names can arrive as `plugin:skill`; an unstripped prefix
        means no SKILL.md is ever found and the hook silently never fires."""
        out = json.loads(run('{"tool_input":{"skill":"plug:repo-config"}}').stdout)
        self.assertIn("repo-config", out["hookSpecificOutput"]["additionalContext"])


class TestStaysSilent(unittest.TestCase):
    def test_never_reminds_skill_retro_about_itself(self):
        """THE recursion guard. skill-retro's own SKILL.md is full of the
        marker string, so a naive grep would fire on it — telling the retro
        skill to retro itself, which its own step 6 guard exists to prevent."""
        self.assertEqual(run('{"tool_input":{"skill":"skill-retro"}}').stdout, "")

    def test_silent_for_a_skill_with_no_retro_step(self):
        self.assertEqual(run('{"tool_input":{"skill":"notebooklm"}}').stdout, "")

    def test_silent_for_an_unknown_skill(self):
        self.assertEqual(run('{"tool_input":{"skill":"no-such-skill"}}').stdout, "")

    def test_silent_when_no_skill_name_present(self):
        self.assertEqual(run('{"tool_input":{}}').stdout, "")


class TestNeverBreaksTheSkillCall(unittest.TestCase):
    """A PostToolUse hook that raises degrades every Skill invocation. These
    are the inputs most likely to arrive malformed."""

    def test_malformed_json_exits_zero_silently(self):
        result = run("not json at all")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_empty_stdin_exits_zero_silently(self):
        result = run("")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_json_without_tool_input_exits_zero(self):
        result = run('{"tool_name":"Skill"}')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_null_tool_input_exits_zero(self):
        result = run('{"tool_input":null}')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
