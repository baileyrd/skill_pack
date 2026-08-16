# Release Notes

unix-philosophy lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/dev_practices/unix-philosophy) —
this log tracks commits against `main`.

---

## v1.0.0 — Initial release
**2026-08-16**

- **Added:** `SKILL.md` with two modes over one body of material — design mode
  (a seven-step checklist for a live design decision: the `and` test, boundary
  format, output discipline, mechanism/policy split, failure behavior, earned
  complexity, stated tradeoff) and audit mode (scope → score eight dimensions →
  rank by present cost → name what's right → report and stop).
- **Added:** `references/philosophy.md` — the source Unix design philosophy
  material (McIlroy's tenet, the five foundational principles, Raymond's
  seventeen rules), extended with a closing section giving the *cost* of each
  principle, so the skill argues from tradeoffs rather than from authority.
- **Added:** `references/audit-rubric.md` — the eight audit dimensions (single
  purpose, composability, interface format, output discipline, mechanism vs
  policy, failure behavior, transparency, simplicity & replaceability) with
  per-dimension signal tables, Pass/Warn/Fail/N-A criteria, severity
  definitions ranked by cost already paid, and the report template.
- **Added:** `references/beyond-the-cli.md` — translations of the principles to
  libraries/modules, HTTP and RPC services, background pipelines, CLIs, and
  agent tools/skills, plus the case where the analogy breaks (distributed
  systems, where `parsimony` cuts against decomposition).
- **Added:** wrap-up retro step wired to `meta/skill-retro`, per this repo's
  retro-by-default convention — read-only, with applying findings kept as a
  separate approved follow-up.
- **Note:** opens a fourth authored category folder, `dev_practices/`, for
  design- and coding-discipline skills. Existing categories are scoped to
  external repo-maintenance loops (`my_loops/`), this repo's own skills
  (`meta/`), a research pipeline (`yt_research_for_cc/`), and framework code
  generation (`web_dev/`) — none of which fits guidance on how software is
  shaped. `ARCHITECTURE.md`'s Structure section and the root `README.md`
  updated to match.
