# Phase 6: Report Generation

After gathering all data, synthesize your findings into a structured report.

### Report Template

Generate the report as a Markdown file (or DOCX if the user prefers) with this structure:

```markdown
# Reverse Engineering Report: [App Name]

**Target URL**: [URL]
**Analysis Date**: [Date]
**Analysis Scope**: Public / Authenticated / Both

---

## Executive Summary

[2-3 paragraph overview of the application: what it does, how it's built, key
architectural decisions, and notable findings.]

## Tech Stack Overview

| Layer          | Technology       | Confidence | Evidence                    |
| -------------- | ---------------- | ---------- | --------------------------- |
| Framework      | [e.g., Next.js]  | High       | [e.g., __NEXT_DATA__ found] |
| UI Library     | [e.g., React 18] | High       | [evidence]                  |
| Styling        | [e.g., Tailwind] | High       | [evidence]                  |
| State Mgmt     | [e.g., Zustand]  | Medium     | [evidence]                  |
| API Style      | [e.g., REST]     | High       | [evidence]                  |
| Auth           | [e.g., Auth0]    | High       | [evidence]                  |
| Hosting        | [e.g., Vercel]   | High       | [evidence]                  |
| Database       | [e.g., Postgres] | Low        | [inferred from X]           |
| CDN            | [e.g., Cloudflare]| High      | [evidence]                  |

## Architecture Diagram

[Describe the architecture in text form, or generate a Mermaid diagram]

## API Endpoints

### [Group 1: e.g., Authentication]

| Method | Endpoint           | Purpose             | Auth Required |
| ------ | ------------------ | ------------------- | ------------- |
| POST   | /api/auth/login    | User login          | No            |
| POST   | /api/auth/refresh  | Token refresh       | Yes (refresh) |

### [Group 2: e.g., Core Resources]
[...]

## Real-Time & WebSocket Architecture

[If applicable. Describe:]
- **Protocol**: [e.g., Socket.IO over WSS, raw WebSocket, Pusher Channels]
- **Endpoint**: [e.g., wss://api.example.com/ws]
- **Channel/Event Structure**: [list event names, channel patterns]
- **Features powered by WS**: [e.g., live notifications, collaborative editing, chat]
- **Message format**: [JSON structure with example keys]
- **Reconnection strategy**: [auto-reconnect, heartbeat interval if observed]

## Authentication & Session Management

[Detailed description of auth flow, token storage, refresh patterns, etc.]

## Data Models (Inferred)

### [Model 1: e.g., User]
```json
{
  "id": "uuid",
  "email": "string",
  "name": "string",
  "role": "enum(admin, user, viewer)",
  "created_at": "ISO 8601",
  "avatar_url": "string | null"
}
```

## Route Map & Navigation Structure

### Site Map

| Route              | Purpose                  | Auth Required | Key Components               |
| ------------------ | ------------------------ | ------------- | ---------------------------- |
| /                  | Landing / Dashboard      | No / Yes      | [hero, stats, feed]          |
| /settings          | User settings            | Yes           | [tabs: profile, billing, …]  |

### User Flows

[Document multi-step flows discovered during exploration:]
- **Onboarding flow**: / → /signup → /onboarding/step-1 → … → /dashboard
- **Checkout flow**: /cart → /checkout/shipping → /checkout/payment → /confirmation

### Interaction Map

[For key pages, document what each interactive element does:]
- **Dashboard**: date picker triggers `GET /api/stats?range=...`, export button
  triggers `POST /api/export`, table rows navigate to `/items/:id`

## UI Architecture

### Design System
[Component library, CSS approach, design tokens if discoverable]

### Key Components
[Major UI patterns identified — layout structure, navigation patterns, data display patterns]

## Third-Party Services (Clone-Relevant)

| Service     | Purpose      | Integration Point         |
| ----------- | ------------ | ------------------------- |
| [e.g., Stripe] | Payments | [e.g., Stripe.js loaded]  |

## Infrastructure

[Hosting, CDN, deployment patterns, PWA status]

## Rebuild Blueprint

If you wanted to clone this application, here's a recommended approach:

### Recommended Stack
[Based on findings, suggest a modern stack that could replicate the functionality]

### Key Implementation Notes
[Gotchas, complex patterns, things that would be tricky to replicate]

### Estimated Complexity
[Rough assessment: simple / moderate / complex / very complex, with reasoning]
```

### Output

Save the report to `/mnt/user-data/outputs/` and present it to the user. If the user
asked for DOCX format, use the docx skill to convert it.

---
