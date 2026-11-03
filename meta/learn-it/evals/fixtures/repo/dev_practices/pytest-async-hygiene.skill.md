---
name: pytest-async-hygiene
description: >-
  Keeps async Python test suites deterministic. Use when async tests are flaky,
  order-dependent, or fail only in CI.
metadata:
  version: "1.0.0"
---
# pytest-async-hygiene

1. Reproduce with randomized order and repetition before changing anything.
2. Never share network clients across tests; create them in fixtures and close them.
3. Prefer widening the event-loop scope (`loop_scope="session"`) when a client must be shared.
