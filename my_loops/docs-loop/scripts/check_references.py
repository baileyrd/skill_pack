#!/usr/bin/env python3
"""check_references.py <repo-root> [doc-path ...] [--all] [--strict]

Settles the mechanically checkable half of documentation drift: every
relative link, every heading anchor, every backticked token that looks like a
repo path, and every path named inside a shell code block is resolved against
the working tree and reported ok / broken.

What this does NOT do is judge prose. "This crate wraps X to provide Y" is
either true or a lie and no amount of path resolution can tell you which — so
a clean run here is not evidence the docs are correct, only that their
pointers resolve. docs-loop step 3 does the real audit; this narrows what it
has to think about.

One false-positive class is structural and worth knowing before you read the
output: a doc that describes a DIFFERENT repo's layout (a skill documenting
its target, a README quoting a downstream consumer's tree) names paths that
correctly don't exist here. Those surface as broken/unresolved and are not
drift. Resolution is against the working tree as it stands, so gitignored
build output being present or absent moves some rows between verdicts — run
on a clean tree if you want the result to be reproducible.

With no doc paths given, every tracked *.md/*.mdx under the repo root is
checked (falling back to a filesystem walk outside a git repo), skipping
.git/, node_modules/, target/, .venv/, dist/, and build/.

Output is TSV on stdout — verdict, kind, doc:line, detail — with a summary on
stderr. Broken rows only by default; --all adds ok/unchecked rows. Exit 0
unless --strict is passed and at least one broken row was found.

Stdlib only, no third-party dependency, in keeping with the standing
minimal-dependencies principle.
"""
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "target", ".venv", "venv",
    "dist", "build", "__pycache__", ".mypy_cache", ".pytest_cache",
}
DOC_SUFFIXES = (".md", ".mdx")
SHELL_LANGS = {"bash", "sh", "shell", "console", "zsh", "shell-session"}

LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)>\s]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
FENCE_RE = re.compile(r"^\s*(?:```+|~~~+)\s*([A-Za-z0-9_+.-]*)\s*$")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
PATHISH_EXT_RE = re.compile(
    r"\.(md|mdx|rs|py|sh|bash|toml|ya?ml|json|jsonc|js|mjs|ts|tsx|jsx|html|css|txt"
    r"|cfg|ini|lock|service|sql|proto|gradle|kt|go|rb|java|c|h|cpp|hpp)$"
)
# Tokens that look like paths but can never be resolved: placeholders, globs,
# URLs, shell/language syntax, home-relative and absolute system paths.
PLACEHOLDER_RE = re.compile(r"[<>{}*?$|]|::|\(\)|\.\.\.|^~|^/")
PROMPT_PREFIXES = ("$ ", "# ", "> ", "% ")


def slugify(heading: str) -> str:
    """GitHub-flavored heading slug: strip emphasis/code markers and
    punctuation, lowercase, whitespace to hyphens. Underscores are kept —
    they're part of identifiers like `my_loops`, not markdown syntax.

    Each whitespace character becomes its own hyphen; they are NOT collapsed.
    "data-style — Reactive Inline Styles" drops the em dash and keeps the two
    spaces around it, giving `data-style--reactive-inline-styles`. Collapsing
    runs of whitespace here produces a slug one hyphen short and reports
    every correct anchor in a doc like that as broken."""
    s = heading.strip().lower()
    s = re.sub(r"[`*~]", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)  # links render as their text
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s", "-", s.strip())
    return s


def strip_fences(lines):
    """Yield (lineno, text, fence_lang) with fence_lang set inside code
    blocks and None outside, so callers can treat the two differently."""
    lang = None
    for i, line in enumerate(lines, start=1):
        m = FENCE_RE.match(line)
        if m:
            lang = None if lang is not None else (m.group(1).lower() or "")
            continue
        yield i, line, lang


def headings_of(path: Path):
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return set()
    slugs, seen = set(), {}
    for _, line, lang in strip_fences(lines):
        if lang is not None:
            continue
        m = HEADING_RE.match(line)
        if not m:
            continue
        base = slugify(m.group(2))
        if not base:
            continue
        n = seen.get(base, 0)
        seen[base] = n + 1
        slugs.add(base if n == 0 else f"{base}-{n}")
    return slugs


