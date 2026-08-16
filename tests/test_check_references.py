#!/usr/bin/env python3
"""Tests for my_loops/docs-loop/scripts/check_references.py.

Every test names the bug it would have caught. That module's logic was wrong
four separate times on the day it was written — each time in a way that read
as obviously correct — so these are regression tests first and specification
second.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath, PureWindowsPath

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "my_loops/docs-loop/scripts/check_references.py"


def load_module():
    """Import by path: the directory is `docs-loop`, and a hyphen can't
    appear in an import statement."""
    spec = importlib.util.spec_from_file_location("check_references", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_references"] = module
    spec.loader.exec_module(module)
    return module


cr = load_module()


class TestSlugify(unittest.TestCase):
    """GitHub heading-slug generation."""

    def test_simple_heading(self):
        self.assertEqual(cr.slugify("Signal Declaration"), "signal-declaration")

    def test_em_dash_keeps_both_spaces(self):
        """REGRESSION: collapsing runs of whitespace produced a slug one
        hyphen short, reporting 12 *correct* anchors in datastar-pro's
        styling.md as broken. GitHub hyphenates each whitespace character,
        so "a — b" is "a--b" once the em dash is removed."""
        self.assertEqual(
            cr.slugify("data-style — Reactive Inline Styles"),
            "data-style--reactive-inline-styles",
        )

    def test_backticks_stripped_underscores_kept(self):
        """Backticks are markdown syntax; an underscore inside an identifier
        is not, and GitHub keeps it."""
        self.assertEqual(cr.slugify("`my_loops` layout"), "my_loops-layout")

    def test_punctuation_dropped(self):
        self.assertEqual(cr.slugify("40+ Easing Functions"), "40-easing-functions")

    def test_parenthetical_removed(self):
        self.assertEqual(
            cr.slugify("Object Syntax (multiple signals at once)"),
            "object-syntax-multiple-signals-at-once",
        )


class TestMaskCodeSpans(unittest.TestCase):
    """Inline code spans are blanked before link extraction."""

    def test_quoted_link_is_not_a_link(self):
        """REGRESSION: a release note *describing* a broken link had that
        link re-reported as broken forever. This repo's own notes walked
        into it — the entry documenting the #operators fix was itself
        flagged, twice."""
        line = "the TOC linked `[Operators](#operators)`."
        self.assertEqual(cr.LINK_RE.findall(cr.mask_code_spans(line)), [])

    def test_double_backtick_span(self):
        """REGRESSION: only single-backtick spans were matched, so a span
        delimited by a run of backticks leaked its contents to both scanners.
        Found by writing the release note for the fix above, which needed
        double backticks to quote the example."""
        line = "quoted: `` `[Operators](#operators)` ``"
        self.assertEqual(cr.LINK_RE.findall(cr.mask_code_spans(line)), [])

    def test_real_link_survives(self):
        line = "see [the guide](target.md) for more"
        self.assertEqual(cr.LINK_RE.findall(cr.mask_code_spans(line)), ["target.md"])

    def test_masking_preserves_length(self):
        """Columns must still line up after masking."""
        line = "a `code` b"
        self.assertEqual(len(cr.mask_code_spans(line)), len(line))


class TestNormalize(unittest.TestCase):
    def test_strips_line_suffix(self):
        """REGRESSION: `path/to/file.md:60` was read as a claim that a file
        named "file.md:60" exists. It's a doc idiom, not a path."""
        self.assertEqual(cr.normalize("my_loops/docs-loop/SKILL.md:60"),
                         "my_loops/docs-loop/SKILL.md")

    def test_strips_line_and_column(self):
        self.assertEqual(cr.normalize("src/main.rs:12:5"), "src/main.rs")

    def test_strips_leading_dot_slash_and_trailing_slash(self):
        self.assertEqual(cr.normalize("./scripts/"), "scripts")

    def test_leaves_a_plain_path_alone(self):
        self.assertEqual(cr.normalize("scripts/run.sh"), "scripts/run.sh")


class TestLooksLikePath(unittest.TestCase):
    def test_accepts_a_real_looking_path(self):
        self.assertTrue(cr.looks_like_path("scripts/run.sh"))

    def test_accepts_bare_filename_with_known_extension(self):
        self.assertTrue(cr.looks_like_path("README.md"))

    def test_rejects_placeholders(self):
        for token in ("<path>", "{{OWNER_REPO}}", "~/.claude/skills", "/usr/bin"):
            with self.subTest(token=token):
                self.assertFalse(cr.looks_like_path(token))

    def test_rejects_rust_paths_and_calls(self):
        for token in ("std::env::var", "main()"):
            with self.subTest(token=token):
                self.assertFalse(cr.looks_like_path(token))

    def test_rejects_urls_and_flags(self):
        self.assertFalse(cr.looks_like_path("https://example.com/x"))
        self.assertFalse(cr.looks_like_path("--dry-run"))


