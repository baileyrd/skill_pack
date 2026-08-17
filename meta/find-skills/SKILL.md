---
name: find-skills
description: >-
  Discovers and installs agent skills from the open ecosystem (skills.sh, `npx skills`) when the
  user is looking for functionality that might already exist as an installable skill. Use whenever
  the user asks "find a skill for X", "is there a skill that can…", "can you do X" about a
  specialized capability, wishes they had help with a domain (design, testing, deployment), or
  asks "how do I do X" where X is a common enough task that someone has likely packaged it.
  Checks the leaderboard first, searches the CLI second, and verifies install count and source
  reputation before recommending anything — a search hit is a candidate, not an endorsement.
  Distinct from this repo's own authoring skills: `my-skill-creator` writes a skill, `learn-it`
  distills one from a session, and this one finds a skill someone else already wrote.
version: 1.0.0
---

# Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

Imported into `skill_pack` and maintained here from now on — same posture as
`web_dev/datastar-pro`. It is this repo's own versioned copy, not a live sync
of an upstream source, so edit it here freely. Changes made on import are
listed in `RELEASE_NOTES.md`.

## When to Use This Skill

Use this skill when the user:

- Asks "how do I do X" where X might be a common task with an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Asks "can you do X" where X is a specialized capability
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows
- Mentions they wish they had help with a specific domain (design, testing, deployment, etc.)

## What is the Skills CLI?

The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools.

**Key commands:**

- `npx skills find [query]` - Search for skills interactively or by keyword
- `npx skills add <package>` - Install a skill from GitHub or other sources
- `npx skills check` - Check for skill updates
- `npx skills update` - Update all installed skills

**Browse skills at:** https://skills.sh/

## How to Help Users Find Skills

### Step 1: Understand What They Need

When a user asks for help with something, identify:

1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 2: Check the Leaderboard First

Before running a CLI search, check the [skills.sh leaderboard](https://skills.sh/) to see if a well-known skill already exists for the domain. The leaderboard ranks skills by total installs, surfacing the most popular and battle-tested options.

For example, top skills for web development include:
- `vercel-labs/agent-skills` — React, Next.js, web design (100K+ installs each)
- `anthropics/skills` — Frontend design, document processing (100K+ installs)

### Step 3: Search for Skills

If the leaderboard doesn't cover the user's need, run the find command:

```bash
npx skills find [query]
```

For example:

- User asks "how do I make my React app faster?" → `npx skills find react performance`
- User asks "can you help me with PR reviews?" → `npx skills find pr review`
- User asks "I need to create a changelog" → `npx skills find changelog`

### Step 4: Verify Quality Before Recommending

**Do not recommend a skill based solely on search results.** Always verify:

1. **Install count** — Prefer skills with 1K+ installs. Be cautious with anything under 100.
2. **Source reputation** — Official sources (`vercel-labs`, `anthropics`, `microsoft`) are more trustworthy than unknown authors.
3. **GitHub stars** — Check the source repository. A skill from a repo with <100 stars should be treated with skepticism.

### Step 5: Present Options to the User

When you find relevant skills, present them to the user with:

1. The skill name and what it does
2. The install count and source
3. The install command they can run
4. A link to learn more at skills.sh

Example response:

```
I found a skill that might help! The "react-best-practices" skill provides
React and Next.js performance optimization guidelines from Vercel Engineering.
(185K installs)

To install it:
npx skills add vercel-labs/agent-skills@react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### Step 6: Offer to Install

Installing a skill runs someone else's instructions in future sessions, at
user level, with whatever tools those sessions have. Treat it as installing a
dependency, not as a search result. **Get an explicit yes naming the skill
before running anything** — presenting options in step 5 is not consent.

```bash
npx skills add <owner/repo@skill> -g
```

`-g` installs globally (user-level), so it affects every future session, not
just this one.

**Do not add `-y`.** The upstream version of this skill did; it suppresses the
CLI's own confirmation prompt, which is the last checkpoint before third-party
instructions land in the user's environment. Skipping the prompt on the user's
behalf removes the one place they'd see what is actually being installed. If
they want it unattended they can say so and you can add the flag then.

After installing, say which skill landed and where, so it isn't a silent change
to how later sessions behave.

## Common Skill Categories

When searching, consider these common categories:

| Category        | Example Queries                          |
| --------------- | ---------------------------------------- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| Documentation   | docs, readme, changelog, api-docs        |
| Code Quality    | review, lint, refactor, best-practices   |
| Design          | ui, ux, design-system, accessibility     |
| Productivity    | workflow, automation, git                |

## Tips for Effective Searches

1. **Use specific keywords**: "react testing" is better than just "testing"
2. **Try alternative terms**: If "deploy" doesn't work, try "deployment" or "ci-cd"
3. **Check popular sources**: Many skills come from `vercel-labs/agent-skills` or `ComposioHQ/awesome-claude-skills`

## When No Skills Are Found

If no relevant skills exist:

1. Acknowledge that no existing skill was found
2. Offer to help with the task directly using your general capabilities
3. Suggest the user could create their own skill with `npx skills init`

Example:

```
I searched for skills related to "xyz" but didn't find any matches.
I can still help you with this task directly! Would you like me to proceed?

If this is something you do often, you could create your own skill:
npx skills init my-xyz-skill
```

For a skill that should live in **this** repo, `npx skills init` is the wrong
tool — use `meta/my-skill-creator`, which applies `skill_pack`'s own
conventions (versioning, `RELEASE_NOTES.md`, category placement). Reach for
`init` only when the skill is meant to be standalone.

## Limitations

- **Install counts and stars measure popularity, not quality or safety.** A
  skill with 100K installs is widely used; that is evidence it works for common
  cases, not that it is correct, current, or safe for yours. Step 4's bar filters
  out the obviously unvetted — it does not vet.
- **No skill content is read before recommending.** The checks are metadata
  only. A skill whose instructions are wrong, stale, or hostile passes every one
  of them if the numbers look good. Read the source for anything that will touch
  credentials, money, or a production system.
- **`npx skills` must be installed and reachable.** No network, no npm, no
  recommendations — say so rather than inventing skill names, which is the
  failure mode here: plausible `owner/repo@skill` strings are easy to generate
  and impossible for the user to distinguish from real ones until the install
  fails.
- **The leaderboard and CLI cover one ecosystem.** Skills distributed some other
  way — a repo, a zip, an internal registry — will not appear, so "no skill
  found" means "none in this index."
