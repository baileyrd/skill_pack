---
name: yt-search
description: Searches YouTube by query using yt-dlp and returns structured, human-readable video results — title, channel, subscriber count, view count, duration, upload date, URL, and a views-to-subscribers engagement ratio. Defaults to the top 20 results from the last 6 months. Use this skill whenever the user asks to search YouTube, find videos on a topic, research YouTube content, pull video stats/metadata, or wants to see which videos on a topic are overperforming (engagement ratio).
version: 1.1.0
---

# YouTube Search

Structured YouTube search backed by `yt-dlp`. No YouTube API key required.

## When to use this skill

Trigger on requests like:
- "Search YouTube for X"
- "Find recent videos about X"
- "What videos are people making about X"
- "Pull the top videos on X with view counts / engagement"

## Prerequisites

`yt-dlp` must be resolvable, either as a CLI on PATH or as an importable Python
module (`pip install yt-dlp`). The script checks both automatically. If neither
is available, install it before continuing:

```bash
pip install yt-dlp
```

## Running a search

Invoke the bundled script with Bash, passing the query as free text plus optional flags:

```bash
python "skills/yt-search/scripts/search.py" <query> [--count N] [--months N] [--no-date-filter] [--json]
```

- `<query>` — free text, no quoting required around individual words (everything
  that isn't a recognized flag is joined into the search query).
- `--count N` — number of results to return. Default: **20**.
- `--months N` — only include videos uploaded in the last N months (accepts
  decimals, e.g. `--months 1.5`). Default: **6**.
- `--no-date-filter` — disable the recency filter and return results regardless of age.
- `--json` — emit a JSON array of result objects instead of the formatted text block
  (fields: `search_rank`, `title`, `channel`, `channel_id`, `view_count`,
  `subscriber_count`, `duration_seconds`, `duration_display`, `upload_date`,
  `upload_date_display`, `engagement_ratio` (raw float or `null`), `video_id`, `url`).
  Diagnostics still go to stderr, so stdout is clean JSON — use this when another
  skill or script needs to consume results programmatically (e.g. `yt-pipeline`).

Examples:

```bash
python scripts/search.py claude code skills
python scripts/search.py AI agents --count 10
python scripts/search.py react tutorials --months 3
python scripts/search.py machine learning --no-date-filter
```

## What it does

1. Resolves `yt-dlp` (CLI on PATH, else `python -m yt_dlp`).
2. Runs `ytsearchN:<query> --dump-json` where N is `2x` the requested count
   (extra headroom so date filtering still leaves enough results).
3. Filters out videos older than `--months` (skipped when `--no-date-filter`).
4. Trims to the requested `--count` and prints one block per video:
   - Title
   - Channel name, subscriber count, view count, duration, upload date, engagement ratio
   - Direct `https://youtube.com/watch?v=...` URL
   - A `─` divider before and between every result

## Engagement ratio

`views / channel_follower_count`, printed as e.g. `2.81x`. This is the views-to-subscribers
ratio: values notably above 1x mean the video is overperforming relative to the channel's
subscriber base (a strong signal for outlier/breakout content); values well below 1x mean
it's underperforming for that channel's size. Shows `N/A` when the channel's subscriber
count isn't available (e.g. hidden subscriber counts) or is zero.

## Numbers are abbreviated

Subscriber and view counts are formatted compactly (`1.2M`, `45.2K`, `830`) rather than as
raw integers, matching YouTube's own display convention.

## Error handling

- Missing `yt-dlp` → the script exits with an install hint; run `pip install yt-dlp` and retry.
- No query text → the script prints usage and exits nonzero; ask the user for a topic.
- No results (empty search, or none within the recency window) → the script says so on
  stderr and exits 0; relay that to the user and suggest a longer `--months` window or
  `--no-date-filter`.
- Search timeout (120s) → report the timeout; suggest retrying or narrowing the query.

Always present the script's stdout to the user as-is — it is already formatted for
direct display. Summarize stderr diagnostics (filtered count, search timing) only if useful context.

## Wrap-up retro

After presenting results, run a `meta/skill-retro` pass on `yt-search`
itself, grounded in this invocation: did the flag handling in "Running a
search" match what was actually needed, did an "Error handling" path fire
that wasn't cleanly covered, did the engagement-ratio explanation hold up
against this particular result set? Read-only, safe to run unattended —
applying anything `skill-retro` finds is a separate, explicitly-approved
follow-up, not part of this invocation.
