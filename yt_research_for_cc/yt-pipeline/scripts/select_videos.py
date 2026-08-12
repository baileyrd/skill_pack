#!/usr/bin/env python3
"""Auto-select the 5-8 best videos for a topic from yt-search results.

Runs yt-search's search.py (as a subprocess, --json mode) against a topic,
then scores and diversifies the candidate pool down to a shortlist suitable
for feeding into a NotebookLM notebook as sources.

Scoring (each video gets a 0-1 composite):
  - relevance (35%): yt-dlp's own relevance ranking position (ytsearch order).
  - engagement (35%): the views/subscribers ratio from yt-search, log-scaled
    and min-max normalized across the candidate pool (log-scaled so one huge
    outlier doesn't flatten every other score to ~0). Videos with an unknown
    ratio (hidden subscriber count) get the pool median rather than being
    punished.
  - recency (30%): linear decay across the requested --months window (newer
    is better). Unknown upload dates get the pool median.

Diversity: greedy selection in composite-score order, capping how many
videos may come from the same channel so one prolific channel can't fill
the whole shortlist.

Count: adaptive between 5 and 8. Always takes the top 5. Extends to 6, 7,
then 8 only while the next candidate's composite score is still at least
half the top score (avoids padding the shortlist with also-rans just to
hit a round number).

The JSON output also includes up to 4 `backups` — diversified candidates
just outside the selected shortlist — so a caller (yt-pipeline) can top up
the source count if a selected video fails to ingest (e.g. NotebookLM
rejects a YouTube source with no available captions).
"""

import json
import math
import statistics
import subprocess
import sys
from pathlib import Path

DEFAULT_FETCH_COUNT = 30
DEFAULT_MONTHS = 6
MIN_SELECT = 5
MAX_SELECT = 8
WEIGHT_RELEVANCE = 0.35
WEIGHT_ENGAGEMENT = 0.35
WEIGHT_RECENCY = 0.30
DAYS_PER_MONTH = 30.44

USAGE = (
    "Usage: select_videos.py <topic> [--count N] [--months N] [--json]\n"
    "  --count N   videos to fetch from yt-search before scoring (default 30)\n"
    "  --months N  recency window passed to yt-search (default 6)\n"
    "  --json      emit JSON instead of a human-readable table"
)


def parse_args(argv):
    args = argv[1:]
    fetch_count = DEFAULT_FETCH_COUNT
    months = DEFAULT_MONTHS
    json_output = False
    topic_parts = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-h", "--help"):
            print(USAGE)
            sys.exit(0)
        elif arg == "--count" and i + 1 < len(args):
            fetch_count = int(args[i + 1])
            i += 2
        elif arg == "--months" and i + 1 < len(args):
            months = float(args[i + 1])
            i += 2
        elif arg == "--json":
            json_output = True
            i += 1
        else:
            topic_parts.append(arg)
            i += 1
    topic = " ".join(topic_parts).strip()
    if not topic:
        print(USAGE, file=sys.stderr)
        sys.exit(1)
    return topic, fetch_count, months, json_output


def find_yt_search_script():
    """Locate yt-search's search.py as a sibling skill (~/.claude/skills/yt-search/scripts/search.py)."""
    here = Path(__file__).resolve()
    skills_root = here.parents[2]  # .../skills/yt-pipeline/scripts/select_videos.py -> .../skills
    candidate = skills_root / "yt-search" / "scripts" / "search.py"
    if candidate.exists():
        return candidate
    return None


