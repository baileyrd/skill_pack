---
name: my-skill-creator
description: >-
  Creates, edits, evals and tunes Agent Skills for the skill_pack repo:
  interview, draft SKILL.md, run test prompts with and without the skill,
  benchmark with variance analysis, iterate, optimize the description for
  triggering, package. Applies skill_pack's conventions (metadata.version,
  RELEASE_NOTES, category placement, repo checks) and wires a wrap-up retro
  to meta/skill-retro into every skill it drafts. Use when the user wants to
  create a skill, improve or restructure an existing one, run skill evals or
  benchmarks, or fix a skill that triggers too often or not at all. Prefer
  this over the generic skill-creator whenever the skill lives in, or is
  headed for, skill_pack.
metadata:
  version: "1.6.0"
---

# My Skill Creator

## Rules that hold for every skill you draft or edit here

These come first because Claude Code keeps only the start of a skill after
a conversation is compacted. The sections below explain each one.

- Frontmatter uses only the spec's six keys: `name`, `description`,
  `license`, `compatibility`, `metadata`, `allowed-tools`. Version goes in
  `metadata.version` as a quoted semver string; any other top-level key
  fails claude.ai upload. Claude Code-only keys are the exception, and only
  for skills that will never leave Claude Code (see "Frontmatter").
- `description`: third person, ≤1024 characters, the main use case in the
  first sentence, written as a `>-` block scalar.
- Body under 500 lines and 20,000 bytes (~5,000 tokens), both enforced by
  `check_repo.py`; must-survive rules at the top, depth in `references/`.
- Scripts run through their interpreter (`python3 scripts/x.py`), paths
  relative to the skill folder.
- Every authored skill gets `RELEASE_NOTES.md` and a wrap-up retro step
  ("Retro by default"); every change lands through a PR after
  `python3 scripts/check_repo.py` passes.
- Evals before polish: a no-skill baseline, then at least three realistic
  prompts.

This is skill_pack's fork of Anthropic's `skill-creator`: upstream's process,
plus the repo conventions and the retro step.

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


## Communicating with the user

Users range from first-time terminal users to engineers. Match their
vocabulary: "evaluation" and "benchmark" are usually fine; explain "JSON" or
"assertion" in a few words unless the user has shown they know them.

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
- **description**: What the skill does and when to use it. This is the primary triggering mechanism, so all "when to use" information goes here, not in the body. Lead with the main use case: Claude Code truncates long descriptions in its skill listing and drops some entirely when many skills are installed. Include the words users actually type, including casual phrasings and the adjacent requests that should still trigger it. Don't pad it to force triggering; measure instead, with a should-trigger and should-not-trigger set ("Description Optimization"). A task skill that fires when it shouldn't (deploy, commit) is better served by `disable-model-invocation: true` than by a vaguer description.
- **compatibility**: real environment requirements only — binaries, network access, intended product (≤500 chars, optional; most skills don't need it)
- **the rest of the skill :)**

### This repo's own conventions

When the skill will live in `skill_pack`, read
[`references/repo-conventions.md`](references/repo-conventions.md) before
writing files. It covers `metadata.version` and how to bump it, the
1024-character description ceiling and why the description is a `>-` block
scalar, `RELEASE_NOTES.md`, which category folder to use, the README and
CHANGELOG updates, the executable-bit rules for scripts, and landing the change
through a PR. Skip it only for a skill explicitly meant for use outside this
repo.

### Retro by default

Every skill this tool drafts, or substantively improves, gets a wrap-up-retro
step wired to `meta/skill-retro` in the same change, not as a follow-up. The
step's shape depends on the skill (numbered procedure, single-shot utility,
meta skill, or multi-mode), and a light mode may need it excluded. Read
[`references/retro-by-default.md`](references/retro-by-default.md) before
adding one. Running the retro is automatic; applying what it finds always
needs separate approval. Never add it to a vendored skill.

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
them; most skills don't need it. `metadata` is a string-to-string map; this
repo keeps `version` there. Nothing else goes at the top level of a skill
meant to be portable.

Claude Code-only keys (`when_to_use`, `disable-model-invocation`,
`context: fork`, `hooks`, `paths`, …) block a claude.ai upload. When a skill
will only ever run in Claude Code and one of them would help, read
[`references/claude-code-options.md`](references/claude-code-options.md).

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

After writing the skill draft, come up with at least three realistic test prompts — the kind of thing a real user would actually say. Share them with the user: [you don't have to use this exact language] "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

Where the runs are backgroundable and cheap to redo, it is fine to launch them and present the prompts in the *same* turn rather than blocking on confirmation — say explicitly that you have done so, and that a changed prompt just means a rerun. Blocking a user on a confirm while nothing executes wastes their time for no gain. Do block when a run is expensive, slow, or has side effects outside the workspace.

Save test cases to `evals/evals.json` (`skill_name`, then `evals[]` of `id`,
`prompt`, `expected_output`, `files`; full schema in `references/schemas.md`).
Don't write assertions yet; draft them while the runs are in progress.

## Running and evaluating test cases

Read [references/eval-workflow.md](references/eval-workflow.md) and follow it
as one continuous sequence: workspace layout, spawning with-skill and baseline
runs in the same turn, drafting assertions while they run, capturing timing
from each task notification, grading, aggregating, and launching the viewer.
Don't use `/skill-test` or any other testing skill in its place.

## Improving the skill

This is the heart of the loop. You've run the test cases, the user has reviewed the results, and now you need to make the skill better based on their feedback.

### How to think about improvements

1. **Generalize from the feedback.** The skill will run on far more prompts
   than the few you are iterating on. Prefer a different metaphor or working
   pattern over fiddly, overfit fixes or rigid MUSTs.
2. **Keep the prompt lean.** Read the transcripts, not only the outputs, and
   cut instructions that make the model waste time.
3. **Explain the why.** A reason generalizes better than ALWAYS/NEVER in
   capitals; treat capitals as a yellow flag and reframe.
4. **Bundle repeated work.** If every test run wrote the same helper script,
   put it in `scripts/` and tell the skill to use it.

Draft a revision, then reread it fresh before running the next iteration.

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
- `references/retro-by-default.md` — which wrap-up-retro shape to add, and when to exclude it
- `references/repo-conventions.md` — skill_pack's file, versioning, placement and PR rules
- `references/claude-code-options.md` — Claude Code-only frontmatter, substitutions, and runtime behavior
- `references/schemas.md` — JSON structures for evals.json, grading.json, etc.

## Dependencies

Everything under `scripts/` is Python standard library except
`scripts/quick_validate.py`, which imports PyYAML to parse frontmatter.
`pip install pyyaml` if it fails on import. Invoke scripts through `python3`;
the sync drops the executable bit (`chmod +x scripts/*.py 2>/dev/null || true`
restores it).

---

The core loop, once more: capture intent; draft or edit; run test prompts with
and without the skill; review with the user in `eval-viewer/generate_review.py`
plus quantitative evals; iterate; for `skill_pack`, apply the repo conventions
and the retro step in the draft itself; package; run this skill's own wrap-up
retro. Put these steps on your todo list if you keep one. In Cowork, add
"Create evals JSON and run `eval-viewer/generate_review.py` so human can review
test cases" explicitly.
