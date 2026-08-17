# Runtime Probes — Web Shell

Reusable JavaScript snippets for live introspection of a web shell. Each
probe is self-contained and returns a JSON-serializable result. Run them
via `javascript_tool` (Claude in Chrome), `browser_evaluate` (Playwright
MCP), or DevTools Console.

The probes assume `document` and `window` are available. They are designed
to be safe (read-only) and tolerant of partial framework support.

---

## Probe Index

| Probe | Used by phase |
|-------|---------------|
| `frameworkFingerprint` | 01, 02 |
| `regionInventory`      | 03 layout |
| `breakpointObserver`   | 03 layout |
| `routeMap`             | 04 navigation |
| `commandPaletteProbe`  | 04 navigation, 10 extensibility |
| `focusTrap`            | 05 accessibility |
| `ariaCoverage`         | 05 accessibility |
| `keyboardMap`          | 05 accessibility |
| `stateManager`         | 06 state |
| `loadingErrorEmpty`    | 06 state |
| `paintTimings`         | 07 performance |
| `transitionJank`       | 07 performance |
| `tokenAudit`           | 08 theming |
| `themeSwitch`          | 08 theming |
| `pluginSlots`          | 10 extensibility |
| `errorBoundary`        | 11 observability |
| `telemetrySinks`       | 11 observability |
| `persistedLayout`      | 13 persistence |

---

## frameworkFingerprint

```javascript
(() => {
  const s = {};
  s.react = !!(window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || document.querySelector('[data-reactroot], #__next, #___gatsby'));
  s.nextjs = !!(window.__NEXT_DATA__ || document.getElementById('__NEXT_DATA__'));
  s.vue = !!(window.__VUE__ || window.__vue_app__ || document.querySelector('[data-v-]'));
  s.nuxt = !!(window.__NUXT__ || window.$nuxt);
  s.angular = !!(window.ng || document.querySelector('[ng-version]'));
  s.svelte = !!document.querySelector('[class*="svelte-"]');
  s.solid = !!document.querySelector('[data-hk]');
  s.qwik = !!document.querySelector('[q\\:container]');
  s.remix = !!window.__remixContext;
  s.astro = !!document.querySelector('[data-astro-cid]');
  s.htmx = !!window.htmx;
  s.datastar = !!(window.Datastar || document.querySelector('[data-on-load], [data-signals]'));
  s.alpine = !!window.Alpine;
  s.tauriEmbedded = !!window.__TAURI__;
  s.electronEmbedded = !!(window.electronAPI || window.process?.versions?.electron);
  return Object.fromEntries(Object.entries(s).filter(([, v]) => v));
})()
```

## regionInventory

Inventory the shell's high-level regions: header, sidebar, main, footer,
status bar, drawer, modal layer.

```javascript
(() => {
  const candidates = {
    header:    'header, [role="banner"], [data-region="header"], .app-header, .topbar',
    nav:       'nav, [role="navigation"], aside nav, [data-region="nav"]',
    sidebar:   'aside, [role="complementary"], [data-region="sidebar"], .sidebar',
    main:      'main, [role="main"], [data-region="main"], .app-main',
    footer:    'footer, [role="contentinfo"], [data-region="footer"]',
    statusbar: '[role="status"], [data-region="statusbar"], .statusbar',
    modalRoot: '[data-modal-root], [role="dialog"], .modal-root, #modal-root',
    drawerRoot: '[data-drawer-root], .drawer-root',
    commandPalette: '[role="combobox"][aria-expanded], [data-command-palette], .cmdk-root, [cmdk-root]'
  };
  const results = {};
  for (const [name, sel] of Object.entries(candidates)) {
    const els = [...document.querySelectorAll(sel)];
    results[name] = els.length === 0 ? null : {
      count: els.length,
      first: els[0] ? {
        tag: els[0].tagName.toLowerCase(),
        rect: els[0].getBoundingClientRect().toJSON(),
        ariaLabel: els[0].getAttribute('aria-label')
      } : null
    };
  }
  results.viewport = { w: window.innerWidth, h: window.innerHeight, dpr: window.devicePixelRatio };
  return results;
})()
```

## breakpointObserver

Resize the window across common breakpoints (call once per width). For
Playwright/Puppeteer, use `page.setViewportSize` between calls; for
Claude in Chrome, use `resize_window` then re-run `regionInventory`.

Common widths to test: 360 (mobile), 768 (tablet), 1024 (laptop), 1440
(desktop), 1920 (large).

## routeMap

```javascript
(() => {
  const internal = (h) => {
    try { return new URL(h, location.origin).hostname === location.hostname; }
    catch { return false; }
  };
  const links = [...document.querySelectorAll('a[href]')]
    .map(a => new URL(a.href, location.origin).pathname)
    .filter((v, i, a) => internal(v) && a.indexOf(v) === i)
    .sort();
  const buildManifest = window.__BUILD_MANIFEST;
  const nextRoutes = buildManifest ? Object.keys(buildManifest).filter(k => !k.startsWith('_')) : null;
  return {
    discoveredFromLinks: links,
    framework: nextRoutes ? 'next.js' : null,
    declaredRoutes: nextRoutes
  };
})()
```