def looks_like_path(token: str) -> bool:
    token = token.strip()
    if not token or " " in token or "\t" in token:
        return False
    if token.startswith("-") or "://" in token or token.startswith("@"):
        return False
    if PLACEHOLDER_RE.search(token):
        return False
    return "/" in token or bool(PATHISH_EXT_RE.search(token))


def normalize(token: str) -> str:
    token = token.strip().strip("\"'").rstrip(",.;:")
    while token.startswith("./"):
        token = token[2:]
    # `path/to/file.md:60` and `file.rs:12:5` are a doc idiom, not a claim
    # that a file named "file.md:60" exists — resolve the path part.
    token = re.sub(r":\d+(?::\d+)?$", "", token)
    return token.rstrip("/")


def resolve(root: Path, doc: Path, candidate: str):
    """Resolve a doc-relative or root-relative path. Returns the resolved
    Path if something exists there, else None."""
    cand = candidate.lstrip("/") if candidate.startswith("/") else candidate
    for base in (doc.parent, root):
        target = (base / cand)
        if target.exists():
            return target
    return None


def classify_path(root: Path, doc: Path, candidate: str, basenames: set):
    """Split "doesn't resolve" into two very different findings.

    `broken` is reserved for paths anchored in a directory that really
    exists — `scripts/gone.py` in a repo that has `scripts/` is a claim
    about this tree, and it's false. Everything else is `unresolved`: a bare
    filename nothing in the tree matches, or a path whose first segment
    isn't a real directory, is just as likely a runtime artifact
    (`storage_state.json`), an example (`./local-file.pdf`), or prose that
    happened to contain a slash (`status/wait/cancel`) as it is stale. Both
    get reported; conflating them buries the real ones."""
    if resolve(root, doc, candidate):
        return "ok"
    if "/" in candidate:
        first = candidate.split("/", 1)[0]
        if (root / first).exists() or (doc.parent / first).exists():
            return "broken"
        return "unresolved"
    # A bare filename that exists somewhere in the tree is normal prose
    # ("edit `SKILL.md`"), not a location claim.
    return "ok" if candidate in basenames else "unresolved"


def index_basenames(root: Path) -> set:
    """Every filename in the working tree, tracked or not. Untracked counts:
    a doc claim is about the tree as it stands right now, and a file added
    but not yet committed is still there."""
    names = set()
    for args in (["ls-files"], ["ls-files", "--others", "--exclude-standard"]):
        try:
            out = subprocess.run(
                ["git", "-C", str(root)] + args,
                capture_output=True, text=True, check=True,
            ).stdout.split("\n")
            names.update(Path(p).name for p in out if p.strip())
        except (OSError, subprocess.CalledProcessError):
            names = set()
            break
    if names:
        return names
    for path in root.rglob("*"):
        if path.is_file() and not any(part in SKIP_DIRS for part in path.parts):
            names.add(path.name)
    return names


def docs_under(base: Path):
    return sorted(
        p for p in base.rglob("*")
        if p.is_file()
        and p.suffix.lower() in DOC_SUFFIXES
        and not any(part in SKIP_DIRS for part in p.parts)
    )


def collect_docs(root: Path, args):
    if args:
        named = [Path(a) if Path(a).is_absolute() else root / a for a in args]
        expanded = []
        for path in named:
            # A directory argument means "every doc under here" — scoping a
            # run to one skill or one docs/ subtree is the common case.
            expanded.extend(docs_under(path) if path.is_dir() else [path])
        return expanded
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--", "*.md", "*.mdx"],
            capture_output=True, text=True, check=True,
        ).stdout.split("\n")
        tracked = [root / p for p in out if p.strip()]
        if tracked:
            return sorted(tracked)
    except (OSError, subprocess.CalledProcessError):
        pass
    found = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in DOC_SUFFIXES or not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        found.append(path)
    return found


