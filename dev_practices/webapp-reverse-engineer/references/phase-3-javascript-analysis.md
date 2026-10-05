# Phase 3: Deep JavaScript Analysis

Goal: Understand the application's internal architecture by inspecting its JavaScript.

## Contents

- [3.1 Source Map Detection](#31-source-map-detection)
- [3.2 Bundle Analysis](#32-bundle-analysis)
- [3.3 Route Structure Discovery](#33-route-structure-discovery)
- [3.4 Data Model Inference](#34-data-model-inference)
- [3.5 State Management Deep Dive](#35-state-management-deep-dive)

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
