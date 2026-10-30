#!/usr/bin/env python3
"""Tests for scripts/build_skill_zips.py's `skill_version`.

The version names the archive (`<skill>-v<version>.zip`). After the move from a
top-level `version` to `metadata.version`, a reader still looking at the old
location would silently drop the suffix from every zip.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "scripts/build_skill_zips.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_skill_zips", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_skill_zips"] = module
    spec.loader.exec_module(module)
    return module


bsz = load_module()


class TestSkillVersion(unittest.TestCase):
    def version(self, frontmatter: str) -> str | None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp)
            (skill / "SKILL.md").write_text(f"---\n{frontmatter}---\n\n# Body\n", encoding="utf-8")
            return bsz.skill_version(skill)

    def test_quoted_metadata_version(self):
        self.assertEqual(self.version('name: demo\nmetadata:\n  version: "1.4.0"\n'), "1.4.0")

    def test_version_after_other_metadata_keys(self):
        self.assertEqual(self.version("name: demo\nmetadata:\n  author: x\n  version: 2.0.1\n"), "2.0.1")

    def test_no_version_is_none(self):
        """notebooklm carries no version and gets an unsuffixed zip."""
        self.assertIsNone(self.version("name: demo\n"))

    def test_top_level_version_is_ignored(self):
        self.assertIsNone(self.version("name: demo\nversion: 1.0.0\n"))

    def test_metadata_block_ends_at_next_top_level_key(self):
        self.assertIsNone(self.version("metadata:\n  author: x\nlicense: MIT\n"))


if __name__ == "__main__":
    unittest.main()
