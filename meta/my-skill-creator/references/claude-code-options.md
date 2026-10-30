# Claude Code-only skill options

Read this when a skill will only ever run in Claude Code and its behavior
would benefit from a feature the Agent Skills spec doesn't have. Every key
below makes the skill fail a claude.ai upload, the Skills API and
`package_skill.py`, so `quick_validate.py` (run on every skill by this repo's
tests) rejects them. Using one here means deciding that the skill is Claude
Code-only and changing that validator's allowlist in the same PR.

Source: [Claude Code skills docs](https://code.claude.com/docs/en/skills).

## Frontmatter keys

| Key | Effect | Use it when |
| --- | --- | --- |
| `when_to_use` | Extra trigger text appended to `description`; the two share a 1,536-character listing cap | The description is crowded and trigger phrasings would push the use case out of the first sentence |
| `disable-model-invocation: true` | Only `/name` invokes it; its description leaves the listing | A task with side effects (deploy, commit, publish) that must not fire on its own |
| `user-invocable: false` | Hidden from the `/` menu; only Claude invokes it | Background knowledge a user would never call directly |
| `context: fork` + `agent` | Runs in a subagent (`Explore`, `Plan`, `general-purpose`, or a custom one) | A self-contained task whose working context shouldn't fill the main conversation; never for guideline-only skills |
| `paths` | Globs limiting automatic activation to matching files | A skill that only applies to one part of a repo |
| `hooks` | Hooks registered while the skill is active, for the rest of the session | A rule that must hold every time, not only when Claude remembers it |
| `allowed-tools` / `disallowed-tools` | Pre-approve or remove tools for the invoking turn | Fewer permission prompts for the skill's own scripts; `allowed-tools` is also in the spec, marked experimental |
| `model`, `effort` | Override model or effort for the turn | Rarely; prefer the session's settings |
| `arguments`, `argument-hint` | Named positional arguments (`$name`) and autocomplete hint | A slash-command style skill with inputs |

## Substitutions and injected context

- `$ARGUMENTS`, `$0`, `$1`, `$name`: arguments as typed.
- `${CLAUDE_SKILL_DIR}`: the directory holding `SKILL.md`, wherever the skill is
  installed (personal, project, plugin, synced). Claude Code expands it before
  Claude reads the skill; other clients leave it literal, so a portable skill
  should say paths are relative to the skill folder and may add
  `${CLAUDE_SKILL_DIR}` as the Claude Code form, not rely on it alone.
- `` !`cmd` `` and fenced ```` ```! ```` blocks run before the skill is sent and
  are replaced by their output. A non-zero exit aborts the invocation; append
  `|| true` where failure is acceptable.

## Runtime behavior worth writing for

- The skill is added to the conversation once and not re-read. Phrase standing
  rules for the whole task ("run the tests after every edit").
- After compaction only the first 5,000 tokens of each invoked skill are
  re-attached (25,000 shared across skills). Put the rules that must survive at
  the top.
- The skill listing is budgeted at about 1% of the context window. With many
  skills installed some descriptions are dropped, so lead with the main use
  case.
