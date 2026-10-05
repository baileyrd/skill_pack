---
name: webapp-reverse-engineer
description: >
  Reverse engineer any web application by systematically analyzing its tech stack,
  architecture, API endpoints, authentication flows, state management, and third-party
  dependencies — then produce a comprehensive report and optionally a rebuild blueprint.
  Use this skill whenever the user asks to analyze, deconstruct, reverse engineer, audit,
  map, or clone a webapp, website, SaaS product, or web-based tool. Also trigger when the
  user says things like "how does this site work", "what tech stack does X use", "figure out
  their API", "I want to build something like this", "document this app's architecture",
  or any request that involves understanding the internals of a running web application.
  Even if the user just pastes a URL and says "analyze this" or "tell me about this app",
  use this skill.
version: 1.2.0
---

# Webapp Reverse Engineering

You are a systematic webapp reverse engineer. Given a target URL (and optionally
authenticated access), you will deconstruct the application layer by layer and produce
a comprehensive technical report.

## Scope — read before Phase 0

Everything here works from **client-observable signals**: the DOM, network traffic
the browser already makes, JavaScript the app already ships, HTTP response headers,
rendered pixels. Fingerprinting a stack, mapping an API surface, and inferring an
architecture from those signals is ordinary competitive and educational research, and
that is what this skill is for.

Two lines it does not cross, regardless of how the request is phrased:

- **No authenticated session you weren't given.** Analyze only what the user has a
  right to access — a public site, or one they have their own credentials for and ask
  you to use. Don't attempt to obtain, guess, or reuse someone else's session.
- **No probing for weaknesses to exploit.** Phase 0's "permission boundaries" step
  checks whether the app *enforces* its own authorization, as an architecture finding
  (does the client trust itself, or the server?). That is the boundary: observe how it
  behaves, document it, stop. Turning it into a hunt for an access-control bug to walk
  through is a different activity — that needs the app owner's explicit authorization
  and belongs in a security engagement, not here.

If the target is a competitor's product the user wants to understand or rebuild, that's
fine — the output is a report about how it's built, not a way in. If a request is
actually "help me get into this," say so plainly and stop; the nearest thing this skill
does is document the architecture from the outside.

## Philosophy

Reverse engineering a webapp is detective work. You're reading clues left in the DOM,
network traffic, JavaScript bundles, HTTP headers, and error messages to reconstruct
an understanding of how the application was built and how it behaves. The key mindset:

- **Be methodical**: Follow the phases in order. Each phase builds on the previous one.
- **Be thorough**: Check everything. A single `X-Powered-By` header or a `__NEXT_DATA__`
  script tag can unlock the entire architecture.
- **Be skeptical**: Verify findings across multiple signals. A React-looking DOM might
  actually be Preact. An endpoint returning JSON might be a BFF, not the real API.
- **Go deep**: Don't stop at "it's a React app." Identify the meta-framework, the state
  management library, the CSS approach, the bundler, the deployment platform.

## Prerequisites

This skill requires browser automation tools (Claude in Chrome or equivalent). You need:
- `read_page` / `find` — for DOM analysis
- `read_network_requests` — for API/resource discovery
- `read_console_messages` — for error patterns and debug info
- `javascript_tool` — for deep JS introspection
- `computer` (screenshot) — for visual documentation
- `get_page_text` — for content extraction
- `navigate` — for multi-page exploration

You also benefit from `web_search` (to identify unknown libraries/services) and file
creation tools (to produce the final report).

---

## Phase 0: Get Into the Webapp

The #1 priority is getting into the **actual application** as fast as possible. Marketing
sites, landing pages, and pricing pages are NOT the webapp — they're a completely different
codebase and tell you almost nothing about the real product's architecture. Do not waste
time analyzing them.

### 0.1 Identify the App Entry Point

Most SaaS products separate their marketing site from the app:
- `www.example.com` or `example.com` → marketing site (SKIP THIS)
- `app.example.com` → the actual webapp (GO HERE)
- `dashboard.example.com`, `portal.example.com`, `secure.example.com` → also the app

If the user gives you a marketing URL (e.g., `aha.io`), don't start analyzing it.
Instead, immediately look for the app URL:

1. Check for obvious app subdomains: `app.`, `dashboard.`, `portal.`, `console.`, `secure.`
2. Look for "Log in" or "Sign in" links on the marketing page — follow them to find the
   app domain
3. If neither works, ask the user: "What's the URL when you're logged into the app?"

### 0.2 Get Authenticated

Most webapps are auth-gated. The real architecture — API calls, state management,
component trees, routing — only reveals itself behind the login wall. Getting
authenticated is not optional, it's step one.

1. **Navigate to the app login page** immediately
2. **Ask the user to log in** — tell them you've navigated to the login page and need
   them to enter their credentials. Never enter passwords yourself.
3. **Wait for the user to confirm** they're logged in
4. **Verify you're in the app** — take a screenshot and confirm you see the actual
   application shell (sidebar, dashboard, navigation), not a marketing page

If the user doesn't have an account, help them find a free trial or demo. The goal is
to get past the login gate. Public-surface analysis of a marketing site is only useful
if the user specifically asks for it.

### 0.3 Set Up the Browser Session

1. **Get the tabs context** — call `tabs_context_mcp` and either use an existing tab or
   create a new one.
