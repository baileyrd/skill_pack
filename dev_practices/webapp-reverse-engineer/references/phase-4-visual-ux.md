# Phase 4: Visual & UX Architecture

Goal: Document the UI layer — component structure, design system, layout patterns.

## Contents

- [4.1 Component Tree Analysis](#41-component-tree-analysis)
- [4.2 Design System Detection](#42-design-system-detection)
- [4.3 Visual Documentation](#43-visual-documentation)

### 4.1 Component Tree Analysis

```javascript
(() => {
  // Walk the DOM and identify component boundaries
  const root = document.getElementById('root') || document.getElementById('__next')
    || document.getElementById('app') || document.body;

  function walkTree(el, depth = 0, maxDepth = 4) {
    if (depth > maxDepth) return null;

    const info = {
      tag: el.tagName?.toLowerCase(),
      id: el.id || undefined,
      classes: el.className && typeof el.className === 'string'
        ? el.className.split(' ').filter(c => c && !c.startsWith('svelte-') && c.length < 40).slice(0, 5)
        : undefined,
      role: el.getAttribute?.('role') || undefined,
      dataTestId: el.getAttribute?.('data-testid') || el.getAttribute?.('data-cy') || undefined,
      childCount: el.children?.length || 0
    };

    // Only recurse into structural elements
    if (el.children && el.children.length > 0 && el.children.length < 20) {
      info.children = [...el.children]
        .slice(0, 10)
        .map(c => walkTree(c, depth + 1, maxDepth))
        .filter(Boolean);
    }

    return info;
  }

  return JSON.stringify(walkTree(root), null, 2);
})()
```

### 4.2 Design System Detection

```javascript
(() => {
  const html = document.documentElement.outerHTML;

  const designSystems = {
    'Material UI / MUI': /Mui[A-Z]|mui-|MuiButton/.test(html),
    'Ant Design': /ant-|antd/.test(html),
    'Chakra UI': /chakra-/.test(html),
    'shadcn/ui': /data-radix|radix-/.test(html),
    'Radix UI': /data-radix/.test(html),
    'Headless UI': /headlessui/.test(html),
    'Bootstrap': /bootstrap|btn-primary|col-md/.test(html),
    'Tailwind UI': !!(document.querySelector('[class*="max-w-"][class*="mx-auto"]')),
    'Mantine': /mantine/.test(html)
  };

  const detected = Object.entries(designSystems).filter(([_, v]) => v).map(([k]) => k);

  // CSS methodology
  const cssApproach = {
    cssModules: !!document.querySelector('[class*="_"]') && /[a-zA-Z]+_[a-zA-Z0-9]{5,}/.test(html),
    styledComponents: /sc-[a-zA-Z]/.test(html),
    emotion: /css-[a-z0-9]+/.test(html),
    tailwind: /\b(flex|grid|p-\d|m-\d|text-\w|bg-\w)\b/.test(html),
    BEM: /[a-z]+__[a-z]+--[a-z]+/.test(html)
  };

  const detectedCSS = Object.entries(cssApproach).filter(([_, v]) => v).map(([k]) => k);

  return JSON.stringify({ designSystems: detected, cssApproach: detectedCSS }, null, 2);
})()
```

### 4.3 Visual Documentation

Take screenshots at each major section/route and after key interactions. These serve
two purposes: they help you analyze the UI during the session, and they become visual
references in the final report.

**How to capture and save screenshots for the report:**

1. Take the screenshot: `computer(action: "screenshot", tabId: ...)`
2. Claude receives the image and can analyze it visually
3. To include it in the report, save it to disk using `upload_image` or by running
   a script that captures the page via the browser

For each screenshot, note:
- The route / URL at the time of capture
- What state the UI is in (e.g., "dashboard with date filter set to 'Last 7 days'")
- What UI patterns are visible (card layout, data table, chart type, etc.)

**Key moments to screenshot:**
- Each top-level route (the "resting state" of each page)
- Before and after opening modals, drawers, or expanding sections
- Different tab states within a page
- Empty states and error states
- Mobile/responsive views if relevant (use `resize_window` to simulate)

If the report is Markdown, reference screenshots by filename:
```markdown
![Dashboard overview](screenshots/dashboard-overview.png)
```

If the report is DOCX, use the docx skill's image embedding capabilities.

---
