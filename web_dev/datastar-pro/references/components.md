# Datastar Pro - Complete Component Reference

## Core Attributes (17)

### Data Binding & State
| Attribute | Requirement | Purpose |
|-----------|------------|---------|
| `data-bind` | exclusive | Two-way binding: inputs ↔ signals. Supports text, number, range, checkbox, radio, file (base64), select, textarea, web components |
| `data-signals` | - | Declare/patch signals. Key: `data-signals:name=$val`. Object: `data-signals='{"k":"v"}'`. Modifier: `ifmissing` |
| `data-ref` | exclusive | Create signal referencing DOM element |
| `data-computed` | must value | Create computed signal. Key: `data-computed:name="expr"`. Object syntax supported |
| `data-indicator` | exclusive | Signal tracking SSE request status (true=STARTED, false=FINISHED) |

### Rendering
| Attribute | Requirement | Purpose |
|-----------|------------|---------|
| `data-text` | must value | Bind element.textContent to expression |
| `data-show` | must value | Toggle display:none based on boolean |
| `data-class` | must value | Toggle CSS classes. Key: `data-class:name="bool"`. Object: `data-class='{"k":bool}'`. Modifier: casing |
| `data-style` | must value | Set inline styles. Key: `data-style:prop="val"`. Object syntax. Auto camelCase→kebab-case |
| `data-attr` | must value | Sync HTML attributes. Key: `data-attr:name="val"`. Object syntax. Handles true/false/null |
| `data-json-signals` | - | Output JSON stringified signals. Modifier: `terse` |

### Lifecycle & Events
| Attribute | Requirement | Purpose |
|-----------|------------|---------|
| `data-init` | must value | Execute on element load. Modifier: `delay.500ms` |
| `data-on` | must key | Event listener. Key=event name. Modifiers: window, document, prevent, stop, capture, passive, once, outside, delay, debounce, throttle, viewtransition |
| `data-effect` | must value | Side effect, reruns on dependency changes |
| `data-on-interval` | must value | Execute at intervals. Modifiers: `duration.1000`, `leading` |
| `data-on-signal-patch` | must value | React to signal patches. `patch` param available. Filter support |
| `data-on-intersect` | must value | Intersection observer. Modifiers: full, half, threshold.N, exit, once |

## Pro Attributes (10)

| Attribute | Requirement | Purpose |
|-----------|------------|---------|
| `data-persist` | - | Persist signals to localStorage. Key=storage key (default 'datastar'). Modifier: `session` |
| `data-query-string` | - | Bidirectional URL↔signal sync. Modifier: `history` (pushState vs replaceState). Auto-parses types |
| `data-replace-url` | must value | Update browser URL without reload |
| `data-animate` | must value | Animate values. Key: `data-animate:attr="val"`. 40+ easing functions. Modifiers: duration, ease, delay, loop, pingpong |
| `data-on-raf` | must value | Execute on requestAnimationFrame. Timing modifiers supported |
| `data-on-resize` | must value | Execute on element resize (ResizeObserver) |
| `data-scroll-into-view` | - | Scroll element into view. Modifiers: smooth/instant/auto, vstart/vcenter/vend/vnearest, hstart/hcenter/hend/hnearest, focus |
| `data-view-transition` | must value | Set view-transition-name CSS property. Browser compat check |
| `data-custom-validity` | must value | Form validation. Works with input/select/textarea. Expression returns validation message string |
| `data-rocket` | - | Rocket component template engine (see rocket.md) |

## Core Actions (4 + 5 HTTP methods)

| Action | Syntax | Purpose |
|--------|--------|---------|
| `@get` | `@get(url, opts?)` | GET request via SSE |
| `@post` | `@post(url, opts?)` | POST request via SSE |
| `@patch` | `@patch(url, opts?)` | PATCH request via SSE |
| `@put` | `@put(url, opts?)` | PUT request via SSE |
| `@delete` | `@delete(url, opts?)` | DELETE request via SSE |
| `@peek` | `@peek(() => $sig)` | Access signal without subscribing |
| `@setAll` | `@setAll(value, filter?)` | Set all matching signals |
| `@toggleAll` | `@toggleAll(filter?)` | Toggle all matching boolean signals |

### Fetch Options
```typescript
{
  selector?: string,              // Form selector
  headers?: Record<string, string>,
  contentType?: 'json' | 'form',
  filterSignals?: { include?, exclude? },
  openWhenHidden?: boolean,
  payload?: any,
  requestCancellation?: AbortController | 'auto',
  retry?: 'auto' | boolean,
  retryInterval?: number,
  retryScaler?: number,
  retryMaxWaitMs?: number,
  retryMaxCount?: number
}
```

## Pro Actions (2)

| Action | Syntax | Purpose |
|--------|--------|---------|
| `@clipboard` | `@clipboard(text, isBase64?)` | Copy to clipboard via Clipboard API |
| `@fit` | `@fit(value, oldMin, oldMax, newMin, newMax, clamp?, round?)` | Linear interpolation/remapping |

## Watchers (2)

| Watcher | SSE Event | Purpose |
|---------|-----------|---------|
| `patchSignals` | `datastar-patch-signals` | Merge server signals into client. Fields: `signals {json}`, `onlyIfMissing true` |
| `patchElements` | `datastar-patch-elements` | Patch DOM from server. Fields: `selector`, `mode` (remove/outer/inner/replace/prepend/append/before/after), `elements`, `useViewTransition`, `namespace` |

## Codecs (Pro - Type System for Props)

Built-in codecs in `/library/src/pro/utils/codecs.ts`:
- `string` - String values
- `int` - Integer values
- `float` - Float values
- `boolean` - Boolean values
- `date` - Date objects
- `json` - JSON objects
- Supports chaining, validation, default values