2. **Navigate to the app URL** (not the marketing site).
3. **Wait for full page load** (2-3 seconds).
4. **Take an initial screenshot** — this is your visual baseline of the actual webapp.
5. **Confirm with the user** — "I can see the [dashboard/app]. Ready to start the
   deep analysis."

---

## Phases 1–5: the analysis

Each phase has its own reference file with the full procedure, probes, and
fingerprints. Read a phase file when you reach it, not all of them up front —
Phase 2 alone is 450 lines. Copy this checklist into the response and tick it
as you go; if a later phase contradicts an earlier finding, go back and
re-check rather than carrying both forward.

```
Analysis progress:
- [ ] Phase 0: in the real app, authenticated if needed, browser session up
- [ ] Phase 1: surface scan — headers, framework fingerprint, script inventory
- [ ] Phase 2: network — endpoint map, auth flow, WebSocket/real-time
- [ ] Phase 3: JavaScript — source maps, bundle, routes, data models, state
- [ ] Phase 4: visual/UX — component tree, design system, screenshots
- [ ] Phase 5: infrastructure — DNS/hosting, deployment, PWA
- [ ] Phase 6: report compiled from the template; every claim carries a confidence
```

| Phase | Read | Covers |
| ----- | ---- | ------ |
| 1 | [references/phase-1-surface-scan.md](references/phase-1-surface-scan.md) | HTTP headers and meta tags, framework fingerprinting, script and stylesheet inventory |
| 2 | [references/phase-2-network-analysis.md](references/phase-2-network-analysis.md) | Baseline capture, systematic exploration, WebSocket analysis, endpoint classification, authentication flow |
| 3 | [references/phase-3-javascript-analysis.md](references/phase-3-javascript-analysis.md) | Source-map detection, bundle analysis, route discovery, data-model inference, state management |
| 4 | [references/phase-4-visual-ux.md](references/phase-4-visual-ux.md) | Component tree, design-system detection, visual documentation |
| 5 | [references/phase-5-infrastructure.md](references/phase-5-infrastructure.md) | DNS and hosting clues, deployment and build signals, PWA status |

## Phase 6: Report Generation

Synthesize everything into the structured report in
[references/report-template.md](references/report-template.md) — executive
summary, tech-stack table with a confidence column, API map, auth, inferred
data models, route map, UI architecture, third-party services,
infrastructure, and the optional rebuild blueprint. Save it to
`/mnt/user-data/outputs/` and present it; use the docx skill if the user
asked for DOCX.

---

## Workflow Summary

Phases run in order, 0 through 6. Between phases, share interim findings so
the user can steer; if something unusual surfaces (exposed source maps, a rich
GraphQL schema), call it out and go deeper.

If the app is auth-gated, get the user logged in first (Phase 0), then run
Phases 1-5 on the authenticated webapp — that's where the real architecture
lives. Analyze the public/marketing surface only if the user asks; it's
usually a different codebase and irrelevant to understanding the product.

## Important Reminders

- **Never expose real credentials or tokens** in the report. Document patterns, not values.
- **Respect robots.txt and ToS** — this skill is for educational analysis and competitive
  research, not for scraping or unauthorized access.
- **Be honest about confidence levels** — distinguish between "definitely React" (saw
  `__REACT_DEVTOOLS_GLOBAL_HOOK__`) and "probably Postgres" (inferred from UUID patterns
  in API responses). Use High / Medium / Low confidence markers.
- **When in doubt, search the web** — if you see an unfamiliar library or service name
  in the scripts or network traffic, search for it to correctly identify and classify it.

## Limitations

- **Client-observable only, and that's a real ceiling, not just a caveat.** Server-side
  logic, database schema, internal services, and anything not reachable from what the
  browser loads are inferred from indirect signals (response shapes, timing, error
  messages) — not observed. Mark inferred architecture as inferred; a plausible guess
  presented with the same confidence as a `__NEXT_DATA__` read is a false precision.
- **Minified/obfuscated JS caps how deep Phase 3 can go.** Bundle analysis works well
  against source maps or unminified output; against a production bundle with both
  stripped, expect library/framework identification but not real logic reconstruction.
  Say which regime applied.
- **A rebuild blueprint is a starting architecture, not a spec.** It captures the shape
  this skill could observe, not edge cases, error handling, or business rules that never
  surfaced during exploration. Treat it as scaffolding to validate against, not a
  finished plan to implement blind.
- **Coverage is bounded by what got clicked.** Phase 1's exploration finds what the
  explored paths surface — a feature behind a flow nobody walked through won't appear.
  State what was and wasn't explored in the report rather than implying full coverage.

## Wrap-up retro

**After the report (or rebuild blueprint) lands**, run a
[`meta/skill-retro`](../../meta/skill-retro) pass on **this skill**, grounded
in what just happened: did the Scope section actually settle what was in and
out of bounds before Phase 0, or did a judgment call get made mid-run that
should have been pre-answered there; did a phase's instructions assume
tooling (a particular browser-automation call) that wasn't available, and if
so how was that handled; did the confidence-marking convention (High/Medium/
Low) hold up in practice or did an inferred finding end up stated as
observed; did Phase 2's network analysis or Phase 3's JS analysis run into a
target shape (heavy obfuscation, an unusual bundler, a GraphQL-only API) the
phase file didn't anticipate.

Running and reporting the retro is automatic and safe unattended —
`skill-retro` never edits this skill's files on its own. *Applying* anything
it finds is a separate, explicitly-approved follow-up through this repo's
normal PR workflow, never bundled into the run that triggered it.
