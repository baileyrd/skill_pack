# Release Notes

unix-philosophy lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/dev_practices/unix-philosophy) —
this log tracks commits against `main`.

---

## v1.1.2 — YAML-safe description
**2026-08-16**

- **Fixed ([#59](https://github.com/baileyrd/skill_pack/issues/59)):** the
  frontmatter `description` was an unquoted plain scalar containing `": "`,
  which is invalid YAML — a colon-space inside a plain scalar reads as the start
  of a nested mapping. It is now a `>-` block scalar. The *value* is byte-for-byte
  unchanged; this is a representation fix, verified by round-tripping the parsed
  string before and after.
- **Why it went unnoticed:** `scripts/check_repo.py` parses frontmatter with a
  hand-rolled line-based parser that tolerates the construct, so CI stayed green
  and packaging worked, while anything using a real YAML parser rejected the file
  outright. `quick_validate.py` was the instance that surfaced it. The repo was
  validating with a parser more permissive than its consumers'.

---

## v1.1.1 — Track the eval analysis alongside the evals
**2026-08-16**

- **Added:** `evals/analysis/` — the analyst passes and benchmark aggregates
  from both eval iterations, with a README summarizing what the evidence
  supports. Doc-only; no change to the skill's instructions.
- **Why:** the run outputs live under `*-workspace/`, which is gitignored as
  scratch, so the conclusions were about to die with the session that produced
  them. What the evidence supports (this skill makes recommendations
  *accountable* — it does not make the analysis smarter) and what it does not
  (the "when not to apply this" section is unvalidated; eval-5 scored 8/8 both
  with and without the skill) are exactly the things that get quietly
  overstated once the numbers are gone.
- **Kept deliberately:** the note that five of the eight discriminating
  assertion-slots come from assertions rewritten after iteration 1 failed to
  discriminate, and which of those survive scrutiny. A benchmark whose
  measurements were revised until they showed a result should carry that fact
  next to the result.

---

## v1.1.0 — Scope the wrap-up retro to audit mode
**2026-08-16**

- **Changed:** the wrap-up `skill-retro` step now fires **only after an audit
  report**, not after every invocation. Design mode explicitly does not trigger
  one, and the section says why: the sibling skills carrying this step are
  long-running loops that file issues and merge PRs, where a retrospective is
  small next to the work it reflects on, whereas a design-mode consultation is
  often a few paragraphs answering one question.
- **Why, specifically:** during v1.0.0's eval runs, two independent design-mode
  invocations reported *skipping* the retro because the environment was
  read-only and subagents were barred. Both were correct to skip. A final step
  that a run routinely reports not doing is worse than no step — it trains the
  reader to treat the skill's instructions as advisory. The retro was wired to
  every invocation by convention rather than by fit; this scopes it to the
  substantial, artifact-producing mode where it earns its cost.
- **Added:** an escape hatch for the case the change gives up — a design
  conversation that does turn into substantial work is still worth a retro, but
  as an explicit request the user rules on, not an automatic step.
- **Changed:** the retro's prompts are now audit-specific (did a dimension get
  stretched into an N/A, did the severity bands sort these findings or did
  everything pile into one) rather than spanning both modes.

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
