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
version: 1.0.0
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

## Phase 1: First Impressions & Surface Scan

Goal: Identify the broad technology fingerprint without going deep yet.

### 1.1 HTTP Headers & Meta Tags

Run this JavaScript to extract server-side clues:

```javascript
(async () => {
  // Fetch the page to read response headers
  const res = await fetch(window.location.href, { method: 'HEAD' });
  const headers = {};
  res.headers.forEach((v, k) => headers[k] = v);

  // Gather meta tags
  const metas = [...document.querySelectorAll('meta')].map(m => ({
    name: m.getAttribute('name') || m.getAttribute('property') || m.getAttribute('http-equiv'),
    content: m.getAttribute('content')
  })).filter(m => m.name);

  // Check for generator tags
  const generator = document.querySelector('meta[name="generator"]')?.content;

  return JSON.stringify({ headers, metas, generator }, null, 2);
})()
```

**What to look for:**
- `X-Powered-By` → server framework (Express, ASP.NET, PHP, etc.)
- `Server` → web server (nginx, Apache, Cloudflare, Vercel, Netlify)
- `X-Frame-Options`, `Content-Security-Policy` → security posture
- `Set-Cookie` → session management approach
- `meta[name="generator"]` → CMS or framework (Next.js, WordPress, Hugo, etc.)

### 1.2 Framework Fingerprinting

Run this JavaScript to detect client-side frameworks:

```javascript
(() => {
  const signals = {};

  // React
  const reactRoot = document.querySelector('[data-reactroot], #__next, #___gatsby');
  signals.react = !!(window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || reactRoot
    || document.querySelector('[data-react-helmet]'));

  // Next.js
  signals.nextjs = !!(document.getElementById('__NEXT_DATA__')
    || window.__NEXT_DATA__ || window.__next);

  // Vue
  signals.vue = !!(window.__VUE__ || window.__vue_app__
    || document.querySelector('[data-v-]') || document.querySelector('#app.__vue-content-placeholders'));

  // Nuxt
  signals.nuxt = !!(window.__NUXT__ || window.$nuxt || document.getElementById('__nuxt'));

  // Angular
  signals.angular = !!(window.ng || document.querySelector('[ng-version]')
    || document.querySelector('[_nghost-ng-]') || window.getAllAngularRootElements);

  // Svelte / SvelteKit
  signals.svelte = !!(document.querySelector('[class*="svelte-"]')
    || document.querySelector('script[data-sveltekit-hydrate]'));

  // Remix
  signals.remix = !!(window.__remixContext || window.__remixManifest);

  // Astro
  signals.astro = !!document.querySelector('[data-astro-cid]');

  // jQuery
  signals.jquery = !!(window.jQuery || window.$?.fn?.jquery);

  // Tailwind (check for utility classes)
  const hasTailwind = [...document.querySelectorAll('[class]')].some(el =>
    /\b(flex|grid|p-\d|m-\d|text-\w|bg-\w|rounded|shadow)\b/.test(el.className));
  signals.tailwind = hasTailwind;

  // Webpack / Vite
  signals.webpack = !!(window.webpackJsonp || window.webpackChunk
    || document.querySelector('script[src*="webpack"]'));
  signals.vite = !!document.querySelector('script[type="module"][src*="/@vite"]');

  // State management
  signals.redux = !!window.__REDUX_DEVTOOLS_EXTENSION__;
  signals.mobx = !!window.__MOBX_DEVTOOLS_GLOBAL_HOOK__;
  signals.zustand = !!window.__zustand;

  // Filter to only detected signals
  const detected = Object.entries(signals).filter(([_, v]) => v).map(([k]) => k);
  return JSON.stringify({ detected, raw: signals }, null, 2);
})()
```

### 1.3 Script & Stylesheet Inventory

