# Session log, 2026-11-01: fixing flaky async tests in rusty_tick's Python client

User: CI fails about 1 in 5 runs on test_sync_roundtrip, never locally.
Claude: Ran the suite 50 times with `pytest -p no:randomly --count 50` (pytest-repeat). 0 failures. Ran with `pytest -p randomly --count 50`: 9 failures. Order-dependent.
Claude: test_sync_roundtrip passes alone; fails when test_offline_queue runs first. Both use a module-level `httpx.AsyncClient` created at import time.
User: why would that matter?
Claude: The client binds to the event loop that was running when it was first used. pytest-asyncio 0.23 gives each test function its own loop by default, so the second test reuses a client tied to a closed loop: "RuntimeError: Event loop is closed", but only on the connection-pool path, which is why it is intermittent.
Claude: First fix attempt: set `asyncio_default_fixture_loop_scope = "session"` in pyproject. Failures dropped to 2 in 50 but did not stop: test functions still get function-scoped loops; only fixtures moved.
Claude: Second attempt: mark the module `pytestmark = pytest.mark.asyncio(loop_scope="session")`. 0 in 200. But that hides the real bug: the client should not be module-level.
User: yeah, do it properly.
Claude: Replaced the module-level client with an async fixture `client` that yields `httpx.AsyncClient()` and closes it with `await client.aclose()`. Removed the loop_scope marks. 0 failures in 200 randomized runs.
Claude: Also found `respx` mocks leaking between tests because `respx.mock` was used as a decorator on a class; switched to the `respx_mock` fixture. CI green 10 runs in a row.
User: we hit this exact event-loop thing in two other repos last month too.