class TestComponentRootAndClassify(unittest.TestCase):
    """Path resolution against doc dir → component root → repo root."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        # A skill-shaped component: SKILL.md at its root, scripts/ beside it,
        # and a references/ doc that refers to `scripts/run.sh` the way a
        # reader reads it — relative to the component, not to itself.
        skill = self.root / "my_loops" / "demo-skill"
        (skill / "scripts").mkdir(parents=True)
        (skill / "references").mkdir()
        (skill / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")
        (skill / "scripts" / "run.sh").write_text("#!/bin/sh\n", encoding="utf-8")
        (self.root / "scripts").mkdir()
        self.doc = skill / "references" / "guide.md"
        self.doc.write_text("# guide\n", encoding="utf-8")
        self.skill = skill

    def tearDown(self):
        self._tmp.cleanup()

    def test_component_root_found(self):
        self.assertEqual(cr.component_root(self.root, self.doc), self.skill)

    def test_component_relative_path_resolves(self):
        """REGRESSION: without component-relative resolution, every skill's
        `references/*.md` saying `scripts/run.sh` was reported broken — 23
        rows across this repo."""
        bases = cr.resolution_bases(self.root, self.doc)
        self.assertEqual(cr.classify_path(bases, "scripts/run.sh", set()), "ok")

    def test_missing_file_under_a_real_dir_is_broken(self):
        bases = cr.resolution_bases(self.root, self.doc)
        self.assertEqual(cr.classify_path(bases, "scripts/gone.sh", set()), "broken")

    def test_unknown_first_segment_is_unresolved_not_broken(self):
        """`status/wait/cancel` is prose with slashes, not a false claim
        about this tree — the distinction that cut 302 rows to 11."""
        bases = cr.resolution_bases(self.root, self.doc)
        self.assertEqual(cr.classify_path(bases, "status/wait/cancel", set()), "unresolved")

    def test_bare_filename_known_elsewhere_is_ok(self):
        bases = cr.resolution_bases(self.root, self.doc)
        self.assertEqual(cr.classify_path(bases, "CONTRIBUTING.md", {"CONTRIBUTING.md"}), "ok")

    def test_bare_filename_unknown_is_unresolved(self):
        bases = cr.resolution_bases(self.root, self.doc)
        self.assertEqual(cr.classify_path(bases, "storage_state.json", set()), "unresolved")


class TestHistorical(unittest.TestCase):
    def test_changelog_and_release_notes_are_historical(self):
        for name in ("CHANGELOG.md", "RELEASE_NOTES.md", "History.md"):
            with self.subTest(name=name):
                self.assertTrue(cr.is_historical(Path(name)))

    def test_docs_audit_is_historical(self):
        """REGRESSION: a run that deleted a file and recorded the deletion in
        docs-audit.md made the NEXT run flag its own report as new breakage —
        with CI wired in, that turns a completed fix into a red build."""
        self.assertTrue(cr.is_historical(Path("docs-audit.md")))

    def test_ordinary_doc_is_not_historical(self):
        for name in ("README.md", "ARCHITECTURE.md", "docs-audit-probe.md"):
            with self.subTest(name=name):
                self.assertFalse(cr.is_historical(Path(name)))

    def test_path_row_downgrades_only_in_historical_docs(self):
        self.assertEqual(cr.path_row("broken", "inline-path", True),
                         ("unresolved", "historical-inline-path"))
        self.assertEqual(cr.path_row("broken", "inline-path", False),
                         ("broken", "inline-path"))

    def test_path_row_never_downgrades_ok(self):
        self.assertEqual(cr.path_row("ok", "inline-path", True), ("ok", "inline-path"))


class TestBaseline(unittest.TestCase):
    def test_key_excludes_line_number(self):
        """An accepted row must not return as new because someone added a
        paragraph above it."""
        self.assertEqual(
            cr.baseline_key("inline-path", "README.md:78", "zip/x.zip"),
            cr.baseline_key("inline-path", "README.md:12", "zip/x.zip"),
        )

    def test_key_distinguishes_different_docs(self):
        self.assertNotEqual(
            cr.baseline_key("inline-path", "README.md:1", "x"),
            cr.baseline_key("inline-path", "OTHER.md:1", "x"),
        )

    def test_load_skips_comments_and_blanks(self):
        with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False,
                                         encoding="utf-8") as fh:
            fh.write("# a reason\n\ninline-path\tREADME.md\tzip/x.zip\n")
            path = Path(fh.name)
        try:
            self.assertEqual(cr.load_baseline(path),
                             {"inline-path\tREADME.md\tzip/x.zip"})
        finally:
            path.unlink()

    def test_missing_baseline_is_empty_not_fatal(self):
        self.assertEqual(cr.load_baseline(Path("/nonexistent/baseline.tsv")), set())


class TestHeadingsOf(unittest.TestCase):
    def test_headings_inside_code_fences_are_ignored(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                         encoding="utf-8") as fh:
            fh.write("# Real\n\n```bash\n# Not A Heading\n```\n\n## Second\n")
            path = Path(fh.name)
        try:
            self.assertEqual(cr.headings_of(path), {"real", "second"})
        finally:
            path.unlink()

    def test_duplicate_headings_get_suffixes(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                         encoding="utf-8") as fh:
            fh.write("## Notes\n\n## Notes\n")
            path = Path(fh.name)
        try:
            self.assertEqual(cr.headings_of(path), {"notes", "notes-1"})
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()


class TestWherePathsArePosix(unittest.TestCase):
    """`where` fields must use forward slashes on every platform.

    REGRESSION (issue #49): `check_doc` built `where` as f"{rel}:{lineno}"
    from a `Path`. On Windows that stringifies with backslashes, while
    `docs-refs-baseline.tsv` stores forward slashes. `baseline_key` is
    kind+where+detail, so no baselined row ever matched on a Windows
    checkout: three long-accepted findings resurfaced as NEW and buried the
    one genuinely new finding, which only CI (Linux) surfaced.

    The damage is the masking, not the noise — a check whose output differs
    by platform trains you to distrust it, and then you miss the real one.

    These tests drive `rel_where` with `PureWindowsPath` rather than relying
    on the host platform. That is the whole point: an earlier version of this
    class asserted "no backslash in `where`" against real `Path`s, passed on
    Linux with the fix *reverted*, and would have shipped as a test that
    could never fail. On POSIX, `str(PosixPath)` and `.as_posix()` are the
    same string — only a Windows-flavoured path can tell them apart.
    """

    def test_rel_where_posix_paths(self):
        root = PurePosixPath("/home/user/skill_pack")
        doc = PurePosixPath("/home/user/skill_pack/meta/skill-retro/references/fmt.md")
        self.assertEqual(cr.rel_where(root, doc), "meta/skill-retro/references/fmt.md")

    def test_rel_where_windows_paths_still_emit_forward_slashes(self):
        """The actual regression. Fails if `.as_posix()` is dropped."""
        root = PureWindowsPath(r"C:\dev\skill_pack")
        doc = PureWindowsPath(r"C:\dev\skill_pack\meta\skill-retro\references\fmt.md")
        where = cr.rel_where(root, doc)
        self.assertEqual(where, "meta/skill-retro/references/fmt.md")
        self.assertNotIn("\\", where)

    def test_rel_where_outside_root_windows(self):
        """The `else` branch is a `where` field too, and had the same bug."""
        root = PureWindowsPath(r"C:\dev\skill_pack")
        doc = PureWindowsPath(r"D:\elsewhere\notes\x.md")
        self.assertEqual(cr.rel_where(root, doc), "D:/elsewhere/notes/x.md")

    def test_where_is_posix_end_to_end(self):
        """Integration cover: the row `check_doc` actually emits."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "meta" / "skill-retro" / "references"
            nested.mkdir(parents=True)
            doc = nested / "fmt.md"
            doc.write_text("See `nope/missing.md` for details.\n", encoding="utf-8")
            rows = []
            cr.check_doc(root, doc, rows, cr.index_basenames(root))
            self.assertTrue(rows, "expected at least one row")
            for _v, _k, where, _d in rows:
                self.assertTrue(where.startswith("meta/skill-retro/references/"), where)

    def test_baseline_key_is_separator_sensitive(self):
        """Why normalization must happen where `where` is built, not at compare."""
        self.assertNotEqual(
            cr.baseline_key("inline-path", "meta/skill-retro/x.md:11", "a/b.md"),
            cr.baseline_key("inline-path", "meta\\skill-retro\\x.md:11", "a/b.md"),
        )
