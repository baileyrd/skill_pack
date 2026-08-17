# Phase 13 — Persistence

Audit how the shell remembers state across sessions: layout (panel
sizes, sidebar collapse, dock positions), theme, recently-opened items,
window bounds, user preferences, and feature flags / overrides. Also:
how it handles persisted-state corruption and version migrations.

---

## What we evaluate

| Concern               | Question                                          |
|-----------------------|---------------------------------------------------|
| Storage targets       | localStorage / IndexedDB / cookies / config file / OS keychain? |
| Layout persistence    | Sidebar size, panel splits, dock positions saved? |
| Window persistence    | Window bounds, display, maximized state? (desktop) |
| Theme / appearance    | Survives restart? Honors OS preference if no override? |
| User preferences      | Saved per user? Per device? Per workspace?        |
| Recently-opened       | List or jump-list maintained correctly?           |
| Schema versioning     | Persisted format versioned and migrated?          |
| Corruption handling   | Garbage value → graceful fallback or hard crash?  |
| Storage namespacing   | Keys scoped to avoid collisions with other apps?  |
| Privacy / sensitivity | Any secret-ish state stored unencrypted?          |
| Reset path            | User can clear / reset persisted state?           |

---

## Static probes

### Web

```bash
# Storage usage
rg -n 'localStorage\.|sessionStorage\.|document\.cookie' --type ts --type tsx | wc -l
rg -n '\bindexedDB\b|\bopenDB\b|@dexie' --type ts --type tsx

# Persisted-state library
rg -l 'redux-persist|zustand/middleware/persist|jotai/utils/atomWithStorage|pinia-plugin-persistedstate' --type ts

# Storage key inventory
rg -n "localStorage\.(setItem|getItem)\(['\"]" --type ts --type tsx
rg -n "sessionStorage\.(setItem|getItem)\(['\"]" --type ts --type tsx

# Schema version field
rg -n 'schemaVersion|persistVersion|migrateState|migration' --type ts --type tsx
```

### Desktop

```bash
# Tauri config / store APIs
rg -n 'tauri-plugin-store|tauri-plugin-window-state|tauri::api::path' src-tauri/

# Electron storage
rg -n 'electron-store|conf\(\)|electron-window-state' --type ts --type js

# OS keychain
rg -n 'keytar|tauri-plugin-stronghold|secret-service' --type ts --type js --type rust
```

### CLI / TUI

```bash
# XDG / platform paths
rg -n 'XDG_CONFIG_HOME|XDG_DATA_HOME|XDG_STATE_HOME|appdirs|app_dirs|directories::ProjectDirs' --type rust --type py --type go

# Config file format
fd -t f 'config\.(toml|yaml|yml|json|ini)' --max-depth 4

# Version / migration
rg -n 'config_version|schema_version|migrate_config' --type rust --type py --type go
```

---

## Runtime probes

### Web

From `references/runtime-probes-web.md`:

1. `persistedLayout` — inventory localStorage / sessionStorage / cookie
   keys related to UI state. Also detect IndexedDB presence.
2. **Round-trip test**: change shell preferences (collapse sidebar,
   resize a panel, switch theme, set a workspace). Reload the page.
   Confirm each change restores.
3. **Corruption test**: in DevTools Console:
   ```javascript
   localStorage.setItem('app:layout', '{{{not valid json');
   location.reload();
   ```
   Confirm the shell falls back to defaults rather than crashing.
4. **Cross-tab sync**: open the app in two tabs of the same browser.
   Change a preference in tab A. Does tab B receive the change (via
   `storage` event), need a refresh, or stay diverged?
5. **Privacy sanity**: scan the storage payload for anything that looks
   like a token, email, or PII. The shell layer probably shouldn't
   store secrets in plain text.
6. **Reset path**: confirm there's a user-facing way to clear UI state
   (Settings → Reset layout, or similar).

### Desktop

In addition to renderer-side probes:

