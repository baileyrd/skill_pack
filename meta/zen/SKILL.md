---
name: zen
description: >-
  Regular clean-up of a Claude setup: scans skills, agents, plugins, hooks,
  settings, CLAUDE.md, memory, connectors, scheduled jobs, chats and
  artifacts for what is broken, unused, duplicated or out of date, builds one
  review page where the owner rules on each item, then applies only approved
  items, reversibly where the platform allows. Use for "/zen", "tidy my
  setup", "declutter my Claude", "my setup is bloated", "clean up my skills /
  connectors / scheduled tasks / chats / artifacts", "which skills do I never
  use", "which connectors are broken", "why does every chat start so heavy",
  or the fortnightly tidy. Not for a token-cost audit of one project's
  context and CLAUDE.md rules (context-audit), things that are down right now,
  or a security review.
compatibility: Claude Code (desktop Code tab, terminal or IDE) on macOS, Windows or Linux. Requires python3, standard library only; the review page needs the Artifact tool.
metadata:
  version: "1.0.0"
---

# Zen

A setup collects skills, connectors, scheduled jobs, hooks, rules, chats and pages faster than
anyone prunes them, and much of it loads into every session. Zen finds what is broken, unused,
duplicated or out of date, puts it on one review page where the owner rules on each item, and
applies only what they approved, reversibly where the platform allows.

**The script counts; you judge; the owner decides.** The scan costs no tokens and the page
builds itself. Your job is the judgement the script can't make.

## What it can reach

Run it from **Claude Code**: the desktop app's Code tab, the terminal or an IDE.

| Thing | Sees it | Can change it |
|---|---|---|
| Skills, agents, plugins, hooks, settings, CLAUDE.md, memory, context files | yes | yes |
| Connectors | yes, every tab | Code tab: switch per session; removal is on claude.ai |
| Code-tab chats and sidebar groups | yes | only in the desktop Code tab (its `ccd_*` tools) |
| Cowork chats, projects, scheduled tasks, skills, plugins | yes, from Cowork's files on this computer | **no**: the owner clicks; give the path |
| Artifacts | yes, with the Artifact tool | delete only (there is no archive) |
| claude.ai chats, Projects, account memory | no | no: point to the web app |

Inside Cowork the scan sees much less (each session has its own sandboxed `.claude`), so
recommend the Code tab.

It runs on macOS, Windows and Linux. Scheduled jobs come from LaunchAgents on a Mac, Task
Scheduler on Windows, and systemd and cron on Linux. The commands below say `python3`; on
Windows use `python` or `py` if `python3` isn't found.

Scripts run through `python3`; to run one directly, `chmod +x scripts/*.py` first (the skill sync drops the executable bit).

## Rules

- **Nothing changes before the owner rules on it.** "Clean it up" means scan and show them.
- **Read the rulings back before the first change**, and apply only items ruled do, archive or
  delete. A keep is a keep, even when you'd still change it.
- **Archive, don't delete.** Artifacts have no archive, so delete only rows ruled delete.
  Session history and Cowork project archives can't be undone; say so on the row.
- **"No recorded run" is not "dead".** Check callers (an agent named in CLAUDE.md is on call by
  design), packaging and seasonality before suggesting removal.
- **Never show connector URLs.** Some carry API keys.
- **Don't edit the Claude app's own files** (`~/Library/Application Support/Claude` on a Mac;
  `%APPDATA%\Claude` or `%LOCALAPPDATA%\Packages\Claude_*\LocalCache\Roaming\Claude` on Windows).
- **Restructuring is a plan, not a tidy.** Merges and rewrites get a diff and their own decision.

## Steps

1. **Scan.** `python3 <this skill's folder>/scripts/zen_scan.py --project-dir <workspace>`. It
   takes one to two minutes; run it plainly, with no `timeout` wrapper. With `quick`, add the
   script's `--quick`. Other flags: `--days N`, `--context-dir <dir>`, `--skip-mcp` if connector
   checks hang. If `not_checked` says the Claude app's folder isn't where it usually is and the
   owner uses the desktop app, tell them and ask whether to search their user folder for it (up
   to a minute and a half); on a yes, run the scan again with `--find-app`. Read `summary.json`, `report.md`, and the last line of `history.jsonl` to say
   what changed since the previous run. The run folder holds:

   | File | Shape |
   |---|---|
   | `findings.json` | list of {id, area, kind, item, evidence, action, risk, reversible, undo} |
   | `interface.json` | list of desktop chats: {id, surface, title, last, idle_days, folder, turns, archived, scheduled, one_off, stray_folder, idle} |
   | `corrections.jsonl` | one JSON per line: {type: "correction", when, project, text} or {type: "fired_on", skill, when, asked} |
   | `facts.jsonl` | one JSON per line: {topic, file, line, text} |
   | `context_inventory.json` | {coverage, folders, files} |
   | `artifacts.txt`, `review.json` | yours to write (step 2 to 4); `review.html` is built from them |
