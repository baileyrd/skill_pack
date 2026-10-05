---
name: my-skill-creator
description: This repo's own copy of the skill-creator workflow (draft → test → eval → iterate → optimize description → package), adapted to skill_pack's own authoring conventions and with one behavioral change from the upstream version — every skill it drafts or improves gets a wrap-up-retro step wired to meta/skill-retro by default, not as a separate follow-up change. Use when users want to create a skill from scratch, edit or optimize an existing skill in this repo, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy — same triggers as upstream skill-creator, but prefer this copy over the generic one whenever the target skill lives in (or is meant to land in) skill_pack, since it applies this repo's own conventions and the retro-by-default rule automatically.
version: 1.4.0
---

# My Skill Creator

skill_pack's own copy of Anthropic's `skill-creator` (see
`/mnt/skills/examples/skill-creator` or the vendored original this was
forked from), kept and versioned in this repo rather than used from
outside it, with two additions layered on top of the unchanged upstream
workflow:

1. **This repo's own conventions** are applied automatically when drafting
   or editing a skill meant to live in `skill_pack` — see "This repo's own
   conventions" below, right after "Write the SKILL.md."
2. **Retro by default** — every skill this tool drafts or substantively
   improves gets a wrap-up-retro step wired to `meta/skill-retro`, applied
   at draft time rather than as a separate follow-up PR. See "Retro by
   default" below.

Everything else — the interview, the eval/benchmark loop, description
optimization, packaging — is the same process upstream `skill-creator`
already describes well; this file doesn't re-explain what it doesn't
change.

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run claude-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
  - While the runs happen in the background, draft some quantitative evals if there aren't any (if there are some, you can either use as is or modify if you feel something needs to change about them). Then explain them to the user (or if they already existed, explain the ones that already exist)
  - Use the `eval-viewer/generate_review.py` script to show the user the results for them to look at, and also let them look at the quantitative metrics
- Rewrite the skill based on feedback from the user's evaluation of the results (and also if there are any glaring flaws that become apparent from the quantitative benchmarks)
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress through these stages. So for instance, maybe they're like "I want to make a skill for X". You can help narrow down what they mean, write a draft, write the test cases, figure out how they want to evaluate, run all the prompts, and repeat.

On the other hand, maybe they already have a draft of the skill. In this case you can go straight to the eval/iterate part of the loop.

Of course, you should always be flexible and if the user is like "I don't need to run a bunch of evaluations, just vibe with me", you can do that instead.

Then after the skill is done (but again, the order is flexible), you can also run the skill description improver, which we have a whole separate script for, to optimize the triggering of the skill.

Cool? Cool.

## Communicating with the user

The skill creator is liable to be used by people across a wide range of familiarity with coding jargon. If you haven't heard (and how could you, it's only very recently that it started), there's a trend now where the power of Claude is inspiring plumbers to open up their terminals, parents and grandparents to google "how to install npm". On the other hand, the bulk of users are probably fairly computer-literate.

So please pay attention to context cues to understand how to phrase your communication! In the default case, just to give you some idea:

- "evaluation" and "benchmark" are borderline, but OK
- for "JSON" and "assertion" you want to see serious cues from the user that they know what those things are before using them without explaining them

It's OK to briefly explain terms if you're in doubt, and feel free to clarify terms with a short definition if you're unsure if the user will get it.

---

## Creating a skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. The user may need to fill the gaps, and should confirm before proceeding to the next step.

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them. Suggest the appropriate default based on the skill type, but let the user decide.

### Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Check available MCPs - if useful for research (searching docs, finding similar skills, looking up best practices), research in parallel via subagents if available, otherwise inline. Come prepared with context to reduce burden on the user.

### Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier
- **description**: When to trigger, what it does. This is the primary triggering mechanism - include both what the skill does AND specific contexts for when to use it. All "when to use" info goes here, not in the body. Note: currently Claude has a tendency to "undertrigger" skills -- to not use them when they'd be useful. To combat this, please make the skill descriptions a little bit "pushy". So for instance, instead of "How to build a simple fast dashboard to display internal Anthropic data.", you might write "How to build a simple fast dashboard to display internal Anthropic data. Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard.'"
- **compatibility**: real environment requirements only — binaries, network access, intended product (≤500 chars, optional; most skills don't need it)
- **the rest of the skill :)**

### This repo's own conventions

When the skill being drafted or edited is going to live in `skill_pack`
(the common case for anyone reaching for this copy instead of the generic
upstream one), layer these on top of the interview above — read
`meta/learn-it/references/skill-authoring-conventions.md` for the full
detail; summarized here:

- Add a `version: 1.0.0` field to the frontmatter (new skill), or bump it
  by hand — semver: patch for wording/doc-only fixes, minor for new
  guidance/steps, major only for an actual contract change — when editing
  an existing one. Every skill in this repo carries this field.
- **`description` has a hard ceiling of 1024 characters** — claude.ai's limit,
  enforced by `scripts/check_repo.py`'s `manifests` check. Write it long and
  information-dense as the guidance above and in
  `meta/learn-it/references/skill-authoring-conventions.md` says, then *check
  the length before committing*. Those two instructions genuinely conflict, and
  the limit wins; following the "be thorough" advice as written naturally
  overshoots. When trimming, cut trigger-phrase examples before cutting the
  statement of what the skill does and how — triggering degrades gracefully
  with fewer example phrasings, and not at all gracefully if the reader can no
  longer tell what the skill is for.
- **Write the description as a YAML block scalar** (`description: >-`, wrapped
  and indented) rather than one long plain line, unless you are certain it
  contains no `": "`. A colon followed by a space inside an unquoted plain
  scalar is invalid YAML — the parser reads it as a nested mapping — and a
  description that quotes a trigger phrase (`Audit mode reviews what exists:
  "..."`) hits this easily. `check_repo.py`'s hand-rolled parser tolerates it,
  so the repo's own checks stay green while every real consumer rejects the
  file. Four skills shipped this way before it was noticed.
- Add a `RELEASE_NOTES.md` next to the new/edited `SKILL.md`:
  reverse-chronological, one dated entry per meaningful change, explaining
  what changed and why.
- Place the skill directory under the right category folder (`my_loops/`,
  `yt_research_for_cc/`, `meta/`) — or flag "this doesn't fit an existing
  category" as its own decision to confirm rather than forcing a fit or
  defaulting silently.
- Keep `SKILL.md` itself lean; push depth into `references/`. Only add
  `scripts/`/`assets/` when there's real content for them.
- After writing or editing, update the root `README.md`'s category table
  and the root `CHANGELOG.md`'s `Unreleased` section, and sanity-check with
  `python3 scripts/build_skill_zips.py` — this repo's own multi-skill
  build, distinct from this skill's own `scripts/package_skill.py` (which
  packages a *single* skill for upload elsewhere). Run both when the skill
  lands in this repo: `package_skill.py` only if the user also wants a
  portable `.skill` file to hand off, `build_skill_zips.py` regardless, as
  the repo-wide sanity check.
- If any new file is a script (`.sh`/`.py` meant to be executed directly),
  verify its executable bit landed as `100755` after `git add` — this repo
  runs `core.fileMode=false`, so a brand-new script needs an explicit check
  (`git ls-files -s <path>`), not an assumption that `chmod +x` alone
  survives staging.
