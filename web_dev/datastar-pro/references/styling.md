# Datastar Pro — Styling, Animation & Visual Reference

All styling in Datastar Pro is runtime/inline — zero CSS files. Use `data-style`, `data-class`,
and `data-animate` attributes to reactively control appearance. This file is the single source
for all styling, animation, view transition, and scroll behavior documentation.

For design tokens and theming, see `references/stellar.md` — Stellar CSS is the first-party
companion framework that provides CSS custom properties for consistent design systems.

For quick reference, see SKILL.md. For core concepts, see `references/core.md`.

## Table of Contents

- [data-style — Reactive Inline Styles](#data-style--reactive-inline-styles)
- [data-class — Reactive CSS Classes](#data-class--reactive-css-classes)
- [data-show — Conditional Display](#data-show--conditional-display)
- [data-animate — Animation System (Pro)](#data-animate--animation-system-pro)
- [40+ Easing Functions](#40-easing-functions)
- [data-view-transition — View Transitions (Pro)](#data-view-transition--view-transitions-pro)
- [data-scroll-into-view — Scroll Behavior (Pro)](#data-scroll-into-view--scroll-behavior-pro)
- [data-on-intersect — Intersection Observer](#data-on-intersect--intersection-observer)
- [data-on-raf — RequestAnimationFrame (Pro)](#data-on-raf--requestanimationframe-pro)
- [data-on-resize — Resize Observer (Pro)](#data-on-resize--resize-observer-pro)
- [Timing Modifiers](#timing-modifiers-apply-to-many-attributes)
- [Practical Recipes](#practical-recipes)
- [Animation Performance Tips](#animation-performance-tips)
- [Inspector Design Tokens](#inspector-design-tokens-css-custom-properties)
- [Text Transformation Utilities](#text-transformation-utilities)

---

## data-style — Reactive Inline Styles

Set inline CSS properties that update reactively when signals change.

### Single Property (Key Syntax)

```html
<div data-style:backgroundColor="$color"></div>
<div data-style:fontSize="$size + 'px'"></div>
<div data-style:opacity="$isVisible ? 1 : 0"></div>
<div data-style:transform="'translateX(' + $offset + 'px)'"></div>
```

Property names use **camelCase** — automatically converted to kebab-case in CSS.

### Object Syntax (Multiple Properties)

```html
<div data-style='{"fontSize": $size + "px", "opacity": $fade, "color": $theme === "dark" ? "white" : "black"}'></div>
```

### Signal-Driven Themes

```html
<div data-signals:theme="'light'"
     data-style:backgroundColor="$theme === 'dark' ? '#1a1a2e' : '#ffffff'"
     data-style:color="$theme === 'dark' ? '#e0e0e0' : '#333333'">
  <button data-on:click="$theme = $theme === 'dark' ? 'light' : 'dark'">
    Toggle Theme
  </button>
  <p>Content styled by signal</p>
</div>
```

### Behavior Notes

- Auto-converts camelCase to kebab-case (`backgroundColor` → `background-color`)
- MutationObserver tracks external style changes
- Restores original styles on element cleanup
- Expressions re-evaluate whenever referenced signals change

---

## data-class — Reactive CSS Classes

Toggle CSS classes based on signal expressions.

### Single Class (Key Syntax)

```html
<div data-class:active="$isActive"></div>
<div data-class:hidden="!$visible"></div>
<button data-class:selected="$tab === 'home'" data-class:disabled="$loading"></button>
```

### Object Syntax (Multiple Classes)

```html
<div data-class='{"active": $isActive, "highlighted": $isNew, "error": $hasError}'></div>
```

### Casing Modifier

Convert signal-derived class names between casing conventions:

```html
<!-- Convert camelCase signal value to kebab-case class name -->
<div data-class:myClass__casing.kebab="true"></div>
<!-- Outputs: class="my-class" -->
```

Casing options: `camel`, `kebab`, `snake`, `pascal`.

### Navigation/Tab Pattern

```html
<div data-signals:activeTab="'home'">
  <button data-class:active="$activeTab === 'home'"
          data-on:click="$activeTab = 'home'">Home</button>
  <button data-class:active="$activeTab === 'settings'"
          data-on:click="$activeTab = 'settings'">Settings</button>
</div>
```

### Behavior Notes

- Supports space-separated class names
- Uses `CSS.escape()` for safe class names
- Expression must evaluate to truthy/falsy

---

## data-show — Conditional Display

Toggle `display: none` based on a boolean expression.

```html
<div data-show="$isVisible">Shown when $isVisible is true</div>
<div data-show="$items.length > 0">Items exist</div>
<div data-show="!$loading && $results.length === 0">No results found</div>
```

Preserves the element's original display value when re-shown.

---

## data-animate — Animation System (Pro)

Animate CSS properties using Datastar's built-in animation engine. Uses `requestAnimationFrame`
for smooth, GPU-friendly rendering.

### Basic Syntax

```
data-animate:property="targetValue"
```

Add modifiers with `__`:

```
data-animate:property="targetValue"__duration.1000ms__ease.outcubic__delay.200ms
```

### Simple Fade-In

```html
<div data-signals:show="false"
     data-animate:opacity="$show ? 1 : 0"__duration.500ms__ease.outcubic
     data-style:opacity="0"
     data-init__delay.100ms="$show = true">
  Fades in on load
</div>
```

### Slide + Fade Entrance

```html
<div data-signals:entered="false"
     data-animate:opacity="$entered ? 1 : 0"__duration.600ms__ease.outcubic
     data-animate:transform="$entered ? 'translateY(0)' : 'translateY(-20px)'"__duration.600ms__ease.outback
     data-style:opacity="0"
     data-style:transform="'translateY(-20px)'"
     data-init__delay.100ms="$entered = true">
  Slides down and fades in
</div>
```

### Staggered Entrance Sequence

Use `delay` modifier to stagger child animations:

```html
<div data-signals:animateIn="false"
     data-init__delay.100ms="$animateIn = true">

  <h1 data-animate:opacity="$animateIn ? 1 : 0"__duration.600ms__ease.outcubic
      data-animate:transform="$animateIn ? 'translateY(0)' : 'translateY(-20px)'"__duration.600ms__ease.outback
      data-style:opacity="0"
      data-style:transform="'translateY(-20px)'">
    Welcome
  </h1>

  <p data-animate:opacity="$animateIn ? 1 : 0"__duration.600ms__ease.outcubic__delay.200ms
     data-animate:transform="$animateIn ? 'translateY(0)' : 'translateY(-20px)'"__duration.600ms__ease.outback__delay.200ms
     data-style:opacity="0"
     data-style:transform="'translateY(-20px)'">
    Subtitle text
  </p>

  <button data-animate:opacity="$animateIn ? 1 : 0"__duration.600ms__ease.outcubic__delay.400ms
          data-style:opacity="0">
    Get Started
  </button>
</div>
```

### Continuous Loop

```html
<!-- Continuous rotation (loading spinner) -->
<div data-animate:transform="'rotate(360deg)'"__duration.3s__ease.linear__loop>
  Loading...
</div>
```

### Ping-Pong (Alternating)

```html
<!-- Pulsing scale effect -->
<div data-animate:transform="'scale(1.1)'"__duration.1s__ease.inoutsine__pingpong>
  Pulse
</div>
```

### Signal-Driven Animation

```html
<div data-signals:progress="0">
  <div data-animate:width="$progress + '%'"__duration.300ms__ease.outcubic
       data-style='{"height": "8px", "backgroundColor": "#4CAF50", "borderRadius": "4px"}'>
  </div>
  <input type="range" data-bind="$progress" min="0" max="100" />
</div>
```

### Phase-Based Animation Sequences

Chain animations using signal phases and `data-effect`:

```html
<div data-signals:phase="0">

  <!-- Phase 1: Fade in background -->
  <div data-init__delay.100ms="$phase = 1"
       data-animate:opacity="$phase >= 1 ? 1 : 0"__duration.500ms__ease.outcubic>

    <!-- Phase 2: Slide in content (after bg fades) -->
    <div data-effect="$phase === 1 && setTimeout(() => $phase = 2, 500)"
         data-animate:transform="$phase >= 2 ? 'translateX(0)' : 'translateX(-100%)'"__duration.400ms__ease.outback>

      <!-- Phase 3: Pop in button (after content slides) -->
      <button data-effect="$phase === 2 && setTimeout(() => $phase = 3, 400)"
              data-animate:transform="$phase >= 3 ? 'scale(1)' : 'scale(0)'"__duration.300ms__ease.outelastic>
        Action
      </button>
    </div>
  </div>
</div>
```

### Scroll-Driven Animation

Combine with `data-on:scroll` and `@fit` for parallax effects:

```html
<div data-signals:scrollY="0"
     data-on:scroll__window__throttle.16ms="$scrollY = window.scrollY">

  <!-- Parallax: moves at half scroll speed -->
  <div data-style:transform="'translateY(' + @fit($scrollY, 0, 1000, 0, -200) + 'px)'">
    Parallax content
  </div>

  <!-- Fade in as user scrolls down -->
  <div data-style:opacity="@fit($scrollY, 200, 600, 0, 1)">
    Appears on scroll
  </div>
</div>
```

### All Modifiers

| Modifier | Syntax | Default | Description |
|----------|--------|---------|-------------|
| `duration` | `__duration.Xms` or `__duration.Xs` | `1000ms` | Animation duration |
| `delay` | `__delay.Xms` or `__delay.Xs` | `0` | Delay before start |
| `ease` | `__ease.easingName` | `linear` | Easing function |
| `loop` | `__loop` | off | Infinite repeat |
| `pingpong` | `__pingpong` | off | Alternate direction each cycle |

### Supported Value Types

- Numeric: `100`, `1.5`
- Suffixed: `100px`, `50%`, `360deg`, `2rem`
- String transforms: `'translateX(100px)'`, `'rotate(45deg) scale(1.5)'`

---

## 40+ Easing Functions

| Category | Functions |
|----------|-----------|
| Linear | `linear` |
| Quadratic | `quadratic`, `inquad`, `outquad`, `inoutquad` |
| Cubic | `cubic`, `incubic`, `outcubic`, `inoutcubic` |
| Quartic | `inquart`, `outquart`, `inoutquart` |
| Quintic | `inquint`, `outquint`, `inoutquint` |
| Sine | `insine`, `outsine`, `inoutsine` |
| Exponential | `inexpo`, `outexpo`, `inoutexpo` |
| Circular | `incirc`, `outcirc`, `inoutcirc` |
| Elastic | `inelastic`, `outelastic`, `inoutelastic` |
| Back | `inback`, `outback`, `inoutback` |
| Bounce | `inbounce`, `outbounce`, `inoutbounce` |
| Golden Ratio | `ingolden`, `outgolden`, `inoutgolden` |

**Naming convention:** `in` = slow start, `out` = slow end, `inout` = slow both ends.

**Common choices:**
- **UI transitions:** `outcubic` (smooth deceleration)
- **Entrances:** `outback` (slight overshoot, feels natural)
- **Exits:** `incubic` (smooth acceleration away)
- **Bouncy elements:** `outelastic` or `outbounce`
- **Loading spinners:** `linear` (constant speed)
- **Attention-grab:** `inoutsine` (gentle pulse)

### Math Utilities (Available in Expressions)

```
lerp(min, max, t, clamped?)         // Linear interpolation
inverseLerp(min, max, value, clamped?) // Inverse lerp
clamp(value, min, max)              // Constrain to range
@fit(value, inMin, inMax, outMin, outMax) // Remap between ranges
```

---

## data-view-transition — View Transitions (Pro)

Leverages the browser's View Transitions API for smooth page/content transitions.

### Basic Setup

```html
<!-- Assign a transition name to an element -->
<img data-view-transition="'hero-image'" src="thumb.jpg" />

<!-- Navigate with view transition -->
<a data-on:click__prevent__viewtransition="@get('/page/detail')">
  View Detail
</a>
```

### Shared-Element Transitions

When source and target elements share the same `view-transition-name`, the browser
animates between them automatically:

```html
<!-- Page 1: thumbnail -->
<img data-view-transition="'product-' + $id" src="thumb.jpg"
     data-on:click__prevent__viewtransition="@get('/product/' + $id)" />

<!-- Page 2 (server response): full image -->
<img data-view-transition="'product-' + $id" src="full.jpg" />
```

### SSE with View Transitions

The server can trigger transitions via the `useViewTransition` field:

```
event: datastar-patch-elements
data: selector #main-content
data: mode outer
data: useViewTransition true
data: elements <div id="main-content"><img data-view-transition="'hero-image'" src="full.jpg" /></div>

```

### Key Details

- `data-view-transition="name"` sets the `view-transition-name` CSS property
- `viewtransition` modifier on `data-on` wraps the callback in `document.startViewTransition()`
- `useViewTransition: true` in SSE response applies transitions during DOM patch
- Gracefully degrades in unsupported browsers (no error, no transition)
- Matching `view-transition-name` values on source/target create shared-element transitions

### Custom Transition Styles

Pair with a `<style>` block for custom transition animations:

```html
<style>
  ::view-transition-old(hero-image) {
    animation: 300ms ease-out fade-out;
  }
  ::view-transition-new(hero-image) {
    animation: 300ms ease-in fade-in;
  }
</style>
```

---

## data-scroll-into-view — Scroll Behavior (Pro)

Scroll an element into view with configurable alignment and behavior.

### Basic Usage

```html
<!-- Smooth scroll to element on load -->
<div data-scroll-into-view>Target element</div>

<!-- Smooth scroll, centered vertically and horizontally -->
<div data-scroll-into-view__smooth__vcenter__hcenter>Centered element</div>

<!-- Instant scroll, aligned to top -->
<div data-scroll-into-view__instant__vstart>Top-aligned element</div>
```

### Focus Modifier (Accessibility)

The `focus` modifier focuses the element after scrolling and sets `tabindex` if needed:

```html
<!-- Modal heading receives focus after scroll -->
<h2 data-scroll-into-view__focus
    data-show="$modalOpen"
    tabindex="-1">
  Modal Title
</h2>
```

### Conditional Scroll (with data-show)

```html
<!-- Scroll to error message when it appears -->
<div data-show="$hasError"
     data-scroll-into-view__smooth__vstart>
  <p data-text="$errorMessage"></p>
</div>
```

### All Modifiers

| Category | Modifiers | Default |
|----------|-----------|---------|
| Behavior | `smooth`, `instant`, `auto` | `smooth` |
| Vertical | `vstart`, `vcenter`, `vend`, `vnearest` | `vcenter` |
| Horizontal | `hstart`, `hcenter`, `hend`, `hnearest` | `hcenter` |
| Focus | `focus` | off |

---

## data-on-intersect — Intersection Observer

Trigger expressions when elements enter or exit the viewport. Useful for
scroll-triggered animations and lazy loading.

```html
<!-- Fire once when element is 50% visible -->
<div data-on-intersect__half__once="$cardVisible = true">
  <div data-animate:opacity="$cardVisible ? 1 : 0"__duration.600ms__ease.outcubic
       data-style:opacity="0">
    Card content
  </div>
</div>

<!-- Fire when element fully visible -->
<div data-on-intersect__full="$inView = true"
     data-on-intersect__exit="$inView = false">
  <div data-class:animate-in="$inView">Content</div>
</div>

<!-- Custom threshold (30% visible) -->
<div data-on-intersect__threshold.30="@get('/api/lazy-content')"></div>
```

### Modifiers

| Modifier | Description |
|----------|-------------|
| `full` | Fires when 100% visible |
| `half` | Fires when 50% visible |
| `threshold.N` | Fires at N% visible (0-100) |
| `exit` | Fires when leaving viewport |
| `once` | Fires only once per element |

---

## data-on-raf — RequestAnimationFrame (Pro)

Execute expressions on every animation frame. Use sparingly — runs at 60fps.

```html
<div data-signals:rotation="0"
     data-on-raf="$rotation = ($rotation + 1) % 360"
     data-style:transform="'rotate(' + $rotation + 'deg)'">
  Spinning element
</div>
```

---

## data-on-resize — Resize Observer (Pro)

Execute expressions when an element's size changes.

```html
<div data-signals:width="0"
     data-on-resize="$width = $el.offsetWidth"
     data-class:compact="$width < 400"
     data-class:wide="$width >= 400">
  Responsive content
</div>
```

---

## Timing Modifiers (Apply to Many Attributes)

These modifiers work on `data-on`, `data-init`, `data-animate`, and other timed attributes.

| Modifier | Syntax | Description |
|----------|--------|-------------|
| `delay` | `__delay.500ms` or `__delay.1s` | Wait before executing |
| `debounce` | `__debounce.300ms` | Execute after pause in triggers |
| `throttle` | `__throttle.200ms` | Execute at most once per interval |

### Debounce Options

```html
<!-- Leading edge: fire immediately, then wait -->
<input data-on:input__debounce.300ms.leading="@get('/search')" />

<!-- No trailing: skip the final delayed call -->
<input data-on:input__debounce.300ms.notrailing="@get('/search')" />
```

### Throttle Options

```html
<!-- No leading: skip the initial immediate call -->
<div data-on:scroll__window__throttle.100ms.noleading="$scrollY = window.scrollY"></div>

<!-- With trailing: include the final call after throttle period -->
<div data-on:mousemove__throttle.50ms.trailing="$mouseX = event.clientX"></div>
```

---

## Practical Recipes

### Fade-In Cards on Scroll

```html
<div data-signals:card1="false" data-signals:card2="false" data-signals:card3="false">

  <div data-on-intersect__half__once="$card1 = true"
       data-animate:opacity="$card1 ? 1 : 0"__duration.600ms__ease.outcubic
       data-animate:transform="$card1 ? 'translateY(0)' : 'translateY(30px)'"__duration.600ms__ease.outback
       data-style:opacity="0"
       data-style:transform="'translateY(30px)'">
    Card 1 content
  </div>

  <div data-on-intersect__half__once="$card2 = true"
       data-animate:opacity="$card2 ? 1 : 0"__duration.600ms__ease.outcubic__delay.100ms
       data-animate:transform="$card2 ? 'translateY(0)' : 'translateY(30px)'"__duration.600ms__ease.outback__delay.100ms
       data-style:opacity="0"
       data-style:transform="'translateY(30px)'">
    Card 2 content
  </div>

  <div data-on-intersect__half__once="$card3 = true"
       data-animate:opacity="$card3 ? 1 : 0"__duration.600ms__ease.outcubic__delay.200ms
       data-animate:transform="$card3 ? 'translateY(0)' : 'translateY(30px)'"__duration.600ms__ease.outback__delay.200ms
       data-style:opacity="0"
       data-style:transform="'translateY(30px)'">
    Card 3 content
  </div>
</div>
```

### Skeleton Loading Placeholder

```html
<div data-signals:loaded="false"
     data-init="@get('/api/content')">

  <!-- Skeleton (shown while loading) -->
  <div data-show="!$loaded"
       data-style='{"height":"200px","borderRadius":"8px","background":"linear-gradient(90deg,#f0f0f0 25%,#e0e0e0 50%,#f0f0f0 75%)","backgroundSize":"200% 100%"}'
       data-animate:backgroundPosition="'-200% 0'"__duration.1.5s__ease.linear__loop>
  </div>

  <!-- Actual content (shown after load) -->
  <div data-show="$loaded" id="content-target"
       data-animate:opacity="$loaded ? 1 : 0"__duration.300ms__ease.outcubic
       data-style:opacity="0">
  </div>
</div>
```

### Notification Slide-In

```html
<div data-signals:showNotify="false" data-signals:notifyMsg="''">
  <div data-show="$showNotify"
       data-animate:transform="$showNotify ? 'translateX(0)' : 'translateX(100%)'"__duration.300ms__ease.outback
       data-animate:opacity="$showNotify ? 1 : 0"__duration.300ms__ease.outcubic
       data-style='{"position":"fixed","top":"20px","right":"20px","padding":"16px 24px","background":"#323232","color":"white","borderRadius":"8px","zIndex":"1000"}'
       data-style:transform="'translateX(100%)'">
    <span data-text="$notifyMsg"></span>
    <button data-on:click="$showNotify = false"
            data-style='{"marginLeft":"12px","background":"none","border":"none","color":"white","cursor":"pointer"}'>
      X
    </button>
  </div>
</div>
```

### Dark Mode Toggle

```html
<div data-signals:dark="false"
     data-style:backgroundColor="$dark ? '#1a1a2e' : '#ffffff'"
     data-style:color="$dark ? '#e0e0e0' : '#333333'"
     data-style:transition="'background-color 0.3s, color 0.3s'">

  <button data-on:click="$dark = !$dark"
          data-text="$dark ? 'Light Mode' : 'Dark Mode'">
  </button>

  <div data-style:backgroundColor="$dark ? '#16213e' : '#f5f5f5'"
       data-style:padding="'20px'"
       data-style:borderRadius="'8px'"
       data-style:transition="'background-color 0.3s'">
    Card content adapts to theme
  </div>
</div>
```

---

## Animation Performance Tips

- **Prefer `transform` and `opacity`** — these are GPU-composited and avoid layout thrashing
- **Avoid animating** `width`, `height`, `top`, `left` — they trigger expensive layout recalculations
- **Use `@peek`** to read signals in animation expressions without creating reactive subscriptions
- **Use `@fit`** to remap values (e.g., scroll position to opacity) without intermediate signals
- **Use `data-on-raf` sparingly** — it runs at 60fps and can cause performance issues if the expression is heavy
- **Throttle scroll handlers** — `data-on:scroll__window__throttle.16ms` limits to ~60fps

---

## Inspector Design Tokens (CSS Custom Properties)

Datastar Pro's inspector uses design tokens for theming. Useful if building inspector-like UIs.

### Light Theme

```css
--inspector-bg: #ebede9;
--inspector-bg-light: #c7cfcc;
--inspector-bg-hover: #d9dedc;
--inspector-bg-dark: #a8b5b2;
--inspector-color: #090a14;
--inspector-color-blur: #819796;
--inspector-color-filtered: #d73a49;
--inspector-color-matched: #28a745;
--color-purple: #A599FF;
--color-gold: #FFA116;
--color-html5: #E34C26;
```

### Dark Theme (`prefers-color-scheme: dark`)

```css
--inspector-bg: #202e37;
--inspector-bg-light: #394a50;
--inspector-bg-hover: #1a262e;
--inspector-bg-dark: #577277;
--inspector-color: #ebede9;
--inspector-color-filtered: #f97583;
--inspector-color-matched: #34d058;
```

### Signal Highlight Animation

```css
@keyframes datastar-highlight-pulse {
  0%, 100% { box-shadow: 0 0 0 2px rgba(165,153,255,0.8); }
  50% { box-shadow: 0 0 0 4px rgba(165,153,255,1); }
}
.datastar-signal-highlight {
  animation: datastar-highlight-pulse 0.8s ease-in-out infinite;
}
```

---

## Text Transformation Utilities

Available in the Datastar runtime for programmatic casing conversion:

```typescript
kebab(str)   // camelCase → kebab-case (for CSS properties)
camel(str)   // kebab-case → camelCase (for JS objects)
snake(str)   // → snake_case
pascal(str)  // → PascalCase
title(str)   // → Title Case
modifyCasing(str, mods, defaultCase='camel')
```
