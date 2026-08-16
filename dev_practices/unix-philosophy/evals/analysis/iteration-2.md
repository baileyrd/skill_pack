# Iteration 2 — analyst pass

## Headline

| | With skill | Baseline | Delta |
|---|---|---|---|
| Pass rate | **53/53 (100%)** | 45/53 (85% ± 10%) | **+15pp** |
| Time | 153.8s | 111.4s | +38% |
| Tokens (median) | 55.8k | 40.2k | +39% |

Iteration 1 was +3pp inside a ±8% band — noise. Iteration 2 is +15pp with the
with-skill configuration at zero variance (it passed everything). That is
outside the noise band and is a real effect.

**Caveat on the mean-token figure**: `benchmark.md` reports with-skill tokens as
112,097 ± 141,322. One run (eval-6 with_skill) consumed 400,391 tokens, ~8x the
next highest. The median is the honest number: 55.8k vs 40.2k. The stddev
exceeding the mean is the giveaway that the mean is meaningless here.

## Per-eval

| Eval | With | Baseline | Discriminating assertions |
|---|---|---|---|
| 1 — design, feature creep | 7/7 | 6/7 | A4 (ongoing cost, unminimized) |
| 2 — audit, symptom disclosed | 12/12 | 10/12 | A1 (verdict scale), A11 (truncation depth) |
| 3 — counterweight, over-decomposition | 8/8 | 6/8 | A6 (reframe), A8 (cost of own rec) |
| 4 — cold audit, library | 10/10 | 9/10 | A8 (verdict scale) |
| 5 — trap, literal application | 8/8 | **8/8** | none |
| 6 — agent tool surface | 8/8 | 6/8 | A2 (triggering mechanism), A7 (cost of own rec) |

## What actually separates the configurations

Two things, repeatedly:

1. **Stating the cost of its own recommendation** — eval-1 A4, eval-3 A8,
   eval-6 A7. The baseline routinely delivers a strong recommendation and then
   either omits its downside or minimizes it in the same sentence ("~40 lines,
   and you may already have most of it"; "five tool definitions is rounding
   error"; "that's free correctness"). This is the skill's "state the tradeoff
   out loud" step and its argue-from-present-cost framing doing the work.
2. **Completing the causal chain to a mechanism** — eval-6 A2. The baseline
   justified splitting an MCP tool via schema precision and permissions but
   never reached *why* it matters (a tool doing five things can't be described
   precisely, so the model triggers it unreliably). A plausible reason that
   stops short of the mechanism.

Secondarily, the **verdict scale** (eval-2 A1, eval-4 A8) — the baseline never
produces one unprompted. Real, but it is presentation, not substance.

## The negative result, stated plainly

**eval-5, the trap, did not discriminate: 8/8 both.** It was built specifically
to test whether the "when not to apply this" section earns its place — whether
the base model, invited to apply the philosophy literally to 4GB float32
arrays, would take the bait. It did not. Both runs refused JSON, both did the
arithmetic (~1.07e9 values, 14–15GB of text per boundary, ~32–38GB peak RAM),
both separated the recombination goal from the transport, both cleared the
strict A3 bar on naming the throughput cost as a weighed tradeoff.

The hypothesis was that the counterweight material would be load-bearing. On
this evidence it is not. Keeping it is defensible as insurance — the failure it
guards against is severe and this is one prompt — but the claim "the skill
prevents doctrine being applied where it doesn't fit" is unsupported.

## Honest read on the measurement

Five of the eight discriminating assertion-slots come from assertions I wrote or
rewrote *after* seeing iteration 1 fail to discriminate. That is legitimate
(iteration 1's assertions were demonstrably mis-specified — one penalized the
correct behavior) but it warrants scrutiny: am I measuring better output, or
this skill's house style?

- **A4/A8/A7 (cost of own recommendation)** survive the test. Carrying an
  unmitigated ongoing cost is better advice under any reading, independent of
  this skill.
- **eval-6 A2 (triggering mechanism)** survives. It is a factual claim about
  how tool selection works, not a stylistic preference.
- **A1/A8 (verdict scale)** do *not* survive it. These reward a format the
  skill prescribes. They are legitimate as a consistency measure but should not
  be counted as evidence of better analysis.

Discounting the two format assertions, the delta is +6 assertion-slots rather
than +8 — still outside the noise band, still real.

## Grader notes carried forward (not acted on this iteration)

- **eval-3 A3** is worded as an enumerated triple (invoice/tax/ledger as one
  transactional unit); the with-skill run made the argument for the
  invoice↔ledger pair and kept tax in-process on different grounds. Passed, but
  the assertion should be reworded around the coupled cluster.
- **eval-2 A6** passed for with_skill on a technicality: it names the hardcoded
  webhook and prescribes env vars but scopes "security of the webhook" out,
  never framing it as a live credential in version control the way the baseline
  did. Worth splitting into two assertions.
- **eval-4 A1–A7** are now non-discriminating; A8 does nearly all the
  separating work, making eval-4 more a formatting test than the depth test it
  was designed as. The baseline additionally found defects the with-skill run
  missed (429 never retried, no connection pooling, no trace propagation,
  URL injection via unquoted path) — worth new assertions.

## Skill change made this iteration

Two with-skill runs reported *skipping* the wrap-up `skill-retro` step
(read-only sandbox, no subagents). Both were right to. The step had been wired
to every invocation by repo convention rather than by fit. Scoped to audit mode
only in **v1.1.0**. Note the eval outputs above were produced against v1.0.0;
no assertion tests the retro step, so the grades are unaffected.
