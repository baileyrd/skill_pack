# Phase 10 — Extensibility

Audit the shell's contribution surface: plugin slots, command palette
extension API, customization hooks, action registries, and how third-
party (or in-house) code plugs into the shell without reaching into its
guts.

A non-extensible shell is fine if it's deliberately closed. The audit
flags either: (1) extensibility claimed but not delivered, or (2)
extensibility delivered without proper isolation / failure containment.

---

## What we evaluate

| Concern               | Question                                          |
|-----------------------|---------------------------------------------------|
| Contribution model    | Is there one? What can be contributed?            |
| Slot inventory        | Where in the shell can third-parties render?      |
| Command / action API  | Can extensions register palette commands?         |
| Menu contribution     | Can extensions add menu items / context items?    |
| Settings contribution | Can extensions add settings panels?               |
| Theming contribution  | Can extensions add theme tokens?                  |
| Discovery & registration | How are extensions found and loaded?           |
| Manifest format       | Versioned, validated, typed?                      |
| Lifecycle             | Activate / deactivate / hot-reload behavior       |
| Isolation             | Plugin failure → shell failure?                   |
| Permissions / scoping | What can a plugin reach? Is it scoped?            |
| Dev experience        | Templates, types, debug surface, docs             |

---

## Static probes

### Web

```bash
# Plugin / extension keywords
rg -n 'registerPlugin|definePlugin|registerExtension|defineExtension|registerCommand|registerAction' --type ts --type tsx --type js

# Slot system
rg -n 'data-slot|<Slot|<slot\b|defineSlots|teleport=' --type ts --type tsx --type vue --type svelte

# SDK / API package
fd -t d 'sdk|plugin-api|extension-api|@<org>/sdk'

# Manifest schema
fd -t f 'plugin\.json|manifest\.json|extension\.json'

# Sandbox primitives (web workers, iframes for plugins)
rg -n 'new Worker|<iframe|sandbox=|@vue/runtime-core/createApp' --type ts --type tsx
```

### Desktop

```bash
# Tauri plugin system
rg -n 'tauri::plugin|Plugin::new|Builder::new\(\)\.plugin' src-tauri/

# Electron extension loading
rg -n 'session\.loadExtension|BrowserView' --type ts --type js

# WASM plugin runtime
rg -n 'wasmtime|wasmer|wasm-bindgen' src-tauri/Cargo.toml package.json
```

### CLI / TUI

```bash
# Python entry-point plugins
rg -n 'entry_points\s*=\s*\{|pkg_resources\.iter_entry_points' --type py setup.py setup.cfg pyproject.toml

# Node CLI sub-commands / plugins
rg -n 'addCommand\(|registerCommand\(|cli\.command\(' --type ts --type js

# Rust dynamic plugin loading (rare; usually compile-time features)
rg -n 'libloading|abi_stable|cfg\(feature' --type rust
```

---

## Runtime probes

### Web

From `references/runtime-probes-web.md`:

1. `pluginSlots` — inventory data-slot / data-plugin-slot elements; SDK
   globals on `window`.
2. **Register a no-op plugin** if a sandbox / dev mode allows it. Confirm:
   - It loads without modifying the shell's state.
   - It appears in the appropriate slot / palette / menu.
   - Unloading restores the prior state.
3. **Failure containment**: plant a plugin that throws synchronously on
   activate. Confirm:
   - The shell stays up.
   - The error reaches a boundary, not the console only.
   - Other plugins continue to function.
4. **Permission scoping**: if the SDK exposes shell APIs (navigation,
   storage, theming), confirm a plugin can only do what its manifest
   declares.

### Desktop

In addition to the renderer-side web probes:

1. Tauri plugin registration check — `tauri::plugin` calls in Rust map
   to invokable commands; verify the contribution surface from the
   Tauri side.
2. If the app runs plugins in WASM / a separate process, verify
   isolation by killing the plugin process and confirming the shell
   recovers.

### CLI / TUI

1. List plugins / extensions via the user-facing command (`<app> plugin
   list` or equivalent).
2. Install a no-op plugin from the docs / template, verify it shows in
   the list and surfaces in the expected place.
3. Plant a failing plugin, confirm the TUI starts without it (graceful
   skip vs hard fail).

---

## Verdict rubric

### Pass

- Documented contribution model with at least: commands, slots,
  settings, theming.
- Manifest is versioned and validated at load time.
- SDK is typed (TS / Pydantic / typed Rust API).
- Plugin failure isolated to the plugin (shell stays up; other plugins
  unaffected).
- Hot reload supported in dev.
- Templates and docs exist for plugin authors.
- Permission scope is explicit (manifest declares; runtime enforces).

### Warn

- Contribution model exists but is inconsistent (commands work, slots
  don't, or vice versa).
- Manifest unversioned; loads anything.
- SDK exists but is untyped.
- Plugin failure logs but doesn't surface to the user.
- No hot reload.

### Fail

- Extensibility claimed (in docs, marketing, types) but no functional
  contribution surface.
- Plugin failure crashes the shell.
- Plugins run with full shell privileges and no scoping.
- No discovery mechanism — plugins must be hard-coded into the shell.

### Not applicable

- Shell is deliberately closed (no extensibility shipped, no plans).
  Mark as `verdict: "Skipped"` with `skipReason: "Closed shell by
  design."`

---

## Severity examples

- **Critical**: a plugin can execute arbitrary code in the shell process
  without scoping or review (security boundary missing).
- **High**: a plugin throwing on activate kills the shell; no isolation.
- **Medium**: SDK exists but types are partially missing; plugin authors
  have to read source.
- **Low**: plugin manifest field naming inconsistent (camelCase vs
  snake_case in different examples).

---

## Findings entry schema

```json
{
  "id": "10-extensibility",
  "name": "Extensibility",
  "verdict": "Warn",
  "verdictRationale": "Contribution model exists for commands and theming; slot contribution unimplemented despite SDK exposing the type. Plugin failures are caught but only logged.",
  "evidence": [
    { "kind": "probe", "ref": "pluginSlots", "summary": "0 slots in DOM; SDK type Slot exists" },
    { "kind": "snippet", "ref": "packages/plugin-sdk/src/index.ts:42", "summary": "registerSlot() exported but no consumer" },
    { "kind": "log", "ref": "/tmp/shell-audit/10-failing-plugin.log", "summary": "Plugin throw caught, logged to console only" }
  ],
  "findings": [
    {
      "id": "SH-070",
      "title": "Plugin failures swallowed silently",
      "severity": "High",
      "description": "When a plugin throws during activation, the shell catches the error and logs to `console.error`. No telemetry, no user-facing notification, no record in the plugin manager. The plugin appears 'active' in the UI but provides no functionality.",
      "evidence": ["src/plugins/loader.ts:88", "/tmp/shell-audit/10-failing-plugin.log"],
      "remediation": "On activation failure, mark the plugin's status as `error` in the plugin manager UI, surface a toast to the user, and emit a telemetry event. Log full stack to the structured logger.",
      "scope": "all plugin activations",
      "confidence": "high"
    }
  ],
  "completedAt": "<ISO datetime>"
}
```

---

## Checkpoint

```
Phase 10 complete — Extensibility: Warn

Top issues:
  • [High]   Plugin activation failures are swallowed (logged only)
  • [Medium] Slot SDK exported but no consumer points wired up in the shell
  • [Low]    Plugin manifest schema unversioned

Findings recorded: 4 (1 High, 2 Medium, 1 Low)
Proceed to Phase 11 (Observability)?
```
