Sprint 6 — Concurrency infrastructure
=====================================

**Objectif.** Support safe multi-threaded callback execution; formalize callback group management.

**Livrable.** "Applications can safely use multi-threaded executors without manual choreography."

---

Content
-------

Callback group helpers
^^^^^^^^^^^^^^^^^^^^^^

Framework support for scoped callback group creation:

- ``create_callback_group_for_component(name: str, group_type: str = "exclusive") -> CallbackGroup``
- ``node.callback_group_for(component_name) -> CallbackGroup`` — retrieve or create
- Internal registry: ``_component_callback_groups`` dict

Callback group binding
^^^^^^^^^^^^^^^^^^^^^^^

Update component constructors to optionally accept ``callback_group``:

- ``ServiceComponent(..., callback_group=None)`` → use default or provided
- ``ClientComponent(..., callback_group=None)`` → same
- Same for Publisher, Subscriber, Timer if applicable

Concurrency safety audit
^^^^^^^^^^^^^^^^^^^^^^^^

Verify (or update) that:

- ``LifecycleComponentNode`` RLock protects component registration and state transitions
- Component lifecycle state is atomically readable
- Concurrent callbacks cannot corrupt component state
- Document concurrency contract in ``docs/architecture.rst``

Thread-safe component destruction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ensure:

- Component can be destroyed while callbacks are executing
- Callbacks check component state before accessing resources
- ``_release_resources`` is idempotent (safe to call multiple times)

Optional: Lifecycle-aware callback gating in multi-threaded context
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Gating still works in multi-threaded executor
- Callbacks from different threads respect component activation state
- No race between deactivate and in-flight callback

---

Tests to write
--------------

Callback group tests
^^^^^^^^^^^^^^^^^^^^

- [ ] ``create_callback_group_for_component`` creates group
- [ ] Same component name returns same group (idempotent)
- [ ] Different components → different groups
- [ ] Component constructor accepts ``callback_group`` parameter
- [ ] Service/Client created with explicit group are called via that group

Concurrency tests (multi-threaded executor)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [ ] Multiple subscribers with different callback groups receive messages concurrently
- [ ] Component activation state is consistent across threads
- [ ] Deactivate blocks new callbacks while in-flight callbacks complete
- [ ] Component destruction is safe if callbacks are executing (no use-after-free)

Data race tests
^^^^^^^^^^^^^^^

- [ ] Concurrent calls to ``add_component`` from multiple threads
- [ ] Concurrent lifecycle transitions from multiple threads (should fail + log)
- [ ] Concurrent reads of component state from multiple threads (should be atomic)

Lock contention tests
^^^^^^^^^^^^^^^^^^^^^

- [ ] High-frequency component registration does not deadlock
- [ ] Lifecycle transitions do not block all callbacks (use fine-grained locking if needed)

---

Risks and mitigation
--------------------

**Risk 1: Lock contention bottleneck**

- **Problem**: Single RLock on the entire node becomes a bottleneck in high-concurrency scenarios.
- **Mitigation**:
  - Measure lock hold times (use ``perf`` or profiler if needed)
  - If contention is real, fine-grain locks (per-component or per-state)
  - For now, assume RLock is sufficient (single executor or cooperative multi-threading)
  - Document concurrency assumptions clearly

**Risk 2: Callback modifies component state during execution**

- **Problem**: Callback in Component A deletes Component B or transitions the node.
- **Mitigation**:
  - Documented contract: "callbacks must not call ``add_component``, ``remove_component``, or lifecycle transitions"
  - Enforcement: ``ConcurrentTransitionError`` if attempted (already exists)
  - Test: verify that callback cannot trigger second transition

**Risk 3: In-flight callbacks after component removal**

- **Problem**: Component is removed; callback is still executing and tries to access component state.
- **Mitigation**:
  - Component state is immutable after creation (no in-callback mutations)
  - Callbacks only read component state, don't modify node state
  - On removal, component is marked as detached; any access raises ``ComponentNotAttachedError``
  - Test: callback executing during component removal (use barrier hooks)

**Risk 4: Deadlock on reentrant transitions**

- **Problem**: Callback calls lifecycle transition; deadlock on RLock re-acquisition.
- **Mitigation**:
  - RLock is reentrant by design (already handled)
  - Prevent transition inside callback: check ``_in_transition`` flag, raise if True
  - Test: reentrant transition from callback (must fail deterministically)

---

Dependencies
------------

- Requires: Concurrency contract (Sprint 2 / architecture.rst)
- Requires: All components (Sprints 1, 4) with gating
- Requires: Testing utilities (Sprint 3) for multi-threaded test helpers

---

Scope boundaries
----------------

**In-scope:**

- Callback group creation and scoping helpers
- Concurrency safety verification
- Thread-safe component lifecycle (no use-after-free)
- Documentation of concurrency contract
- Multi-threaded executor support

**Out-of-scope:**

- Custom executor implementation
- Lock-free data structures (complexity not justified yet)
- Performance tuning (measure first, then optimize if needed)
- Parallel component initialization (sequential is safer and simpler)

---

Success signal
--------------

- [x] ``node.create_callback_group_for_component(name)`` works
- [x] Components accept ``callback_group`` parameter
- [x] All concurrency tests pass
- [x] No race conditions detected (use TSan if available)
- [x] Concurrency contract documented in ``docs/architecture.rst``
- [x] Ruff, Pyright, Pytest all green
- [x] Example: multi-threaded node with explicit callback groups (``examples/multi_threaded_node.py`` or similar)

---

Location
--------

- Module: ``src/lifecore_ros2/core/_concurrency.py`` (or extend existing)
- Updated: ``src/lifecore_ros2/core/*.py``, ``src/lifecore_ros2/components/*.py``
- Tests: ``tests/test_concurrency_*.py`` (new)
- Docs: Update ``docs/architecture.rst`` with concurrency section

---

Related design notes
--------------------

- :doc:`../design_notes/callback_groups` — reference for callback group design
