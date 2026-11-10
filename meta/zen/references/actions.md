# Applying approved items

**Read the rulings first.** Before the first change, read every ruling back from the page
(ArtifactData `list`, collection `rulings`) or from the chat. Apply only `do`, `archive` and
`delete` rulings. A `keep` means leave it, even when you still think the change is right. Follow
each ruling's note; a note can change what the owner wants.

Apply one item at a time, in the order the review lists them. Stop at the first failure and say
what failed and what is left. `<helper>` is
`python3 <this skill's folder>/scripts/zen_apply.py --run <run> --project-dir <workspace>`.

## What reaches what

The desktop app's own tools exist only when the skill runs in its **Code tab**, and they reach
**Code-tab sessions only**. Cowork chats, Cowork projects and Cowork scheduled tasks can't be
changed from here: `archive_session` answers "not found" for a Cowork chat, and the scheduled-tasks
tool doesn't list Cowork tasks. Those rows are the owner's to click; give the click path and
move on. Grouping Cowork chats means moving them into a Cowork project, also done in Cowork.

## Actions

| Approved item | How | Undo |
|---|---|---|
| Skill you own: name only, slash-only, hidden | `<helper> override <skill> name-only` / `user-invocable-only` / `off` | `undo` |
| Skill, agent, plist, scratch or context folder | `<helper> archive <path>`; follow the workspace's archive convention with `--archive-root` (check `archive/README.md`) | `undo` |
| Scheduled job: pause (Mac launch agent, Windows Task Scheduler task) | `<helper> pause-job <label or task name>` | `undo` |
| Settings or instruction file: edit | `<helper> backup <file>` first, then edit it, showing the diff | `undo` restores the copy |
| Plugin off on this machine | `<helper> plugin-off <name>@<marketplace>`; account plugins are `<name>@synced` | `undo` |
| Plugin installed twice | `claude plugin uninstall <key> --scope project` (or the scope to drop) | reinstall |
| Local server in `.mcp.json` | `<helper> mcp-off <name>` | `undo` |
| claude.ai connector unused here | Code tab: `ccd_connectors session_connectors_status` first for the exact names, then `set_session_connector_enabled` with that name. It also turns the connector off by default for new sessions; say so. Otherwise `/mcp disable <name>` | switch it back on |
| Connector broken | the owner reconnects it with `/mcp` | n/a |
| Connector removed for good | claude.ai › Customize › Connectors | re-add |
| Code-tab chat: archive | `ccd_session_mgmt archive_session` with the `local_…` id from `interface.json` | unarchive in the app |
| Code-tab chats: group | `ccd_sidebar create_group` with the name, then `move_sessions` with its `group_id` and the session ids (`self` is the current chat) | move back |
| Pin or unpin | `ccd_sidebar set_pinned`; artifacts: Artifact `pin` / `unpin` | flip back |
| Artifact delete | Artifact `delete`, only for rows ruled delete; check design systems and decks by reading them first | **none** |
| Cowork chat, project or task | the owner, in Cowork. Archiving a Cowork project deletes its instructions, links and memory | **project: none** |
| Desktop Code-tab scheduled task | `scheduled-tasks update_scheduled_task` | edit back |
| Cloud routine | `RemoteTrigger`, or the owner uses `/schedule` | edit back |
| Mod off | set `"<name>": false` in `~/.claude/mods/switches.json` (after `<helper> backup`) | set true |
| Merge, rewrite, stacked versions, contradictions | a planned change with the diff, not part of the tidy | n/a |
| Session history retention | `cleanupPeriodDays`, only after an explicit yes to losing old sessions | **none** |

## Before archiving

- Read the callers the report lists. A skill another skill calls by path breaks silently; an
  agent named in CLAUDE.md is on call by design.
- Ask whether it ships somewhere: a plugin build, a member package, a client folder.
- Seasonal work (monthly, quarterly, yearly) looks unused in 30 days. Ask.

## After applying

1. Record each result in the page's **`applied`** collection (one document per ruling id:
   `done`, `skipped` or `failed`, a short note, the time). Never write over `rulings`; those are
   the owner's.
2. Re-run the scan with the same `--days`, quick is fine.
3. Write `results.json` (shape in review-page.md), rebuild the page with
   `build_page.py --run <first run> --results results.json --out <same page file>` and publish
   it to the same file path so the link stays. Give the owner three numbers before and after
   (tokens before the first message, broken items, chats and pages cleared), what's left for
   them, and anything you undid because a ruling said keep.
4. Tell them `<helper> undo` reverses everything the helper did, and which changes it doesn't
   cover (artifact deletes, app actions).