def fetch_candidates(topic, fetch_count, months):
    script = find_yt_search_script()
    if script is None:
        print(
            "Error: yt-search skill not found (expected ../yt-search/scripts/search.py "
            "next to yt-pipeline). Install the yt-search skill first.",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = [sys.executable, str(script), topic, "--count", str(fetch_count), "--months", str(months), "--json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        print("Error: yt-search timed out after 180 seconds.", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(f"Error: yt-search failed:\n{result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    try:
        videos = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Error: could not parse yt-search output:\n{result.stdout[:500]}", file=sys.stderr)
        sys.exit(1)

    return videos


def days_old(upload_date):
    if not upload_date or len(upload_date) != 8:
        return None
    from datetime import datetime

    try:
        dt = datetime.strptime(upload_date, "%Y%m%d")
    except ValueError:
        return None
    return (datetime.now() - dt).days


def score_candidates(videos, months):
    n = len(videos)
    window_days = max(months * DAYS_PER_MONTH, 1)

    # Engagement: log-scale raw ratios, min-max normalize, median-impute unknowns.
    known_ratios = [v["engagement_ratio"] for v in videos if v.get("engagement_ratio") is not None]
    log_ratios = [math.log1p(r) for r in known_ratios] if known_ratios else [0.0]
    lo, hi = min(log_ratios), max(log_ratios)
    median_engagement_norm = statistics.median(
        [(math.log1p(r) - lo) / (hi - lo) if hi > lo else 1.0 for r in known_ratios]
    ) if known_ratios else 0.5

    # Recency: linear decay across the window, median-impute unknown dates.
    known_ages = [d for d in (days_old(v.get("upload_date")) for v in videos) if d is not None]
    median_recency_norm = (
        statistics.median([max(0.0, 1 - age / window_days) for age in known_ages]) if known_ages else 0.5
    )

    scored = []
    for v in videos:
        rank = v.get("search_rank", n)
        relevance_norm = 1 - (rank - 1) / (n - 1) if n > 1 else 1.0

        ratio = v.get("engagement_ratio")
        if ratio is None:
            engagement_norm = median_engagement_norm
        else:
            log_r = math.log1p(ratio)
            engagement_norm = (log_r - lo) / (hi - lo) if hi > lo else 1.0

        age = days_old(v.get("upload_date"))
        if age is None:
            recency_norm = median_recency_norm
        else:
            recency_norm = max(0.0, min(1.0, 1 - age / window_days))

        composite = (
            WEIGHT_RELEVANCE * relevance_norm
            + WEIGHT_ENGAGEMENT * engagement_norm
            + WEIGHT_RECENCY * recency_norm
        )
        scored.append(
            {
                **v,
                "relevance_score": round(relevance_norm, 3),
                "engagement_score": round(engagement_norm, 3),
                "recency_score": round(recency_norm, 3),
                "composite_score": round(composite, 4),
            }
        )

    scored.sort(key=lambda v: v["composite_score"], reverse=True)
    return scored


def diversify(scored, target_pool_size):
    """Greedy-select in score order, capping videos per channel so one channel
    can't dominate. Cap starts tight and relaxes if the pool can't fill out
    otherwise."""
    cap = max(1, math.ceil(target_pool_size / 3))
    selected = []
    seen_ids = set()

    while len(selected) < min(target_pool_size, len(scored)):
        per_channel = {}
        progressed = False
        for v in scored:
            vid = v.get("video_id")
            if vid in seen_ids:
                continue
            channel = v.get("channel", "Unknown")
            if per_channel.get(channel, 0) >= cap:
                continue
            selected.append(v)
            seen_ids.add(vid)
            per_channel[channel] = per_channel.get(channel, 0) + 1
            progressed = True
            if len(selected) >= min(target_pool_size, len(scored)):
                break
        if not progressed:
            break
        if len(selected) < min(target_pool_size, len(scored)):
            cap += 1  # relax the cap and sweep again

    return selected


def adaptive_select(diversified):
    if not diversified:
        return []
    top_score = diversified[0]["composite_score"]
    selected = diversified[:MIN_SELECT]
    for candidate in diversified[MIN_SELECT:MAX_SELECT]:
        if candidate["composite_score"] >= 0.5 * top_score:
            selected.append(candidate)
        else:
            break
    return selected


def main():
    topic, fetch_count, months, json_output = parse_args(sys.argv)

    candidates = fetch_candidates(topic, fetch_count, months)
    if not candidates:
        print(f"No candidate videos found for '{topic}'.", file=sys.stderr)
        sys.exit(0)

    scored = score_candidates(candidates, months)
    diversified = diversify(scored, MAX_SELECT * 2)  # wide diversified pool to pick the adaptive cut from
    selected = adaptive_select(diversified)
    selected_ids = {v.get("video_id") for v in selected}
    backups = [v for v in diversified if v.get("video_id") not in selected_ids][:4]

    if len(selected) < MIN_SELECT:
        print(
            f"Warning: only {len(selected)} qualifying video(s) found for '{topic}' "
            f"within the last {months:g} months (wanted {MIN_SELECT}-{MAX_SELECT}). "
            "Consider a larger --months window.",
            file=sys.stderr,
        )

    if json_output:
        print(json.dumps(
            {"topic": topic, "count": len(selected), "videos": selected, "backups": backups},
            indent=2,
        ))
        return

    divider = "\u2500" * 60
    print(f"Selected {len(selected)} video(s) for \"{topic}\":\n", file=sys.stderr)
    print(divider)
    for i, v in enumerate(selected, 1):
        print(f" {i}. {v['title']}")
        print(f"    {v['channel']}  \u00b7  score {v['composite_score']:.2f} "
              f"(rel {v['relevance_score']:.2f} / eng {v['engagement_score']:.2f} / rec {v['recency_score']:.2f})")
        print(f"    {v['url']}")
        print(divider)


if __name__ == "__main__":
    main()
