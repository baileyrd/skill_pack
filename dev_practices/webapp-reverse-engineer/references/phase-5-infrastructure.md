# Phase 5: Infrastructure & Deployment

Goal: Identify the hosting, CDN, and deployment infrastructure.

### 5.1 DNS & Hosting Clues

Look at the response headers and script sources for hosting signals:
- `server: Vercel` → Vercel
- `x-vercel-id` → Vercel
- `x-amz-*` headers → AWS
- `cf-ray` header → Cloudflare
- `x-served-by: cache-*` → Fastly
- `fly-request-id` → Fly.io
- `netlify` in headers → Netlify
- `railway` → Railway
- Script sources from `*.supabase.co` → Supabase
- Script sources from `*.firebaseio.com` → Firebase

### 5.2 Deployment Patterns

```javascript
(() => {
  const patterns = {};

  // Check for service worker (PWA)
  patterns.serviceWorker = 'serviceWorker' in navigator;

  // Check manifest
  const manifest = document.querySelector('link[rel="manifest"]');
  patterns.webManifest = manifest ? manifest.href : null;

  // Environment hints
  const envHints = {};
  if (window.__ENV__) envHints.__ENV__ = Object.keys(window.__ENV__);
  if (window.__CONFIG__) envHints.__CONFIG__ = Object.keys(window.__CONFIG__);
  if (window.ENV) envHints.ENV = Object.keys(window.ENV);
  patterns.envHints = envHints;

  // Check for common deployment artifacts
  patterns.nextjs = !!window.__NEXT_DATA__;
  patterns.buildId = window.__NEXT_DATA__?.buildId;

  return JSON.stringify(patterns, null, 2);
})()
```

---
