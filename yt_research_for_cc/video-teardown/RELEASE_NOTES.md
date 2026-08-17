# Release Notes

video-teardown lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/yt_research_for_cc/video-teardown) —
this log tracks commits against `main`.

---

## v1.1.0 — Add wrap-up retro
**2026-08-17**

- **Added:** a `Wrap-up retro` step, run after the deliverable ships — a
  [`meta/skill-retro`](../../meta/skill-retro) pass on this skill itself:
  did the transcript-first ordering in step 1 actually save the frame budget
  it claims to; did the luma-triage thresholds need hand-correction and by
  how much; did every reconstructed claim get checked against a real source
  before shipping, or did verification get skipped under time pressure for
  something that felt obvious; did a new anti-pattern turn up that isn't
  already one of the four listed; did the ffmpeg/yt-dlp version notes still
  hold.
- **Why:** this repo's audit- and artifact-producing skills — `unix-philosophy`
  in audit mode, and the three `dev_practices/` skills productized alongside
  it — all carry this step; `video-teardown` fits the same shape (a
  substantial, artifact-producing invocation with a real verification pass)
  and was found missing it only when every skill in the repo was checked
  against the convention directly, not as part of any prior change to this
  skill. Read-only and safe unattended; applying anything the retro finds is
  a separate, explicitly-approved follow-up, never bundled into the run that
  triggered it.

---

## v1.0.0 — Initial release
**2026-08-16**

- **Added:** `video-teardown` — turning a video into a verified, structured
  deliverable (build guide, runbook, parts list, checklist) rather than a
  one-off answer about its contents. Distilled by `meta/learn-it` from a
  session that reconstructed a 12-minute hardware build video into a BOM, an
  8-step guide, a graphics catalogue, and a single-file interactive checklist.

- **Added:** `references/ffmpeg-extraction-recipes.md` — caption fetching and
  VTT dedupe, per-frame seeking, scene-change extraction, the luma-triage
  script with its tuning notes and known failure modes, and the verification
  pass checklist.

- **Scope note:** deliberately *not* an edit to `trying/watch.skill`, which overlaps
  on the first half (yt-dlp download, ffmpeg frames, read-and-answer). `watch`
  is vendored third-party MIT code by `bradautomates` with its own
  `LICENSE`/`CHANGELOG.md` and upstream repo, shipped here as a zip archive
  and using frontmatter that does not follow this repo's conventions
  (`argument-hint`, `allowed-tools`, `author`, no `version:`). Editing it in
  place would fork someone else's skill and forfeit upstream updates.
  `video-teardown` sits above it and says so in its own description.

- **Evidence basis:** every pattern, anti-pattern and gotcha traces to a real
  incident in the originating session. The load-bearing anti-pattern —
  trusting a documentation summary over primary video evidence — comes from a
  correction that was itself wrong: a creator's on-screen "Pool Options"
  setting was flagged as misattributed based on a docs page, then vindicated
  by a screenshot in the same video.

- **Known limitation:** the luma-triage thresholds (Y<45 / Y>150) rest on a
  single video with one visual style and are documented as a method to
  re-derive per video, not a calibrated constant. Per `learn-it`'s standing
  caveat on single-session evidence.
