# The review page

`scripts/build_page.py` builds it from the run folder and `assets/review.html`. Don't write the
page by hand: the template already has the ruling controls, batches, the sidebar-group picker,
the "hide titles" switch for screen recording and the saved-rulings store.

```
python3 <skill>/scripts/build_page.py --run <run> [--artifacts <run>/artifacts.txt] [--review <run>/review.json]
```

Publish the file it prints with the Artifact tool: `capabilities: {"db": {}}`, `icon: checklist`.
Check it by opening the published page; a local preview can't run it.

## What builds itself

- Headline numbers and the token bar, from `summary.json`.
- Sections in this order: Broken, Risky, Declutter, What loads every chat, Context layer,
  Everything else. Findings are grouped by type; each group has a suggestion and its members.
- Declutter rows from `interface.json` (Code-tab chats, with archive picks; Cowork chats, marked
  "you do this in the app") and from the Cowork project findings.
- Artifact rows, when you pass `--artifacts`: save the text of an Artifact `list` call (scope
  mine, limit 200) to `<run>/artifacts.txt`. Repeated titles keep the newest, untitled pages older
  than 14 days are set to delete, pages not updated in 60+ days are set to keep.

## review.json (your judgement, all optional)

```json
{
  "sections": [{"key": "broken", "nav": "Broken", "title": "Broken", "tone": "var(--crit)",
                "lede": "These fail today.", "items": [
      {"id": "G-hooks", "title": "Three hooks stop working outside the project folder", "sugg": "do",
       "body": "Plain words, with <code>names</code> where useful.",
       "members": ["T-218", "T-219"], "memberSugg": {"T-219": "ask"}},
      {"id": "G-dupes", "title": "...", "sugg": "do", "members": {"area": "skills", "kind": ["duplicate"]}}]}],
  "added": [{"id": "Z-01", "area": "context", "kind": "contradiction", "item": "my-business.md vs CONTRACT.md",
             "evidence": "Quote A (date) / quote B (date)", "action": "Keep B", "risk": "med"}],
  "questions": [{"id": "Q-1", "q": "Which ElevenLabs connector is the one to keep?", "opts": ["The original", "ElevenLabs (2)"]}],
  "sidebar_groups": ["AIOS builds", "Videos", "Research"],
  "chat_groups": {"local_<id>": "Videos"}
}
```

- Give `sections` to replace the automatic grouping with better wording; keep the six keys and
  their order, and keep a section even when it's empty.
- `added` is for findings from your judgement pass (contradictions, misfires, outdated rules);
  give them `Z-` ids.
- At most four questions.
- `chat_groups` suggests a sidebar group for each chat the owner keeps.

## Rulings

Each row saves to the `rulings` collection: `decision` (keep, do, change, ask, archive, delete),
`note`, `sidebarGroup`. Saving doesn't apply anything; the owner says "apply my zen rulings" in
chat. Then follow references/actions.md: read the rulings back first, record results in
`applied`, never over `rulings`.

## results.json (after applying)

```json
{"when": "applied 6 Nov, 13:10", "lede": "What changed, checked against your rulings.",
 "before_after": [["Tokens before your first message", "~42,000", "~30,000"], ["Broken", "16", "6"]],
 "fine": "How the after figure was measured.",
 "done": ["<b>Hooks fixed.</b> ..."], "left": ["<b>Cowork:</b> archive the 48 chats ..."],
 "undone": ["<b>my-business.md</b> reverted: you ruled Keep."]}
```
