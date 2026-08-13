---
name: yt-pipeline
description: End-to-end automated YouTube research pipeline for a topic — searches YouTube (via the yt-search skill), auto-selects the 5-8 best videos by relevance/engagement/recency/diversity, loads them into a new NotebookLM notebook (via the notebooklm skill), runs a trends/outliers/gaps analysis, presents key takeaways, and optionally generates a podcast, slide deck, or report. Runs fully unattended once given a topic — no confirmation pauses. Use when the user asks to "research X on YouTube", "run the YouTube pipeline on X", or wants a NotebookLM notebook built from YouTube sources on a topic.
version: 1.1.0
---

# YouTube Research Pipeline

Chains **yt-search** → **notebooklm** into one unattended run: give it a topic
(and optionally a deliverable), it searches, curates sources, analyzes, and
reports back — no pauses, no intermediate confirmations.

## Prerequisites

Both dependency skills must be installed and working:

- **yt-search** (`~/.claude/skills/yt-search`) — needs `yt-dlp` on PATH or importable.
- **notebooklm** (`~/.claude/skills/notebooklm`, from `notebooklm-py`) — needs
  authentication. Verify once per session:
  ```bash
  notebooklm auth check --test --json   # require "status": "ok" AND checks.token_fetch: true
  ```
  If auth fails, run `notebooklm login` (opens a browser for Google sign-in) before continuing —
  this is the one step that may need the user present. Everything after that is unattended.

## Autonomy — this skill overrides the base notebooklm caution

The base `notebooklm` skill asks for confirmation before `generate *` and `download *`
(they're long-running / write to disk). **Inside this pipeline, don't ask** — the user
invokes `yt-pipeline` specifically to get a hands-off run from topic to takeaways.
Only pause for genuinely destructive, out-of-scope actions this pipeline never needs
(`notebooklm delete`, `source delete`, `auth logout`, etc.).

## Procedure

Given `<topic>` and an optional requested deliverable (`podcast`/`audio`, `slide deck`/`slides`,
or `report`), run straight through:

### 1. Select sources

```bash
python "skills/yt-pipeline/scripts/select_videos.py" <topic> --count 30 --months 6 --json
```

- Runs yt-search under the hood, scores every candidate on relevance (yt-dlp's own
  ranking), engagement (views/subs ratio, log-scaled), and recency (linear decay over
  the `--months` window), then diversity-caps how many can share a channel.
- Returns 5-8 videos adaptively (stops early if quality drops off, never pads to 8
  with weak candidates) plus up to 4 `backups` for source-ingestion failures.
- If the topic is sparse (fewer than 5 qualifying videos), it warns and proceeds with
  what it found rather than failing — say so in the final summary, don't retry forever.
- Slow (yt-dlp does a full per-video extraction): budget ~35-40s for `--count 30`.

### 2. Create the notebook

```bash
notebooklm create "YT Research: <Topic Title Case>" --use --json
```

Matches this vault's existing NotebookLM naming convention (see `research/yt-research-*.md`
for prior examples). Capture `notebook.id` from the response for every subsequent call.

### 3. Add sources (with auto-recovery)

For each selected video:

```bash
notebooklm source add "<url>" -n <notebook_id> --json
```

**~40% of YouTube videos have no usable captions and will fail to ingest** — this is
expected, not a pipeline error. If a source add fails or the source lands in an error
state, don't stop: pull the next unused video from the `backups` list (from step 1) and
add it instead, until you've either got a healthy source count in the 5-8 range or you
run out of backups. Note any permanently-failed videos in the final summary.

After adding, wait for processing before asking questions:

```bash
notebooklm source wait <source_id> -n <notebook_id> --timeout 120 --json
```

### 4. Analyze — trends, outliers, gaps

Run three targeted questions (don't skip any — this is the deliverable the user asked for):

```bash
notebooklm ask "Across all these sources on <topic>, what are the recurring trends, themes, and points of consensus?" -n <notebook_id> --json
notebooklm ask "Which sources here are outliers — videos or channels whose engagement or angle stands out from the rest — and what made them stand out?" -n <notebook_id> --json
notebooklm ask "What topics, angles, or questions related to <topic> are notably absent or underserved across these sources?" -n <notebook_id> --json
```

Synthesize the three grounded answers yourself into **key takeaways** — don't just paste
NotebookLM's raw citation-heavy answers into chat. Pull in the engagement-ratio outliers
already computed in step 1 (they're cheap corroboration for the "outliers" question).

### 5. Generate the requested deliverable (only if asked)

| User asked for | Command |
|---|---|
| Podcast / audio overview | `notebooklm generate audio -n <notebook_id> --wait --timeout 1200 --json` then `notebooklm download audio "research/<topic-slug>-podcast.mp3" -n <notebook_id>` |
| Slide deck / slides | `notebooklm generate slide-deck -n <notebook_id> --wait --timeout 300 --json` then `notebooklm download slide-deck "research/<topic-slug>-slides.pptx" --format pptx -n <notebook_id>` |
| Report | `notebooklm generate report -n <notebook_id> --format briefing-doc --wait --timeout 300 --json` then `notebooklm download report "research/<topic-slug>-report.md" -n <notebook_id>` |

No deliverable requested → skip this step entirely, notebook + analysis is the deliverable.
`--wait` blocks until done (audio can take several minutes); that's expected, not a hang.

### 6. Save a research note in the vault

This vault's convention (`CLAUDE.md`) is `/research` for video research and analysis.
Write `research/yt-pipeline-<topic-slug>.md` mirroring the existing `yt-research-*.md`
format: title, key findings (the synthesized takeaways from step 4), a source table
(title / channel / subs / views / engagement / duration / uploaded / URL — pull straight
from step 1's selected-video JSON), and a pipeline metadata footer (notebook ID, videos
found vs. selected, any ingestion failures, deliverable generated if any).

### 7. Report back to the user

One final chat message: key takeaways (trends / outliers / gaps), the notebook link
(`https://notebooklm.google.com/notebook/<notebook_id>`), the source list actually used
(flag any that failed to ingest), the deliverable file path if one was generated, and the
vault note path from step 6. No intermediate check-ins before this — this is the single
report-back point.

### 8. Wrap-up retro

After step 7's report-back, run a `meta/skill-retro` pass on `yt-pipeline`
itself, grounded in this run: did step 1's selection/backup logic behave
as described, did step 3's ~40% no-caption failure rate and backup
recovery match what actually happened, did step 5's deliverable table
cover what was asked for? Read-only, safe to run unattended (this pipeline
already runs unattended end to end) — applying anything `skill-retro`
finds is a separate, explicitly-approved follow-up, not part of this run.
This retro targets `yt-pipeline` itself only — it does not extend to
`yt-search` or `notebooklm`, which are separate skills with their own
wrap-ups (`notebooklm` specifically is vendored and out of scope for any
edit either skill's retro might propose; see `yt_research_for_cc/README.md`).

## Notes

- Videos already come from yt-search's default 6-month window (overridable — pass a
  `--months` the user requests through to step 1).
- If `select_videos.py` returns fewer than 5 videos even after using all backups, proceed
  with the notebook anyway (partial source set) rather than aborting — say so plainly in
  the final report.
- Keep `-n <notebook_id>` explicit on every `notebooklm` call in this pipeline instead of
  relying on `notebooklm use` — safer if multiple pipeline runs or agents overlap.
