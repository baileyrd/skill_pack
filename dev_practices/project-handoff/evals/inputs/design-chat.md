# Design chat transcript (2026-11-01)

Nano: I want a small tool that posts a morning digest of my rusty_tick tasks into my Hermes Discord channel. Due today, overdue, and anything tagged "focus".
Claude: A few shapes: (a) a Hermes skill that queries Tick on a schedule, (b) a standalone Rust CLI run by cron/systemd timer that hits Tick's API and posts to a Discord webhook. (b) keeps it decoupled from Hermes.
Nano: (b). Rust, single binary. It runs on the Fedora home server.
Claude: For Tick access, the MCP server or the HTTP API?
Nano: HTTP API, it's on localhost:7420. No auth on localhost.
Claude: Format suggestion: three sections, max 10 items each, with "+N more" overflow.
Nano: Sounds good.
Claude: Should it skip posting when there's nothing due?
Nano: Yeah, no empty posts.
Claude: Timezone — server is UTC?
Nano: Server is UTC but I'm in Central. Digest at 6:30 Central.
Claude: Webhook URL from an env var, DIGEST_WEBHOOK_URL?
Nano: Fine. Never commit it.
Nano: Later maybe weekends off, not sure yet.
Nano: Ok write me a prompt to stand this up in Claude Code. Repo will be baileyrd/tick_digest, doesn't exist yet.
