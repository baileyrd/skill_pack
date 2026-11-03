#!/usr/bin/env python3
"""notify: send a message to a chat webhook.

Exit codes: 0 sent, 2 bad usage, 3 webhook rejected, 4 network error after retries.
"""
import argparse
import configparser
import csv
import json
import os
import pathlib
import sys
import time
import urllib.request

CONFIG = pathlib.Path.home() / ".notifyrc"


def load_config() -> dict[str, str]:
    parser = configparser.ConfigParser()
    parser.read(CONFIG)
    return dict(parser["default"]) if parser.has_section("default") else {}


def send(url: str, text: str, retries: int) -> int:
    body = json.dumps({"text": text}).encode()
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, body, {"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return 0 if resp.status < 300 else 3
        except urllib.error.HTTPError as exc:
            if exc.code < 500:
                return 3
        except OSError:
            pass
        time.sleep(2 ** attempt)
    return 4


def main() -> int:
    cfg = load_config()
    p = argparse.ArgumentParser(prog="notify")
    p.add_argument("message", nargs="?")
    p.add_argument("--url", default=os.environ.get("NOTIFY_URL", cfg.get("url")))
    p.add_argument("--retries", type=int, default=int(cfg.get("retries", 3)))
    p.add_argument("--stdin", action="store_true", help="read the message from stdin")
    p.add_argument("--legacy-csv", metavar="FILE", help=argparse.SUPPRESS)
    args = p.parse_args()
    if not args.url:
        print("notify: no webhook URL (use --url, NOTIFY_URL or ~/.notifyrc)", file=sys.stderr)
        return 2
    if args.legacy_csv:
        with open(args.legacy_csv, newline="") as fh:
            for row in csv.reader(fh):
                send(args.url, " | ".join(row), args.retries)
        return 0
    text = sys.stdin.read() if args.stdin else args.message
    if not text:
        print("notify: empty message", file=sys.stderr)
        return 2
    return send(args.url, text, args.retries)


if __name__ == "__main__":
    sys.exit(main())
