#!/usr/bin/env python3
"""YouTube search via yt-dlp with structured, human-readable output.

Searches YouTube for a query, filters to a recency window, and prints
each result's title, channel, subscriber count, view count, duration,
upload date, URL, and a views-to-subscribers engagement ratio.
"""

import importlib.util
import io
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta

# Force UTF-8 output so emoji / non-ASCII video titles never crash on Windows.
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DEFAULT_COUNT = 20
DEFAULT_MONTHS = 6
DAYS_PER_MONTH = 30.44  # average month length; avoids drift over large --months values

USAGE = (
    "Usage: search.py <query> [--count N] [--months N] [--no-date-filter] [--json]\n"
    "Example: search.py claude code tutorial --count 5 --months 3"
)


def parse_args(argv):
    """Parse query text, --count N, --months N, --json, and --no-date-filter from argv."""
    args = argv[1:]
    count = DEFAULT_COUNT
    months = DEFAULT_MONTHS
    json_output = False
    query_parts = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-h", "--help"):
            print(USAGE)
            sys.exit(0)
        elif arg == "--count" and i + 1 < len(args):
            try:
                count = int(args[i + 1])
            except ValueError:
                print(f"Error: --count requires an integer, got '{args[i + 1]}'", file=sys.stderr)
                sys.exit(1)
            if count <= 0:
                print("Error: --count must be a positive integer", file=sys.stderr)
                sys.exit(1)
            i += 2
        elif arg == "--months" and i + 1 < len(args):
            try:
                months = float(args[i + 1])
            except ValueError:
                print(f"Error: --months requires a number, got '{args[i + 1]}'", file=sys.stderr)
                sys.exit(1)
            i += 2
        elif arg == "--no-date-filter":
            months = 0
            i += 1
        elif arg == "--json":
            json_output = True
            i += 1
        else:
            query_parts.append(arg)
            i += 1
    query = " ".join(query_parts).strip()
    if not query:
        print(USAGE, file=sys.stderr)
        sys.exit(1)
    return query, count, months, json_output


def resolve_ytdlp_cmd():
    """Return the argv prefix to invoke yt-dlp, or None if it isn't available."""
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    if importlib.util.find_spec("yt_dlp") is not None:
        return [sys.executable, "-m", "yt_dlp"]
    return None


def format_number(n):
    """Format a count as a compact human-readable string (e.g. 1,234 -> 1.2K)."""
    if n is None:
        return "N/A"
    n = int(n)
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000:
        return f"{sign}{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{sign}{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{sign}{n / 1_000:.1f}K"
    return f"{sign}{n}"


def format_duration(info):
    """Extract a human-readable duration from yt-dlp info."""
    if info.get("duration_string"):
        return info["duration_string"]
    dur = info.get("duration")
    if dur is None:
        return "N/A"
    dur = int(dur)
    hours, remainder = divmod(dur, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def format_date(raw):
    """Convert a YYYYMMDD string to a human-readable date (e.g. Jan 10, 2026)."""
    if not raw or len(raw) != 8:
        return "N/A"
    try:
        return datetime.strptime(raw, "%Y%m%d").strftime("%b %d, %Y")
    except ValueError:
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"


def get_cutoff_date(months):
    """Get the cutoff date as a YYYYMMDD string, `months` months before today."""
    if months <= 0:
        return None
    cutoff = datetime.now() - timedelta(days=months * DAYS_PER_MONTH)
    return cutoff.strftime("%Y%m%d")


def engagement_ratio_value(views, subs):
    """Raw views/subs ratio as a float, or None when subs are missing/zero."""
    if not subs or subs <= 0 or views is None:
        return None
    return views / subs


def engagement_ratio(views, subs):
    """Views-to-subscribers ratio: how many times a video's views exceed the
    channel's subscriber count. Higher = video is overperforming for the channel's size."""
    value = engagement_ratio_value(views, subs)
    return f"{value:.2f}x" if value is not None else "N/A"


def main():
    query, count, months, json_output = parse_args(sys.argv)

    ytdlp_cmd = resolve_ytdlp_cmd()
    if ytdlp_cmd is None:
        print(
            "Error: yt-dlp not found. Install it with: pip install yt-dlp",
            file=sys.stderr,
        )
        sys.exit(1)

    # Fetch extra results up front so date filtering still leaves `count` videos.
    fetch_count = count * 2 if months > 0 else count
    search_query = f"ytsearch{fetch_count}:{query}"
    cmd = ytdlp_cmd + [
        search_query,
        "--dump-json",
        "--no-download",
        "--no-warnings",
        "--quiet",
    ]

    months_label = f", last {months:g} months" if months > 0 else ""
    print(f'Searching YouTube for: "{query}" (top {count} results{months_label})...\n', file=sys.stderr)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        print("Error: Search timed out after 120 seconds.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: yt-dlp not found. Install it with: pip install yt-dlp", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0 and not result.stdout.strip():
        print(f"Error: yt-dlp failed:\n{result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    videos = []
    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue
        try:
            videos.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    if not videos:
        print("No results found.", file=sys.stderr)
        sys.exit(0)

    cutoff = get_cutoff_date(months)
    if cutoff:
        filtered = [v for v in videos if (v.get("upload_date") or "00000000") >= cutoff]
        skipped = len(videos) - len(filtered)
        videos = filtered
        if skipped:
            print(f"(Filtered out {skipped} video(s) older than {months:g} months)\n", file=sys.stderr)

    if not videos:
        print(f"No results found within the last {months:g} months.", file=sys.stderr)
        sys.exit(0)

    videos = videos[:count]

    if json_output:
        results = []
        for i, info in enumerate(videos, 1):
            views = info.get("view_count")
            subs = info.get("channel_follower_count")
            video_id = info.get("id", "")
            results.append(
                {
                    "search_rank": i,
                    "title": info.get("title") or "Unknown Title",
                    "channel": info.get("channel") or info.get("uploader") or "Unknown",
                    "channel_id": info.get("channel_id"),
                    "view_count": views,
                    "subscriber_count": subs,
                    "duration_seconds": info.get("duration"),
                    "duration_display": format_duration(info),
                    "upload_date": info.get("upload_date"),
                    "upload_date_display": format_date(info.get("upload_date", "")),
                    "engagement_ratio": engagement_ratio_value(views, subs),
                    "video_id": video_id,
                    "url": f"https://youtube.com/watch?v={video_id}" if video_id else None,
                }
            )
        print(json.dumps(results, indent=2))
        return

    divider = "\u2500" * 60

    print(divider)
    for i, info in enumerate(videos, 1):
        title = info.get("title") or "Unknown Title"
        channel = info.get("channel") or info.get("uploader") or "Unknown"
        views = info.get("view_count")
        subs = info.get("channel_follower_count")
        duration = format_duration(info)
        date = format_date(info.get("upload_date", ""))
        video_id = info.get("id", "")
        url = f"https://youtube.com/watch?v={video_id}" if video_id else "N/A"
        ratio = engagement_ratio(views, subs)

        meta = (
            f"{channel} ({format_number(subs)} subs)  \u00b7  {format_number(views)} views"
            f"  \u00b7  {duration}  \u00b7  {date}  \u00b7  engagement {ratio}"
        )

        print(f" {i:>2}. {title}")
        print(f"     {meta}")
        print(f"     {url}")
        print(divider)


if __name__ == "__main__":
    main()
