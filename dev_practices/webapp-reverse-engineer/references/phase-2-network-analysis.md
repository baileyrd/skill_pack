# Phase 2: Network Traffic Analysis

Goal: Map every API endpoint, understand data shapes, and discover the backend architecture.

## Contents

- [2.1 Capture Baseline Traffic](#21-capture-baseline-traffic)
- [2.2 Systematic App Exploration](#22-systematic-app-exploration)
- [2.3 WebSocket Analysis](#23-websocket-analysis)
- [2.4 Classify Endpoints](#24-classify-endpoints)
- [2.5 Authentication Flow Analysis](#25-authentication-flow-analysis)

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