- **The bit does not survive delivery, so don't let a skill depend on it.**
  Whatever it is in git, the sync that hands a skill to a session drops mode
  bits — every script arrives as `0644`, measured at 31 of 31 in a live
  session — so a drafted step that names a script path on its own fails with
  `permission denied`
  ([#1](https://github.com/baileyrd/skill_pack/issues/1)). Any skill drafted
  here that ships scripts must either name the interpreter at each invocation
  (prefix it with `bash` or `python3`) or document the recovery
  (`chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true`).
  `tests/test_script_invocation.py` enforces this and will fail the PR
  otherwise.
- Land the change through this repo's standing PR workflow (branch, PR,
  merge with a merge commit on green CI or no CI) — same as
  `CONTRIBUTING.md` requires for anything else here.

None of this applies when the skill being drafted is explicitly meant for
use *outside* `skill_pack` (e.g. the user wants a `.skill` file to hand to
someone else, unrelated to this repo) — in that case, follow upstream
`skill-creator`'s process unmodified and skip this section entirely.

### Retro by default

Every skill this tool drafts from scratch, or substantively improves (a
real behavioral/content change, not a typo fix), gets a **wrap-up-retro
step wired to `meta/skill-retro`** added at the same time — this is the
one behavioral difference from upstream `skill-creator`. It follows the
convention already applied across every authored skill in `skill_pack`
(`my_loops/rust-migration` and its five siblings, `yt-search`,
`yt-pipeline`, `meta/skill-retro`'s own step 6, `meta/learn-it`'s own step
6). Build it into the first draft the same way `name`/`description`/
`version` are part of every draft — not an afterthought to suggest once
the skill is otherwise "done."

Before picking a shape, check the retro's cost against a **typical**
invocation of the skill, not just its heaviest one. Every existing skill
carrying a wrap-up retro is a long-running loop, where a retrospective is
small next to the work it reflects on. Shape-matching without that check is
how you end up with a final step that runs routinely fail to execute — and a
step a run reports skipping is worse than no step, because it teaches the
reader that this skill's instructions are advisory.

How to phrase it depends on the skill's own shape — match what's already
established here, don't invent a new pattern:
- **A skill with numbered `Run`/`Procedure` steps** (the `my_loops` shape):
  add a final numbered step, "Wrap-up retro," right after whatever step
  reports back to the user — see `my_loops/rust-migration/SKILL.md` step 4
  or `yt_research_for_cc/yt-pipeline/SKILL.md` step 8 for the phrasing
  pattern. Ground it in *that skill's own* specific steps, not generic
  boilerplate — name what this particular skill's retro should actually
  check (which step's judgment call, which classification, which script).
- **A single-shot utility with no numbered steps** (the `yt-search` shape):
  add a short closing section, "## Wrap-up retro," after whatever the
  skill's last section already is.
- **A skill that is itself explicitly self-referential or meta** (like this
  one, or `skill-retro`): follow `skill-retro`'s own step 6 pattern —
  grounded in how *this run* of the tool went, guarded against firing
  twice on a direct self-invocation.
- **A skill with multiple modes of differing weight** — a quick consultation
  versus a full report-producing pass: scope the retro to the mode that
  produces a substantial artifact, and say so in the section heading and its
  first line, e.g. `## Wrap-up retro — audit mode only`. State plainly why the
  lighter mode is excluded, and offer the retro there as an explicit user
  request rather than an automatic step.
  This bullet exists because `dev_practices/unix-philosophy` was drafted
  against the three shapes above, none of which fit: it has a design mode that
  may be three paragraphs answering one question and an audit mode that emits a
  full report. Shape 2 was applied unconditionally, and **two independent
  design-mode eval runs reported *skipping* the retro** — correctly, since a
  retrospective on the skill's own instructions is disproportionate appended to
  a short chat answer, and it fires in contexts that can't support it (a
  read-only sandbox, no subagents). Fixed downstream in that skill's v1.1.0.

Always state explicitly that running/reporting the retro is automatic and
safe to run unattended, but *applying* anything `skill-retro` finds is a
separate, explicitly-approved follow-up — never bundle an applied fix into
the run that triggered the retro. And never add this step to a skill
that's vendored from elsewhere and not meant to be hand-edited (the
`notebooklm` exception, documented in `yt_research_for_cc/README.md`) —
check whether the target skill is actually authored in this repo before
adding anything to it.

### Skill Writing Guide

