# Eval analysis

Why this skill is shaped the way it is, kept next to the evals that produced the
evidence. The run outputs themselves are scratch (`*-workspace/`, gitignored);
these conclusions are not.

| File | What's in it |
|---|---|
| [`iteration-1.md`](iteration-1.md) | First run, 3 evals / 23 assertions. **+3pp, inside the noise.** Only 2 of 23 assertions discriminated; two were mis-specified, one of them penalizing the correct behavior. Diagnosis: the prompts were too easy, not the skill too weak. |
| [`iteration-2.md`](iteration-2.md) | Second run after repairing the set, 6 evals / 53 assertions. **+15pp, outside the noise.** Names what actually separates the configurations, and records the negative result on eval-5. |
| [`iteration-1-benchmark.md`](iteration-1-benchmark.md), [`iteration-2-benchmark.md`](iteration-2-benchmark.md) | Raw aggregate output. Iteration 2's mean token figure is distorted by one 400k outlier — see `iteration-2.md` for the median. |

## The two things worth carrying forward

**What the skill measurably does.** It makes recommendations *accountable* —
stating the ongoing cost of its own advice, and completing the causal chain to a
mechanism instead of stopping at a plausible reason. It does not make the
analysis smarter; the base model is already strong at this kind of design
reasoning. Claims about this skill should stay inside that boundary.

**What it does not do — recorded because it's easy to quietly drop.** Eval-5
was built specifically to test whether the "when not to apply this" counterweight
material is load-bearing: invite the model to apply the philosophy literally to
4GB float32 arrays and see if it takes the bait. It didn't, with or without the
skill — 8/8 both. The section stays as insurance against a severe failure mode,
but the claim that it prevents misapplied doctrine is **unsupported by this
evidence**. If a future iteration wants to justify that section, it needs a
prompt that actually defeats the baseline.

## Reading these critically

`iteration-2.md` flags this itself and it bears repeating: five of the eight
discriminating assertion-slots come from assertions rewritten *after* iteration
1 failed to discriminate. Rewriting a measurement that failed to detect an
expected difference is exactly how a benchmark gets talked into a result. The
analysis separates the assertions that survive that scrutiny (cost accounting,
triggering mechanism — better advice under any reading) from the two that don't
(the verdict-scale assertions, which reward a format this skill prescribes).
Discounting the latter, the delta is +6 slots rather than +8.
