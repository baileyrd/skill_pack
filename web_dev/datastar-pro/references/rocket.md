# Datastar Pro - Rocket Template Engine

## Overview
Rocket is a Pro-only component template engine (currently alpha.6). It enables reusable components with local state, props, conditionals, and loops - all within the Datastar attribute-driven paradigm.

**File:** `/library/src/pro/attributes/rocket.ts`

## Component Registration
```html
<!-- Define a component template -->
<template data-rocket:MyComponent>
  <div>
    <h2 data-text="$title"></h2>
    <p data-text="$description"></p>
  </div>
</template>

<!-- Use the component -->
<div data-rocket="MyComponent" data-props:title="'Hello'" data-props:description="'World'">
</div>
```

## Features

### Props
- Passed via `data-props:propName="expression"` attributes
- Support codec validation (string, int, float, boolean, date, json)
- Default values supported
- Type checking with custom parameters

### Component-Scoped Signals
- Each component instance gets its own signal scope
- Prevents signal name collisions between instances
- Local state isolated from global signals

### Local Component Actions
- Components can define instance-scoped actions
- Available only within component template

### Conditional Rendering
```html
<div data-if="$condition">Shown when true</div>
<div data-else-if="$otherCondition">Fallback</div>
<div data-else>Default</div>
```
- ConditionalManager handles branch management
- Exclusive rendering (only one branch visible)
- Reactive - re-evaluates on signal changes

### Loop Rendering
```html
<div data-for="item in $items">
  <span data-text="$item.name"></span>
</div>
```
- Iterates over arrays/collections
- Each iteration gets scoped context
- Reactive - updates on array changes

### Data Imports
- ESM imports supported
- IIFE imports for legacy compatibility

## Codecs System
Located at `/library/src/pro/utils/codecs.ts`

Built-in codecs:
| Codec | Purpose |
|-------|---------|
| `string` | String values |
| `int` | Integer parsing |
| `float` | Float parsing |
| `boolean` | Boolean coercion |
| `date` | Date object parsing |
| `json` | JSON parse/stringify |

Codec features:
- Chainable operations
- Validation with error messages
- Default value support
- Custom parameter passing

## Style Scoping
- Light DOM style scoping (alpha.6)
- No Shadow DOM by default
- CSS scoping via generated selectors

## Changelog Highlights
- **alpha.6:** Light DOM style scoping, fixed nested conditionals, template literal fixes
- **alpha.5:** Bug fixes
- **alpha.4:** Released with v1.0.0-RC.7
- **alpha.3-2:** Major feature additions

## Bundle
Rocket adds ~45KB to the bundle (83KB total for datastar-pro-rocket.js vs 38KB for datastar-pro.js)