## commandPaletteProbe

```javascript
(() => {
  const triggers = ['Mod+K', 'Mod+Shift+P', 'Mod+/', '?'];
  const palette = document.querySelector('[role="combobox"][aria-expanded], [cmdk-root], [data-command-palette]');
  const dispatch = (combo) => {
    const evt = new KeyboardEvent('keydown', {
      key: combo.split('+').pop(),
      ctrlKey: combo.includes('Mod'),
      metaKey: combo.includes('Mod'),
      shiftKey: combo.includes('Shift'),
      bubbles: true
    });
    document.dispatchEvent(evt);
  };
  return {
    paletteFoundAtStartup: !!palette,
    paletteRect: palette?.getBoundingClientRect().toJSON() || null,
    knownTriggers: triggers,
    note: 'Dispatch each trigger via dispatch(combo) and re-query for the palette node.'
  };
})()
```

## focusTrap

```javascript
(() => {
  const focusable = [...document.querySelectorAll(
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
  )];
  const dialogs = [...document.querySelectorAll('[role="dialog"], dialog[open]')];
  return {
    focusableCount: focusable.length,
    activeDialog: dialogs.find(d => d.getAttribute('aria-modal') === 'true' || d.open) ? true : false,
    activeElement: document.activeElement ? {
      tag: document.activeElement.tagName,
      id: document.activeElement.id,
      role: document.activeElement.getAttribute('role')
    } : null
  };
})()
```

## ariaCoverage

```javascript
(() => {
  const interactive = [...document.querySelectorAll('button, a, input, select, textarea, [role="button"], [role="link"], [role="menuitem"], [role="tab"]')];
  const missing = interactive.filter(el => {
    const hasName = el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')
      || (el.textContent && el.textContent.trim()) || el.getAttribute('title');
    return !hasName;
  });
  const landmarks = ['banner','navigation','main','complementary','contentinfo','search']
    .map(role => ({ role, count: document.querySelectorAll(`[role="${role}"], ${role === 'banner' ? 'header' : role === 'navigation' ? 'nav' : role === 'main' ? 'main' : role === 'complementary' ? 'aside' : role === 'contentinfo' ? 'footer' : ''}`).length }));
  return {
    interactiveTotal: interactive.length,
    missingAccessibleName: missing.length,
    missingExamples: missing.slice(0, 10).map(el => el.outerHTML.slice(0, 200)),
    landmarks
  };
})()
```

## keyboardMap

```javascript
(() => {
  const shortcuts = [];
  // Heuristic: scan for `aria-keyshortcuts` and visible "kbd" elements
  document.querySelectorAll('[aria-keyshortcuts]').forEach(el => {
    shortcuts.push({ source: 'aria-keyshortcuts', combo: el.getAttribute('aria-keyshortcuts'),
                     label: el.getAttribute('aria-label') || el.textContent?.trim().slice(0, 60) });
  });
  document.querySelectorAll('kbd').forEach(el => {
    shortcuts.push({ source: 'kbd-element', combo: el.textContent.trim(),
                     context: el.parentElement?.textContent?.trim().slice(0, 80) });
  });
  return { shortcuts };
})()
```

## stateManager

```javascript
(() => {
  const s = {};
  s.redux = !!window.__REDUX_DEVTOOLS_EXTENSION__;
  s.mobx = !!window.__MOBX_DEVTOOLS_GLOBAL_HOOK__;
  s.zustand = !!window.__zustand;
  s.jotai = !!window.__jotai;
  s.recoil = !!window.__RECOIL_DEVTOOLS_EXTENSION__;
  s.reactQuery = !!window.__REACT_QUERY_STATE__ || !!document.querySelector('[data-react-query]');
  s.swr = !!window.__SWR_DEVTOOLS_REACT__;
  s.tanstackRouter = !!window.__TANSTACK_ROUTER__;
  return Object.fromEntries(Object.entries(s).filter(([, v]) => v));
})()
```

## loadingErrorEmpty

Heuristics to detect each state's presence in the live shell. Run *after*
navigating to a page in each condition (loading, error, empty data).

```javascript
(() => {
  const skeletons = document.querySelectorAll('[class*="skeleton"], [aria-busy="true"], [data-loading="true"]').length;
  const spinners = document.querySelectorAll('[role="progressbar"], [class*="spinner"], [class*="loading"]').length;
  const errors = document.querySelectorAll('[role="alert"], [class*="error"], [data-error]').length;
  const empties = document.querySelectorAll('[data-empty], [class*="empty-state"]').length;
  return { skeletons, spinners, errors, empties };
})()
```

## paintTimings

