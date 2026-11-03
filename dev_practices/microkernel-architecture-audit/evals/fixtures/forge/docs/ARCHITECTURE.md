# FORGE architecture

FORGE is a FastAPI microkernel. The core owns routing, the event bus and the
plugin registry; everything else is a plugin.

Invariants:

1. Plugins depend only on `forge_sdk` (the public `PluginContext` API). They never
   import from `core`.
2. Every plugin declares the capabilities it needs in `plugin.toml`
   (`capabilities = ["http.fetch", "bus.publish"]`). The host grants only those;
   any other call is refused.
3. Bus messages are versioned (`{"type": ..., "version": N, "payload": ...}`) so
   plugins can be upgraded independently.
4. A plugin that fails to load is reported and disabled; it never takes the core down.
