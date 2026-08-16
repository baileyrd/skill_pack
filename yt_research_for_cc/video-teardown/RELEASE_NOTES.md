# Release Notes

video-teardown lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/yt_research_for_cc/video-teardown) —
this log tracks commits against `main`.

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

- **Scope note:** deliberately *not* an edit to `trying/watch`, which overlaps
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