```javascript
(() => {
  const paint = performance.getEntriesByType('paint');
  const nav = performance.getEntriesByType('navigation')[0];
  return {
    fcp: paint.find(p => p.name === 'first-contentful-paint')?.startTime,
    fp: paint.find(p => p.name === 'first-paint')?.startTime,
    domContentLoaded: nav?.domContentLoadedEventEnd,
    loadEvent: nav?.loadEventEnd,
    transferSize: nav?.transferSize,
    encodedBodySize: nav?.encodedBodySize
  };
})()
```

## transitionJank

Install before triggering a route transition; collect after.

```javascript
(() => {
  if (window.__jankObserver) return 'already installed';
  window.__longTasks = [];
  const obs = new PerformanceObserver(list => {
    for (const e of list.getEntries()) window.__longTasks.push({ start: e.startTime, duration: e.duration });
  });
  obs.observe({ entryTypes: ['longtask'] });
  window.__jankObserver = obs;
  return 'installed; trigger transition then read window.__longTasks';
})()
```

## tokenAudit

```javascript
(() => {
  const root = getComputedStyle(document.documentElement);
  const tokens = {};
  for (let i = 0; i < root.length; i++) {
    const name = root[i];
    if (name.startsWith('--')) tokens[name] = root.getPropertyValue(name).trim();
  }
  // Sample of inline color usage that bypasses tokens
  const inline = [...document.querySelectorAll('[style*="color"], [style*="background"]')].slice(0, 20)
    .map(el => el.getAttribute('style'));
  return {
    tokenCount: Object.keys(tokens).length,
    tokenSample: Object.fromEntries(Object.entries(tokens).slice(0, 30)),
    inlineColorUsages: inline
  };
})()
```

## themeSwitch

After flipping the theme (via UI), diff the token set:

```javascript
(() => {
  const root = getComputedStyle(document.documentElement);
  const snapshot = {};
  for (let i = 0; i < root.length; i++) {
    const n = root[i];
    if (n.startsWith('--')) snapshot[n] = root.getPropertyValue(n).trim();
  }
  if (!window.__themeSnapshotA) { window.__themeSnapshotA = snapshot; return 'A captured; flip theme then re-run.'; }
  const a = window.__themeSnapshotA;
  const changed = Object.keys(snapshot).filter(k => snapshot[k] !== a[k]);
  const unchanged = Object.keys(snapshot).filter(k => snapshot[k] === a[k] && k.includes('color'));
  return { changedTokens: changed.length, unchangedColorTokens: unchanged.length, changes: changed.slice(0, 50) };
})()
```

## pluginSlots

```javascript
(() => {
  const sdkGlobals = ['aha','app','plugin','extension','sdk'].filter(k => window[k] && typeof window[k] === 'object');
  const slots = [...document.querySelectorAll('[data-slot], [data-plugin-slot], [slot]')]
    .map(el => ({ slot: el.getAttribute('slot') || el.getAttribute('data-slot') || el.getAttribute('data-plugin-slot'), tag: el.tagName.toLowerCase() }));
  return { sdkGlobals, slots: slots.slice(0, 30), slotCount: slots.length };
})()
```

## errorBoundary

```javascript
(() => {
  // Trigger a controlled error in a benign element to see if a boundary catches it.
  // Read-only version: just look for boundary indicators in the DOM.
  const boundaries = [...document.querySelectorAll('[data-error-boundary], [class*="error-boundary"]')];
  return { boundariesPresent: boundaries.length };
})()
```

## telemetrySinks

```javascript
(() => {
  const sinks = {};
  sinks.sentry = !!window.Sentry;
  sinks.datadog = !!(window.DD_RUM || window.datadogRum);
  sinks.bugsnag = !!window.Bugsnag;
  sinks.posthog = !!window.posthog;
  sinks.segment = !!window.analytics?.invoked;
  sinks.amplitude = !!window.amplitude;
  sinks.googleAnalytics = !!(window.gtag || window.ga);
  sinks.consoleErrorPatched = console.error.toString().length > 50;
  return Object.fromEntries(Object.entries(sinks).filter(([, v]) => v));
})()
```

## persistedLayout

```javascript
(() => {
  const ls = {};
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i);
    const v = localStorage.getItem(k);
    if (k && /layout|panel|sidebar|theme|ui|pref|workspace|dock/i.test(k)) {
      ls[k] = v ? v.slice(0, 200) : null;
    }
  }
  const ss = {};
  for (let i = 0; i < sessionStorage.length; i++) {
    const k = sessionStorage.key(i);
    const v = sessionStorage.getItem(k);
    if (k && /layout|panel|sidebar|theme|ui|pref/i.test(k)) ss[k] = v ? v.slice(0, 200) : null;
  }
  return {
    localStorageLayoutKeys: Object.keys(ls),
    localStorageSamples: ls,
    sessionStorageLayoutKeys: Object.keys(ss),
    indexedDBPresent: 'indexedDB' in window,
    cookieKeys: document.cookie.split(';').map(c => c.trim().split('=')[0]).filter(k => /layout|theme|ui|pref/i.test(k))
  };
})()
```
