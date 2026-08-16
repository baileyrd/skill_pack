#!/usr/bin/env python3
"""reportgen - pull deploy stats and make the weekly report."""

import argparse
import csv
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta

SLACK_WEBHOOK = "https://hooks.slack.com/services/T00000/B00000/XXXXXXXX"
DB_PATH = "/var/lib/deploys/deploys.db"
OUTPUT_DIR = "/home/ops/reports"


def fetch_deploys(days):
    print("Fetching deploys...")
    since = datetime.now() - timedelta(days=days)
    rows = []
    try:
        with open(DB_PATH) as fh:
            for line in fh:
                rec = json.loads(line)
                if datetime.fromisoformat(rec["ts"]) >= since:
                    rows.append(rec)
    except Exception:
        pass
    print("Got %d deploys" % len(rows))
    return rows


def summarize(rows):
    print("Summarizing...")
    by_service = {}
    for r in rows:
        svc = r.get("service", "unknown")
        if svc not in by_service:
            by_service[svc] = {"total": 0, "failed": 0, "durations": []}
        by_service[svc]["total"] += 1
        if r.get("status") != "ok":
            by_service[svc]["failed"] += 1
        by_service[svc]["durations"].append(r.get("duration", 0))
    return by_service


def render(by_service):
    lines = []
    lines.append("=" * 60)
    lines.append("  WEEKLY DEPLOY REPORT  " + datetime.now().strftime("%Y-%m-%d"))
    lines.append("=" * 60)
    for svc, s in sorted(by_service.items()):
        rate = (1 - s["failed"] / s["total"]) * 100 if s["total"] else 0
        avg = sum(s["durations"]) / len(s["durations"]) if s["durations"] else 0
        flag = "OK" if rate > 95 else "NEEDS ATTENTION"
        lines.append("")
        lines.append("  %s [%s]" % (svc.upper(), flag))
        lines.append("    deploys: %d   failures: %d" % (s["total"], s["failed"]))
        lines.append("    success rate: %.1f%%" % rate)
        lines.append("    avg duration: %.1fs" % avg)
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def write_csv(by_service, path):
    print("Writing CSV to %s" % path)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["service", "total", "failed", "success_rate"])
        for svc, s in sorted(by_service.items()):
            rate = (1 - s["failed"] / s["total"]) * 100 if s["total"] else 0
            w.writerow([svc, s["total"], s["failed"], "%.1f%%" % rate])


def notify(text):
    print("Posting to Slack...")
    payload = json.dumps({"text": "```%s```" % text}).encode()
    req = urllib.request.Request(
        SLACK_WEBHOOK, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        print("Posted to Slack!")
    except Exception as e:
        print("Slack post failed: %s" % e)


def main():
    p = argparse.ArgumentParser(description="Generate the weekly deploy report")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--no-slack", action="store_true")
    p.add_argument("--serve", action="store_true", help="run the dashboard instead")
    args = p.parse_args()

    if args.serve:
        from http.server import HTTPServer, SimpleHTTPRequestHandler

        os.chdir(OUTPUT_DIR)
        print("Serving dashboard on :8080")
        HTTPServer(("", 8080), SimpleHTTPRequestHandler).serve_forever()
        return

    rows = fetch_deploys(args.days)
    by_service = summarize(rows)
    text = render(by_service)
    print(text)

    stamp = datetime.now().strftime("%Y%m%d")
    write_csv(by_service, os.path.join(OUTPUT_DIR, "deploys-%s.csv" % stamp))
    with open(os.path.join(OUTPUT_DIR, "report-%s.txt" % stamp), "w") as fh:
        fh.write(text)

    if not args.no_slack:
        notify(text)

    print("All done!")
    sys.exit(0)


if __name__ == "__main__":
    main()
