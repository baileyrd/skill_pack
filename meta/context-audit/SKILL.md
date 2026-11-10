---
name: context-audit
description: >-
  Audits a Claude Code setup for token waste and context bloat and returns a
  0-100 health score with fixes ranked by impact. A script checks MCP servers,
  skills and their description budget, settings, effort level, LSP / code
  intelligence, hooks, compaction, subagents, status line and .claudeignore;
  Claude then tests every CLAUDE.md and rules-file line for defaults,
  contradictions, redundancy, bandaids and vagueness. Use when the user says
  "audit my context", "check my settings", "why is Claude so slow", "token
  optimization", "trim my CLAUDE.md", "context audit" or runs /context-audit.
  Not for pruning unused skills, connectors, chats or scheduled jobs across a
  whole setup (that is zen).
compatibility: Claude Code only (reads .claude/ and ~/.claude/). Requires python3, standard library only.
metadata:
  version: "1.0.0"
---

# Context Audit

Bloated context costs more and produces worse output. This skill finds
the waste and tells you what to cut. Based on Anthropic's official cost
management docs and real-world testing.

Most of the audit is deterministic — a Python script runs all the file
and config checks. Only CLAUDE.md rule analysis needs language judgment,
which you (Claude) handle directly.

Core principle: **the context window is the most important resource to
manage** (Anthropic docs). Context hygiene is an ongoing systems problem,
not a one-time tweak.

## Step 1: Run the Deterministic Checks

Run the audit script against the current project:

```bash
python3 <this skill's folder>/scripts/check_context.py --project-dir .
```

Scripts run through `python3`; to run one directly, `chmod +x scripts/*.py` first (the skill sync drops the executable bit).

The script returns JSON with:
- `score` — base score out of 100 (deterministic checks only)
- `checks` — per-category details (MCP, skills, settings, LSP, etc.)
- `findings` — flat list, pre-sorted by deduction severity

Parse the JSON. The script covers: MCP servers, skill metrics, effort
level, LSP stack (binary + plugin + enforcement hook), global settings,
.claudeignore, hook config, subagents, agent teams, and status line.

## Step 2: Get /context Baseline (Optional)

Ask the user to run `/context` and paste the output if they want exact
token counts. Without it, proceed with the script's config-based analysis
and note that numbers are estimated.

## Step 3: Analyze CLAUDE.md Rules

The script doesn't touch CLAUDE.md rules — that's a language task.
Read all CLAUDE.md files (project root, `.claude/CLAUDE.md`,
`~/.claude/CLAUDE.md`, any `CLAUDE.local.md`) and any `.claude/rules/*.md`.

Count total lines across all files. Test every rule against five filters:

| Filter | Flag when... |
|--------|-------------|
| Default | Claude already does this without being told ("write clean code", "handle errors") |
| Contradiction | Conflicts with another rule in same or different file |
| Redundancy | Repeats something already covered elsewhere |
| Bandaid | Added to fix one bad output, not improve outputs generally |
| Vague | Interpreted differently every time ("be natural", "use good tone") |

Add deductions to the score from Step 1:
- CLAUDE.md > 200 lines (no progressive disclosure): −10
- CLAUDE.md > 500 lines: −20
- Per 5 rules flagged by filters: −5
- Contradictions between files: −10
- No compaction instructions in CLAUDE.md (if > 100 lines): −5

If CLAUDE.md > 200 lines, check for progressive disclosure opportunities:
rules that only apply to specific tasks (API conventions, deployment,
testing) should move to skills or reference files with one-line pointers.

Check for compaction instructions. CLAUDE.md can include guidance like:
"When compacting, preserve the full list of modified files and test
commands." If missing and file is > 100 lines, recommend adding them.

## Step 4: Report

Combine the script's findings + CLAUDE.md deductions. Final score = base
score from script − CLAUDE.md deductions, floored at 0.

Score labels: 90-100 CLEAN, 70-89 NEEDS WORK, 50-69 BLOATED, 0-49 CRITICAL.
Severity: CRITICAL > 10pts, WARNING 5-10pts, INFO < 5pts.

Output format:

```
# Context Audit

Score: {N}/100 [{CLEAN|NEEDS WORK|BLOATED|CRITICAL}]

## Context Breakdown
{Token numbers from /context if available, otherwise:}
{From script: X local MCP servers, Y skills (description budget: N/8000),
CLAUDE.md: N lines, LSP state: {FULL|PARTIAL|NONE}}
Run `/context` for exact token counts.

## Issues Found (by impact)

### [{CRITICAL|WARNING|INFO}] {Category}
{What's wrong — plain English}
**Fix:** {One-line actionable fix}
**Saves:** {Estimated impact — high/medium/low}

### Rules to Cut (CLAUDE.md)
{Each flagged rule: the text, which filter, one-line reason}

### Conflicts
{Contradictions between files, with paths}

## Top 5 Fixes (ranked by token savings)
1. {Highest-impact fix}
2. {Second}
3. {Third}
4. {Fourth}
5. {Fifth}

## Systems Checklist
- [ ] Language server binary installed (pyright, tsserver, gopls, etc.)
- [ ] LSP plugin installed for your language
- [ ] PreToolUse hook enforces LSP over Grep
- [ ] Effort level configured for routine work
- [ ] .claudeignore covers build artifacts
- [ ] Preprocessing hooks for test/log output
- [ ] Status line showing context usage
- [ ] Compaction instructions in CLAUDE.md
- [ ] Subagent models set to haiku where appropriate
```

## Step 5: Offer to Fix

After the report:

"Want me to fix any of these? I can:
- Add missing settings (autocompact, bash output, effort level)
- Add .claudeignore with sane defaults for your project
- Add compaction instructions to your CLAUDE.md
- Show a cleaned-up CLAUDE.md with flagged rules removed
- Add preprocessing hooks for test/log output
- Add `disable-model-invocation: true` to archived/unused skills
- Configure subagent models
- Set up a status line for context monitoring
- Show which skills to split into reference files
- Walk you through LSP setup if flagged (server + plugin + enforcement hook)"

For LSP setup: install binary → install plugin → offer to add the hook
(use `/opt/homebrew/bin/node` in the hook command on macOS — VS Code's
Claude Code extension doesn't inherit Homebrew PATH). Remind user to
fully quit and relaunch the editor after wiring the hook.

Auto-apply settings.json, .claudeignore, and hook configs (safe,
reversible). Show diffs for CLAUDE.md and skills — let the user confirm
before modifying instruction files.

## Wrap-up retro

After the report (and any fixes) are delivered, run a `meta/skill-retro`
pass on this skill grounded in the run: did `check_context.py` miss or
misread anything you had to correct by hand, did the five CLAUDE.md filters
flag rules the user then kept, did the deductions produce a score the user
found believable? Reporting is automatic and safe to run unattended;
applying any finding is a separate, approved change.
