# Datastar Pro - Architecture & Project Structure

## Directory Layout
```
datastar-pro/
├── library/src/
│   ├── bundles/           # 6 bundle entry points
│   ├── engine/            # Core reactivity engine
│   │   ├── engine.ts      # Plugin system, MutationObserver, attribute parsing
│   │   ├── signals.ts     # Reactive signal system (3000+ lines)
│   │   ├── types.ts       # TypeScript type definitions
│   │   └── consts.ts      # Constants and escape sequences
│   ├── plugins/
│   │   ├── attributes/    # 17 core attribute plugins
│   │   ├── actions/       # 4 core action plugins (fetch, peek, setAll, toggleAll)
│   │   └── watchers/      # 2 watcher plugins (patchSignals, patchElements)
│   ├── pro/
│   │   ├── attributes/    # 10 pro attribute plugins
│   │   ├── actions/       # 2 pro action plugins (clipboard, fit)
│   │   └── utils/codecs.ts # Type codec system
│   └── utils/             # 8 utility modules
│       ├── text.ts        # String case transforms (kebab, camel, snake, pascal)
│       ├── paths.ts       # Nested path manipulation
│       ├── math.ts        # lerp, inverseLerp, clamp, fit
│       ├── timing.ts      # delay, debounce, throttle modifiers
│       ├── dom.ts         # DOM utilities
│       ├── polyfills.ts   # Browser polyfills
│       ├── tags.ts        # HTML/SVG tag parsing
│       └── view-transitions.ts # View Transition API
├── webcomponents/
│   └── datastar-inspector/ # <datastar-inspector> debug web component
├── *.js                   # Pre-compiled minified bundles
└── *.js.map               # Source maps
```

## Build System
- No package.json in root (pre-compiled distribution)
- TypeScript: ES2021 target, ESNext modules, bundler resolution
- Path aliases: @engine, @plugins, @pro, @utils
- Strict mode, no unused locals/parameters

## Engine Architecture

### Plugin Registration
```typescript
attribute({ name, requirement, returnsValue?, argNames?, apply })
action({ name, apply })
watcher({ name, apply })
```

### Requirements System
- `'exclusive'` - key XOR value (not both)
- `'must'` - must be provided
- `'allowed'` - optional
- `'denied'` - must not be provided

### Reactivity Engine (signals.ts)
- Signal<T>: mutable reactive value
- Computed<T>: derived/lazy value with dependency tracking
- Effect: side effect that reruns on dependency changes
- Dependency graph with automatic tracking via Proxy
- Batch updates: beginBatch()/endBatch()
- Peek: access without subscribing
- Deep reactive objects with nested proxy support
- Path-based updates: mergePatch(), mergePaths()
- Filtering: filtered({ include?, exclude? }) with RegExp

### Attribute Parsing
Format: `data-pluginName[:key]__mod1.tag1__mod2.tag2`
- Plugin name extracted from attribute name
- Optional key after colon
- Modifiers after double underscore, with dot-separated tags
- Stored as: Map<modName, Set<tags>>

### Expression System
- `$signalName` → signal reference (auto-transformed to `$['signalName']`)
- `$nested.path` → deep access
- `@actionName(args)` → action invocation
- IIFE support: `(() => { ... })()`
- Escaped sequences between DSP/DSS markers

### MutationObserver
- Watches DOM for added/removed elements
- Auto-applies plugins to dynamically inserted elements
- Tracks cleanups per element per attribute
- Handles script re-execution in patched content

### Cleanup Pattern
- Plugin apply() returns optional cleanup function
- cleanups Map manages multiple handlers per element
- Auto cleanup on element removal via MutationObserver

## TypeScript Patterns
- Type parameters with constraints
- Proxy objects for dynamic API surfaces
- WeakMap for element metadata storage
- Generic types for signal, computed, effect
- Discriminated unions for plugin types
