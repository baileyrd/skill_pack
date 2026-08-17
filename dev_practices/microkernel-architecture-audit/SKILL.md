---
name: microkernel-architecture-audit
description: Perform a detailed, multi-dimensional audit of a microkernel-style system. Evaluates core/plugin boundaries, IPC contracts, capability-based security, WASM sandbox integrity, plugin lifecycle, dependency inversion, async concurrency, and test coverage. Produces a structured markdown report with Pass/Warn/Fail verdicts per dimension. Targets Nexus Forge (Rust/Tauri), FORGE (FastAPI), or any generic microkernel codebase.
version: 1.1.0
---

# Skill: Microkernel Architecture Audit

## Purpose

Perform a detailed, multi-dimensional audit of a microkernel-style system given source code,
architecture documentation (markdown, ADRs), or both. Produce a structured markdown report
with Pass / Warn / Fail verdicts per dimension, concrete findings, and actionable
recommendations.

This skill targets three system archetypes but applies to any microkernel-patterned codebase:

| Archetype | Stack |
|-----------|-------|
| **Nexus Forge** | Rust / Tauri multi-crate workspace, WASM-sandboxed plugins, capability SDK |
| **FORGE** | Python / FastAPI multi-agent orchestration, authority chain, typed Pydantic contracts |
| **Generic** | Any language; language-agnostic principles apply throughout |

---

## Trigger Conditions

Use this skill when the user says any of:

- "audit my microkernel / plugin architecture"
- "review my core/plugin boundary"
- "check my IPC contracts / capability model"
- "do a deep architecture review of [project]"
- Uploads source files or docs and asks for an architecture review

---

## Input Handling

### Step 1 — Identify available inputs

Check what has been provided before starting the audit:

```
[ ] Source code files or directory listing
[ ] Architecture docs: markdown, ADRs, READMEs, design notes
[ ] Both (preferred — enables cross-referencing intent vs. implementation)
[ ] Neither (conversation-only — audit what the user describes; flag gaps explicitly)
```

If source code is uploaded, scan for:
- `Cargo.toml` / workspace manifests → Rust/Tauri archetype
- `pyproject.toml` / `fastapi` imports → FORGE/Python archetype
- `*.wasm`, `wit/*.wit`, `plugin-sdk/` → WASM plugin system
- `*_test.rs`, `test_*.py`, `conftest.py` → test surface

If docs are provided, extract:
- Stated architectural goals and invariants
- ADR decisions (especially sandbox, IPC, capability design)
- Any explicitly called-out anti-patterns or known issues

### Step 2 — Determine archetype

Use file signatures to auto-detect the archetype. If ambiguous, ask the user one question:
> "Is this primarily a Rust/Tauri workspace, a Python/FastAPI system, or a different stack?"

---

## Audit Dimensions

Run **all eight** dimensions in sequence. For each, follow the evaluation protocol described
below, then assign a verdict.

### Verdict Legend

| Verdict | Meaning |
|---------|---------|
| ✅ **PASS** | Dimension is well-implemented; only minor notes if any |
| ⚠️ **WARN** | Partially implemented or inconsistent; specific gaps identified |
| ❌ **FAIL** | Dimension is missing, broken, or actively violates the pattern |

---

### Dimension 1 — Core / Plugin Boundary Enforcement

**What to evaluate:**

- Is there a clear, explicit contract separating the kernel core from plugin code?
- Does the core expose a minimal surface (thin API, no business logic leakage)?
- Can plugins directly call core internals, or is all access mediated?
- Are there accidental leakages (e.g., `pub` on internal structs, direct imports across
  crate boundaries, shared global state)?

**Rust signals:**
- `pub(crate)` vs `pub` discipline in core crates
- Plugin crates importing only from `forge-plugin-sdk`, never from `forge-core` internals
- `#[doc(hidden)]` or sealed trait patterns for internal APIs

**Python signals:**
- Agent modules importing only from declared interface modules, not internal service layers
- No circular imports between core orchestrator and agent implementations
- `__all__` discipline in public modules

**Failure patterns:**
- Plugins importing core internals directly
- Core containing plugin-specific logic
- No defined boundary (everything in one module/crate)

---

### Dimension 2 — IPC / Message-Passing Contracts

