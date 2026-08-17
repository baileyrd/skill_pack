# Release Notes

webapp-reverse-engineer lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/dev_practices/webapp-reverse-engineer) —
this log tracks commits against `main`: reverse chronological, one entry per
meaningful change, honest about what's still open.

---

## v1.0.0 — Productized out of `need_to_productize/`
**2026-08-17**

Moved from `need_to_productize/webapp-reverse-engineer.skill` (a staged zip
archive, neither versioned nor packaged nor installed) into `dev_practices/` as
a real skill directory.

Systematically deconstructs a running web application from client-observable
signals — DOM, network traffic, JS bundles, headers, error messages — through
six phases (surface scan, network analysis, JS deep-dive, visual/UX
architecture, infrastructure, report) into a tech-stack report and optional
rebuild blueprint. The phase content, report template, and Philosophy section
are untouched.

### Changed on productization

- **Added `version: 1.0.0`** and this log — the staged file had neither.
- **Added a `Scope` section, read before Phase 0.** The skill already had one
  line at the very end ("Respect robots.txt and ToS... not for scraping or
  unauthorized access") — after 1200 lines of instructions, past where an
  agent following them step by step would already be acting. Moved the actual
  gate to the top: client-observable analysis of a target the user has a right
  to access is in scope; using someone else's session, or probing for a
  weakness to walk through, is not — regardless of how the request is phrased.
- **Reworded the "Permission boundaries" step** in Phase 1 to match. It read
  *"if authenticated, try accessing admin-only routes or performing actions
  you shouldn't be able to"* — which is the exact language the new Scope
  section rules out. Rewritten around the user's own session only, observing
  where the *UI* draws its access lines (absent nav item vs. disabled vs.
  present-but-erroring) as a client-architecture finding, not an attempt to
  reach anything.
- **Added a `Limitations` section**, which the original had none of. Leads
  with the real ceiling: everything here is inferred from client-observable
  signals, so server logic, schema, and internal services are inferred from
  indirect evidence, not observed — mark inferred findings as inferred rather
  than presenting a guess with `__NEXT_DATA__`-read confidence. Also notes
  minified/obfuscated JS caps how deep Phase 3 can go, and that the rebuild
  blueprint is scaffolding to validate against, not a spec to implement blind.

### Not changed

- No eval set, no benchmark. Report quality across different app stacks is
  unmeasured, and the browser-automation prerequisites (`read_page`,
  `read_network_requests`, etc.) weren't exercised here — this container has
  no browser session to point at a live target.

**Category note:** lands in `dev_practices/` alongside `unix-philosophy` and
`shell-ui-architecture-audit` — the charter's "structured review of what
already exists" half, applied to an external target rather than a repo the
user owns.