The full, current checklist — Anthropic's published authoring guidance with
this repo's additions — lives in
[`meta/learn-it/references/skill-authoring-conventions.md`](../learn-it/references/skill-authoring-conventions.md)
("Anthropic's authoring guidance, as applied here"). Read it before drafting;
what follows is the part worth having in front of you while writing.

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### Progressive Disclosure

Three loading levels: metadata (name + description, ~100 tokens, always in
context), the SKILL.md body (loaded on trigger, under 500 lines — enforced
here by `scripts/check_repo.py`), bundled resources (loaded or executed only
when needed). Push depth into `references/`, link each file directly from
SKILL.md with a line on *when* to read it, and keep references one level
deep — a reference that points at a further reference tends to get
`head -100`'d rather than read. Any reference over 100 lines gets a
`## Contents` list at the top so a partial read still shows its scope.

**Domain organization**: when a skill supports several domains or stacks,
one reference file per variant (one per cloud provider, one per framework)
so only the relevant one is read.

#### Frontmatter

`name`: ≤64 chars, lowercase/digits/hyphens, matches the directory, no
"anthropic"/"claude". `description`: third person, ≤1024 chars, says what the
skill does *and* when to use it, with the trigger phrases a user would
actually type. `compatibility` (≤500 chars): only when the skill has real
environment requirements — binaries, network, a product — and then name
them; most skills don't need it. Non-spec keys (`context`, `paths`,
`disable-model-invocation`, …) are Claude Code-only and fail a claude.ai
upload; this repo's `version` is the one deliberate extra.

#### Degrees of freedom

Match specificity to fragility. Heuristics and a goal where several
approaches are valid (a review, an analysis); a template or parameterized
script where a preferred pattern exists; an exact command with "don't add
flags" where the operation is fragile and sequence matters. Give one default
with an escape hatch rather than a menu of libraries.

#### Workflows and feedback loops

For multi-step work, give a copyable checklist and a verification step that
sends the reader *back* to an earlier step on failure — "validate; if it
fails, fix and validate again; only then proceed." For skills with scripts,
prefer a validator script over asking Claude to eyeball it, and make the
script solve the problem (helpful errors, justified constants) rather than
defer to Claude.

#### Principle of Lack of Surprise

Skills must not contain malware, exploit code, or anything that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests to create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities. "Roleplay as an XYZ" is fine.

#### Writing Patterns

Use the imperative. Say why a rule matters instead of ALL-CAPS musts — newer
models follow a reason better than an order, and over-prescription makes
them worse, not safer. Pick one term per concept and keep it. No
time-sensitive wording ("before August use the old API") — a "current
method / old patterns" split instead. Forward slashes in every path. MCP
tools by their fully qualified `Server:tool` name. Name a dependency's
install step rather than assuming it's present.

**Output formats**: give a template, strict ("use exactly this") or loose
("a sensible default; adapt") as the task needs. **Examples**: input/output
pairs beat descriptions for anything stylistic.

### Writing Style

Draft, then reread with fresh eyes and cut what isn't pulling weight. Keep
the skill general rather than fitted to the test prompts. Test with every
model it will run on — what Opus finds over-explained, Haiku may need.

### Test Cases

After writing the skill draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user: [you don't have to use this exact language] "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

Where the runs are backgroundable and cheap to redo, it is fine to launch them and present the prompts in the *same* turn rather than blocking on confirmation — say explicitly that you have done so, and that a changed prompt just means a rerun. Blocking a user on a confirm while nothing executes wastes their time for no gain. Do block when a run is expensive, slow, or has side effects outside the workspace.

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts. You'll draft assertions in the next step while the runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema (including the `assertions` field, which you'll add later).

## Running and evaluating test cases

Read [references/eval-workflow.md](references/eval-workflow.md) and follow it
as one continuous sequence: workspace layout, spawning with-skill and baseline
runs in the same turn, drafting assertions while they run, capturing timing
from each task notification, grading, aggregating, and launching the viewer.
Don't use `/skill-test` or any other testing skill in its place.