**What to evaluate:**

- Are all cross-boundary messages defined as explicit typed contracts?
- Are request/response pairs versioned or at minimum clearly named?
- Is there a single canonical IPC mechanism (no ad-hoc side channels)?
- Are error responses typed (not raw strings or untyped exceptions)?

**Rust signals:**
- Enums or structs in a shared `forge-ipc` crate for all message types
- `serde` derive on all IPC types with `#[serde(deny_unknown_fields)]` or similar strictness
- No raw `String` or `serde_json::Value` crossing the IPC boundary

**Python signals:**
- Pydantic models for all agent inputs/outputs
- Typed `TypedDict` or dataclasses for internal messages
- No `dict` / `Any` at boundary points

**Failure patterns:**
- Untyped JSON blobs crossing boundaries
- Multiple parallel IPC channels with overlapping responsibilities
- No versioning strategy for evolving contracts

---

### Dimension 3 — Capability-Based Security Model

**What to evaluate:**

- Does the system implement a capability model (plugins declare what they need; core grants
  only what is declared)?
- Are capabilities explicit, enumerable, and auditable?
- Is there a default-deny posture (plugins get nothing unless granted)?
- Can a plugin escalate its own capabilities at runtime?

**Rust signals:**
- A `Capabilities` / `CapabilitySet` type in the SDK
- Plugin manifest declaring required capabilities before load
- Core performing capability check before dispatching any sensitive operation
- No `unsafe` paths that bypass capability checks

**Python signals:**
- Agent permission declarations in config/manifest
- Authority chain enforcement (ESC → CDTO → DTO → DEFTs) validated before execution
- No agent can invoke another agent's tools directly outside the orchestrator

**Failure patterns:**
- Capabilities are advisory (checked sometimes, skipped other times)
- No capability declaration at all; plugins get ambient access
- Single monolithic permission level for all plugins

---

### Dimension 4 — Plugin Sandbox Integrity (WASM)

*Skip this dimension (mark N/A) if the system has no WASM plugin layer.*

**What to evaluate:**

- Are WASM modules loaded in isolated linear memory spaces?
- Can a WASM plugin access host memory outside its own allocation?
- Are host functions (imports into WASM) explicitly allowlisted?
- Is the sandbox enforced at the engine level (Wasmtime, Wasmer) or only by convention?
- Does the plugin SDK prevent raw pointer passing across the host/guest boundary?

**Rust signals:**
- `wasmtime::Store` or `wasmer::Store` per plugin instance (not shared)
- Host function imports defined in a controlled `Linker` with explicit grants only
- No `unsafe` in the plugin-host bridge that could expose host memory
- ABI uses value types or serialized buffers, never raw pointers

**Failure patterns:**
- Shared WASM store across plugins (memory isolation failure)
- Host functions added to linker without capability checks
- Plugin code compiled to native (not WASM) as a convenience shortcut, bypassing sandbox

---

### Dimension 5 — Extensibility & Plugin Lifecycle

**What to evaluate:**

- Can new plugins be added without modifying core?
- Is there a defined plugin lifecycle (discover → load → init → execute → unload)?
- Are lifecycle hooks implemented and called consistently?
- Can plugins be hot-reloaded or dynamically registered at runtime?
- Is there a plugin registry / manifest system?

**Rust signals:**
- `PluginHost` trait with `load`, `unload`, `dispatch` methods
- Plugin discovery via directory scan or manifest file, not hard-coded registration
- `forge-plugin-sdk` stable ABI version field checked on load
- CorePlugins vs WASM plugins distinguished by type, not by special-casing

**Python signals:**
- Agent registry with dynamic registration path
- Agent initialization separated from execution
- No hard-coded agent lists in the orchestrator

**Failure patterns:**
- Adding a plugin requires editing core source
- No lifecycle hooks; plugins are just functions that get called
- No versioning / compatibility check on plugin load

---

### Dimension 6 — Dependency Inversion & Coupling

**What to evaluate:**

- Does core depend on abstractions, not concrete plugin implementations?
- Are interface/trait definitions in a shared neutral layer (not owned by core or plugin)?
- Is there evidence of inappropriate coupling (core knowing plugin names, plugin knowing
  core implementation details)?
