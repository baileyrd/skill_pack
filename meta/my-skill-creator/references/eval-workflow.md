# Running and evaluating test cases

Moved out of `SKILL.md` to keep it under 500 lines; read in full when the test-run step begins.

This section is one continuous sequence — don't stop partway through. Do NOT use `/skill-test` or any other testing skill.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize results by iteration (`iteration-1/`, `iteration-2/`, etc.), then one directory per test case, then per configuration, then **one directory per run**:

```
<skill-name>-workspace/
└── iteration-1/
    └── eval-<ID>-<descriptive-name>/
        ├── eval_metadata.json
        ├── with_skill/
        │   └── run-1/              <-- this level is required, even with one run
        │       ├── outputs/
        │       ├── grading.json
        │       └── timing.json
        └── without_skill/
            └── run-1/
                ├── outputs/
                ├── grading.json
                └── timing.json
```

The `run-N/` level exists so a configuration can hold several runs and the aggregator can compute a stddev across them. With a single run it looks like pointless nesting — don't flatten it. `scripts/aggregate_benchmark.py` discovers runs with `config_dir.glob("run-*")` and **silently skips** any configuration directory without one, so a flattened workspace produces a benchmark reporting zero runs rather than an error.

Don't create all of this upfront — just create directories as you go.

## Contents

- [Step 1: Spawn all runs (with-skill AND baseline) in the same turn](#step-1-spawn-all-runs-with-skill-and-baseline-in-the-same-turn)
- [Step 2: While runs are in progress, draft assertions](#step-2-while-runs-are-in-progress-draft-assertions)
- [Step 3: As runs complete, capture timing data](#step-3-as-runs-complete-capture-timing-data)
- [Step 4: Grade, aggregate, and launch the viewer](#step-4-grade-aggregate-and-launch-the-viewer)
- [What the user sees in the viewer](#what-the-user-sees-in-the-viewer)
- [Step 5: Read the feedback](#step-5-read-the-feedback)

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn — one with the skill, one without. This is important: don't spawn the with-skill runs first and then come back for baselines later. Launch everything at once so it all finishes around the same time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/run-1/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline run** (same prompt, but the baseline depends on context):
- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `without_skill/run-1/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill (`cp -r <skill-path> <workspace>/skill-snapshot/`), then point the baseline subagent at the snapshot. Save to `old_skill/run-1/outputs/`.

Write an `eval_metadata.json` for each test case (assertions can be empty for now). Give each eval a descriptive name based on what it's testing — not just "eval-0". Use this name for the directory too. If this iteration uses new or modified eval prompts, create these files for each new eval directory — don't assume they carry over from previous iterations.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step 2: While runs are in progress, draft assertions

Don't just wait for the runs to finish — you can use this time productively. Draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `evals/evals.json`, review them and explain what they check.

Good assertions are objectively verifiable and have descriptive names — they should read clearly in the benchmark viewer so someone glancing at the results immediately understands what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

Update the `eval_metadata.json` files and `evals/evals.json` with the assertions once drafted. Also explain to the user what they'll see in the viewer — both the qualitative outputs and the quantitative benchmark.

### Step 3: As runs complete, capture timing data

When each subagent task completes, you receive a notification containing `total_tokens` and `duration_ms`. Save this data immediately to `timing.json` in the run directory (`<workspace>/iteration-<N>/eval-<ID>/<configuration>/run-1/timing.json` — alongside `outputs/`, not inside it):

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This is the only opportunity to capture this data — it comes through the task notification and isn't persisted elsewhere. Process each notification as it arrives rather than trying to batch them.

### Step 4: Grade, aggregate, and launch the viewer

Once all runs are done:

1. **Grade each run** — spawn a grader subagent (or grade inline) that reads `agents/grader.md` and evaluates each assertion against the outputs. Save results to `grading.json` in each run directory.

   `grading.json` needs **both** an `expectations` array and a `summary` block — `agents/grader.md` and `references/schemas.md` carry the full schema, and it's worth passing the required shape to the grader explicitly rather than assuming it reads them:

   ```json
   {
     "expectations": [
       {"text": "<assertion verbatim>", "passed": true, "evidence": "<quote or specific reference>"}
     ],
     "summary": {"passed": 2, "failed": 1, "total": 3, "pass_rate": 0.67}
   }
   ```

   Both halves are load-bearing and they're read by different consumers: the viewer renders `expectations` and depends on those exact field names (not `name`/`met`/`details` or other variants), while `scripts/aggregate_benchmark.py` reads `summary.pass_rate` and **defaults it to `0.0` when absent**. A grading file with a perfect `expectations` array and no `summary` therefore produces a benchmark reporting 0.0% for every configuration, with no warning — which reads as the skill under test having failed catastrophically rather than as a schema mismatch. If a benchmark comes back at 0.0%, check for `summary` before believing it.

   For assertions that can be checked programmatically, write and run a script rather than eyeballing it — scripts are faster, more reliable, and can be reused across iterations.

2. **Aggregate into benchmark** — run the aggregation script from the `my-skill-creator` directory:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each configuration, with mean ± stddev and the delta. If generating benchmark.json manually, see `references/schemas.md` for the exact schema the viewer expects.
Put each with_skill version before its baseline counterpart.

3. **Do an analyst pass** — read the benchmark data and surface patterns the aggregate stats might hide. See `agents/analyzer.md` (the "Analyzing Benchmark Results" section) for what to look for — things like assertions that always pass regardless of skill (non-discriminating), high-variance evals (possibly flaky), and time/token tradeoffs.

4. **Launch the viewer** with both qualitative outputs and quantitative data:
   ```bash
   nohup python <my-skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

   **Any environment without a display** — Cowork, remote/web Claude Code, a headless server, CI: use `--static <output_path>` to write a standalone HTML file instead of starting a server, then surface that file to the user with whatever file-delivery tool is available. Decide by whether a browser can actually open, not by which product you think you are running in: this list will always lag the environments that exist, and `nohup ... &` plus "I've opened the results in your browser" is a confident lie anywhere it doesn't. Feedback downloads as a `feedback.json` when the user clicks "Submit All Reviews"; copy it into the workspace directory for the next iteration to pick up.

Note: please use generate_review.py to create the viewer; there's no need to write custom HTML.

5. **Tell the user** something like: "I've opened the results in your browser. There are two tabs — 'Outputs' lets you click through each test case and leave feedback, 'Benchmark' shows the quantitative comparison. When you're done, come back here and let me know."

### What the user sees in the viewer

The "Outputs" tab shows one test case at a time:
- **Prompt**: the task that was given
- **Output**: the files the skill produced, rendered inline where possible
- **Previous Output** (iteration 2+): collapsed section showing last iteration's output
- **Formal Grades** (if grading was run): collapsed section showing assertion pass/fail
- **Feedback**: a textbox that auto-saves as they type
- **Previous Feedback** (iteration 2+): their comments from last time, shown below the textbox

The "Benchmark" tab shows the stats summary: pass rates, timing, and token usage for each configuration, with per-eval breakdowns and analyst observations.

Navigation is via prev/next buttons or arrow keys. When done, they click "Submit All Reviews" which saves all feedback to `feedback.json`.

### Step 5: Read the feedback

When the user tells you they're done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus your improvements on the test cases where the user had specific complaints.

Kill the viewer server when you're done with it:

```bash
kill $VIEWER_PID 2>/dev/null
```
