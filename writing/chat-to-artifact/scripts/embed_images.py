#!/usr/bin/env python3
"""Inline every local image of an HTML document so the file stands alone.

Usage: python3 scripts/embed_images.py <doc.html>

Each <img src="relative/path.png"> is replaced in place by a base64 data URI,
resolved against the document's own folder. Remote (http, https, //) and
already-inlined (data:) sources are left alone; check_doc.py reports remote
ones. Exits 1, changing nothing, if any local image is missing or is not an
image type.
"""

from __future__ import annotations

import base64
import mimetypes
import re
import sys
from pathlib import Path

IMG_SRC = re.compile(r"(<img\b[^>]*?\bsrc\s*=\s*)([\"'])(.*?)\2", re.IGNORECASE | re.DOTALL)
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
SKIP = re.compile(r"^(data:|https?:|//)", re.IGNORECASE)
MAX_BYTES = 5 * 1024 * 1024  # one image this size already makes the page slow to share

mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("image/webp", ".webp")


def data_uri(path: Path) -> str:
    """Return the data URI for an image file, or raise ValueError with the reason."""
    if not path.is_file():
        raise ValueError(f"missing image {path}")
    mime, _ = mimetypes.guess_type(path.name)
    if mime is None or not mime.startswith("image/"):
        raise ValueError(f"not an image type: {path}")
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError(f"{path} is {len(data) // 1024} KB; resize it below {MAX_BYTES // 1024} KB")
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def embed(text: str, base: Path) -> tuple[str, int, list[str]]:
    """Return (new text, images inlined, errors) for an HTML document in folder base."""
    errors: list[str] = []
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        prefix, quote, src = match.groups()
        if SKIP.match(src.strip()):
            return match.group(0)
        try:
            uri = data_uri(base / src.strip())
        except ValueError as exc:
            errors.append(str(exc))
            return match.group(0)
        count += 1
        return f"{prefix}{quote}{uri}{quote}"

    # Comments (the template's own usage notes) are copied through untouched.
    parts = re.split(f"({COMMENT.pattern})", text, flags=re.DOTALL)
    out = [part if COMMENT.fullmatch(part) else IMG_SRC.sub(replace, part) for part in parts]
    return "".join(out), count, errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    path = Path(argv[1])
    if not path.is_file():
        print(f"no such file: {path}", file=sys.stderr)
        return 2
    text, count, errors = embed(path.read_text(encoding="utf-8"), path.parent)
    for error in errors:
        print(error)
    if errors:
        return 1
    path.write_text(text, encoding="utf-8")
    print(f"ok: {count} image(s) inlined in {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
