# Extraction and triage recipes

Detail pulled out of `SKILL.md` to keep it lean. Everything here was run for
real against a 12:05 / 3840×2160 / 60fps / AV1 `.webm`, 449 MB.

## 1. Transcript from native captions

```bash
yt-dlp --write-auto-sub --write-sub --sub-lang en \
       --write-description --write-info-json \
       --skip-download -o "cap" "<url-or-video-id>"
```

A yt-dlp-downloaded file usually carries the ID in its name as `[ID].ext`, so a
local file you never fetched yourself can still be matched back to its captions.

Auto-caption VTT uses a rolling window — each cue repeats the previous line, so
a naive read gives you every sentence two or three times. Dedupe:

```python
import re
txt = re.sub(r'<[^>]+>', '', open('cap.en.vtt', encoding='utf-8').read())
out, seen = [], set()
for block in re.split(r'\n\n+', txt):
    lines = block.strip().split('\n')
    ts = next((l.split(' --> ')[0].split('.')[0] for l in lines if '-->' in l), None)
    if not ts:
        continue
    for l in lines:
        l = l.strip()
        if '-->' in l or not l or l.startswith('WEBVTT') or re.match(r'^(Kind|Language):', l):
            continue
        if l not in seen:
            seen.add(l)
            out.append(f'[{ts}] {l}')
open('transcript.txt', 'w', encoding='utf-8').write('\n'.join(out))
```

362 clean timestamped lines / ~18 KB out of a 127 KB VTT, for the video above.

## 2. Uniform frame sampling

Seek per frame. `-ss` before `-i` is the whole trick — it seeks to the nearest
keyframe rather than decoding forward from zero.

```bash
V="video.webm"
for t in $(seq 5 15 725); do
  ffmpeg -v error -ss $t -i "$V" -frames:v 1 \
         -vf "scale=1280:-1" -q:v 3 \
         "frames/f_$(printf '%04d' $t).jpg" -y
done
```

49 frames at 1280px from a 4K source: 3.7 MB, a few seconds total. Decoding the
same file end-to-end takes minutes.

Sizing: 1280px is enough to read section headings and diagram labels. Go to
1920px only when you need to read UI field values — it roughly doubles token
cost per frame.

## 3. Scene-change extraction

```bash
ffmpeg -ss 100 -to 600 -i "$V" \
  -vf "select='gt(scene,0.35)',scale=1920:-1,showinfo" \
  -fps_mode vfr -q:v 2 "graphics/g_%03d.jpg" -y 2> "graphics/scenes.log"
```

- **`-fps_mode vfr` is mandatory on ffmpeg 9.** `-vsync vfr` was removed. The
  failure mode is silent: exit 0, zero files written. Always verify with
  `ls *.jpg | wc -l` rather than trusting the exit code.
- Threshold `0.35` is a reasonable default. Lower catches more transitions
  (and more near-duplicates); higher risks missing a single-hold graphic.
- `showinfo` writes per-frame stats to stderr — that is what feeds triage below,
  so always redirect it to a file.

## 4. Luma triage

`showinfo` logs `mean:[Y U V]` per frame. Y is average brightness 0–255. On a
tutorial with dark graphics this separates categories almost perfectly.

```python
import re, os, shutil
log = open('scenes.log', encoding='utf-8', errors='ignore').read()
rows = re.findall(r'pts_time:([0-9.]+).*?mean:\[(\d+) (\d+) (\d+)\]', log, re.S)

seen, out = set(), []
for t, y, u, v in rows:
    t = float(t)
    if t not in seen:
        seen.add(t)
        out.append((t, int(y)))
out.sort()

OFFSET = 100  # whatever -ss you passed
for i, (t, y) in enumerate(out, 1):
    src = f'g_{i:03d}.jpg'
    a = int(t + OFFSET)
    stamp = f'{a // 60:02d}m{a % 60:02d}s'
    dest = 'diagrams' if y < 45 else ('screenshots' if y > 150 else 'other')
    os.makedirs(dest, exist_ok=True)
    shutil.move(src, os.path.join(dest, f'{stamp}_{src}'))
```

Observed split on the reference video: **22 diagrams / 9 screenshots / 42
talking-head**. The 9 screenshots held every configuration value the final
document depended on.

### Tuning and known failure modes

- **Re-derive per video.** Y<45 / Y>150 fits a dark-grid graphic style on a
  bright talking-head background. A light-themed tutorial inverts entirely.
  Dump the Y distribution first and look for the gaps.
- **Dark-themed UI misfiles as "diagram."** A Rufus window (Y=35) and the Quad9
  homepage (Y=42) both landed in `diagrams/` and had to be moved by hand.
- **Chroma is a weak second axis.** `abs(U-128)+abs(V-128)` was tried to isolate
  talking-head frames and did not separate cleanly — a neutrally-lit room reads
  nearly greyscale. Y alone did better.
- **Timestamp the filenames.** `08m12s_g_054.jpg` is far easier to cross-check
  against the transcript than `g_054.jpg`.

## 5. Verification pass

Before any reconstructed detail ships:

1. List every claim not directly visible in a frame — menu paths, field labels,
   version numbers, flags, credentials.
2. Fetch the official documentation for each.
3. Where docs and the video disagree, **go back to the frames.** The video is
   primary evidence.
4. Tag survivors `[on screen, MM:SS]` or `[reconstructed]` inline.
5. List the doc URLs actually consulted at the end of the artifact.

On the reference run this pass corrected four field names, pinned a software
version from a single download-page frame, surfaced two setup steps the video
never mentioned — and reversed one "correction" that had wrongly contradicted
the creator.
