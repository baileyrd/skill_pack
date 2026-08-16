#!/usr/bin/env python3
"""Tests for scripts/check_repo.py's frontmatter parsing.

`read_frontmatter` is the input to the `manifests` check, which decides
whether a skill's `name` matches its directory and its `version` is semver.
A parser that silently returns the wrong dict makes that check pass on a
broken skill, which is worse than not having it.

The git-dependent checks (exec-bits, line-ends) and the packaging smoke test
are verified by fault injection instead — see ADR-0002. Mocking `git
cat-file` would test the mock.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "scripts/check_repo.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_repo", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_repo"] = module
    spec.loader.exec_module(module)
    return module


chk = load_module()


def write(text: str) -> Path:
    fh = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    fh.write(text)
    fh.close()
    return Path(fh.name)


class TestReadFrontmatter(unittest.TestCase):
    def setUp(self):
        self.paths = []

    def tearDown(self):
        for p in self.paths:
            p.unlink(missing_ok=True)

    def frontmatter(self, text):
        path = write(text)
        self.paths.append(path)
        return chk.read_frontmatter(path)

    def test_reads_name_and_version(self):
        fm = self.frontmatter("---\nname: demo\nversion: 1.2.3\n---\n\n# Body\n")
        self.assertEqual(fm["name"], "demo")
        self.assertEqual(fm["version"], "1.2.3")

    def test_description_with_colons_does_not_break_parsing(self):
        """Every real description in this repo contains colons, em dashes and
        parenthetical asides. A naive split would mangle the fields after
        it — and `version` comes after `description` in every SKILL.md."""
        fm = self.frontmatter(
            "---\n"
            "name: demo\n"
            "description: Does a thing: and another; see http://example.com for why\n"
            "version: 2.0.0\n"
            "---\n"
        )
        self.assertEqual(fm["name"], "demo")
        self.assertEqual(fm["version"], "2.0.0")

    def test_indented_continuation_is_not_a_field(self):
        """A wrapped description continuing onto an indented line must not be
        mistaken for a new key."""
        fm = self.frontmatter(
            "---\nname: demo\ndescription: line one\n  version: not-a-real-field\n"
            "version: 3.1.4\n---\n"
        )
        self.assertEqual(fm["version"], "3.1.4")

    def test_body_content_after_frontmatter_is_ignored(self):
        """my-skill-creator's body contains the literal text `version: 1.0.0`
        as instructional prose. Only the frontmatter block counts — getting
        this wrong is how a version bump silently edits documentation."""
        fm = self.frontmatter(
            "---\nname: demo\nversion: 1.0.0\n---\n\n"
            "Add a `version: 1.0.0` field to the frontmatter of a new skill.\n"
        )
        self.assertEqual(fm["version"], "1.0.0")

    def test_no_frontmatter_returns_empty(self):
        self.assertEqual(self.frontmatter("# Just a heading\n"), {})

    def test_unreadable_file_returns_empty_not_raises(self):
        self.assertEqual(chk.read_frontmatter(Path("/nonexistent/SKILL.md")), {})


class TestReadDescription(unittest.TestCase):
    """claude.ai rejects a skill whose description exceeds MAX_DESCRIPTION, and
    that rejection happens at upload — after every local tool has passed the
    file. Five skills shipped over the limit at once because nothing measured
    it; these cover the measuring, including the block-scalar form that made
    the first version of the check read datastar-pro as 1 character."""

    def setUp(self):
        self.paths = []

    def tearDown(self):
        for p in self.paths:
            p.unlink(missing_ok=True)

    def description(self, text):
        path = write(text)
        self.paths.append(path)
        return chk.read_description(path)

    def test_reads_inline_description(self):
        d = self.description("---\nname: demo\ndescription: Does a thing\nversion: 1.0.0\n---\n")
        self.assertEqual(d, "Does a thing")

    def test_inline_description_keeps_colons_and_urls(self):
        d = self.description(
            "---\nname: demo\ndescription: Does a thing: see http://example.com\nversion: 1.0.0\n---\n"
        )
        self.assertEqual(d, "Does a thing: see http://example.com")

    def test_folded_block_scalar_is_joined_not_truncated(self):
        """datastar-pro writes its description as `>`. Reading the indicator as
        the value reports 1 character and lets any length slip through."""
        d = self.description(
            "---\nname: demo\ndescription: >\n  first line\n  second line\nversion: 1.0.0\n---\n"
        )
        self.assertEqual(d, "first line second line")

    def test_literal_block_scalar_is_joined(self):
        d = self.description(
            "---\nname: demo\ndescription: |\n  first line\n  second line\nversion: 1.0.0\n---\n"
        )
        self.assertEqual(d, "first line second line")

    def test_block_ends_at_next_top_level_key(self):
        """The block must not swallow `version` — a wrong length is a nuisance,
        but swallowing the key that follows it is a silently wrong manifest."""
        d = self.description(
            "---\nname: demo\ndescription: >\n  only this\nversion: 9.8.7\n---\n"
        )
        self.assertEqual(d, "only this")

    def test_missing_description_returns_empty(self):
        self.assertEqual(self.description("---\nname: demo\nversion: 1.0.0\n---\n"), "")

    def test_no_frontmatter_returns_empty(self):
        self.assertEqual(self.description("# Just a heading\n"), "")

    def test_unreadable_file_returns_empty_not_raises(self):
        self.assertEqual(chk.read_description(Path("/nonexistent/SKILL.md")), "")

    def test_every_skill_in_repo_is_within_the_limit(self):
        """The end-to-end guard: this is the assertion that would have caught
        the five rejected uploads before they were built into zips."""
        over = []
        for path in sorted(chk.REPO_ROOT.rglob("SKILL.md")):
            if ".git" in path.parts or "zip" in path.parts:
                continue
            length = len(chk.read_description(path))
            if length > chk.MAX_DESCRIPTION:
                over.append(f"{path.parent.name}: {length}")
        self.assertEqual(over, [], f"descriptions over {chk.MAX_DESCRIPTION}: {over}")


class TestSemver(unittest.TestCase):
    def test_accepts_plain_semver(self):
        for v in ("1.0.0", "0.1.2", "12.34.56"):
            with self.subTest(v=v):
                self.assertTrue(chk.SEMVER.match(v))

    def test_rejects_common_near_misses(self):
        for v in ("v1.0.0", "1.0", "1.0.0-beta", "", "latest"):
            with self.subTest(v=v):
                self.assertFalse(chk.SEMVER.match(v))


class TestVendoredExemption(unittest.TestCase):
    def test_notebooklm_is_the_only_exemption(self):
        """The exemption list is a standing waiver from the manifest rules.
        It should stay at exactly one entry unless something is vendored;
        a growing list means the rules are being worked around."""
        self.assertEqual(chk.VENDORED, {"yt_research_for_cc/notebooklm"})


if __name__ == "__main__":
    unittest.main()