## Improving the skill

This is the heart of the loop. You've run the test cases, the user has reviewed the results, and now you need to make the skill better based on their feedback.

### How to think about improvements

1. **Generalize from the feedback.** The big picture thing that's happening here is that we're trying to create skills that can be used a million times (maybe literally, maybe even more who knows) across many different prompts. Here you and the user are iterating on only a few examples over and over again because it helps move faster. The user knows these examples in and out and it's quick for them to assess new outputs. But if the skill you and the user are codeveloping works only for those examples, it's useless. Rather than put in fiddly overfitty changes, or oppressively constrictive MUSTs, if there's some stubborn issue, you might try branching out and using different metaphors, or recommending different patterns of working. It's relatively cheap to try and maybe you'll land on something great.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Make sure to read the transcripts, not just the final outputs — if it looks like the skill is making the model waste a bunch of time doing things that are unproductive, you can try getting rid of the parts of the skill that are making it do that and seeing what happens.

3. **Explain the why.** Try hard to explain the **why** behind everything you're asking the model to do. Today's LLMs are *smart*. They have good theory of mind and when given a good harness can go beyond rote instructions and really make things happen. Even if the feedback from the user is terse or frustrated, try to actually understand the task and why the user is writing what they wrote, and what they actually wrote, and then transmit this understanding into the instructions. If you find yourself writing ALWAYS or NEVER in all caps, or using super rigid structures, that's a yellow flag — if possible, reframe and explain the reasoning so that the model understands why the thing you're asking for is important. That's a more humane, powerful, and effective approach.

4. **Look for repeated work across test cases.** Read the transcripts from the test runs and notice if the subagents all independently wrote similar helper scripts or took the same multi-step approach to something. If all 3 test cases resulted in the subagent writing a `create_docx.py` or a `build_chart.py`, that's a strong signal the skill should bundle that script. Write it once, put it in `scripts/`, and tell the skill to use it. This saves every future invocation from reinventing the wheel.

This task is pretty important (we are trying to create billions a year in economic value here!) and your thinking time is not the blocker; take your time and really mull things over. I'd suggest writing a draft revision and then looking at it anew and making improvements. Really do your best to get into the head of the user and understand what they want and need.

### The iteration loop

After improving the skill:

1. Apply your improvements to the skill
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs. If you're creating a new skill, the baseline is always `without_skill` (no skill) — that stays the same across iterations. If you're improving an existing skill, use your judgment on what makes sense as the baseline: the original version the user came in with, or the previous iteration.
3. Launch the reviewer with `--previous-workspace` pointing at the previous iteration
4. Wait for the user to review and tell you they're done
5. Read the new feedback, improve again, repeat

Keep going until:
- The user says they're happy
- The feedback is all empty (everything looks good)
- You're not making meaningful progress

---

## Advanced: Blind comparison

For situations where you want a more rigorous comparison between two versions of a skill (e.g., the user asks "is the new version actually better?"), there's a blind comparison system. Read `agents/comparator.md` and `agents/analyzer.md` for the details. The basic idea is: give two outputs to an independent agent without telling it which is which, and let it judge quality. Then analyze why the winner won.

This is optional, requires subagents, and most users won't need it. The human review loop is usually sufficient.

---

## Description Optimization

The description is what decides whether a skill triggers at all. After the
skill is otherwise done, offer to optimize it: build 20 realistic
should/should-not-trigger queries, review them with the user, run
`scripts/run_loop.py`, apply `best_description`. Full procedure, with the
query-writing guidance that makes or breaks it, in
[references/description-optimization.md](references/description-optimization.md).
Requires `claude -p` (Claude Code only).

---

## Package and Present (only if a file-delivery tool is available)

Check whether you have access to a tool that presents files to the user — `present_files`, or `SendUserFile` in Cowork remote. If you have neither, skip this step. If you do, package the skill and send the user the resulting `.skill` file with that tool:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