```javascript
(() => {
  const scripts = [...document.querySelectorAll('script[src]')].map(s => {
    const url = new URL(s.src, window.location.origin);
    return {
      src: s.src,
      isThirdParty: url.hostname !== window.location.hostname,
      type: s.type || 'text/javascript',
      async: s.async,
      defer: s.defer,
      hostname: url.hostname
    };
  });

  const styles = [...document.querySelectorAll('link[rel="stylesheet"]')].map(l => {
    const url = new URL(l.href, window.location.origin);
    return {
      href: l.href,
      isThirdParty: url.hostname !== window.location.hostname,
      hostname: url.hostname
    };
  });

  // Group third-party scripts by domain
  const thirdPartyDomains = {};
  scripts.filter(s => s.isThirdParty).forEach(s => {
    if (!thirdPartyDomains[s.hostname]) thirdPartyDomains[s.hostname] = [];
    thirdPartyDomains[s.hostname].push(s.src);
  });

  return JSON.stringify({
    totalScripts: scripts.length,
    firstPartyScripts: scripts.filter(s => !s.isThirdParty).length,
    thirdPartyScripts: scripts.filter(s => s.isThirdParty).length,
    thirdPartyDomains,
    stylesheets: styles.length,
    scripts: scripts.slice(0, 30) // Cap to avoid huge output
  }, null, 2);
})()
```

**Identify third-party services that are relevant to cloning** — focus on:
- Auth providers (Auth0, Firebase Auth, Clerk, Supabase Auth)
- Payment processors (Stripe, PayPal)
- Real-time services (Pusher, Ably, Firebase Realtime)
- Search (Algolia, Typesense, Elasticsearch)
- Analytics only if they reveal architecture (e.g., Segment implies event-driven patterns)

Ignore purely observational third parties (Google Analytics, Hotjar, etc.) unless the
user specifically asks.

---

## Phase 2: Network Traffic Analysis

Goal: Map every API endpoint, understand data shapes, and discover the backend architecture.

### 2.1 Capture Baseline Traffic

Before interacting with the page, read the network requests that fired on load:

```
read_network_requests(tabId, urlPattern="/api/")
```

Also check for GraphQL:
```
read_network_requests(tabId, urlPattern="graphql")
```

And generic XHR/fetch:
```
read_network_requests(tabId, urlPattern="")
```

### 2.2 Systematic App Exploration

Before interacting, **install the WebSocket interceptor from Phase 2.3.2** so you
capture real-time traffic alongside HTTP requests.

Exploring a webapp is not random clicking — it's a structured traversal. The goal is
to visit every meaningful state of the application and document what happens at each
transition. Think of it like crawling a graph: pages are nodes, interactions are edges,
and API calls are the side effects you're recording.

#### Step 1: Build a Navigation Map

First, discover all the top-level entry points without clicking anything:

```javascript
(() => {
  // Primary navigation links
  const navElements = document.querySelectorAll('nav a, header a, [role="navigation"] a, aside a');
  const navLinks = [...navElements].map(a => ({
    text: a.textContent.trim().substring(0, 60),
    href: a.href,
    isInternal: new URL(a.href, location.origin).hostname === location.hostname
  })).filter(l => l.isInternal && l.text);

  // Buttons that look like navigation (tabs, sidebar items)
  const navButtons = [...document.querySelectorAll(
    '[role="tab"], [role="menuitem"], [data-tab], [class*="nav-item"], [class*="sidebar"] a, [class*="sidebar"] button'
  )].map(el => ({
    text: el.textContent.trim().substring(0, 60),
    tag: el.tagName.toLowerCase(),
    role: el.getAttribute('role'),
    ariaLabel: el.getAttribute('aria-label')
  })).filter(b => b.text);

  // Footer links (often reveal hidden pages)
  const footerLinks = [...document.querySelectorAll('footer a')].map(a => ({
    text: a.textContent.trim().substring(0, 60),
    href: a.href,
    isInternal: new URL(a.href, location.origin).hostname === location.hostname
  })).filter(l => l.isInternal && l.text);

  return JSON.stringify({
    primaryNav: navLinks,
    tabsAndMenuItems: navButtons,
    footerLinks,
    totalDiscovered: navLinks.length + navButtons.length + footerLinks.length
  }, null, 2);
})()
```

Use `read_page` with `filter: "interactive"` to get a full inventory of clickable
elements on the current view. This shows you everything you *can* interact with.

#### Step 2: Depth-First Route Traversal

Work through the navigation map methodically. For each route/page:

1. **Screenshot (before)** — capture current state before navigating away
2. **Navigate** — click the link or use `navigate` for direct URL access
3. **Wait** — allow 2-3 seconds for data fetching and rendering
4. **Screenshot (after)** — capture the new page in its loaded state
5. **Read network** — `read_network_requests` with `clear: true` to capture only
   this transition's API calls
