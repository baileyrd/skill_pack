#!/usr/bin/env python3
"""Check a chat-to-artifact document before it is delivered.

Usage: python3 scripts/check_doc.py <file.html|file.md>

Prints one finding per line and exits 1 if there are any, 0 on a clean pass.
Checks: leftover {{PLACEHOLDER}}s, a missing or empty title, the Claude Docs
byline (Markdown), external resources that break the page offline (HTML), and
strings shaped like credentials.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PLACEHOLDER = re.compile(r"\{\{\s*[A-Z_]+\s*\}\}")
HTML_TITLE = re.compile(r"<title>\s*(.*?)\s*</title>", re.IGNORECASE | re.DOTALL)
BYLINE = re.compile(r"^\d{4}-\d{2}-\d{2}( · \S.*)?$")

# Tags whose src/href is fetched when the page loads. Plain <a href> links are
# fine: the page still renders without them.
EXTERNAL_RESOURCE = re.compile(
    r"<(script|link|img|iframe|source|video|audio)\b[^>]*\b(src|href)\s*=\s*[\"']?(https?:)?//",
    re.IGNORECASE,
)
CSS_IMPORT = re.compile(r"@import\s+(url\()?[\"']?(https?:)?//", re.IGNORECASE)
CSS_URL = re.compile(r"url\(\s*[\"']?(https?:)?//", re.IGNORECASE)

SECRETS: dict[str, re.Pattern[str]] = {
    "API key (sk-...)": re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"),
    "Stripe key": re.compile(r"\b[sr]k_(live|test)_[A-Za-z0-9]{8,}"),
    "GitHub token": re.compile(r"\b(ghp|gho|ghs|ghu|github_pat)_[A-Za-z0-9_]{20,}"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Slack token": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "credentials in URL": re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s@]+@"),
}


def check_html(text: str) -> list[str]:
    """Return findings specific to an HTML document."""
    findings: list[str] = []
    title = HTML_TITLE.search(text)
    if title is None or not title.group(1):
        findings.append("missing or empty <title>")
    for pattern, label in ((EXTERNAL_RESOURCE, "external resource"),
                           (CSS_IMPORT, "external CSS @import"),
                           (CSS_URL, "external CSS url()")):
        for match in pattern.finditer(text):
            findings.append(f"{label} at line {line_of(text, match.start())}: inline it or drop it")
    return findings


def check_markdown(text: str) -> list[str]:
    """Return findings for the Claude Docs head: '# Title', then the byline."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or not lines[0].startswith("# ") or len(lines[0]) < 3:
        return ["first line must be the '# Title' heading (no front matter)"]
    if len(lines) < 2 or not BYLINE.match(lines[1]):
        return ["second line must be the byline 'YYYY-MM-DD · Author' (or the date alone)"]
    return []


def check_common(text: str) -> list[str]:
    """Return findings that apply to every format."""
    findings = [
        f"leftover placeholder {m.group(0)} at line {line_of(text, m.start())}"
        for m in PLACEHOLDER.finditer(text)
    ]
    for label, pattern in SECRETS.items():
        for match in pattern.finditer(text):
            findings.append(f"possible {label} at line {line_of(text, match.start())}: remove it")
    return findings


def check(path: Path) -> list[str]:
    """Return every finding for the document at path."""
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in (".html", ".htm"):
        specific = check_html(text)
    elif suffix in (".md", ".markdown"):
        specific = check_markdown(text)
    else:
        return [f"unsupported file type {suffix or '(none)'}: expected .html or .md"]
    return specific + check_common(text)


def line_of(text: str, offset: int) -> int:
    """1-based line number of a character offset."""
    return text.count("\n", 0, offset) + 1


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    path = Path(argv[1])
    if not path.is_file():
        print(f"no such file: {path}", file=sys.stderr)
        return 2
    findings = check(path)
    for finding in findings:
        print(finding)
    if not findings:
        print(f"ok: {path}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
