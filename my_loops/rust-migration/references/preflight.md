# Tooling preflight, checks 2 onward

Read this in step 0, right after check 1 (restoring script permissions, which
stays in `SKILL.md`), and run every check here before reporting that the loop
has started.

2. `command -v gh`. If `gh` is absent — Claude Code on the web, a container
   without it installed — the three scripts that shell out to it **cannot
   run**. The GitHub MCP tools are the substitute: use them for step 2's issue
   filing, step 3's capability picking, and step 3's CI-wait-and-merge. Say so
   in the wrap-up report, so the run's mechanics are legible rather than
   looking like the scripts ran, and do **not** silently skip a step just
   because its script is unavailable.
   (`check_manifest_coverage.sh` doesn't touch `gh` and still works.)
3. One cheap read against the API (list issues, page size 1). A rate limit or
   an auth failure discovered here costs nothing; discovered mid-loop it
   strands work in flight. See "Stop conditions" for what to do when it fails
   later.
4. Note which CI-status mechanism the target uses. A repo whose CI reports via
   **Actions checks** returns `total_count: 0` from the commit-status
   endpoint — that is *not* evidence CI is missing, and reading it that way
   will make you think a green run never happened. Match a run to the PR by
   `head_sha`, never by branch: runs are associated to PRs by branch name, so
   a stale run from an earlier PR on a reused branch can appear attached to
   the current one and read as a pass for code it never ran against.
5. Note that **closing an issue** (`gh issue close` or the MCP `issue_write`
   update-state call) can hit the same rate limit as `search_issues`/`gh
   issue list --search`, even though closing isn't obviously a search —
   some tool implementations resolve the issue's ID via an internal
   search-based lookup first. If closes start failing with a rate-limit
   error while comments/reads on the same issues still succeed, treat it
   as the GitHub-API-rate-limited stop condition (the work itself is not
   failing, only the state transition) rather than assuming something
   broke — comment the outcome on each issue as a durable record and retry
   the close once the limit clears.