- Does the dependency graph flow in one direction only?

**Rust signals:**
- Traits defined in `forge-plugin-sdk`, implemented in plugin crates
- Core imports only the SDK, never individual plugin crates
- `Cargo.toml` workspace graph is acyclic with clear directionality

**Python signals:**
- Abstract base classes or protocols in a `contracts` / `interfaces` module
- Orchestrator depends on `AgentProtocol`, not `ConcreteAgent`
- No circular imports detected (`pipdeptree` or `import-linter` evidence)

**Failure patterns:**
- Core imports concrete plugin types
- Plugin imports core business logic
- Circular dependencies (A → B → A) in the module/crate graph

---

### Dimension 7 — Async Patterns & Concurrency Safety

**What to evaluate:**

- Is there a consistent async model throughout the system?
- Are async boundaries explicit and well-defined?
- Is shared mutable state protected (locks, channels, or immutability)?
- Are there potential deadlocks (lock ordering, blocking inside async contexts)?
- Are tasks/futures properly cancelled and cleaned up?

**Rust signals:**
- Consistent use of `tokio` (not mixing `async-std` / `tokio` runtimes)
- No `std::sync::Mutex` held across `.await` points
- `Arc<Mutex<T>>` vs `Arc<RwLock<T>>` used appropriately
- Plugin dispatch is non-blocking (uses channels or `spawn`)
- No `block_on` inside async context

**Python signals:**
- Consistent `asyncio` throughout (no `gevent` / `threading` mixing)
- No synchronous blocking calls inside `async def` functions
- Background tasks use `asyncio.create_task` with proper cancellation
- FastAPI endpoints use `async def` where I/O is involved

**Failure patterns:**
- Mixed sync/async in the same call stack without explicit bridging
- Mutex / lock held across an await point
- Global mutable state without synchronization
- Fire-and-forget tasks with no error handling

---

### Dimension 8 — Test Coverage & Error Handling

**What to evaluate:**

- Are core/plugin boundary contracts tested (not just happy-path logic)?
- Are error types explicit, typed, and propagated correctly?
- Is there negative-path testing (bad inputs, missing capabilities, plugin load failures)?
- Are integration tests present that exercise the full core → plugin → response path?
- Is test coverage meaningful (tests the contract, not the implementation detail)?

**Rust signals:**
- `#[cfg(test)]` modules in core and SDK crates
- `thiserror` / `anyhow` used consistently; no raw `.unwrap()` in production paths
- Integration tests in `tests/` that load a mock plugin via the actual `PluginHost`
- Error variants model real failure modes (not just `Error(String)`)

**Python signals:**
- `pytest` with `conftest.py` fixtures for agent/orchestrator setup
- Pydantic validation errors caught and re-raised as domain errors
- Tests for each agent's input/output contract, not just internal logic
- `httpx.AsyncClient` tests for FastAPI boundary endpoints

**Failure patterns:**
- `.unwrap()` / `expect()` in non-test Rust code without justification
- `except Exception: pass` in Python
- No tests for plugin load failure, bad IPC messages, or capability denial
- 100% coverage on trivial code, 0% on boundary logic

---

## Output Format

Produce the audit report in this exact structure:

```markdown
# Microkernel Architecture Audit Report
**System:** [name]
**Archetype:** [Nexus Forge | FORGE | Generic]
**Inputs:** [Code | Docs | Both | Conversation]
**Date:** [today]

---

## Executive Summary

[2–4 sentences: overall health, most critical finding, top recommendation]

## Audit Scorecard

| # | Dimension | Verdict | One-line summary |
|---|-----------|---------|-----------------|
| 1 | Core / Plugin Boundary | ✅ / ⚠️ / ❌ | ... |
| 2 | IPC / Message Contracts | ✅ / ⚠️ / ❌ | ... |
| 3 | Capability-Based Security | ✅ / ⚠️ / ❌ | ... |
| 4 | Plugin Sandbox (WASM) | ✅ / ⚠️ / ❌ / N/A | ... |
| 5 | Extensibility & Lifecycle | ✅ / ⚠️ / ❌ | ... |
| 6 | Dependency Inversion | ✅ / ⚠️ / ❌ | ... |
| 7 | Async / Concurrency | ✅ / ⚠️ / ❌ | ... |
| 8 | Test Coverage & Errors | ✅ / ⚠️ / ❌ | ... |

---

## Detailed Findings

### 1. Core / Plugin Boundary Enforcement — [VERDICT]

**Findings:**
- [Specific observation with file/line reference if available]
- ...

**Recommendations:**
- [Concrete, actionable fix]
- ...

[Repeat for each dimension]

---

## Cross-Cutting Observations

[Patterns that span multiple dimensions — e.g., "boundary leakage correlates with missing
capability checks in the same crates"]

## Prioritized Action Items

| Priority | Item | Dimension(s) |
|----------|------|-------------|
| P0 | [Fix critical failure] | [#] |
| P1 | [Address warning] | [#] |
| P2 | [Improvement] | [#] |

## Appendix: Evidence References

[File paths, line numbers, doc sections cited in findings]
```

