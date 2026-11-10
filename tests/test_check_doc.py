#!/usr/bin/env python3
"""Tests for writing/chat-to-artifact/scripts/check_doc.py.

Each test names the delivery failure it guards: a page that breaks offline,
a key pasted into the chat that ends up in the shared document, a template
placeholder left in, or a plain link wrongly flagged as a resource.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "writing/chat-to-artifact/scripts/check_doc.py"
TEMPLATE = REPO_ROOT / "writing/chat-to-artifact/assets/template.html"


def load_module():
    """Import by path: the skill directory name has a hyphen."""
    spec = importlib.util.spec_from_file_location("check_doc", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_doc"] = module
    spec.loader.exec_module(module)
    return module


cd = load_module()


def filled(body: str, title: str = "Cache rollout") -> str:
    """The real template with every placeholder replaced."""
    text = TEMPLATE.read_text(encoding="utf-8")
    for key, value in {"TITLE": title, "SUBTITLE": "2026-11-10", "BODY": body, "FOOTER": "f"}.items():
        text = text.replace("{{" + key + "}}", value)
    return text


class TestHtml(unittest.TestCase):
    def check(self, text: str, suffix: str = ".html") -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / f"doc{suffix}"
            path.write_text(text, encoding="utf-8")
            return cd.check(path)

    def test_filled_template_passes(self):
        self.assertEqual(self.check(filled("<p>ok</p>")), [])

    def test_unfilled_template_flags_placeholders(self):
        """Delivering the template with {{BODY}} still in it."""
        findings = self.check(TEMPLATE.read_text(encoding="utf-8"))
        self.assertTrue(any("{{BODY}}" in f for f in findings))

    def test_cdn_script_and_stylesheet_flagged(self):
        """A CDN dependency renders blank when opened offline or attached."""
        body = ('<script src="https://cdn.example.com/x.js"></script>'
                '<link rel="stylesheet" href="//fonts.example.com/f.css">')
        findings = self.check(filled(body))
        self.assertEqual(sum("external resource" in f for f in findings), 2)

    def test_css_import_flagged(self):
        findings = self.check(filled("<style>@import url('https://x.example/a.css');</style>"))
        self.assertTrue(any("@import" in f for f in findings))

    def test_plain_link_not_flagged(self):
        """Anchors are fine: the page renders without following them."""
        self.assertEqual(self.check(filled('<a href="https://github.com/o/r/pull/1">PR</a>')), [])

    def test_empty_title_flagged(self):
        self.assertIn("missing or empty <title>", self.check(filled("<p>x</p>", title="")))

    def test_pasted_key_flagged(self):
        """A key pasted into the chat must not reach the shared document."""
        findings = self.check(filled("<p>key sk-live-9f8a7b6c5d4e3f2a1b0c</p>"))
        self.assertTrue(any("API key" in f for f in findings))

    def test_credentials_in_url_flagged(self):
        findings = self.check(filled("<p>postgres://app:hunter2@db.internal/x</p>"))
        self.assertTrue(any("credentials in URL" in f for f in findings))

    def test_markdown_claude_docs_head_passes(self):
        doc = "# Kiln naming\n\n2026-11-10 · Sam\n\nThe CLI is called kiln.\n"
        self.assertEqual(self.check(doc, ".md"), [])
        self.assertEqual(self.check("# Kiln naming\n\n2026-11-10\n\nLead.\n", ".md"), [])

    def test_markdown_front_matter_flagged(self):
        """Front matter pushes the title off line one; Claude Docs shows it as text."""
        findings = self.check("---\ntitle: x\n---\n# Kiln\n\n2026-11-10\n", ".md")
        self.assertTrue(findings[0].startswith("first line must be the '# Title'"))

    def test_markdown_missing_byline_flagged(self):
        """A doc with no as-of date gives the reader no idea how stale it is."""
        findings = self.check("# Kiln naming\n\nThe CLI is called kiln.\n", ".md")
        self.assertTrue(findings[0].startswith("second line must be the byline"))

    def test_unsupported_suffix(self):
        self.assertTrue(self.check("x", ".txt")[0].startswith("unsupported file type"))


if __name__ == "__main__":
    unittest.main()