1. Locate the platform config dir:
   - macOS: `~/Library/Application Support/<bundleId>/`
   - Linux: `$XDG_CONFIG_HOME/<app>/` or `~/.config/<app>/`
   - Windows: `%APPDATA%\<app>\`
2. Capture the file tree before / after a shell-state change:
   ```bash
   diff -ruN before-config/ after-config/
   ```
3. Window state restore: resize/move/maximize, quit, relaunch. Confirm
   the bounds restore. Repeat across multi-monitor (move to second
   display, quit, relaunch).
4. Corruption test: corrupt the store file (`echo '{' > store.json`),
   relaunch. Confirm the app starts with defaults rather than failing.
5. Secrets check: confirm any auth tokens use OS keychain (keytar,
   stronghold, secret-service) — never the plain config file.

### CLI / TUI

1. Run the app, change a preference / theme / view. Quit.
2. Diff the config file:
   ```bash
   diff -u /tmp/before-config /tmp/after-config
   ```
3. Relaunch and confirm preference restoration.
4. Corrupt the config file:
   ```bash
   echo 'not valid' > ~/.config/<app>/config.toml
   <app>
   ```
   Confirm a graceful fallback (warn, write a backup, recreate from
   defaults) rather than a stack trace.
5. Schema migration: if the app supports older config versions, drop in
   an old-format file and confirm it migrates cleanly.

---

## Verdict rubric

### Pass

- Persisted state survives restart for: layout, theme, recently-used,
  window bounds (desktop), preferences.
- Storage keys are namespaced (e.g., `app:layout`, not bare `layout`).
- Persisted format is versioned with a working migration path.
- Corruption falls back to defaults and writes a `*.bak` of the broken
  file.
- Secrets aren't in plaintext; OS keychain is used.
- A user-facing reset path exists.
- Cross-tab / multi-window awareness is at least documented.

### Warn

- One persisted concern doesn't actually persist (e.g., panel sizes lost
  on reload).
- Storage keys not namespaced (works fine alone, breaks if embedded).
- No schema version (works today; future migrations will be painful).
- Cross-tab sync absent and undocumented.

### Fail

- Persisted state corruption locks the user out (app crashes on launch,
  no recovery path short of deleting the config).
- Auth tokens / secrets stored in plaintext localStorage / config file.
- Persisted layout writes constantly (every keystroke), causing perf
  issues.
- Window bounds restore to off-screen coordinates after a display
  change (loses windows).

---

## Severity examples

- **Critical**: corruption of persisted layout file crashes the app on
  launch with no recovery path.
- **Critical**: auth token saved to plain config file, readable by any
  process with file-read access.
- **High**: window bounds restore off-screen on second-display
  disconnection (windows are effectively lost until config is hand-
  edited).
- **Medium**: panel sizes don't restore (annoying but not blocking).
- **Low**: recently-opened list keeps stale entries forever (no cap, no
  purge).

---

## Findings entry schema

```json
{
  "id": "13-persistence",
  "name": "Persistence",
  "verdict": "Warn",
  "verdictRationale": "Layout, theme, and recently-used persist across reload. Storage keys are namespaced. Schema unversioned; corruption falls back to defaults but no .bak written. Auth uses keychain — clean.",
  "evidence": [
    { "kind": "probe", "ref": "persistedLayout", "summary": "5 namespaced keys under 'app:'" },
    { "kind": "log", "ref": "/tmp/shell-audit/13-corruption-test.log", "summary": "Corruption recovers to defaults; no backup written" },
    { "kind": "snippet", "ref": "src/persistence/serialize.ts:18", "summary": "JSON.parse without try/catch in 1 path" }
  ],
  "findings": [
    {
      "id": "SH-100",
      "title": "Persisted state has no schema version",
      "severity": "Medium",
      "description": "The persisted layout JSON has no `version` field. Today this works, but the next breaking change will mean either silently losing user state (best case) or crashing on parse (worst case). No migration path is in place.",
      "evidence": ["src/persistence/schema.ts", "/tmp/shell-audit/13-storage-dump.json"],
      "remediation": "Add `schemaVersion: 1` to the persisted shape now. Add a `migrate(state, fromVersion)` step in the load path. Cost is low; future cost is high if deferred.",
      "scope": "all persisted shell state",
      "confidence": "high"
    }
  ],
  "completedAt": "<ISO datetime>"
}
```

---

## Checkpoint

```
Phase 13 complete — Persistence: Warn

Top issues:
  • [Medium] Persisted state has no schema version (future migration risk)
  • [Medium] Corruption fallback works but doesn't preserve a .bak file
  • [Low]    Recently-opened list grows unbounded

Findings recorded: 4 (0 High, 2 Medium, 2 Low)
Proceed to Phase 14 (Synthesis)?
```