2. **Declutter pass, every run.**
   - Artifacts: if the Artifact tool exists, `list` (scope mine, limit 200) and save its text to
     `<run>/artifacts.txt`. The page groups it.
   - Chats: `interface.json` already holds every desktop chat with its id and the archive picks.
     In the Code tab, also read `ccd_sidebar list_sections` and `ccd_session_mgmt list_sessions`
     for pins and existing groups. For the chats worth keeping, suggest 3 to 6 sidebar groups by
     topic and put them in `review.json` (`sidebar_groups`, `chat_groups`).
   - Cowork chats and projects come from the scan; they show on the page as the owner's to do.
3. **Judgement pass (skip with `quick`).** Each result that needs a ruling goes into
   `review.json` → `added`, with a `Z-` id; checks that found nothing go in the chat summary. Spot-check three of them against the raw files first; drop any you can't back.
   - Context layer: [references/context-layer.md](references/context-layer.md): folders first,
     then signals, then the contradiction check on `facts.jsonl`.
   - Misfiring skills (`fired_on` in `corrections.jsonl`) and rules the owner has since
     contradicted (`correction` lines against CLAUDE.md, rules and the memory index), quoting
     both sides with dates.
   - Overlap pairs: say which skill owns the job.
   - Cloud routines with `RemoteTrigger` if available. Exact numbers, optionally:
     `perl -e 'alarm 300; exec @ARGV' claude -p "/context"` from the workspace (on Windows,
     `claude -p "/context"` with the shell tool's timeout set to five minutes).
4. **Questions.** At most four, in `review.json` → `questions`: which skills ship to members or
   clients, which uploads exist for the claude.ai app, which duplicate connector stays.
5. **Build and publish the review page.** `python3 <skill>/scripts/build_page.py --run <run>
   --artifacts <run>/artifacts.txt [--review <run>/review.json]`, then publish the printed file
   with the Artifact tool, `capabilities: {"db": {}}`, `icon: checklist`, and open it. Rewrite
   section wording in `review.json` only when the automatic grouping reads badly. Details:
   [references/review-page.md](references/review-page.md). Each run gets its own page; earlier
   review pages show under Declutter as superseded. In chat, give the three headline numbers and
   the link. Without the Artifact tool, present `report.md`'s sections in chat.
6. **Apply when the owner says so** ("apply my zen rulings"), following
   [references/actions.md](references/actions.md): rulings first, one change at a time, the
   helper for anything it covers so `zen_apply.py --run <run> undo` reverses it.
7. **Show the results on the same page.** Record each result in the page's `applied`
   collection, re-scan, write `results.json`, rebuild with `--results` to the same file and
   republish so the link stays. Lead with before and after: tokens before the first message,
   broken items, chats and pages cleared. List what's left for the owner (Cowork, claude.ai).
8. **Offer the rhythm.** A scan every two weeks as a desktop scheduled task that builds the page
   and waits for rulings, never one that applies changes on its own.
9. **Wrap-up retro.** Once results are on the page (or the owner stops after the review), run a
   `meta/skill-retro` pass on this skill grounded in the run: findings the owner ruled keep
   that the scan flagged (false positives), judgement-pass items you dropped on spot-check,
   apply steps `zen_apply.py` didn't cover. Skip it on an unattended scheduled scan. Reporting
   is automatic; applying a finding is a separate, approved change.

## Built-in checks worth pointing to

`/doctor` (setup checkup), `/doctor prompt-audit` (conflicting or outdated instructions),
`/skill-doctor` (per-skill cost and use), `/usage` (what uses the plan), `/context` (exactly
what loaded). Use them to confirm numbers, not to replace the owner's decisions.

## Common mistakes

| Mistake | Instead |
|---|---|
| Applying from your suggestions, then reverting what the owner kept | Read the rulings first |
| Writing results into the owner's `rulings` | Use the `applied` collection |
| Archiving Cowork chats from the Code tab | They're click-only; list them with the path |
| Guessing a connector's name for the desktop toggle | Read `session_connectors_status` first |
| Building the review page by hand | `build_page.py`; it's the same page every time |
| Archiving a quiet agent that CLAUDE.md names | It's on call; keep it |
| Deleting chats to declutter | Archive them; history feeds usage reports |
| Quoting the token estimate as exact | Say "about"; `/context` has the exact figure |
