---
name: video-teardown
description: Turns a video into a verified, structured deliverable — build guide, runbook, parts list, checklist — not just an answer about it. Reads video without video/audio input by pairing a cheap yt-dlp captions pass with targeted ffmpeg extraction, triaging frames by scene-change detection and mean-luma sorting so only the few carrying information get read. The second half is the point - any menu path, flag, field name or version reconstructed from narration is verified against official docs before shipping, and every claim is marked shown-on-screen with a timestamp or reconstructed. Use when someone wants a video turned into instructions, documentation, a parts list or checklist - "turn this video into a guide", "write up what they did", "document this tutorial", "what hardware and software did they use", "make a checklist from this" - or hands over a local video file wanting more than a summary. Companion to the vendored trying/watch skill, the better pick for one-off "what happens in this video" questions.
version: 1.1.0
---

# video-teardown

A video is two cheap streams (narration, still frames) and one expensive one
(your attention on those frames). The whole craft is spending attention only
where frames actually carry information — and then not shipping anything you
inferred from narration without checking it against a real source first.

**Scope boundary.** [`trying/watch.skill`](../../trying/watch.skill) already does
"download it, sample frames, answer a question." Prefer it for one-off
comprehension — it is the cheaper tool. Reach for this skill
when the output is a document someone will *follow* — where a wrong menu path
or an invented part number costs them an afternoon.

## Workflow

Order matters; it is the whole cost-control story.

1. **Transcript first.** It is ~5k tokens for a 12-minute video versus ~60k for
   a dense frame sample, and it gives you the map: chapter structure, the
   vocabulary, and the timestamps worth looking at. Never sample frames blind.
2. **Description and chapters.** `--write-description --write-info-json` often
   hands you the parts list and section markers directly. Cheaper than deducing
   either from pixels.
3. **Targeted frames.** Now that you know where the content is, extract there.
4. **Verify before writing.** Everything reconstructed gets checked against
   official docs. This is not optional polish — see Anti-patterns.
5. **Artifact, with provenance marked throughout.**

## Preferred patterns

- **Native captions over transcription.** `yt-dlp --write-auto-sub
  --skip-download` when the filename or URL carries a video ID. Free, instant,
  already timestamped. Dedupe the rolling-window repeats out of the VTT.
- **Seek per frame, don't decode the file.** `-ss` *before* `-i` seeks to the
  nearest keyframe and decodes one frame. Decoding a 12-minute 4K AV1 file
  straight through to grab 50 stills is minutes of CPU for no gain.
- **Scene detection when you want *distinct* visuals; uniform sampling when you
  want coverage.** They answer different questions. Uniform sampling every N
  seconds tells you what the video is about. `select='gt(scene,0.35)'` tells you
  how many *different* things it showed. Cataloguing graphics needs the second.
- **Triage frames by brightness before reading them.** `showinfo` already logs
  `mean:[Y U V]` per frame; parse it and sort. In one real case this split 73
  extracted frames into 22 dark diagrams, 9 light UI screenshots, and 42
  talking-head shots — and only the 9 screenshots contained the config values
  the whole document depended on. Reading all 73 would have cost ~15× the
  tokens for the same answer.
- **Mark provenance inline, not in a preamble.** `[on screen, 6:00]` versus
  `[reconstructed]` next to the claim itself. A caveat at the top of a document
  is not read by the person skimming to step 4. Flagging your own weakest
  inference is also what lets the user direct the next round of work.
- **State plainly when the source was right and you were wrong.** See below.

## Anti-patterns

- **Trusting a documentation summary over primary evidence.** The real incident
  this skill exists for: a creator said he set "Pool Options: Round Robin with
  Sticky Address" on a gateway group. A docs page described Pool Options as a
  NAT-only setting, so it was flagged as a likely misattribution. A screenshot
  at 6:00 of the same video showed the field plainly on the gateway-group page.
  **The source was right; the correction was wrong.** When narration and a
  secondary summary disagree, go find the frame before writing the correction —
  the video is primary evidence and a docs summary is not.
- **Shipping reconstructed menu paths as if observed.** Narrated tutorials show
  animated diagrams, not UI. In a 12-minute build video only *four* frames
  contained real application screenshots. Every other path in the write-up was
  reconstruction and had to be labelled and verified as such.
- **Sampling uniformly when the question is "what did they show?"** You will
  miss single-hold graphics entirely and collect twenty near-identical
  talking-head frames.
- **Reading every extracted frame.** Triage first. Frames are the dominant
  token cost of this entire workflow.

## Gotchas

- **ffmpeg 9 removed `-vsync`.** Use `-fps_mode vfr`. The failure is *silent* —
  the command exits 0 and writes zero files. Check the output count, never
  assume success from the exit code.
- **Luma triage breaks on dark-themed UI.** A Rufus window and the Quad9
  homepage both sorted as "dark diagram." Expect to hand-correct a few.
- **The thresholds are not constants.** Y<45 / Y>150 came from one video with
  one visual style. Re-derive per video; treat them as a starting point.
- **Scene-change frames can land mid-transition.** A frame captured at the cut
  may show a half-drawn diagram. Uniform samples often render the same graphic
  more cleanly — cross-check against both sets.
- **Auto-captions mangle product names.** "OPNsense" came through as "Open
  Sense" and "opensense.org" throughout. Never copy a product name, domain, or
  command straight from auto-captions into a document.
- **Windows:** use `python`, not `python3` — the latter is a Store stub.

## Quick reference

```bash
# transcript + description, no video download
yt-dlp --write-auto-sub --write-description --skip-download --sub-lang en "<url-or-id>"

# uniform coverage — seek per frame, do not decode the whole file
for t in $(seq 5 15 725); do
  ffmpeg -v error -ss $t -i "$V" -frames:v 1 -vf "scale=1280:-1" -q:v 3 "f_$t.jpg" -y
done

# distinct visuals — ffmpeg 9 syntax
ffmpeg -ss 100 -to 600 -i "$V" \
  -vf "select='gt(scene,0.35)',scale=1920:-1,showinfo" \
  -fps_mode vfr -q:v 2 g_%03d.jpg 2> scenes.log
```

Triage recipe, threshold-tuning notes, and the VTT dedupe snippet live in
[`references/ffmpeg-extraction-recipes.md`](references/ffmpeg-extraction-recipes.md).

## Version notes

Written against **ffmpeg 9.0** and **yt-dlp 2026.x**. The `-vsync` → `-fps_mode`
change landed in ffmpeg 7 and the option was removed outright by 9; on ffmpeg 6
or older, `-vsync vfr` is still the correct spelling.

Luma-triage thresholds are **single-video evidence** — one 4K tutorial with a
dark-grid graphic style. Treat as a method, not a calibrated constant.

## Wrap-up retro

**After the deliverable ships**, run a
[`meta/skill-retro`](../../meta/skill-retro) pass on **this skill**, grounded
in what just happened: did the transcript-first ordering in step 1 actually
save the frame budget it claims to, or did the video's structure force frames
before the map was useful; did the luma-triage thresholds (Y<45 / Y>150) need
hand-correction the way the Gotchas section already warns they might, and by
how much; did every reconstructed claim actually get checked against a real
source before shipping, or did step 4 get skipped under time pressure for a
claim that felt obvious; did a new anti-pattern show up that isn't one of the
four already listed; did the ffmpeg/yt-dlp version notes still hold, or did a
flag behave differently than documented.

Running and reporting the retro is automatic and safe unattended —
`skill-retro` never edits this skill's files on its own. *Applying* anything
it finds is a separate, explicitly-approved follow-up through this repo's
normal PR workflow, never bundled into the run that triggered it.
