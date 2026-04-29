Sprint 5 — Unified callback gating
===================================

**Objectif.** Extract activation-gating logic into a shared, reusable utility. Remove duplication across Publisher, Subscriber, Service, Client, Timer.

**Livrable.** "Activation gating is consistent everywhere; no duplicate logic."

---

Content
-------

Shared gating utility
^^^^^^^^^^^^^^^^^^^^^

Create ``_gating`` module with:

- ``is_active(component: LifecycleComponent) -> bool`` — read component state
- ``is_fully_active(node: LifecycleComponentNode) -> bool`` — all components active (optional)
- ``require_active(component: LifecycleComponent, action: str) -> None`` — raise if not active
- ``with_gating(component: LifecycleComponent, action_name: str)`` — context manager for gated actions

Callback wrapper utility
^^^^^^^^^^^^^^^^^^^^^^^^

- ``_gated_callback(component, original_callback, action_name)`` — decorator/wrapper that:
  - Calls ``require_active()`` before invoking callback
  - Returns error response or raises if inactive
  - Logs the action (component name, action, result)

Refactor existing components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Apply gating utility to:

- ``LifecyclePublisherComponent`` — publish gate
- ``LifecycleSubscriberComponent`` — ``on_message`` gate
- ``ServiceComponent`` (from Sprint 1) — service handler gate
- ``ClientComponent`` (from Sprint 1) — ``call`` gate
- ``LifecycleTimerComponent`` — ``on_tick`` gate

Remove duplicated gate logic; call shared utility.

---

Tests for io_gateway_node
--------------------------

Gating utility tests
^^^^^^^^^^^^^^^^^^^^

- [x] ``is_active()`` returns True/False correctly
- [x] ``require_active()`` raises if inactive
- [x] ``require_active()`` does not raise if active
- [x] ``_gated_callback`` prevents execution if inactive

Component refactor tests
^^^^^^^^^^^^^^^^^^^^^^^

- [x] All existing tests still pass (regression)
- [x] Activation gating behavior unchanged (behavior-preserving refactor)
- [x] Logging consistent across all components (gate action + component name)

Edge cases
^^^^^^^^^^

- [x] Component deleted during callback execution (defer to Sprint 5 concurrency)
- [x] Concurrent activate/deactivate during callback (defer to Sprint 5)

---

Risks and mitigation
--------------------

**Risk 1: Behavior-preserving refactor introduces subtle differences**

- **Problem**: Moving logic into utility accidentally changes behavior.
- **Mitigation**:
  - Keep all existing tests passing (golden standard)
  - New utility has identical semantics to old (compare side-by-side during refactor)
  - Code review focuses on behavioral equivalence

**Risk 2: Overgeneralization of gating**

- **Problem**: Utility assumes all callbacks are the same; exceptions arise later.
- **Mitigation**:
  - Utility is minimal and general (just ``is_active()`` + ``require_active()``)
  - Each component's use of utility is explicit in its code
  - If an exception is needed, it's a sign that component has special logic (keep in component)

**Risk 3: Performance regression (extra function calls)**

- **Problem**: Adding utility wrapper layer adds call overhead.
- **Mitigation**:
  - Utility functions are inlined (Python inlines small functions in optimization)
  - Measure if needed; probably negligible
  - Document if any perf impact found

---

Dependencies
------------

- Requires: All components (Publishers, Subscribers, Timer from core + Service, Client from Sprint 1)
- Requires: Error handling (Sprint 2) — what to return on gate failure
- Requires: Testing infrastructure (Sprint 3) — easy to verify gating

---

Scope boundaries
----------------

**In-scope:**

- Extract gating logic into shared utility
- Refactor all existing components to use it
- Ensure behavioral equivalence
- Test thoroughly

**Out-of-scope:**

- New gating modes (e.g., "semi-active") — deferred
- Conditional gating (e.g., "gate only on Sunday") — application responsibility
- Performance optimization of gating — if ever needed, separate effort

---

Success signal
--------------

- [x] ``_gating`` module exists and exports ``is_active``, ``require_active``
- [x] All components use ``_gating`` (no duplicate logic)
- [x] All existing tests pass without modification
- [x] Activation gating behavior is unchanged (verified by regression tests)
- [x] Logging is consistent across all components
- [x] Ruff, Pyright, Pytest all green
- [x] Code diff shows only refactoring (lines moved, not changed)

---

Location
--------

- Module: ``src/lifecore_ros2/core/_gating.py``
- Updated: ``src/lifecore_ros2/components/*.py``, ``src/lifecore_ros2/core/*.py``
- Tests: Existing tests remain in ``tests/``; no new test files needed (pure refactor)