def check_doc(root: Path, doc: Path, rows: list, basenames: set):
    rel = doc.relative_to(root) if doc.is_relative_to(root) else doc
    try:
        lines = doc.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        rows.append(("broken", "unreadable", f"{rel}:0", str(exc)))
        return

    own_slugs = headings_of(doc)

    for lineno, line, lang in strip_fences(lines):
        where = f"{rel}:{lineno}"

        if lang is None:
            for raw in LINK_RE.findall(line):
                target = raw.strip()
                if target.startswith(("http://", "https://", "mailto:", "tel:")):
                    rows.append(("unchecked", "external-link", where, target))
                    continue
                path_part, _, anchor = target.partition("#")
                path_part = normalize(path_part)
                if not path_part:
                    verdict = "ok" if not anchor or anchor.lower() in own_slugs else "broken"
                    rows.append((verdict, "anchor", where, f"#{anchor}"))
                    continue
                resolved = resolve(root, doc, path_part)
                if resolved is None:
                    rows.append(("broken", "link", where, target))
                    continue
                if anchor and resolved.suffix.lower() in DOC_SUFFIXES:
                    ok = anchor.lower() in headings_of(resolved)
                    rows.append(("ok" if ok else "broken", "link-anchor", where, target))
                else:
                    rows.append(("ok", "link", where, target))

            for token in INLINE_CODE_RE.findall(line):
                if not looks_like_path(token):
                    continue
                cand = normalize(token)
                if not cand:
                    continue
                rows.append(
                    (classify_path(root, doc, cand, basenames), "inline-path", where, token)
                )
            continue

        if lang not in SHELL_LANGS:
            continue

        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for prefix in PROMPT_PREFIXES:
            if stripped.startswith(prefix):
                stripped = stripped[len(prefix):].strip()
                break
        tokens = stripped.split()
        if tokens:
            rows.append(("unchecked", "command", where, stripped))
        for token in tokens[1:]:
            if not looks_like_path(token):
                continue
            cand = normalize(token)
            if not cand:
                continue
            rows.append(
                (classify_path(root, doc, cand, basenames), "shell-path", where, token)
            )


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    unknown = flags - {"--all", "--strict", "--help", "-h"}
    if unknown or "--help" in flags or "-h" in flags or not args:
        print(__doc__, file=sys.stderr)
        return 0 if flags & {"--help", "-h"} else 2

    root = Path(args[0]).resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2

    docs = collect_docs(root, args[1:])
    if not docs:
        print(f"No markdown docs found under {root}.", file=sys.stderr)
        return 0

    basenames = index_basenames(root)
    rows = []
    for doc in docs:
        if not doc.is_file():
            rows.append(("broken", "missing-doc", str(doc), "named on the command line, not on disk"))
            continue
        check_doc(root, doc, rows, basenames)

    show_all = "--all" in flags
    for verdict, kind, where, detail in rows:
        if verdict in ("broken", "unresolved") or show_all:
            print(f"{verdict}\t{kind}\t{where}\t{detail}")

    counts = {}
    for verdict, kind, _, _ in rows:
        counts[(verdict, kind)] = counts.get((verdict, kind), 0) + 1
    broken = sum(n for (verdict, _), n in counts.items() if verdict == "broken")

    print(f"\n--- {len(docs)} docs, {len(rows)} references ---", file=sys.stderr)
    for (verdict, kind), n in sorted(counts.items()):
        print(f"{verdict:>9}  {kind:<14} {n}", file=sys.stderr)
    if not show_all:
        print("(broken + unresolved rows shown above; --all to see ok/unchecked too)", file=sys.stderr)
    print(
        "broken    = anchored in a directory that exists, so the claim is about\n"
        "            THIS tree and it is false — fix these.\n"
        "unresolved= nothing in the tree matches; could equally be a runtime file,\n"
        "            an example, or prose with a slash in it — read before acting.\n"
        "unchecked = commands and external links; running/fetching them is\n"
        "            docs-loop step 5's job, not this script's.\n"
        "Resolvable references only — prose accuracy is step 3's job either way.",
        file=sys.stderr,
    )

    return 1 if (broken and "--strict" in flags) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
