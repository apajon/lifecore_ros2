Sprint 3 — Testing infrastructure
==================================

**Objectif.** Provide reusable test utilities to accelerate framework and application testing.

**Livrable.** "Application tests can verify lifecycle behavior without boilerplate."

Status
------

Implemented in ``lifecore_ros2.testing`` as an extensible package with focused
submodules:

- ``fakes`` for reusable lifecycle, topic, timer, service, and client fakes
- ``fixtures`` for pytest-compatible node fixtures
- ``assertions`` for lifecycle state, transition order, and activation gating checks
- ``helpers`` for common activate/deactivate and logging flows
- ``concurrency`` for small threaded transition probes

The package uses concrete ROS 2 message/service types for the standard topic and
service fakes: ``std_msgs.msg.String`` and ``std_srvs.srv.Trigger``.

Documentation entry points:

- User guide: :doc:`/testing`
- API reference: :doc:`/api`

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

- [x] Using fixtures to test a node with standard fake components
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
- [x] Public utilities have concise docstrings
- [x] Example usage is covered by ``tests/testing``
- [x] Generic lifecycle test doubles were migrated to use these utilities
- [x] Ruff, Pyright, Pytest passed on the targeted test migration
- [x] No external testing library added (pytest remains a development dependency)

---

Location
--------

- Module package: ``src/lifecore_ros2/testing/``
- Tests: ``tests/testing/`` plus migrated existing lifecycle/component tests
- Examples: ``docs/testing.rst`` and focused tests under ``tests/testing/``
