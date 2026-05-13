Sprint 8 - Concurrency infrastructure
=====================================

Status:
  Archived / Completed

Completed in:
  Unknown

Outcome:
  See sprint body.

Follow-ups:
  See docs/planning/backlog.rst if applicable.


**Objective.** Support safe multi-threaded callback execution and formalize the
callback-group contract.

**Deliverable.** Applications can use multi-threaded executors without manual
choreography beyond documented ROS 2 callback-group choices.

---

Decisions already made
----------------------

- The library should support ROS 2 callback groups without hiding ROS 2
  executor semantics.
- Callback groups are borrowed resources when supplied by the application.
- Component lifecycle state must remain coherent when callbacks and lifecycle
  transitions overlap.
- Concurrent transitions should fail deterministically instead of racing.

Scope
-----

The sprint covers callback-group binding, documented concurrency expectations,
and a safety audit of lifecycle state access.

Verify or update that:

- component registration and lifecycle transitions are protected
- lifecycle state reads are coherent
- concurrent transitions fail deterministically
- callbacks cannot corrupt component lifecycle state

Thread-safe cleanup expectations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Clarify what happens when cleanup, deactivation, or destruction overlaps with
in-flight callbacks. Prefer documented constraints and deterministic errors over
implicit best effort.

To decide during sprint planning
--------------------------------

Decisions resolved (2026-05-07):

**C1 — Callback-group helper API.**
``LifecycleComponentNode.get_or_create_callback_group(component_name, group_type=None)``
is implemented. The helper is idempotent per ``(component_name, group_type)`` pair.
The caller-owned pattern remains fully supported: a component constructed with an
explicit ``callback_group`` uses that group as-is.

**C2 — Default group type.**
``MutuallyExclusiveCallbackGroup`` is the default. ``ReentrantCallbackGroup`` must be
requested explicitly. Rationale: the default must protect component-internal state
against accidental reentrancy under ``MultiThreadedExecutor``; intra-component
parallelism is an application decision, not a framework surprise.

**C3 — ``_is_active`` locking.**
``_is_active`` is protected by ``_active_lock: threading.Lock`` on every
``LifecycleComponent`` instance. All reads in the public API (``is_active`` property,
``require_active()``, ``@when_active`` gate) and all writes in the framework entry
points (``on_activate``, ``on_deactivate``, ``on_cleanup``, ``on_shutdown``,
``on_error``, ``_rollback_failed_configure``) acquire ``_active_lock``.
The concurrency contract does not depend on CPython's GIL.

**In-flight callback policy.**
At the ``@when_active`` gate, ``_is_active`` is snapshotted under ``_active_lock``
at gate entry. A callback in flight when deactivation commits will complete its
current execution but will not be re-invoked. No runtime fence is provided; this
is a "drop at next gate" policy, documented here and in component docstrings.

---

Validation
----------

- [x] Callback group creation is idempotent per component name.
- [x] Different component names receive distinct groups when requested.
- [x] Component constructors pass callback groups to ROS resource creation.
- [x] Concurrent lifecycle transitions fail with the expected typed error.
- [x] Component activation state remains coherent across threads.
- [x] Deactivate prevents new gated callbacks while respecting in-flight work.

---

Risks and mitigation
--------------------

**Risk: lock contention.** Document the intended executor model and measure only
if a real bottleneck appears.

**Risk: callbacks trigger lifecycle transitions.** Enforce the existing
reentrant-transition rules and add regression tests.

**Risk: use-after-cleanup behavior.** Keep cleanup and callback gating explicit;
do not promise arbitrary concurrent destruction unless tests prove it.

---

Dependencies
------------

- Requires: Sprint 6 gating semantics.
- Requires: Sprint 7 cleanup ownership semantics.
- Requires: Sprint 3 testing helpers.
- Requires: existing error handling contract.

---

Scope boundaries
----------------

In scope:

- callback group helper design
- component constructor support
- concurrency contract documentation
- focused concurrency tests

Out of scope:

- custom executor implementation
- lock-free data structures
- arbitrary multi-executor topology support

---

Success signal
--------------

- [x] Multi-threaded use has a documented, test-backed contract.
- [x] Callback groups are easier to wire without hiding ROS 2 semantics.
- [x] Existing lifecycle guarantees remain intact.

---

Shipped — 2026-05-08
====================

Test coverage: 13 new tests (10 callback-group helper + 3 ``_is_active`` thread-safety
regressions), on top of 6 pre-existing concurrent-transition tests.

**Decisions locked:**

- C1: ``LifecycleComponentNode.get_or_create_callback_group(component_name, group_type=None)``
  — idempotent per ``(name, type)`` pair, protected by the existing ``threading.RLock``.
- C2: Default group type is ``MutuallyExclusiveCallbackGroup``; ``ReentrantCallbackGroup``
  must be requested explicitly.
- C3: ``_is_active`` protected by ``_active_lock: threading.Lock`` on every
  ``LifecycleComponent``; contract is GIL-independent.
- In-flight policy: "drop at next gate" — a callback that passed the ``@when_active``
  gate before deactivation commits completes its current execution and is not re-invoked.

**Commitments:**

- ``src/lifecore_ros2/core/lifecycle_component_node.py``: ``_callback_groups`` registry,
  ``get_or_create_callback_group`` helper.
- ``src/lifecore_ros2/core/lifecycle_component.py``: ``_active_lock``, all
  ``_is_active`` read/write sites wrapped, ``@when_active`` gate snapshot,
  ``_on_deactivate`` in-flight policy documented in docstring.
- ``tests/core/test_callback_group_helper.py``: 10 helper tests (idempotency, type
  conflict, thread safety).
- ``tests/core/test_regression_active_lock.py``: 3 tests (in-flight visibility,
  post-deactivate coherence, post-cleanup coherence).
- ``docs/architecture.rst``: thread-safety table extended, new
  ``_is_active`` thread safety and in-flight policy subsection, invariant entries
  updated.
- ``docs/patterns.rst``: new ``get_or_create_callback_group`` pattern entry.
- Class docstrings updated on both ``LifecycleComponentNode`` and ``LifecycleComponent``.

**Next phases ready for:**

- Observability (Sprint 9) — concurrency contract is now explicit and tested.
- Health status (Sprint 10) — ``_is_active`` reads are thread-safe.
- Any ``MultiThreadedExecutor`` application — callback group contract is documented.
