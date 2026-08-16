# Iteration 1 — analyst pass

## Headline

| | With skill | Baseline | Delta |
|---|---|---|---|
| Pass rate | 22/23 (95% ± 8%) | 21/23 (92% ± 7%) | +3pp |
| Time | 137.0s ± 33.4s | 105.3s ± 8.3s | **+30%** |
| Tokens | 53,646 ± 5,701 | 41,328 ± 1,624 | **+30%** |

**The +3pp is inside the noise.** With one run per cell and a ±8% stddev, this
is not evidence the skill improved output quality on these prompts. The cost
side (+30% time, +30% tokens) is the only measurement here that is clearly
outside the noise band.

## Only 2 of 23 assertions discriminated

| Assertion | With | Without | Note |
|---|---|---|---|
| eval-2 A1 — explicit Pass/Warn/Fail scale | PASS | **FAIL** | The one clean win. With-skill produced the 8-dimension verdict table; baseline delivered the same findings as unstructured prose. |
| eval-1 A4 — states cost of own recommendation | PASS | PASS (marginal) | With-skill had a dedicated cost section with four named ongoing costs plus a do-the-simple-thing escape hatch; baseline stated the cost as "10 lines vs 60" and immediately dismissed it. Passed on the letter, not the spirit. |

The other 21 assertions passed identically in both configurations. Both graders
independently flagged this without being prompted to.

## Two assertions were mis-specified — my error, not the skill's

- **eval-3 A6** ("declines to answer 'anything I should split further' as
  posed") **failed in both runs**, and both graders said the assertion is
  wrong: no strong answer refuses the question outright. Both runs did the
  better thing — reframed the split axis from services to modules and answered
  on that basis. An assertion that penalizes the correct behavior is worse than
  no assertion. Should be rewritten to reward the reframe.
- **eval-1 A4** is too loose: a cost mentioned and immediately minimized passes
  it. Should require a cost the author does not dismiss in the same breath.

## The prompts are too easy

This is the root cause of the non-discrimination, and it's a flaw in the eval
set rather than a finding about the skill:

- **eval-2** hands over the symptom ("silently produced an empty report for two
  weeks"). That converts an audit into a bug hunt with the answer half-given —
  any competent reader greps for the exception handler. The baseline also
  produced a *better* root-cause hypothesis than the with-skill run (a
  timezone-naive `datetime.now()` comparison), so on substance the baseline
  arguably won this one.
- **eval-3** is a well-known trap. "Should six services be six services at
  6 engineers / 400 customers" is a question the base model recognizes and
  answers correctly on instinct.
- **eval-1** is loaded: the user reports a teammate already disagreeing, which
  signals the expected answer.

## What this actually says about the skill

The defensible claim from this data is **consistency of structure**, not a
per-prompt quality jump: the skill reliably produces the verdict table, the
severity ordering, the what's-already-right section, and the explicit cost
accounting. The baseline produces those sometimes, depending on the prompt.
Across many invocations that consistency is the value — but it is *not* the
claim "the skill makes the answer better", and this iteration does not support
that claim.

## For iteration 2

1. Rewrite eval-3 A6 and tighten eval-1 A4.
2. Replace or add harder prompts where the baseline plausibly fails:
   - an audit with **no symptom disclosed**, where the defect must be found cold;
   - a design case where the *naive* answer is confidently wrong (e.g. one where
     the Unix-flavored instinct is the trap and the right answer is to bundle);
   - a non-CLI surface — a library API or agent-tool design — since
     `beyond-the-cli.md` is a third of the skill's material and no current eval
     exercises it.
3. Consider ≥2 runs per cell so the stddev means something.

## Tooling notes (for the my-skill-creator retro)

- `aggregate_benchmark.py` requires a `summary` block (`pass_rate`/`passed`/
  `failed`/`total`) in each `grading.json`. The SKILL.md documents only the
  `expectations` array. Without `summary` it reports **0.0% pass rate silently**
  — no warning, no error — which reads as a catastrophic skill failure rather
  than a schema mismatch.
- The workspace layout in "Running and evaluating test cases" (`eval-<ID>/
  with_skill/outputs/`) contradicts `aggregate_benchmark.py`, which requires an
  intermediate `run-N/` directory. Following SKILL.md as written produces a
  workspace the aggregator finds no runs in.
- `benchmark.md` emitted `**Model**: <model-name>` unsubstituted and
  `**Evals**: 1, 2, 3 (3 runs each per configuration)` — there was 1 run per
  configuration across 3 evals, so that line is wrong as printed.
