#!/usr/bin/env python3
"""Tests for meta/my-skill-creator/scripts/quick_validate.py's frontmatter allowlist.

`validate_skill` is a hard gate in front of `package_skill.py` — a skill that
fails it cannot be packaged at all. The allowlist is vendored from upstream
skill-creator, where `version` is not a frontmatter key. This repo requires
`version` on every authored skill and enforces that in `check_repo.py`, so an
un-patched allowlist puts the two validators in direct contradiction: one fails
a skill *without* `version`, the other fails the same skill *with* it.

Bug this would have caught (issue #58): `package_skill.py` refused to package
`yt_research_for_cc/video-teardown` — and by extension every other skill in
this repo — with "Unexpected key(s) in SKILL.md frontmatter: version". The
divergence from upstream is deliberate and easy to lose on a re-sync, which is
exactly why it needs a test rather than only a comment.

Verified by reverting the fix (removing 'version' from ALLOWED_PROPERTIES) and
watching test_version_is_allowed and test_every_repo_skill_validates fail.
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

    def test_version_is_allowed(self):
        """`version` must validate — this repo requires it on every skill.

        The regression: upstream's allowlist omits `version`, so this returned
        False and blocked packaging for every authored skill in the repo.
        """
        skill = write_skill(self.tmpdir, extra="version: 1.0.0\n")
        ok, message = self.qv.validate_skill(str(skill))
        self.assertTrue(ok, f"a skill with `version` should validate, got: {message}")

    def test_version_absent_still_validates(self):
        """Adding `version` to the allowlist must not make it required here.

        `check_repo.py` is what enforces its presence; this validator only
        decides whether the key is *permitted*. Conflating the two would make
        the fix reject upstream-shaped skills.
        """
        skill = write_skill(self.tmpdir, extra="")
        ok, message = self.qv.validate_skill(str(skill))
        self.assertTrue(ok, f"a skill without `version` should still validate, got: {message}")

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

        - #58: the frontmatter allowlist rejected `version`, a key this repo
          requires, so `package_skill.py` could package nothing.
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
