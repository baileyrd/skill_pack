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

Paths resolve against three bases, nearest first: the doc's own directory,
its nearest enclosing component (a directory with a SKILL.md or a language
manifest), and the repo root. The component base is what makes shorthand
like `scripts/run.sh` inside that component's `references/` resolve the way
a reader reads it.

One false-positive class survives all of that, and it's structural: a doc
describing a DIFFERENT component's or repo's layout (a skill documenting its
target, a README quoting a downstream consumer's tree) names paths that
correctly don't exist here. Those are not drift. Resolution is also against
the working tree as it stands, so gitignored build output being present or
absent moves some rows between verdicts — run on a clean tree if you want
the result to be reproducible.

With no doc paths given, every tracked *.md/*.mdx under the repo root is
checked (falling back to a filesystem walk outside a git repo), skipping
.git/, node_modules/, target/, .venv/, dist/, and build/.

Output is TSV on stdout — verdict, kind, doc:line, detail — with a summary on
stderr. Broken rows only by default; --all adds ok/unchecked rows. Exit 0
unless --strict is passed and at least one broken row was found.

`--baseline FILE` accepts a set of already-known broken rows so CI can fail on
NEW breakage only — without it, a repo with any of the structural
false-positive class described above is red from day one, and an always-red
check is worse than none. Each baseline line is `kind<TAB>doc<TAB>detail`,
deliberately without the line number, so an accepted row doesn't come back as
new when someone adds a paragraph above it. Entries that stop matching are
reported as stale but never fail the run.

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
# Code spans use a run of N backticks closed by the same run, so a span can
# itself contain backticks: ``a `b` c``. Matching only single-backtick spans
# leaves the inner content exposed to the link/path scanners below.
INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")
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


def mask_code_spans(line: str) -> str:
    """Blank out inline code spans, preserving length so column positions
    still line up.

    A doc that *quotes* markdown link syntax inside backticks —
    "the TOC linked `[Operators](#operators)`" — is describing a link, not
    making one. Without this, every release note that documents a broken
    link re-reports that same broken link forever, which is exactly the
    trap a docs checker should not walk into."""
    return INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line)


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


def component_root(root: Path, doc: Path):
    """Nearest ancestor of `doc` that looks like a self-contained component
    — a directory holding a SKILL.md, a manifest, or its own README.

    Docs inside such a component name paths relative to the COMPONENT, not
    to the file or the repo: a skill's `references/foo.md` says
    `scripts/run.sh` meaning its own sibling `scripts/`, and a package's
    `docs/guide.md` says `src/main.rs` meaning the package's. Resolving
    only against the doc's directory and the repo root reports every one of
    those as broken, which drowns real findings in a monorepo or a repo of
    independently-packaged parts."""
    markers = ("SKILL.md", "Cargo.toml", "pyproject.toml", "package.json", "go.mod")
    current = doc.parent
    while True:
        if any((current / m).exists() for m in markers):
            return current
        if current == root or current.parent == current:
            return None
        current = current.parent


def resolution_bases(root: Path, doc: Path):
    """Where a path in this doc could legitimately be rooted, nearest first.
    Deduplicated, order preserved — the first hit wins in resolve()."""
    bases, seen = [], set()
    for base in (doc.parent, component_root(root, doc), root):
        if base is not None and base not in seen:
            seen.add(base)
            bases.append(base)
    return bases


def resolve(bases, candidate: str):
    """Resolve a candidate against each base in turn. Returns the resolved
    Path if something exists, else None."""
    cand = candidate.lstrip("/") if candidate.startswith("/") else candidate
    for base in bases:
        target = base / cand
        if target.exists():
            return target
    return None


def classify_path(bases, candidate: str, basenames: set):
    """Split "doesn't resolve" into two very different findings.

    `broken` is reserved for paths anchored in a directory that really
    exists — `scripts/gone.py` in a repo that has `scripts/` is a claim
    about this tree, and it's false. Everything else is `unresolved`: a bare
    filename nothing in the tree matches, or a path whose first segment
    isn't a real directory, is just as likely a runtime artifact
    (`storage_state.json`), an example (`./local-file.pdf`), or prose that
    happened to contain a slash (`status/wait/cancel`) as it is stale. Both
    get reported; conflating them buries the real ones."""
    if resolve(bases, candidate):
        return "ok"
    if "/" in candidate:
        first = candidate.split("/", 1)[0]
        if any((base / first).exists() for base in bases):
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


HISTORICAL_DOCS = {
    "changelog", "release_notes", "releasenotes", "history",
    # docs-audit.md is this skill's own report, and its rows persist across
    # runs by design (references/docs-audit-format.md). It therefore
    # accumulates references to things a run deliberately deleted — a row
    # recording "this stub was removed" is the report working, not drift.
    "docs-audit",
}


def is_historical(doc: Path) -> bool:
    """CHANGELOG.md / RELEASE_NOTES.md and friends are logs, not descriptions
    of the current tree. A path in a past entry that no longer resolves is
    usually *correct history* — the entry recording that a file was removed
    is doing its job. docs-loop's own rules say never to rewrite a past
    entry, so reporting those as `broken` sends an auditor to rows they are
    forbidden to act on."""
    return doc.stem.lower() in HISTORICAL_DOCS


def path_row(verdict: str, kind: str, historical: bool):
    """Downgrade a non-resolving path in a historical log to `unresolved`
    with a self-labelling kind, so it reads as "logged, do not touch"
    rather than "drift, go fix it"."""
    if historical and verdict != "ok":
        return ("unresolved", f"historical-{kind}")
    return (verdict, kind)


def rel_where(root, doc) -> str:
    """`doc` relative to `root` as a forward-slashed string.

    Always `.as_posix()`, never the platform separator. This string becomes the
    `where` field of every row, and `where` is part of `baseline_key`. A Windows
    checkout emitting `meta\\skill-retro\\...` never matches a baseline written
    as `meta/skill-retro/...`, so every accepted row resurfaces as NEW and
    buries the findings that are real (issue #49).

    Split out as its own function so the Windows behaviour is testable from any
    platform by passing `PureWindowsPath`s — asserting on `str(Path(...))` from
    a POSIX test process cannot tell the fixed code from the broken code.
    """
    rel = doc.relative_to(root) if doc.is_relative_to(root) else doc
    return rel.as_posix()


def check_doc(root: Path, doc: Path, rows: list, basenames: set):
    rel = rel_where(root, doc)
    try:
        lines = doc.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        rows.append(("broken", "unreadable", f"{rel}:0", str(exc)))
        return

    own_slugs = headings_of(doc)
    bases = resolution_bases(root, doc)
    historical = is_historical(doc)

    for lineno, line, lang in strip_fences(lines):
        where = f"{rel}:{lineno}"

        if lang is None:
            # Links come from prose (code spans masked out); path candidates
            # come from the code spans themselves. Same line, two readings.
            for raw in LINK_RE.findall(mask_code_spans(line)):
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
                resolved = resolve(bases, path_part)
                if resolved is None:
                    rows.append(("broken", "link", where, target))
                    continue
                if anchor and resolved.suffix.lower() in DOC_SUFFIXES:
                    ok = anchor.lower() in headings_of(resolved)
                    rows.append(("ok" if ok else "broken", "link-anchor", where, target))
                else:
                    rows.append(("ok", "link", where, target))

            for match in INLINE_CODE_RE.finditer(line):
                token = match.group(2)
                if not looks_like_path(token):
                    continue
                cand = normalize(token)
                if not cand:
                    continue
                rows.append(
                    path_row(classify_path(bases, cand, basenames), "inline-path", historical)
                    + (where, token)
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
                path_row(classify_path(bases, cand, basenames), "shell-path", historical)
                + (where, token)
            )


def baseline_key(kind: str, where: str, detail: str) -> str:
    """Identity of a broken row for baseline matching: kind + doc + detail,
    deliberately WITHOUT the line number. An accepted row shouldn't come back
    as new just because someone added a paragraph above it."""
    doc = where.rsplit(":", 1)[0]
    return f"{kind}\t{doc}\t{detail}"


def load_baseline(path: Path) -> set:
    """Accepted broken rows, one `kind<TAB>doc<TAB>detail` per line.
    Blank lines and `#` comments ignored."""
    accepted = set()
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            accepted.add(line)
    except OSError as exc:
        print(f"Cannot read baseline {path}: {exc}", file=sys.stderr)
    return accepted


def main(argv):
    args, flags, baseline_path = [], set(), None
    it = iter(argv)
    for a in it:
        if a == "--baseline":
            baseline_path = next(it, None)
            if baseline_path is None:
                print("--baseline needs a file path", file=sys.stderr)
                return 2
        elif a.startswith("--"):
            flags.add(a)
        else:
            args.append(a)
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
            # `.as_posix()` for the same reason as `check_doc`'s `rel`: this is a
            # `where` field, and `where` is part of the baseline identity key.
            rows.append(
                ("broken", "missing-doc", doc.as_posix(), "named on the command line, not on disk")
            )
            continue
        check_doc(root, doc, rows, basenames)

    show_all = "--all" in flags
    for verdict, kind, where, detail in rows:
        if verdict in ("broken", "unresolved") or show_all:
            print(f"{verdict}\t{kind}\t{where}\t{detail}")

    counts = {}
    for verdict, kind, _, _ in rows:
        counts[(verdict, kind)] = counts.get((verdict, kind), 0) + 1

    broken_rows = [r for r in rows if r[0] == "broken"]
    accepted, unused, new_broken = set(), set(), broken_rows
    if baseline_path is not None:
        accepted = load_baseline(Path(baseline_path))
        seen = {baseline_key(k, w, d) for _, k, w, d in broken_rows}
        new_broken = [r for r in broken_rows if baseline_key(r[1], r[2], r[3]) not in accepted]
        unused = accepted - seen
    broken = len(new_broken)

    print(f"\n--- {len(docs)} docs, {len(rows)} references ---", file=sys.stderr)
    for (verdict, kind), n in sorted(counts.items()):
        print(f"{verdict:>9}  {kind:<14} {n}", file=sys.stderr)
    if not show_all:
        print("(broken + unresolved rows shown above; --all to see ok/unchecked too)", file=sys.stderr)
    if baseline_path is not None:
        print(
            f"baseline: {len(accepted)} accepted, {len(broken_rows) - broken} matched, "
            f"{broken} NOT in baseline",
            file=sys.stderr,
        )
        for row in new_broken:
            print(f"  NEW: {row[1]}\t{row[2]}\t{row[3]}", file=sys.stderr)
        if unused:
            # Stale entries are a warning, not a failure: a baseline row whose
            # finding got fixed should be deleted, but forgetting to is not a
            # reason to block a merge.
            print(f"  {len(unused)} baseline entr{'y' if len(unused)==1 else 'ies'} no longer match anything — safe to delete:", file=sys.stderr)
            for entry in sorted(unused):
                print(f"    STALE: {entry}", file=sys.stderr)
    print(
        "broken    = anchored in a directory that exists, so the claim is about\n"
        "            THIS tree and it is false — fix these.\n"
        "unresolved= nothing in the tree matches; could equally be a runtime file,\n"
        "            an example, or prose with a slash in it — read before acting.\n"
        "historical-* = same, but in a CHANGELOG/RELEASE_NOTES, where a path that\n"
        "            no longer resolves is usually correct history. Never \"fix\" one.\n"
        "unchecked = commands and external links; running/fetching them is\n"
        "            docs-loop step 5's job, not this script's.\n"
        "Resolvable references only — prose accuracy is step 3's job either way.",
        file=sys.stderr,
    )

    return 1 if (broken and "--strict" in flags) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