6. **Read page structure** — `read_page` at depth 4-5 to capture the component tree
7. **Inventory interactables** — `read_page` with `filter: "interactive"` to find
   all buttons, inputs, links, toggles on this view

Never skip steps 1 and 4. Every route transition needs a before/after screenshot pair.

Record what you find in a running exploration log like this:

```
Route: /dashboard
  → Triggered: GET /api/user/me, GET /api/dashboard/stats, GET /api/notifications
  → Components: sidebar, stat-cards (x4), activity-feed, chart
  → Interactive elements: date-range picker, export button, filter dropdown, 12 table rows
  → Next to explore: date-range picker, export button, filter dropdown, table row click
```

#### Step 3: Component-Level Interaction

After mapping the routes, go back and interact with the components on each page.
These are the interactions that reveal the app's deeper behavior:

**Disclosure components** (things that reveal hidden content):
- Accordions, expandable sections → click each one, check for lazy-loaded data
- Tabs within a page → click each tab, capture new API calls
- "Show more" / "Load more" buttons → reveals pagination endpoints
- Dropdown menus → open each, note the options (these often come from an API)
- Tooltips / popovers → hover to trigger, may lazy-load data

**Data-entry components** (things that send data):
- Search bars → type a query, observe the search API (debounce timing, query format)
- Filter controls → toggle filters, observe how query params or POST bodies change
- Forms → inspect the fields without submitting (note required fields, validation rules,
  field types). If safe and appropriate, submit with test data to capture the write endpoint
- Inline editing → click editable fields, observe PATCH/PUT calls

**Navigation components** (things that change the view):
- Table rows → click to see if they navigate to a detail view
- Cards / list items → click to reveal detail panels or routes
- Breadcrumbs → click to verify route hierarchy
- Pagination → click through pages, observe offset/cursor patterns
- Back buttons / close buttons → verify they trigger cleanup API calls

**Stateful components** (things with multiple states):
- Toggle switches → flip them, capture the API call
- Checkboxes / multi-select → select multiple items, look for batch endpoints
- Drag-and-drop → if present, reorder items and observe the update call
- Notification badges → click to see if they trigger a "mark as read" endpoint

For each interaction, follow this pattern. **Every step is mandatory — never skip
the screenshot.** The screenshot is your evidence. Without it, the interaction is
undocumented and the report will have gaps.

```
1. Clear network:  read_network_requests(tabId, clear: true)
2. Screenshot:     computer(screenshot) — capture the BEFORE state
3. Find element:   find(tabId, "the element description")
4. Interact:       computer(left_click on the element)
5. Wait:           computer(wait 1-2 seconds)
6. Screenshot:     computer(screenshot) — capture the AFTER state
7. Capture:        read_network_requests(tabId) — record any new API calls
8. Read DOM:       read_page(tabId, ref_id of the changed area) — if relevant
```

Note the before/after screenshot pair (steps 2 and 6). This captures the transition:
what the UI looked like before the interaction and what changed afterward. This is
essential for documenting component behavior in the report — for example, "clicking
the 'Analytics' tab (screenshot 14) replaces the stats cards with a chart view
(screenshot 15) and triggers `GET /api/analytics/overview`."

Save screenshots with descriptive filenames that encode the sequence:

```bash
screenshots/
├── 01-landing-page.png
├── 02-before-click-signin.png
├── 03-after-click-signin-modal-open.png
├── 04-dashboard-overview.png
├── 05-before-click-analytics-tab.png
├── 06-after-click-analytics-tab.png
├── 07-before-open-date-picker.png
├── 08-after-open-date-picker.png
...
```

**When to take additional screenshots beyond the interaction pattern:**
- After scrolling to reveal new content below the fold
- After resizing the window (for responsive behavior analysis)
- When a loading/skeleton state is visible (screenshot quickly before data loads)
- When an error state or empty state appears
- When a toast/notification/snackbar appears (these are transient — capture fast)

#### Step 4: Multi-Step Flows

Some features span multiple steps (wizards, checkout flows, onboarding). When you
encounter one:

1. **Screenshot every step** — before and after each transition in the flow
2. Document each step: screenshot + network calls + form fields
3. Note the step indicator pattern (URL change? step parameter? local state?)
4. Look for draft/save behavior between steps
5. Check if you can navigate backward and whether state persists (screenshot the
   back-navigation result too)
6. Document the final submission endpoint and its full payload shape

#### Step 5: Edge State Discovery