The presented `.skill` (or bare `SKILL.md`) file card shows a **Save skill** button when the user's org allows skill creation; clicking it installs the skill into their profile.

---

## Wrap-up retro

Once the target skill is drafted/improved and (if applicable) packaged —
this is `my-skill-creator`'s own version of "Retro by default," applied to
itself rather than to the skill it just worked on — run a
`meta/skill-retro` pass on `my-skill-creator` itself, grounded in this
run: did the interview in "Capture Intent"/"Interview and Research"
actually surface what the draft needed, did "This repo's own conventions"
cover what this particular skill's placement/versioning needed, did
"Retro by default" produce the right shape of wrap-up step for this
skill, did the eval/iteration loop run cleanly against this repo's own
constraints (no subagents on Claude.ai, no display in Cowork, etc.)? This
follows `skill-retro`'s own step 6 pattern: guarded so a direct
self-retro invocation of `my-skill-creator` doesn't fire this a second
time, and read-only — applying anything found is a separate,
explicitly-approved follow-up through this repo's normal PR workflow, not
part of the run that just finished.

Skip this step entirely when the target skill was explicitly for use
*outside* `skill_pack` (see "This repo's own conventions") — there's
nothing about skill_pack's own conventions to retro against on a run that
never touched them.

---

## Running somewhere other than Claude Code

Claude.ai has no subagents and no display; Cowork has subagents but no
display. Both change the mechanics (serial runs, `--static` viewer, skipped
benchmarks and description optimization) but not the loop. Read
[references/environment-notes.md](references/environment-notes.md) when you
are in either, including its guidance for *updating* an existing skill.

## Reference files

The agents/ directory contains instructions for specialized subagents. Read them when you need to spawn the relevant subagent.

- `agents/grader.md` — How to evaluate assertions against outputs
- `agents/comparator.md` — How to do blind A/B comparison between two outputs
- `agents/analyzer.md` — How to analyze why one version beat another

The references/ directory has additional documentation:
- `references/eval-workflow.md` — the test-run sequence: workspace layout, spawning runs, assertions, timing, grading, viewer
- `references/description-optimization.md` — trigger-query design and the `run_loop.py` procedure
- `references/environment-notes.md` — claude.ai and Cowork adaptations, updating an installed skill
- `references/schemas.md` — JSON structures for evals.json, grading.json, etc.

## Dependencies

Everything under `scripts/` is Python-standard-library only, with one
exception: `scripts/quick_validate.py` imports **PyYAML** (`import yaml`, an
unguarded top-level import) to parse `SKILL.md` frontmatter. Without it that
one script raises `ModuleNotFoundError`; the rest of the skill is unaffected.

`pip install pyyaml` if validation fails on import.

Across all 17 tracked `.py` files in this repo, `yaml` is the only
third-party module that gets *imported*. External **binaries** are a separate
question and several skills need one: `gh` and `git` throughout, `jq` for the
`my_loops` issue-picking scripts, `ripgrep` optionally for their repo scans,
and `yt-dlp` for `yt_research_for_cc`.

---

Repeating one more time the core loop here for emphasis:

- Figure out what the skill is about
- Draft or edit the skill
- Run claude-with-access-to-the-skill on test prompts
- With the user, evaluate the outputs:
  - Create benchmark.json and run `eval-viewer/generate_review.py` to help the user review them
  - Run quantitative evals
- Repeat until you and the user are satisfied
- If the skill lands in `skill_pack`: apply "This repo's own conventions"
  (version, RELEASE_NOTES.md, category folder) and build in a "Retro by
  default" wrap-up-retro step as part of the draft, not after
- Package the final skill and return it to the user
- Run `my-skill-creator`'s own "Wrap-up retro" against this run

Please add steps to your TodoList, if you have such a thing, to make sure you don't forget. If you're in Cowork, please specifically put "Create evals JSON and run `eval-viewer/generate_review.py` so human can review test cases" in your TodoList to make sure it happens.

Good luck!
