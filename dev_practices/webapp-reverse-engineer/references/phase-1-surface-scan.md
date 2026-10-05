# Phase 1: First Impressions & Surface Scan

Goal: Identify the broad technology fingerprint without going deep yet.

## Contents

- [1.1 HTTP Headers & Meta Tags](#11-http-headers--meta-tags)
- [1.2 Framework Fingerprinting](#12-framework-fingerprinting)
- [1.3 Script & Stylesheet Inventory](#13-script--stylesheet-inventory)

### 1.1 HTTP Headers & Meta Tags

Run this JavaScript to extract server-side clues:

```javascript
(async () => {
  // Fetch the page to read response headers
  const res = await fetch(window.location.href, { method: 'HEAD' });
  const headers = {};
  res.headers.forEach((v, k) => headers[k] = v);

  // Gather meta tags
  const metas = [...document.querySelectorAll('meta')].map(m => ({
    name: m.getAttribute('name') || m.getAttribute('property') || m.getAttribute('http-equiv'),
    content: m.getAttribute('content')
  })).filter(m => m.name);

  // Check for generator tags
  const generator = document.querySelector('meta[name="generator"]')?.content;

  return JSON.stringify({ headers, metas, generator }, null, 2);
})()
```

**What to look for:**
- `X-Powered-By` → server framework (Express, ASP.NET, PHP, etc.)
- `Server` → web server (nginx, Apache, Cloudflare, Vercel, Netlify)
- `X-Frame-Options`, `Content-Security-Policy` → security posture
- `Set-Cookie` → session management approach
- `meta[name="generator"]` → CMS or framework (Next.js, WordPress, Hugo, etc.)

### 1.2 Framework Fingerprinting

Run this JavaScript to detect client-side frameworks:

```javascript
(() => {
  const signals = {};

  // React
  const reactRoot = document.querySelector('[data-reactroot], #__next, #___gatsby');
  signals.react = !!(window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || reactRoot
    || document.querySelector('[data-react-helmet]'));

  // Next.js
  signals.nextjs = !!(document.getElementById('__NEXT_DATA__')
    || window.__NEXT_DATA__ || window.__next);

  // Vue
  signals.vue = !!(window.__VUE__ || window.__vue_app__
    || document.querySelector('[data-v-]') || document.querySelector('#app.__vue-content-placeholders'));

  // Nuxt
  signals.nuxt = !!(window.__NUXT__ || window.$nuxt || document.getElementById('__nuxt'));

  // Angular
  signals.angular = !!(window.ng || document.querySelector('[ng-version]')
    || document.querySelector('[_nghost-ng-]') || window.getAllAngularRootElements);

  // Svelte / SvelteKit
  signals.svelte = !!(document.querySelector('[class*="svelte-"]')
    || document.querySelector('script[data-sveltekit-hydrate]'));

  // Remix
  signals.remix = !!(window.__remixContext || window.__remixManifest);

  // Astro
  signals.astro = !!document.querySelector('[data-astro-cid]');

  // jQuery
  signals.jquery = !!(window.jQuery || window.$?.fn?.jquery);

  // Tailwind (check for utility classes)
  const hasTailwind = [...document.querySelectorAll('[class]')].some(el =>
    /\b(flex|grid|p-\d|m-\d|text-\w|bg-\w|rounded|shadow)\b/.test(el.className));
  signals.tailwind = hasTailwind;

  // Webpack / Vite
  signals.webpack = !!(window.webpackJsonp || window.webpackChunk
    || document.querySelector('script[src*="webpack"]'));
  signals.vite = !!document.querySelector('script[type="module"][src*="/@vite"]');

  // State management
  signals.redux = !!window.__REDUX_DEVTOOLS_EXTENSION__;
  signals.mobx = !!window.__MOBX_DEVTOOLS_GLOBAL_HOOK__;
  signals.zustand = !!window.__zustand;

  // Filter to only detected signals
  const detected = Object.entries(signals).filter(([_, v]) => v).map(([k]) => k);
  return JSON.stringify({ detected, raw: signals }, null, 2);
})()
```

### 1.3 Script & Stylesheet Inventory

```javascript
(() => {
  const scripts = [...document.querySelectorAll('script[src]')].map(s => {
    const url = new URL(s.src, window.location.origin);
    return {
      src: s.src,
      isThirdParty: url.hostname !== window.location.hostname,
      type: s.type || 'text/javascript',
      async: s.async,
      defer: s.defer,
      hostname: url.hostname
    };
  });

  const styles = [...document.querySelectorAll('link[rel="stylesheet"]')].map(l => {
    const url = new URL(l.href, window.location.origin);
    return {
      href: l.href,
      isThirdParty: url.hostname !== window.location.hostname,
      hostname: url.hostname
    };
  });

  // Group third-party scripts by domain
  const thirdPartyDomains = {};
  scripts.filter(s => s.isThirdParty).forEach(s => {
    if (!thirdPartyDomains[s.hostname]) thirdPartyDomains[s.hostname] = [];
    thirdPartyDomains[s.hostname].push(s.src);
  });

  return JSON.stringify({
    totalScripts: scripts.length,
    firstPartyScripts: scripts.filter(s => !s.isThirdParty).length,
    thirdPartyScripts: scripts.filter(s => s.isThirdParty).length,
    thirdPartyDomains,
    stylesheets: styles.length,
    scripts: scripts.slice(0, 30) // Cap to avoid huge output
  }, null, 2);
})()
```

**Identify third-party services that are relevant to cloning** — focus on:
- Auth providers (Auth0, Firebase Auth, Clerk, Supabase Auth)
- Payment processors (Stripe, PayPal)
- Real-time services (Pusher, Ably, Firebase Realtime)
- Search (Algolia, Typesense, Elasticsearch)
- Analytics only if they reveal architecture (e.g., Segment implies event-driven patterns)

Ignore purely observational third parties (Google Analytics, Hotjar, etc.) unless the
user specifically asks.

---
