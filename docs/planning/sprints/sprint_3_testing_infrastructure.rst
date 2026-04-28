Sprint 3 — Testing infrastructure
==================================

**Objectif.** Provide reusable test utilities to accelerate framework and application testing.

**Livrable.** "Application tests can verify lifecycle behavior without boilerplate."

---

Content
-------

Fake component implementations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``FakeComponent`` — minimal component that tracks state (called hooks, hook order, failure modes)
- ``FakeServiceComponent`` — returns fixed response or raises on demand
- ``FakeClientComponent`` — simulates service call success/failure
- ``FakePublisherComponent`` — publishes fixed messages
- ``FakeSubscriberComponent`` — tracks received messages
- ``FakeTimerComponent`` — timer with controlled tick scheduling

Test fixtures
^^^^^^^^^^^^^

- ``lifecycle_node_fixture`` — creates a ``LifecycleComponentNode`` for test, tears down after
- ``node_with_components`` — fixture that pre-registers standard fake components
- ``assert_component_state(node, name, expected_state)`` — verify component state
- ``assert_transition_order(log, expected_order)`` — verify hook call order
- ``assert_activation_gated(component)`` — verify gating works

Helpers for common patterns
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``activate_component(node, name)`` — configure + activate in one call (test shorthand)
- ``deactivate_component(node, name)`` — deactivate + cleanup (test shorthand)
- ``collect_logs(logger, test_fn)`` — capture logs during test
- ``expect_log(logs, pattern)`` — assert a log line matches pattern
- ``FailingComponent(fail_at_hook='_on_configure', exception=RuntimeError())`` — component that fails on demand

Concurrency helpers
^^^^^^^^^^^^^^^^^^^

- ``spawn_transition_thread(node, transition_name)`` — call transition from thread (for race testing)
- ``assert_no_race(test_fn)`` — run test multiple times to catch racy behavior
- ``barrier_hook`` — hook that blocks until signaled (for orchestrating concurrent tests)

---

Tests to write
--------------

Fixture tests
^^^^^^^^^^^^^

- [x] ``lifecycle_node_fixture`` creates and destroys node cleanly
- [x] ``FakeComponent`` tracks hook calls and state transitions
- [x] ``FakeComponent`` can be configured to fail at specific hook
- [x] ``assert_component_state`` passes/fails correctly

Helper tests
^^^^^^^^^^^^

- [x] ``activate_component`` calls configure then activate in order
- [x] ``collect_logs`` captures all logs during test
- [x] ``expect_log`` finds or asserts missing pattern
- [x] ``spawn_transition_thread`` runs transition from thread safely

Integration example tests
^^^^^^^^^^^^^^^^^^^^^^^^^

- [x] Using fixtures to test a node with 3 fake components
- [x] Verifying hook call order with ``assert_transition_order``
- [x] Verifying activation gating with ``assert_activation_gated``

---

Risks and mitigation
--------------------

**Risk 1: Fixtures not flexible enough**

- **Problem**: Test needs custom component behavior not covered by fakes.
- **Mitigation**:
  - Fakes are subclassable; easy to override hooks
  - Fixture accepts kwargs for customization
  - Document: "compose fakes + custom components as needed"

**Risk 2: Tests become harder to debug (hidden in helpers)**

- **Problem**: Helpers abstract away details; tests are less readable.
- **Mitigation**:
  - Helpers are minimal and obvious (e.g., ``activate_component`` just calls two methods)
  - Test docstrings explain what is being verified
  - Logging is always available for debugging

**Risk 3: Infrastructure becomes overspecialized**

- **Problem**: Infrastructure is so tailored to lifecycle that it's not useful elsewhere.
- **Mitigation**:
  - Fakes and fixtures use only public API
  - No hidden mocking or patching
  - Document as reusable utilities, not black boxes

---

Dependencies
------------

- Requires: ``LifecycleComponent`` + ``LifecycleComponentNode`` (shipped)
- Requires: pytest (dev dependency, shipped)
- Recommends: Error handling (Sprint 2) so fakes can simulate failures
- Recommends: Service/Client (Sprint 1) so fakes can simulate those

---

Scope boundaries
----------------

**In-scope:**

- Reusable test components (FakeComponent, FakeServiceComponent, etc.)
- Fixtures for common setups
- Helper functions for assertions
- Logging and concurrency utilities for tests

**Out-of-scope:**

- Full mock/patch framework (use ``unittest.mock`` if needed)
- Property-based testing (use Hypothesis if needed)
- Performance benchmarking utilities
- CI-specific tooling

---

Success signal
--------------

- [x] ``from lifecore_ros2.testing import FakeComponent, lifecycle_node_fixture, activate_component`` works
- [x] All utilities have docstrings with usage examples
- [x] Example test file using fixtures (``tests/examples/test_with_fixtures.py``)
- [x] All Sprint 1–2 tests can be rewritten to use these utilities (as regression test)
- [x] Ruff, Pyright, Pytest all green
- [x] No external testing library added (pytest is already a dev dependency)

---

Location
--------

- Module: ``src/lifecore_ros2/testing.py`` or ``src/lifecore_ros2/testing/__init__.py``
- Tests: ``tests/test_testing_infrastructure.py``
- Examples: docstrings + one integration example test
