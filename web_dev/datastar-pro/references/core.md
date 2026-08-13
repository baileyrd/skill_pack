# Datastar Pro — Core Concepts

Deep reference for signals, expressions, modifiers, and data binding. For quick reference, see SKILL.md.
For SSE/server patterns, see `references/backend.md`. For styling/animation, see `references/styling.md`.

## Table of Contents

- [Signal Declaration](#signal-declaration)
- [Expression Syntax](#expression-syntax)
- [Action Calls](#action-calls)
- [Operators in Expressions](#operators-in-expressions)
- [Modifier Syntax](#modifier-syntax)
- [Computed Signals & Effects](#computed-signals--effects)
- [Data Binding Deep-Dive](#data-binding-deep-dive)
- [Signal Filtering](#signal-filtering)
- [Pro Core Features](#pro-core-features)

---

## Signal Declaration

Signals are global reactive state. Any expression referencing a signal re-evaluates when that signal changes.

### Individual Syntax
```html
<div data-signals:count="0"></div>
<div data-signals:name="'hello'"></div>
<div data-signals:active="true"></div>
<div data-signals:items="[]"></div>
```

### Object Syntax (multiple signals at once)
```html
<div data-signals='{"count": 0, "name": "hello", "items": [], "active": true}'></div>
```

### Critical Rules
- **String values need inner quotes:** `data-signals:name="'hello'"` — outer quotes are the HTML attribute, inner quotes make it a string expression
- **Numeric/boolean values have no inner quotes:** `data-signals:count="0"`, `data-signals:active="true"`
- **Signals are global** — declared on any element, accessible everywhere via `$signalName`
- **Signals can be declared on any ancestor** — common pattern is to declare all signals on a root `<div>`

---

## Expression Syntax

### Signal References
```javascript
$signalName          // Simple signal access
$nested.path         // Deep access → $['nested']['path']
$array.0             // Array index → $['array'][0]
$foo-bar             // Kebab case → $['foo-bar']
$foo['key.name']     // Bracket notation for dots in keys
```

### Operators
```javascript
$count++             // Increment
$count--             // Decrement
$count += 5          // Compound assignment
$isActive ? 'on' : 'off'  // Ternary
$items.map(i => i.v)       // Array methods (reactive)
$items.filter(i => i.ok)   // Filtering
(() => { /* block */ })()   // IIFE for multi-statement blocks
```

### Boolean and Comparison
```javascript
$a && $b             // Logical AND
$a || $b             // Logical OR
!$active             // Negation
$count > 0           // Comparison
$name === 'admin'    // Strict equality
```

---

## Action Calls

Actions are invoked with `@` prefix in expressions.

### HTTP Actions
```javascript
@get('/api/data')                    // HTTP GET (SSE response)
@post('/api/submit')                 // HTTP POST
@put('/api/update')                  // HTTP PUT
@patch('/api/partial')               // HTTP PATCH
@delete('/api/remove')               // HTTP DELETE
```

### Utility Actions
```javascript
@clipboard($text)                    // Copy to clipboard (Pro)
@peek(() => $signal)                 // Read signal without subscribing to changes
@setAll(false, 'checkbox_.*')        // Bulk set matching signals
@toggleAll('toggle_.*')              // Bulk toggle matching signals
@fit($val, 0, 100, 0, 1, true)      // Remap value from one range to another (Pro)
```

### Fetch Options
```javascript
@post('/api/submit', {
  selector: '#myForm',               // Scope signal collection to element
  contentType: 'form',               // 'json' (default) or 'form'
  filterSignals: {                   // Filter which signals are sent
    include: /^form_/,
    exclude: /password/
  }
})
```

---

## Modifier Syntax

Modifiers customize attribute behavior. They use `__` (double underscore) as separator, with `.` (dot) for values.

**Pattern:** `data-attribute:key__modifier.value__modifier2`

### Event Modifiers
| Modifier | Effect | Example |
|----------|--------|---------|
| `__prevent` | preventDefault() | `data-on:submit__prevent="handle()"` |
| `__stop` | stopPropagation() | `data-on:click__stop="handle()"` |
| `__once` | Fire once then remove | `data-on:click__once="init()"` |
| `__outside` | Fire on clicks outside element | `data-on:click__outside="$open = false"` |
| `__window` | Listen on window | `data-on:keydown__window="handleKey()"` |
| `__capture` | Use capture phase | `data-on:click__capture="handle()"` |
| `__passive` | Passive listener | `data-on:scroll__passive="track()"` |

### Timing Modifiers
| Modifier | Effect | Example |
|----------|--------|---------|
| `__debounce.Nms` | Debounce by N ms | `data-on:input__debounce.300ms="search()"` |
| `__throttle.Nms` | Throttle by N ms | `data-on:scroll__throttle.100ms="track()"` |
| `__delay.Nms` | Delay execution | `data-init__delay.500ms="loadData()"` |
| `__duration.Ns` | Set duration | `data-on-interval__duration.5s="poll()"` |
| `__leading` | Fire on leading edge | `data-on-interval__duration.5s__leading="poll()"` |

### Animation Modifiers
| Modifier | Effect | Example |
|----------|--------|---------|
| `__duration.Nms` | Animation duration | `data-animate:opacity__duration.500ms="1"` |
| `__ease.NAME` | Easing function | `data-animate:opacity__ease.outcubic="1"` |
| `__delay.Nms` | Animation delay | `data-animate:opacity__delay.200ms="1"` |
| `__loop` | Loop animation | `data-animate:transform__loop="'rotate(360deg)'"` |
| `__reverse` | Reverse on loop | `data-animate:transform__loop__reverse="..."` |

### Intersection Modifiers
| Modifier | Effect | Example |
|----------|--------|---------|
| `__threshold.N` | Visibility % (0-100) | `data-on-intersect__threshold.50="load()"` |
| `__once` | Fire once | `data-on-intersect__once="load()"` |

### Persistence Modifiers
| Modifier | Effect | Example |
|----------|--------|---------|
| `__session` | Use sessionStorage | `data-persist__session` |

### Chaining Modifiers
```html
<!-- Multiple modifiers on one attribute -->
<button data-on:click__prevent__stop__once="submit()">Submit</button>
<input data-on:keydown__window__debounce.300ms="search()" />
<div data-animate:opacity__duration.500ms__ease.outcubic__delay.200ms="1"></div>
```

---

## Computed Signals & Effects

### Computed Signals (derived values)
```html
<!-- Re-evaluates when dependencies change -->
<div data-computed:double="$count * 2"></div>
<div data-computed:fullName="$firstName + ' ' + $lastName"></div>
<div data-computed:filtered="$items.filter(i => i.active)"></div>
<div data-computed:total="$cart.reduce((s, i) => s + i.price, 0)"></div>
```

### Effects (side effects)
```html
<!-- Runs when dependencies change — use for true side effects only -->
<div data-effect="console.log('Count changed:', $count)"></div>
<div data-effect="document.title = $pageTitle"></div>
```

**When to use what:**
- `data-text`, `data-show`, `data-class`, `data-style` — for rendering (preferred)
- `data-computed` — for derived values used by other expressions
- `data-effect` — for side effects that don't map to a specific attribute (e.g., updating document.title)

---

## Data Binding Deep-Dive

`data-bind` creates two-way binding between an input element and a signal.

### Input Types
```html
<!-- Text input -->
<input data-bind="$name" />
<input type="text" data-bind="$name" placeholder="Enter name" />

<!-- Number -->
<input type="number" data-bind="$count" min="0" max="100" />

<!-- Checkbox (boolean signal) -->
<input type="checkbox" data-bind="$agree" />

<!-- Radio buttons (share one signal) -->
<input type="radio" data-bind="$choice" value="a" /> A
<input type="radio" data-bind="$choice" value="b" /> B
<input type="radio" data-bind="$choice" value="c" /> C

<!-- Select dropdown -->
<select data-bind="$choice">
  <option value="">Choose...</option>
  <option value="a">Option A</option>
  <option value="b">Option B</option>
</select>

<!-- Textarea -->
<textarea data-bind="$message" rows="4"></textarea>

<!-- Color picker -->
<input type="color" data-bind="$color" />

<!-- Range slider -->
<input type="range" data-bind="$size" min="12" max="48" />

<!-- File upload (base64 encoded) -->
<input type="file" data-bind="$avatar" />
```

### Binding Patterns
```html
<!-- Bind + display -->
<input data-bind="$name" />
<p data-text="'Hello, ' + $name + '!'"></p>

<!-- Bind + computed -->
<input type="number" data-bind="$price" />
<input type="number" data-bind="$quantity" />
<div data-computed:total="$price * $quantity"></div>
<span data-text="'Total: $' + $total.toFixed(2)"></span>

<!-- Bind + conditional display -->
<input data-bind="$query" />
<div data-show="$query.length > 0">
  <p data-text="'Searching for: ' + $query"></p>
</div>
```

---

## Signal Filtering

Signals can be filtered in multiple contexts using regex patterns.

### In Fetch Requests
```javascript
// Include only signals matching pattern
@get('/api', { filterSignals: { include: /^user_/ } })

// Exclude sensitive signals
@post('/api', { filterSignals: { exclude: /password|token/ } })

// Combine include + exclude
@get('/api', { filterSignals: { include: /^form_/, exclude: /^form_internal_/ } })
```

### In Bulk Operations
```javascript
// Set all matching signals to a value
@setAll(false, 'checkbox_.*')

// Toggle all matching signals
@toggleAll('toggle_.*')
```

### In Persistence
```html
<!-- Persist only matching signals -->
<div data-persist='{"include": "user_.*", "exclude": "temp_.*"}'></div>
```

### Naming Convention
Prefix signals by feature/section for effective filtering:
```html
<div data-signals='{"form_email": "", "form_name": "", "form_password": "", "nav_open": false, "modal_visible": false}'>
```
This enables `filterSignals: { include: /^form_/ }` to send only form data to the server.

---

## Pro Core Features

These are Datastar Pro features related to core signal management. Use only when they add clear value.

### Persist (data-persist)

Save signals to browser storage so they survive page reloads.

```html
<!-- Default: localStorage -->
<div data-persist data-signals:theme="'light'" data-signals:fontSize="16"></div>

<!-- Session storage (clears when tab closes) -->
<div data-persist__session data-signals:tempData="''"></div>

<!-- With signal filtering -->
<div data-persist='{"include": "user_.*", "exclude": "temp_.*"}'
     data-signals:user_name="''" data-signals:user_theme="'light'" data-signals:temp_draft="''">
</div>
```

**Key points:**
- Place `data-persist` on the same element (or ancestor) as the signals you want to persist
- Signals are serialized to JSON in storage
- On page load, stored values override signal defaults
- Use `__session` modifier for session-scoped persistence

### Query String Sync (data-query-string)

Bidirectional sync between URL query parameters and signals.

```html
<!-- Default: replaceState (no history entries) -->
<div data-query-string data-signals:page="1" data-signals:search="''"></div>

<!-- With pushState (creates browser history entries) -->
<div data-query-string__history data-signals:tab="'home'"></div>
```

**Key points:**
- URL reflects signal state: `?page=1&search=hello`
- Bookmarkable/shareable URLs for free
- Use `__history` when the user should be able to navigate back
- Without `__history`, URL updates silently (no back button entries)