---

## Behavior Rules

1. **Evidence-first.** Every finding must cite a specific file, function, line range, doc
   section, or stated design decision. No vague assertions.

2. **Fail loudly on gaps.** If a dimension cannot be evaluated due to missing inputs, mark it
   ⚠️ WARN with the note "Insufficient input to evaluate — [what is needed]". Do not silently
   skip.

3. **Cross-reference intent vs. implementation.** When both docs and code are available,
   explicitly note where implementation diverges from stated architecture.

4. **Don't pad.** If a dimension is genuinely clean, PASS + one sentence is enough. Reserve
   depth for WARN and FAIL items.

5. **Recommendations must be concrete.** Not "improve error handling" — instead:
   "Replace `unwrap()` on line 47 of `forge-plugin-host/src/loader.rs` with a typed
   `PluginLoadError::InvalidManifest` variant and propagate via `?`."

6. **Archetype-aware language.** Use Rust idioms (traits, crates, `Arc<Mutex<T>>`) for Nexus
   Forge, Python idioms (protocols, modules, asyncio) for FORGE, neutral language for
   Generic. Do not mix terminology.

7. **Dimension 4 is optional.** If no WASM layer is detected or mentioned, mark as N/A and
   move on.

8. **Ask before assuming scope.** If the user provides a large codebase, ask: "Which crates /
   modules should I focus on for the audit?" before diving in.

## Limitations

- **Built and worded for two named targets** — Nexus Forge (Rust/Tauri) and FORGE
  (FastAPI) — with a "generic microkernel" fallback for anything else. The archetype
  detection and idiom-matched language (Rule 6) are tuned to those two; a third
  microkernel stack gets the generic path, which is real coverage but thinner than the
  named ones.
- **The eight dimensions assume the microkernel shape already holds.** This audits how
  well a system *that has* a core/plugin split executes that split — it does not first
  verify the split is the right architecture for the problem. A monolith with a plugin
  API bolted on for optics will score on these dimensions rather than being flagged as
  not actually a microkernel.
- **Verdicts are qualitative**, same caveat as this repo's other audit skills: the rubric
  makes them consistent and citable, not objective. Two reviewers can reasonably split
  PASS/WARN on the same evidence.
- **Static-first.** Nothing here launches or drives the system at runtime — WASM sandbox
  integrity (dimension 4) and async concurrency (dimension 7) in particular are easier to
  get wrong from code reading alone than from watching the system misbehave. Treat a
  clean static read on either as provisional, not final.

## Wrap-up retro

**After the scorecard and report land**, run a
[`meta/skill-retro`](../../meta/skill-retro) pass on **this skill**, grounded
in what just happened: did the eight dimensions fit the target or did one
have to be stretched into an N/A beyond dimension 4's documented case; did
the target actually match one of the two named archetypes or fall to the
generic path, and if generic, was Rule 6's idiom-matched language still
usable or did it read as forced; was a verdict recorded without the citation
Rule 1 requires because the evidence was awkward to produce for this
codebase; did Rule 8's ask-before-assuming-scope step actually get asked, or
did scope get inferred from a large codebase without checking.

Running and reporting the retro is automatic and safe unattended —
`skill-retro` never edits this skill's files on its own. *Applying* anything
it finds is a separate, explicitly-approved follow-up through this repo's
normal PR workflow, never bundled into the run that triggered it.
