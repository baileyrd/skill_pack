---
name: datastar-pro
description: >
  Generate complete, production-ready Datastar Pro web applications using its attribute-driven
  reactive framework. Use this skill whenever the user asks to build a web app, page, or UI with
  Datastar, Datastar Pro, or mentions data-* attributes for reactivity, signals ($signalName),
  SSE-based server communication, or the Rocket component engine. Also trigger when the user
  wants a reactive web UI without a heavy framework — Datastar Pro is a 38KB alternative to
  React/Vue/Svelte that works with any backend. Trigger for phrases like "build me a reactive
  page", "create a Datastar app", "SSE-powered UI", "hypermedia application", "Stellar CSS",
  or any mention of data-bind, data-signals, data-on, data-text, data-show, @get, @post,
  or similar Datastar attribute/action syntax.
version: 1.0.1
---

# Datastar Pro Skill

Generate correct, idiomatic Datastar Pro applications. Datastar Pro is an attribute-driven
reactive web framework — no virtual DOM, no JSX, no build step. Everything is declared via
`data-*` HTML attributes, with `$signalName` for reactive state and `@actionName()` for
actions. Server communication uses SSE (Server-Sent Events).

Reviewed and imported into `skill_pack` from
[`baileyrd/datastar-pro-skill`](https://github.com/baileyrd/datastar-pro-skill)'s
audited v1.0 milestone (modularized `SKILL.md` + 6 reference files + 6
evals, all three of the source audit's flagged gaps already resolved in
what was imported — broken README links, `styling.md`'s missing TOC, and
two evals' stale "CDN" wording). `skill_pack` is this skill's maintained
home going forward, not a synced mirror — see `RELEASE_NOTES.md` for what
was deliberately left behind (`datastar-pro-main/`'s proprietary vendored
library source, `.planning/`'s development-process history, `CLAUDE.md`)
and why.

## Before You Start

Read the reference that matches your task:

| Building... | Read | Also read if needed |
|-------------|------|---------------------|
| Any Datastar page (basics) | This file is sufficient | `references/core.md` for expression/modifier deep-dive |
| Server-connected features (forms, search, CRUD) | `references/backend.md` for FastAPI + datastar-py | `references/components.md` for uncommon attributes |
| Styled/animated interfaces | `references/styling.md` | `references/stellar.md` for design tokens and theming |
| Design system / theming / Stellar CSS | `references/stellar.md` | `references/styling.md` for animation specifics |
| Component-based apps (reusable templates) | `references/rocket.md` | Requires Pro license + Rocket bundle |
| Custom plugins | `references/architecture.md` | — |
| Full API lookup | `references/components.md` | Complete attribute/action/watcher tables |

For most tasks, this file alone covers signals, binding, events, and common patterns.
Only read reference files when the task requires deeper API knowledge.

## Bundle Script Tags

Every generated HTML page must include one of these script tags in `<head>`:

```html
<!-- Datastar Pro bundle (38KB) — use this by default -->
<script type="module" src="/static/datastar-pro.js"></script>

<!-- Pro + Rocket bundle (83KB) — only when using data-rocket components -->
<script type="module" src="/static/datastar-pro-rocket.js"></script>
```

Datastar Pro is self-hosted (no public CDN). The bundle includes the full open-source
Datastar framework plus all Pro attributes and actions — no other script tags needed.
Requires a [commercial license](https://data-star.dev/reference/datastar_pro).

For the open-source core only (no Pro features), use the CDN:
```html
<script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-RC.7/bundles/datastar.js"></script>
```

## Quick Reference

### Signals (Reactive State)

Declare signals on any element. They're global and reactive — any expression referencing
a signal re-evaluates when that signal changes.

```html
<!-- Individual signals -->
<div data-signals:count="0" data-signals:name="'hello'">

<!-- Object syntax for multiple signals -->
<div data-signals='{"count": 0, "name": "hello", "items": []}'>

<!-- Read signals in expressions with $ prefix -->
<span data-text="$count"></span>
<span data-text="$name.toUpperCase()"></span>

<!-- Computed signals (derived values) -->
<div data-computed:double="$count * 2"></div>
```

### Data Binding

```html
<input data-bind="$name" />              <!-- text input -->
<input type="number" data-bind="$count" /> <!-- number -->
<input type="checkbox" data-bind="$agree" /> <!-- boolean -->
<select data-bind="$choice">              <!-- select -->
  <option value="a">A</option>
</select>
<textarea data-bind="$message"></textarea> <!-- textarea -->
```

For all input types (color, range, radio, file), see `references/core.md`.

### Event Handling

```html
<!-- Click handler -->
<button data-on:click="$count++">+1</button>

<!-- With modifiers (__ separates modifiers, . separates values) -->
<button data-on:click__prevent__stop="handleSubmit()">Submit</button>
<input data-on:input__debounce.300ms="@get('/search')" />
<div data-on:click__outside="$menuOpen = false"></div>

<!-- Window/document events -->
<div data-on:keydown__window="handleKey()"></div>

<!-- Intervals -->
<div data-on-interval__duration.5s="@get('/poll')"></div>
```

### Conditional Display & Text

```html
<div data-show="$isVisible">Shown when true</div>
<span data-text="$count"></span>
<span data-text="$count === 1 ? 'item' : 'items'"></span>
```

### CSS Classes & Inline Styles

```html
<!-- Toggle classes -->
<div data-class:active="$isActive" data-class:hidden="!$visible"></div>

<!-- Inline styles -->
<div data-style:backgroundColor="$color"></div>
<div data-style='{"fontSize": $size + "px", "opacity": $fade}'></div>
```

For animation (`data-animate`), view transitions, and scroll-into-view, see `references/styling.md`.
For design tokens and theming (Stellar CSS), see `references/stellar.md`.

### HTML Attributes

```html
<button data-attr:disabled="$loading"></button>
<img data-attr:src="$imageUrl" />
<a data-attr='{"href": $link, "target": "_blank"}'></a>
```

### Persist & URL Sync (Pro)

```html
<!-- Save signals to localStorage (survives page reload) -->
<div data-persist data-signals:theme="'light'"></div>

<!-- Bidirectional URL ↔ signal sync -->
<div data-query-string data-signals:page="1" data-signals:search="''"></div>
```

For full persist/query-string options (session storage, filtering, history mode), see `references/core.md`.

## Server Communication (SSE)

Datastar communicates with the server via SSE. The client sends signals as JSON; the server
responds with SSE events to patch the DOM or update signals.

### Client-Side Fetch Actions

```html
<button data-on:click="@get('/api/data')">Load</button>
<button data-on:click="@post('/api/submit')">Submit</button>
<button data-on:click="@put('/api/update')">Update</button>
<button data-on:click="@delete('/api/remove')">Delete</button>

<!-- Loading indicator -->
<div data-signals:loading="false">
  <button data-on:click="@get('/api/data')" data-indicator="$loading">
    Load Data
  </button>
  <span data-show="$loading">Loading...</span>
</div>
```

### Server Response Format (SSE)

The server responds with `Content-Type: text/event-stream`. Each event has an `event:` line,
one or more `data:` lines (with field name prefix), and a blank line terminator:

```
event: datastar-patch-elements
data: selector #target
data: mode inner
data: elements <div>New content</div>

event: datastar-patch-signals
data: signals {"count": 42}

```

**Modes:** `outer` (default), `inner`, `prepend`, `append`, `before`, `after`, `remove`.

### Python (FastAPI + datastar-py) Server Example

```python
from fastapi import FastAPI
from datastar_py.fastapi import DatastarResponse, ReadSignals
from datastar_py.sse import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode

app = FastAPI()

@app.post("/api/increment")
async def increment(signals: ReadSignals):
    count = (signals or {}).get("count", 0) + 1
    return DatastarResponse(SSE.patch_signals({"count": count}))
```

`pip install fastapi datastar-py uvicorn` — for complete patterns (forms, validation,
streaming, auth, deployment), see `references/backend.md`.

## Common Patterns

### Tabbed Interface
```html
<div data-signals:activeTab="'home'">
  <button data-on:click="$activeTab = 'home'"
          data-class:active="$activeTab === 'home'">Home</button>
  <button data-on:click="$activeTab = 'about'"
          data-class:active="$activeTab === 'about'">About</button>

  <div data-show="$activeTab === 'home'">Home content</div>
  <div data-show="$activeTab === 'about'">About content</div>
</div>
```

### Search with Debounce
```html
<div data-signals:query="''" data-signals:results="''">
  <input data-bind="$query"
         data-on:input__debounce.300ms="@get('/api/search')"
         placeholder="Search..." />
  <div id="results" data-text="$results"></div>
</div>
```

### Todo List
```html
<div data-signals:todos="[]" data-signals:newTodo="''">
  <input data-bind="$newTodo"
         data-on:keydown.enter="@post('/api/todos')" />
  <div id="todo-list"></div>
</div>
```

### Modal Dialog
```html
<div data-signals:modalOpen="false">
  <button data-on:click="$modalOpen = true">Open Modal</button>

  <div data-show="$modalOpen"
       data-style='{"position":"fixed","inset":"0","background":"rgba(0,0,0,0.5)","display":"flex","alignItems":"center","justifyContent":"center"}'>
    <div data-style='{"background":"white","padding":"2rem","borderRadius":"8px"}'>
      <h2>Modal Title</h2>
      <p>Modal content here.</p>
      <button data-on:click="$modalOpen = false">Close</button>
    </div>
  </div>
</div>
```

## Key Rules

1. **Always include the bundle script tag** in generated HTML pages
2. **Signals use `$` prefix** in expressions: `$count`, not `count`
3. **Actions use `@` prefix**: `@get()`, `@post()`, not `get()`, `post()`
4. **Modifiers use `__` (double underscore)**: `data-on:click__prevent`, not `data-on:click.prevent`
5. **Modifier values use `.` (dot)**: `__debounce.300ms`, `__duration.1s`
6. **SSE events must follow the exact format** — `event:` line, `data:` lines, blank line terminator
7. **Stellar CSS is the recommended styling companion** — use CSS custom properties for design tokens (forward-compatible with Stellar CSS when it ships); see `references/stellar.md`
8. **Prefer the simplest attribute combination** that achieves the goal
9. **String signal values need inner quotes**: `data-signals:name="'hello'"` (the outer quotes are HTML attribute, inner quotes make it a string expression)

## Wrap-up retro

After generating the requested app/page, run a `meta/skill-retro` pass on
`datastar-pro` itself, grounded in this invocation: did the "Before You
Start" routing table send the right reference file(s) for this task (or
none, when this file alone was sufficient), did a Key Rule get violated or
need a tenth exception this run actually hit, did a reference file's
example need adapting in a way that suggests the doc itself is stale
against the current bundle version? Read-only, safe to run unattended —
applying anything `skill-retro` finds is a separate, explicitly-approved
follow-up, not part of this invocation.
