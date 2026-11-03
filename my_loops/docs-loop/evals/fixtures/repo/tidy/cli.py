"""Command-line entry point."""
import argparse
import pathlib
import time


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tidy")
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--older-than", type=int, required=True, metavar="DAYS")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--exclude", action="append", default=[], help="glob to keep")
    args = parser.parse_args(argv)

    cutoff = time.time() - args.older_than * 86400
    for entry in args.path.iterdir():
        if not entry.is_file() or any(entry.match(g) for g in args.exclude):
            continue
        if entry.stat().st_mtime < cutoff:
            print(f"delete {entry}")
            if not args.dry_run:
                entry.unlink()
    return 0
