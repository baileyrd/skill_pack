# Release Notes

microkernel-architecture-audit lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/dev_practices/microkernel-architecture-audit) —
this log tracks commits against `main`: reverse chronological, one entry per
meaningful change, honest about what's still open.

---

## v1.1.0 — Add wrap-up retro
**2026-08-17**

- **Added:** a `Wrap-up retro` step, run after the scorecard and report land —
  a [`meta/skill-retro`](../../meta/skill-retro) pass on this skill itself: did
  the eight dimensions fit the target or did one get stretched into an N/A
  beyond dimension 4's documented case, did the target match a named archetype
  or fall to the generic path and did Rule 6's idiom-matched language still
  read naturally there, was a verdict recorded without the citation Rule 1
  requires, did Rule 8's ask-before-assuming-scope step actually fire.
- **Why:** productized into `dev_practices/` alongside `unix-philosophy`, which
  already carries this step for its audit mode. The omission was noticed only
  after the fact. Read-only and safe unattended; applying findings is a
  separate, explicitly-approved follow-up.

---

## v1.0.0 — Productized out of `need_to_productize/`
**2026-08-17**

Moved from `need_to_productize/microkernel-architecture-audit.skill` (a staged
zip archive, neither versioned nor packaged nor installed) into
`dev_practices/` as a real skill directory.

Audits a microkernel-style system across eight dimensions — core/plugin
boundaries, IPC contracts, capability-based security, WASM sandbox integrity,
plugin lifecycle, dependency inversion, async concurrency, test coverage —
with archetype-aware language for two named targets (Nexus Forge on Rust/Tauri,
FORGE on FastAPI) and a generic fallback. The eight dimensions, scoring format,
and Behavior Rules are untouched.

### Changed on productization

- **Removed the `tags:` frontmatter key.** Not in this repo's allowed
  property set — `quick_validate.py` rejected the skill outright.
- **Fixed `name: Microkernel Architecture Audit` → `name:
  microkernel-architecture-audit`.** The value was Title Case with spaces;
  every other skill name in this repo is a lowercase hyphenated slug matching
  its directory name, and the mismatch is what `quick_validate.py`'s naming
  check exists to catch.
- **Added `RELEASE_NOTES.md`** — `version: 1.0.0` was already present and
  correct.
- **Added a `Limitations` section**, which the original had none of. Notes the
  audit is tuned to its two named archetypes with a thinner generic fallback
  for anything else; that the eight dimensions assume the microkernel shape
  already holds rather than verifying it's the right architecture in the first
  place (a monolith with a plugin API bolted on for optics can score well
  without being flagged as not actually a microkernel); and that it's
  static-first — dimensions 4 (WASM sandbox) and 7 (async concurrency) are
  easier to get wrong from reading code than from watching the system run, so
  a clean static read on either is provisional.

### Not changed

- No eval set, no benchmark. Scoring consistency across the two named
  archetypes and the generic fallback is unmeasured.

**Category note:** lands in `dev_practices/` alongside `unix-philosophy` and
`shell-ui-architecture-audit` — the charter's "structured review of what
already exists" half.