After the main traversal, probe for edge states that reveal more architecture:

- **Empty states** — navigate to a section with no data. Does it show a placeholder?
  Does it still call the API (returning an empty array)?
- **Error states** — navigate to a nonexistent route (e.g., `/this-does-not-exist`).
  Is there a custom 404? Does it reveal the framework's error handling?
- **Loading states** — throttle the network (if possible) or note any skeleton screens
  or spinners. These reveal the loading architecture (Suspense boundaries, loading
  indicators, optimistic updates).
- **Permission boundaries** — with the access the user actually gave you (see Scope
  above: their own session, nothing borrowed or guessed), note where the *UI itself*
  draws the line — a nav item that's absent for your role versus one that's present but
  disabled versus one that's there and simply errors when clicked. That's a client-side
  architecture finding (does the app hide by capability or just by convenience?), not an
  attempt to reach anything you weren't given access to.

#### Exploration Strategy Tips

- **Work top-down**: primary nav first, then secondary nav, then in-page components
- **Use `find` liberally**: it's the fastest way to locate specific UI elements by
  their purpose (e.g., `find(tabId, "settings gear icon")`)
- **Use `scroll_to`** for elements below the fold before interacting with them
- **Use `zoom`** to inspect small or ambiguous UI elements before clicking
- **Read the page at a focused `ref_id`** when you only need to inspect a specific
  section (e.g., after a modal opens, read just the modal's subtree)
- **Take screenshots frequently** — before and after key interactions. These become
  the visual documentation in the final report
- **Track your exploration state** — mentally (or in a running note) mark which
  navigation items and components you've visited vs. which remain. The goal is
  complete coverage, not random poking

### 2.3 WebSocket Analysis

WebSockets are invisible to `read_network_requests` — they use a persistent connection
that doesn't show up as individual HTTP requests after the initial handshake. You need
to actively intercept them.

#### 2.3.1 Detect Active WebSocket Connections

```javascript
(() => {
  // Check for WebSocket-related globals
  const signals = {};

  // Socket.IO
  signals.socketIO = !!(window.io || document.querySelector('script[src*="socket.io"]'));

  // Pusher
  signals.pusher = !!(window.Pusher || document.querySelector('script[src*="pusher"]'));

  // Ably
  signals.ably = !!(window.Ably || document.querySelector('script[src*="ably"]'));

  // Firebase Realtime / Firestore
  signals.firebaseRealtime = !!(window.firebase?.database || window.firebase?.firestore);

  // Supabase Realtime
  signals.supabaseRealtime = !!document.querySelector('script[src*="supabase"]');

  // ActionCable (Rails)
  signals.actionCable = !!(window.ActionCable || window.App?.cable);

  // Phoenix LiveView / Channels
  signals.phoenixChannels = !!(window.Phoenix || window.liveSocket);

  // Generic WebSocket detection - check if WS constructor has been used
  signals.nativeWebSocket = typeof WebSocket !== 'undefined';

  const detected = Object.entries(signals).filter(([_, v]) => v).map(([k]) => k);
  return JSON.stringify({ detected, raw: signals }, null, 2);
})()
```

#### 2.3.2 Intercept WebSocket Traffic

Install a monkey-patch to capture live WebSocket messages. Run this **before**
interacting with the app, then interact with real-time features (chat, notifications,
live data) and collect results afterward.

```javascript
(() => {
  // Don't install twice
  if (window.__wsInterceptorInstalled) return 'Already installed. Run the collector snippet to read messages.';

  window.__wsCapturedMessages = [];
  window.__wsConnections = [];
  const OrigWebSocket = window.WebSocket;

  window.WebSocket = function(url, protocols) {
    const ws = protocols ? new OrigWebSocket(url, protocols) : new OrigWebSocket(url);
    const connId = window.__wsConnections.length;
    window.__wsConnections.push({
      id: connId,
      url: url,
      protocols: protocols || null,
      openedAt: new Date().toISOString(),
      readyState: ws.readyState
    });

    // Capture incoming messages
    ws.addEventListener('message', (event) => {
      let parsed = null;
      try { parsed = JSON.parse(event.data); } catch(e) {}
      window.__wsCapturedMessages.push({
        connId,
        direction: 'incoming',
        timestamp: new Date().toISOString(),
        dataType: typeof event.data,
        dataLength: event.data?.length || 0,
        preview: typeof event.data === 'string' ? event.data.substring(0, 500) : '[binary]',
        parsed: parsed ? Object.keys(parsed) : null
      });
    });

    // Capture outgoing messages
    const origSend = ws.send.bind(ws);
    ws.send = function(data) {
      let parsed = null;
      try { parsed = JSON.parse(data); } catch(e) {}
      window.__wsCapturedMessages.push({
        connId,
        direction: 'outgoing',
        timestamp: new Date().toISOString(),
        dataType: typeof data,
        dataLength: data?.length || 0,
        preview: typeof data === 'string' ? data.substring(0, 500) : '[binary]',
        parsed: parsed ? Object.keys(parsed) : null
      });
      return origSend(data);
    };

    return ws;
  };

  // Preserve prototype chain
  window.WebSocket.prototype = OrigWebSocket.prototype;
  window.WebSocket.CONNECTING = OrigWebSocket.CONNECTING;
  window.WebSocket.OPEN = OrigWebSocket.OPEN;
  window.WebSocket.CLOSING = OrigWebSocket.CLOSING;
  window.WebSocket.CLOSED = OrigWebSocket.CLOSED;

  window.__wsInterceptorInstalled = true;
  return 'WebSocket interceptor installed. Interact with real-time features, then run the collector.';
})()
```

#### 2.3.3 Collect & Analyze Captured Messages

After interacting with real-time features, collect the captured traffic:

```javascript
(() => {
  const connections = window.__wsConnections || [];
  const messages = window.__wsCapturedMessages || [];

  // Summarize message patterns
  const messageTypes = {};
  messages.forEach(m => {
    if (m.parsed) {
      const typeKey = m.parsed.sort().join(',');
      if (!messageTypes[typeKey]) messageTypes[typeKey] = { count: 0, direction: m.direction, example: m.preview };
      messageTypes[typeKey].count++;
    }
  });

  // Detect protocol patterns
  const protocols = {};
  messages.slice(0, 5).forEach(m => {
    const preview = m.preview;
    if (preview.startsWith('0{') || preview.startsWith('42[')) protocols.socketIO = true;
    if (preview.includes('"event"') && preview.includes('"channel"')) protocols.pusher = true;
    if (preview.includes('"topic"') && preview.includes('"event"') && preview.includes('"payload"')) protocols.phoenix = true;
    if (preview.includes('"type"') && preview.includes('"identifier"')) protocols.actionCable = true;
  });

  return JSON.stringify({
    connections,
    totalMessages: messages.length,
    incomingCount: messages.filter(m => m.direction === 'incoming').length,
    outgoingCount: messages.filter(m => m.direction === 'outgoing').length,
    messagePatterns: messageTypes,
    detectedProtocols: Object.keys(protocols),
    recentMessages: messages.slice(-10) // last 10 for inspection
  }, null, 2);
})()
```

**What to document about WebSockets:**
- **Connection URL** — `wss://` endpoint, any path patterns
- **Protocol** — raw WS, Socket.IO, Pusher, ActionCable, Phoenix Channels, etc.
- **Message format** — JSON structure, event names/types, channel/room patterns
- **Direction patterns** — is it mostly server-push (notifications), bidirectional (chat),
  or client-polling disguised as WS?
- **Reconnection behavior** — does the app auto-reconnect? Is there a heartbeat/ping?
- **What features depend on it** — map each WS channel/event to the UI feature it powers

This is critical for the rebuild blueprint — if the app relies heavily on WebSockets,
the clone needs a real-time layer (e.g., Socket.IO, Supabase Realtime, Ably, or plain WS).

### 2.4 Classify Endpoints

For each discovered endpoint, document:
- **Method** (GET, POST, PUT, DELETE, PATCH)
- **URL pattern** (extract path parameters like `/api/users/:id`)
- **Query parameters**
- **Request headers** (especially Authorization patterns)
- **Response shape** (describe the JSON structure)
- **Purpose** (what UI feature triggered it)

Look for patterns that reveal the API style:
- REST: Resource-oriented paths (`/api/v1/users`, `/api/v1/posts/:id/comments`)
- GraphQL: Single endpoint, operations in request body
- tRPC: Procedure-style paths (`/api/trpc/user.getById`)
- gRPC-web: Binary protocol, specific content types

### 2.5 Authentication Flow Analysis

Pay special attention to:
- Login/signup endpoints
- Token refresh patterns
- OAuth redirects
- Cookie vs. Bearer token patterns
- CSRF token handling
- Session storage (cookies vs. localStorage vs. sessionStorage)

Run this to inspect stored credentials:

```javascript
(() => {
  const storage = {};

  // localStorage
  const ls = {};
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    const val = localStorage.getItem(key);
    if (val && (key.toLowerCase().includes('token') || key.toLowerCase().includes('auth')
        || key.toLowerCase().includes('session') || key.toLowerCase().includes('user'))) {
      ls[key] = val.substring(0, 100) + (val.length > 100 ? '...' : '');
    }
  }
  storage.localStorage = ls;

  // sessionStorage
  const ss = {};
  for (let i = 0; i < sessionStorage.length; i++) {
    const key = sessionStorage.key(i);
    const val = sessionStorage.getItem(key);
    if (val && (key.toLowerCase().includes('token') || key.toLowerCase().includes('auth')
        || key.toLowerCase().includes('session') || key.toLowerCase().includes('user'))) {
      ss[key] = val.substring(0, 100) + (val.length > 100 ? '...' : '');
    }
  }
  storage.sessionStorage = ss;

  // Cookies
  storage.cookies = document.cookie.split(';').map(c => {
    const [name] = c.trim().split('=');
    return name;
  }).filter(Boolean);

  return JSON.stringify(storage, null, 2);
})()
```

**IMPORTANT**: Never include actual token values or credentials in the report. Document
the *pattern* (e.g., "JWT stored in localStorage under key `auth_token`"), not the values.

---

## Phase 3: Deep JavaScript Analysis

Goal: Understand the application's internal architecture by inspecting its JavaScript.

### 3.1 Source Map Detection

```javascript
(() => {
  const scripts = [...document.querySelectorAll('script[src]')];
  const results = [];

  for (const script of scripts.slice(0, 10)) {
    try {
      // Check if sourcemap comment exists (we can't fetch cross-origin, but we can check)
      results.push({ src: script.src, type: script.type });
    } catch(e) {}
  }

  // Check for .map files referenced in the page source
  const pageSource = document.documentElement.outerHTML;
  const sourceMapRefs = pageSource.match(/\/\/[#@]\s*sourceMappingURL=\S+/g) || [];

  return JSON.stringify({ scripts: results, sourceMapRefs }, null, 2);
})()
```

If source maps are publicly accessible, this is a goldmine — you can reconstruct the
original source structure. Fetch them and analyze the file tree.

### 3.2 Bundle Analysis

For webpack/vite bundles, inspect the chunk structure:

```javascript
(() => {
  // Webpack chunks
  const wpChunks = window.webpackChunk || window.webpackJsonp;
  let chunkInfo = null;
  if (wpChunks && Array.isArray(wpChunks)) {
    chunkInfo = {
      type: 'webpack',
      chunkCount: wpChunks.length,
      chunkIds: wpChunks.slice(0, 10).map(c => Array.isArray(c) ? c[0] : 'unknown')
    };
  }

  // Next.js build manifest
  const nextData = window.__NEXT_DATA__;
  let nextInfo = null;
  if (nextData) {
    nextInfo = {
      buildId: nextData.buildId,
      page: nextData.page,
      props: Object.keys(nextData.props || {}),
      runtimeConfig: nextData.runtimeConfig ? Object.keys(nextData.runtimeConfig) : null,
      scriptLoader: nextData.scriptLoader
    };
  }

  // Next.js build manifest for routes
  const buildManifest = window.__BUILD_MANIFEST;
  let routeInfo = null;
  if (buildManifest) {
    routeInfo = {
      pages: Object.keys(buildManifest).filter(k => k !== '__rewrites'),
      totalPages: Object.keys(buildManifest).length
    };
  }

  return JSON.stringify({ chunkInfo, nextInfo, routeInfo }, null, 2);
})()
```

### 3.3 Route Structure Discovery

```javascript
(() => {
  // Try to extract routes from various frameworks

  // Next.js
  const buildManifest = window.__BUILD_MANIFEST;
  if (buildManifest) {
    return JSON.stringify({
      framework: 'next.js',
      routes: Object.keys(buildManifest).filter(k => !k.startsWith('_'))
    }, null, 2);
  }

  // React Router (v6+)
  const routerState = window.__REACT_ROUTER__;
  if (routerState) {
    return JSON.stringify({
      framework: 'react-router',
      state: routerState
    }, null, 2);
  }

  // Collect all internal links as route hints
  const links = [...document.querySelectorAll('a[href]')]
    .map(a => new URL(a.href, window.location.origin))
    .filter(u => u.hostname === window.location.hostname)
    .map(u => u.pathname)
    .filter((v, i, a) => a.indexOf(v) === i) // unique
    .sort();

  return JSON.stringify({
    framework: 'unknown (inferring from links)',
    discoveredPaths: links
  }, null, 2);
})()
```

### 3.4 Data Model Inference

From the API responses captured in Phase 2, reconstruct the likely data models.
Look for:
- Consistent ID patterns (UUIDs, auto-increment, CUIDs)
- Timestamp formats (ISO 8601, Unix timestamps)
- Nested relationships vs. flat + foreign keys
- Pagination patterns (cursor-based, offset-based)
- Enum-like fields (status, type, role)

Use `javascript_tool` to parse `__NEXT_DATA__` or similar server-injected props
for initial data shapes.

### 3.5 State Management Deep Dive

```javascript
(() => {
  const state = {};

  // Redux
  if (window.__REDUX_DEVTOOLS_EXTENSION__) {
    try {
      // Try to get store reference from React tree
      const store = window.__REDUX_DEVTOOLS_EXTENSION__?.store;
      if (store) {
        const s = store.getState();
        state.redux = { keys: Object.keys(s), structure: {} };
        for (const key of Object.keys(s)) {
          state.redux.structure[key] = typeof s[key] === 'object'
            ? Object.keys(s[key] || {}).slice(0, 10)
            : typeof s[key];
        }
      }
    } catch(e) {
      state.redux = { detected: true, error: e.message };
    }
  }

  // Check for global state objects
  const globals = Object.keys(window).filter(k =>
    k.toLowerCase().includes('store') ||
    k.toLowerCase().includes('state') ||
    k.toLowerCase().includes('app')
  ).filter(k => typeof window[k] === 'object' && window[k] !== null);

  state.suspectedGlobalState = globals.slice(0, 20);

  return JSON.stringify(state, null, 2);
})()
```

---

## Phase 4: Visual & UX Architecture

Goal: Document the UI layer — component structure, design system, layout patterns.

### 4.1 Component Tree Analysis

```javascript
(() => {
  // Walk the DOM and identify component boundaries
  const root = document.getElementById('root') || document.getElementById('__next')
    || document.getElementById('app') || document.body;

  function walkTree(el, depth = 0, maxDepth = 4) {
    if (depth > maxDepth) return null;

    const info = {
      tag: el.tagName?.toLowerCase(),
      id: el.id || undefined,
      classes: el.className && typeof el.className === 'string'
        ? el.className.split(' ').filter(c => c && !c.startsWith('svelte-') && c.length < 40).slice(0, 5)
        : undefined,
      role: el.getAttribute?.('role') || undefined,
      dataTestId: el.getAttribute?.('data-testid') || el.getAttribute?.('data-cy') || undefined,
      childCount: el.children?.length || 0
    };

    // Only recurse into structural elements
    if (el.children && el.children.length > 0 && el.children.length < 20) {
      info.children = [...el.children]
        .slice(0, 10)
        .map(c => walkTree(c, depth + 1, maxDepth))
        .filter(Boolean);
    }

    return info;
  }

  return JSON.stringify(walkTree(root), null, 2);
})()
```

### 4.2 Design System Detection

```javascript
(() => {
  const html = document.documentElement.outerHTML;

  const designSystems = {
    'Material UI / MUI': /Mui[A-Z]|mui-|MuiButton/.test(html),
    'Ant Design': /ant-|antd/.test(html),
    'Chakra UI': /chakra-/.test(html),
    'shadcn/ui': /data-radix|radix-/.test(html),
    'Radix UI': /data-radix/.test(html),
    'Headless UI': /headlessui/.test(html),
    'Bootstrap': /bootstrap|btn-primary|col-md/.test(html),
    'Tailwind UI': !!(document.querySelector('[class*="max-w-"][class*="mx-auto"]')),
    'Mantine': /mantine/.test(html)
  };

  const detected = Object.entries(designSystems).filter(([_, v]) => v).map(([k]) => k);

  // CSS methodology
  const cssApproach = {
    cssModules: !!document.querySelector('[class*="_"]') && /[a-zA-Z]+_[a-zA-Z0-9]{5,}/.test(html),
    styledComponents: /sc-[a-zA-Z]/.test(html),
    emotion: /css-[a-z0-9]+/.test(html),
    tailwind: /\b(flex|grid|p-\d|m-\d|text-\w|bg-\w)\b/.test(html),
    BEM: /[a-z]+__[a-z]+--[a-z]+/.test(html)
  };

  const detectedCSS = Object.entries(cssApproach).filter(([_, v]) => v).map(([k]) => k);

  return JSON.stringify({ designSystems: detected, cssApproach: detectedCSS }, null, 2);
})()
```

### 4.3 Visual Documentation

Take screenshots at each major section/route and after key interactions. These serve
two purposes: they help you analyze the UI during the session, and they become visual
references in the final report.

**How to capture and save screenshots for the report:**

1. Take the screenshot: `computer(action: "screenshot", tabId: ...)`
2. Claude receives the image and can analyze it visually
3. To include it in the report, save it to disk using `upload_image` or by running
   a script that captures the page via the browser

For each screenshot, note:
- The route / URL at the time of capture
- What state the UI is in (e.g., "dashboard with date filter set to 'Last 7 days'")
- What UI patterns are visible (card layout, data table, chart type, etc.)

**Key moments to screenshot:**
- Each top-level route (the "resting state" of each page)
- Before and after opening modals, drawers, or expanding sections
- Different tab states within a page
- Empty states and error states
- Mobile/responsive views if relevant (use `resize_window` to simulate)

If the report is Markdown, reference screenshots by filename:
```markdown
![Dashboard overview](screenshots/dashboard-overview.png)
```

If the report is DOCX, use the docx skill's image embedding capabilities.

---

## Phase 5: Infrastructure & Deployment

Goal: Identify the hosting, CDN, and deployment infrastructure.

### 5.1 DNS & Hosting Clues

Look at the response headers and script sources for hosting signals:
- `server: Vercel` → Vercel
- `x-vercel-id` → Vercel
- `x-amz-*` headers → AWS
- `cf-ray` header → Cloudflare
- `x-served-by: cache-*` → Fastly
- `fly-request-id` → Fly.io
- `netlify` in headers → Netlify
- `railway` → Railway
- Script sources from `*.supabase.co` → Supabase
- Script sources from `*.firebaseio.com` → Firebase

### 5.2 Deployment Patterns

```javascript
(() => {
  const patterns = {};

  // Check for service worker (PWA)
  patterns.serviceWorker = 'serviceWorker' in navigator;

  // Check manifest
  const manifest = document.querySelector('link[rel="manifest"]');
  patterns.webManifest = manifest ? manifest.href : null;

  // Environment hints
  const envHints = {};
  if (window.__ENV__) envHints.__ENV__ = Object.keys(window.__ENV__);
  if (window.__CONFIG__) envHints.__CONFIG__ = Object.keys(window.__CONFIG__);
  if (window.ENV) envHints.ENV = Object.keys(window.ENV);
  patterns.envHints = envHints;

  // Check for common deployment artifacts
  patterns.nextjs = !!window.__NEXT_DATA__;
  patterns.buildId = window.__NEXT_DATA__?.buildId;

  return JSON.stringify(patterns, null, 2);
})()
```

---

## Phase 6: Report Generation

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

## Workflow Summary

When this skill triggers, follow these phases in order:

1. **Phase 0**: Get into the actual webapp (find app URL, authenticate, skip marketing site)
2. **Phase 1**: Surface scan (headers, frameworks, scripts)
3. **Phase 2**: Network analysis (API endpoints, auth flows)
4. **Phase 3**: Deep JS analysis (bundles, routes, state, data models)
5. **Phase 4**: Visual/UX analysis (components, design system, screenshots)
6. **Phase 5**: Infrastructure detection (hosting, deployment)
7. **Phase 6**: Compile everything into the structured report

Between phases, share interim findings with the user so they can steer the analysis.
If something particularly interesting emerges (e.g., exposed source maps, a rich
GraphQL schema), call it out and go deeper.

If the app is auth-gated, get the user logged in FIRST (Phase 0), then run Phases 1-5
on the authenticated webapp. This is where the real architecture lives. Only analyze
the public/marketing surface if the user specifically asks for it — it's usually a
completely different codebase and irrelevant to understanding the product.

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
