# Datastar Pro — Backend Integration (FastAPI + datastar-py)

Server reference for building Datastar Pro backends with FastAPI and the official `datastar-py` SDK.
For client-side attributes, see SKILL.md. For core concepts, see `references/core.md`.

## Table of Contents

- [Setup](#setup)
- [SDK Imports](#sdk-imports)
- [Request-Response Pattern](#request-response-pattern)
- [Reading Client Signals](#reading-client-signals)
- [Patching DOM Elements](#patching-dom-elements)
- [Patching Signals](#patching-signals)
- [Removing Elements](#removing-elements)
- [Server Redirects](#server-redirects)
- [Executing Client-Side Scripts](#executing-client-side-scripts)
- [Streaming Progress Updates](#streaming-progress-updates)
- [Form Handling & Validation](#form-handling--validation)
- [Content Negotiation](#content-negotiation)
- [Production Deployment](#production-deployment)
- [Pitfalls & Gotchas](#pitfalls--gotchas)

---

## Setup

```bash
pip install fastapi datastar-py uvicorn
```

Place `datastar-pro.js` (or `datastar-pro-rocket.js` for Rocket) in a `static/` directory.

Minimal runnable app:

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datastar_py.fastapi import DatastarResponse, ReadSignals
from datastar_py.sse import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index():
    return """<!DOCTYPE html>
<html>
<head>
    <script type="module" src="/static/datastar-pro.js"></script>
</head>
<body>
    <div data-signals:count="0">
        <button data-on:click="@post('/api/increment')">+1</button>
        <span id="count" data-text="$count"></span>
    </div>
</body>
</html>"""

@app.post("/api/increment")
async def increment(signals: ReadSignals):
    count = (signals or {}).get("count", 0) + 1
    return DatastarResponse(
        SSE.patch_signals({"count": count})
    )
```

Run with: `uvicorn main:app --reload`

---

## SDK Imports

```python
# FastAPI integration (most common)
from datastar_py.fastapi import (
    DatastarResponse,                    # StreamingResponse subclass with SSE headers
    ReadSignals,                         # Annotated[dict | None, Depends(read_signals)]
    ServerSentEventGenerator as SSE,     # Event constructors
    datastar_response,                   # Decorator alternative
)
from datastar_py.consts import ElementPatchMode  # outer, inner, prepend, append, etc.

# Framework-agnostic (for non-FastAPI use)
from datastar_py.sse import ServerSentEventGenerator as SSE
from datastar_py.consts import SSE_HEADERS

# Server-side HTML attribute builder (for templates)
from datastar_py import attribute_generator as d
```

---

## Request-Response Pattern

Datastar uses SSE as a response format, not a persistent push channel. The lifecycle is:

1. Client sends HTTP request (GET with query params, or POST/PUT/PATCH/DELETE with JSON body)
2. Server responds with `Content-Type: text/event-stream`
3. Server sends one or more SSE events (patch-elements, patch-signals, execute-script, redirect)
4. Server closes the connection (generator exhausts)
5. Client processes events and updates DOM/signals

`DatastarResponse` handles all SSE headers automatically.

### Single Event

```python
@app.get("/api/data")
async def get_data():
    return DatastarResponse(
        SSE.patch_elements("<p>Hello!</p>", selector="#results")
    )
```

### Multiple Events

```python
@app.post("/api/action")
async def action(signals: ReadSignals):
    return DatastarResponse([
        SSE.patch_signals({"status": "saved"}),
        SSE.patch_elements(
            "<p>Done!</p>",
            selector="#message",
            mode=ElementPatchMode.INNER,
        ),
    ])
```

### Decorator Pattern

```python
@app.get("/api/items")
@datastar_response
async def get_items():
    return SSE.patch_elements("<ul><li>Item 1</li></ul>", selector="#items")
```

---

## Reading Client Signals

`ReadSignals` is a FastAPI dependency that extracts signals from Datastar requests.

```python
@app.post("/api/submit")
async def submit(signals: ReadSignals):
    # signals is dict | None
    name = (signals or {}).get("name", "")
    return DatastarResponse(
        SSE.patch_elements(f"<p>Hello, {name}!</p>", selector="#greeting")
    )
```

**How ReadSignals works:**
- Checks for `Datastar-Request: true` header
- **GET requests:** reads signals from `?datastar=<url-encoded-json>` query parameter
- **POST/PUT/PATCH/DELETE:** reads signals from JSON request body
- **Non-Datastar requests:** returns `None`

**Always guard against None:**
```python
count = (signals or {}).get("count", 0)
# NOT: count = signals.get("count", 0)  # TypeError if signals is None
```

---

## Patching DOM Elements

```python
SSE.patch_elements(
    elements="<div>HTML content</div>",     # HTML string (required unless mode=remove)
    selector="#target",                       # CSS selector (default: inferred from element id)
    mode=ElementPatchMode.INNER,             # Patch mode (default: OUTER)
    use_view_transition=True,                # Use View Transition API (default: False)
    namespace=ElementPatchNamespace.SVG,     # html, svg, mathml (default: html)
)
```

**Patch modes:**
| Mode | Behavior |
|------|----------|
| `OUTER` | Replace entire matched element (default) |
| `INNER` | Replace element's children only |
| `PREPEND` | Insert before first child |
| `APPEND` | Insert after last child |
| `BEFORE` | Insert before element |
| `AFTER` | Insert after element |
| `REMOVE` | Remove matched element |
| `REPLACE` | Same as OUTER |

Multi-line HTML is handled automatically — each line becomes a separate `data: elements` line in the SSE event.

---

## Patching Signals

```python
SSE.patch_signals(
    signals={"count": 42, "name": "test"},   # Dict of signal key-value pairs
    only_if_missing=True,                     # Only set signals that don't exist (default: False)
)
```

---

## Removing Elements

```python
SSE.remove_elements(selector="#item-42")
```

Equivalent to `patch_elements` with `mode=REMOVE` but more explicit.

---

## Server Redirects

```python
@app.post("/api/login")
async def login(signals: ReadSignals):
    if await verify_credentials(signals):
        return DatastarResponse(SSE.redirect("/dashboard"))
    return DatastarResponse(
        SSE.patch_elements(
            "<p style='color:red'>Invalid credentials</p>",
            selector="#login-error",
        )
    )
```

---

## Executing Client-Side Scripts

```python
SSE.execute_script(
    script="alert('Done!')",
    auto_remove=True,           # Remove script tag after execution (default: True)
    attributes={"type": "module"},  # Optional extra attributes on script tag
)
```

---

## Streaming Progress Updates

Use an async generator for long-running operations:

```python
import asyncio

@app.post("/api/process")
async def process(signals: ReadSignals):
    async def generate():
        for step in range(5):
            yield SSE.patch_signals({"progress": step * 25})
            yield SSE.patch_elements(
                f"<p>Step {step + 1} of 5...</p>",
                selector="#status",
                mode=ElementPatchMode.INNER,
            )
            await asyncio.sleep(1)

        yield SSE.patch_signals({"progress": 100})
        yield SSE.patch_elements(
            "<p>Complete!</p>",
            selector="#status",
            mode=ElementPatchMode.INNER,
        )

    return DatastarResponse(generate())
```

---

## Form Handling & Validation

### Basic Form Submission

```html
<div data-signals:name="''" data-signals:email="''" data-signals:formErrors="[]">
    <input data-bind="$name" placeholder="Name" />
    <input data-bind="$email" placeholder="Email" />
    <button data-on:click="@post('/api/submit-form')">Submit</button>
    <ul id="error-list"></ul>
    <div id="form-result"></div>
</div>
```

```python
@app.post("/api/submit-form")
async def submit_form(signals: ReadSignals):
    if signals is None:
        return DatastarResponse()  # 204 No Content for non-Datastar requests

    name = signals.get("name", "")
    email = signals.get("email", "")

    # Validate
    errors = []
    if not name:
        errors.append("Name is required")
    if "@" not in email:
        errors.append("Valid email is required")

    if errors:
        return DatastarResponse([
            SSE.patch_signals({"formErrors": errors}),
            SSE.patch_elements(
                "\n".join(f"<li>{e}</li>" for e in errors),
                selector="#error-list",
                mode=ElementPatchMode.INNER,
            ),
        ])

    # Success
    await save_user(name, email)
    return DatastarResponse([
        SSE.patch_signals({"formErrors": [], "name": "", "email": ""}),
        SSE.patch_elements(
            "<p>Thank you for submitting!</p>",
            selector="#form-result",
            mode=ElementPatchMode.INNER,
        ),
    ])
```

### GET with Query Parameter Signals

```python
@app.get("/api/search")
async def search(signals: ReadSignals):
    query = (signals or {}).get("query", "")
    results = await search_database(query)
    html = "".join(f"<li>{r['title']}</li>" for r in results)
    return DatastarResponse(
        SSE.patch_elements(
            f"<ul>{html}</ul>" if html else "<p>No results found</p>",
            selector="#results",
            mode=ElementPatchMode.INNER,
        )
    )
```

### Client-Side Signal Delivery

- **GET requests:** Signals sent as `?datastar=<url-encoded-json>` query parameter
- **POST/PUT/PATCH/DELETE:** Signals sent as JSON request body
- **Headers sent by client:**
  - `Datastar-Request: true`
  - `Accept: text/event-stream, text/html, application/json`
  - `Content-Type: application/json` (for POST/PUT/PATCH/DELETE)

### Client-Side Form Options

```html
<!-- JSON payload (default) -->
<button data-on:click="@post('/api/submit')">Submit</button>

<!-- Scoped signals (only send signals from within #myForm) -->
<button data-on:click="@post('/api/submit', { selector: '#myForm' })">Submit</button>

<!-- Form data content type -->
<button data-on:click="@post('/api/submit', { contentType: 'form' })">Submit</button>

<!-- Filter which signals are sent -->
<button data-on:click="@post('/api/submit', { filterSignals: { include: /^form_/ } })">Submit</button>
```

---

## Content Negotiation

Serve both Datastar SSE and regular JSON API responses from the same endpoint:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.get("/api/data")
async def get_data(request: Request, signals: ReadSignals):
    data = await fetch_data()

    if request.headers.get("Datastar-Request"):
        return DatastarResponse(
            SSE.patch_elements(render_html(data), selector="#data-container")
        )
    return JSONResponse(data)
```

---

## Production Deployment

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Datastar-Request", "Content-Type"],
    expose_headers=["Content-Type"],
)
```

**Critical:** `Datastar-Request` MUST be in `allow_headers` or CORS preflight rejects Datastar requests.

### Authentication

Standard HTTP auth works since Datastar uses regular fetch (not WebSocket):

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/protected")
async def protected(signals: ReadSignals, token=Depends(security)):
    user = verify_token(token.credentials)
    if not user:
        raise HTTPException(status_code=401)
    return DatastarResponse(
        SSE.patch_elements(f"<p>Welcome, {user.name}!</p>", selector="#greeting")
    )
```

Cookie-based auth works automatically since Datastar uses standard fetch. For token-based auth from the client:

```html
<button data-on:click="@get('/api/data', { headers: { 'Authorization': 'Bearer ' + $token } })">
    Load
</button>
```

### Nginx Reverse Proxy

```nginx
location /api/ {
    proxy_pass http://localhost:8000;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    chunked_transfer_encoding off;
    proxy_buffering off;           # Critical for SSE
    proxy_cache off;
    proxy_read_timeout 86400s;     # For long-lived streams
}
```

`DatastarResponse` sets `X-Accel-Buffering: no` automatically, which tells nginx to disable response buffering.

### Error Handling

Return errors as Datastar patches (not HTTP errors) to keep the UI responsive:

```python
@app.post("/api/action")
async def action(signals: ReadSignals):
    try:
        result = await perform_action(signals)
        return DatastarResponse(
            SSE.patch_elements(f"<p>Success: {result}</p>", selector="#result")
        )
    except ValueError as e:
        return DatastarResponse([
            SSE.patch_signals({"error": str(e)}),
            SSE.patch_elements(
                f"<p style='color:red'>{e}</p>",
                selector="#error",
            ),
        ])
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Running in Production

```bash
# Development
uvicorn main:app --reload

# Production (multi-worker)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

For Datastar's short-lived request-response SSE pattern, scaling is identical to regular HTTP — no sticky sessions required, standard horizontal scaling works.

---

## Pitfalls & Gotchas

### ReadSignals returns None for non-Datastar requests
Always guard: `(signals or {}).get("key", default)`. A non-Datastar client (curl, browser) won't send the `Datastar-Request` header.

### DatastarResponse returns 204 for empty content
Passing `None` or an empty iterable returns 204 No Content with no SSE headers. This is by design but can be surprising.

### Missing Datastar-Request in CORS allow_headers
CORS preflight silently rejects requests if the custom header isn't allowed. Always include `"Datastar-Request"` in `allow_headers`.

### Sync generators block the event loop
Always use `async def` generators with `await` for I/O. Sync generators run in a threadpool but waste resources.

### Multi-line HTML is handled correctly by the SDK
`SSE.patch_elements()` splits multi-line HTML into separate `data: elements` lines automatically. Don't manually split.

### SSE wire format (for manual construction)
If you ever need to construct SSE events without the SDK:

```
event: datastar-patch-elements\n
data: selector #target\n
data: mode inner\n
data: elements <div>content</div>\n
\n
```

Each event has: `event:` type line, one or more `data:` lines (with field name prefix), and a blank line terminator. Use the SDK instead of manual construction.

### Don't mix DatastarResponse with sse-starlette EventSourceResponse
`DatastarEvent` strings from the SDK are already formatted. Passing them into `EventSourceResponse` causes double-encoding. Use `DatastarResponse` for Datastar events.

---

## Server-Side Attribute Builder

For server-side HTML templating (Jinja2, Mako, etc.), use the attribute generator:

```python
from datastar_py import attribute_generator as d

attrs = d.signals(count=0, name="'hello'")
# Produces: data-signals='{"count": 0, "name": "'hello'"}'

on_click = d.on("click", "$count++")
# Produces: data-on:click="$count++"

bind = d.bind("$name")
# Produces: data-bind="$name"
```

---

## SSE Wire Format Reference

### Event Types
| Event Type | SDK Method | Purpose |
|-----------|-----------|---------|
| `datastar-patch-elements` | `SSE.patch_elements()` | Patch DOM content |
| `datastar-patch-signals` | `SSE.patch_signals()` | Update reactive signals |
| `datastar-execute-script` | `SSE.execute_script()` | Run client-side JS |

### Retry Configuration (Client-Side)
```javascript
@get('/api/data', {
    retry: 'auto',
    retryInterval: 1000,
    retryScaler: 2,
    retryMaxWaitMs: 30000,
    retryMaxCount: 10
})
```

### Fetch Event Lifecycle
Events on `DATASTAR_FETCH_EVENT` CustomEvent:
1. `started` — Request initiated
2. `finished` — Request completed successfully
3. `error` — HTTP error (status >= 400)
4. `retrying` — Auto-retry in progress
5. `retries-failed` — All retries exhausted
