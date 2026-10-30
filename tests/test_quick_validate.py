#!/usr/bin/env python3
"""Tests for meta/my-skill-creator/scripts/quick_validate.py's frontmatter allowlist.

`validate_skill` is a hard gate in front of `package_skill.py` — a skill that
fails it cannot be packaged at all. The allowlist must be exactly the Agent
Skills spec's six keys, because claude.ai upload and the Skills API hard-error
on anything else.

History: issue #58 found the allowlist rejecting this repo's then top-level
`version`, and fixed it by widening the allowlist. That made the two validators
agree with each other while both disagreed with claude.ai. The version now
lives at `metadata.version` and the allowlist is back to the spec.

Verified by re-adding 'version' to ALLOWED_PROPERTIES and watching
test_top_level_version_rejected fail.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "meta/my-skill-creator/scripts/quick_validate.py"

try:
    import yaml  # noqa: F401

    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False


def load_module():
    spec = importlib.util.spec_from_file_location("quick_validate", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["quick_validate"] = module
    spec.loader.exec_module(module)
    return module


SKILL_TEMPLATE = """---
name: {name}
description: A description long enough to look like a real one, naming what the skill does and when to use it.
{extra}---

# {name}

Body text.
"""


def write_skill(tmpdir: Path, name: str = "sample-skill", extra: str = "") -> Path:
    """Create a minimal skill directory and return its path."""
    skill_dir = tmpdir / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        SKILL_TEMPLATE.format(name=name, extra=extra), encoding="utf-8"
    )
    return skill_dir


@unittest.skipUnless(HAVE_YAML, "quick_validate.py requires PyYAML")
class AllowlistTest(unittest.TestCase):
    """The frontmatter allowlist must match this repo's own conventions."""

    def setUp(self):
        self.qv = load_module()
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_top_level_version_rejected(self):
        """A top-level `version` is not a spec key; claude.ai rejects it on upload."""
        skill = write_skill(self.tmpdir, extra="version: 1.0.0\n")
        ok, message = self.qv.validate_skill(str(skill))
        self.assertFalse(ok, "a top-level `version` should be rejected")
        self.assertIn("version", message)

    def test_metadata_version_allowed(self):
        """`metadata.version` is where this repo keeps the version."""
        skill = write_skill(self.tmpdir, extra='metadata:\n  version: "1.0.0"\n')
        ok, message = self.qv.validate_skill(str(skill))
        self.assertTrue(ok, f"metadata.version should validate, got: {message}")

    def test_version_absent_still_validates(self):
        """This validator decides what is *permitted*; `check_repo.py` decides
        what is required. An upstream-shaped skill with no version passes here.
        """
        skill = write_skill(self.tmpdir, extra="")
        ok, message = self.qv.validate_skill(str(skill))
        self.assertTrue(ok, f"a skill without a version should still validate, got: {message}")

    def test_non_string_metadata_value_rejected(self):
        """The spec types metadata as string-to-string; unquoted `1.0` is a float."""
        skill = write_skill(self.tmpdir, extra="metadata:\n  version: 1.0\n")
        ok, message = self.qv.validate_skill(str(skill))
        self.assertFalse(ok, "an unquoted float metadata value should be rejected")
        self.assertIn("version", message)

    def test_genuinely_unknown_key_still_rejected(self):
        """The allowlist must still reject typos — widening it isn't disabling it.

        Without this, a fix that replaced the check with a no-op would pass
        the other two tests.
        """
        skill = write_skill(self.tmpdir, extra="verison: 1.0.0\n")
        ok, message = self.qv.validate_skill(str(skill))
        self.assertFalse(ok, "a misspelled key should still be rejected")
        self.assertIn("verison", message)


@unittest.skipUnless(HAVE_YAML, "quick_validate.py requires PyYAML")
class RealSkillsTest(unittest.TestCase):
    """The end-to-end invariant, checked against the skills actually in this repo."""

    def test_every_repo_skill_validates(self):
        """Every skill in this repo must pass `quick_validate`, for any reason.

        Deliberately unscoped. It catches two distinct bugs already seen here,
        and would catch a third of a kind nobody has thought of yet:

        - #58: the frontmatter allowlist and this repo's conventions disagreed
          about `version`, so `package_skill.py` could package nothing.
        - #59: four skills had a description containing an unquoted ': ',
          invalid YAML that `check_repo.py`'s hand-rolled parser tolerates and
          PyYAML rejects — so a file could be "valid" here and invalid to
          every real consumer.

        The second is the reason this assertion is worth keeping broad rather
        than narrowed to allowlist rejections: the interesting failures are the
        ones where this repo's own tooling is more permissive than the tools
        that actually load these skills, and those don't announce which
        validation rule they'll trip.
        """
        qv = load_module()
        skills = sorted(
            p.parent for p in REPO_ROOT.rglob("SKILL.md") if ".git" not in p.parts
        )
        self.assertGreater(len(skills), 0, "no skills found — the glob is wrong")

        failures = []
        for skill_dir in skills:
            ok, message = qv.validate_skill(str(skill_dir))
            if not ok:
                failures.append(f"{skill_dir.relative_to(REPO_ROOT)}: {message}")

        self.assertEqual(
            failures, [], "skills rejected by quick_validate.py:\n" + "\n".join(failures)
        )


if __name__ == "__main__":
    unittest.main()
