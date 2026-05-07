Sprint 8 - Concurrency infrastructure
=====================================

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

- Exact callback-group helper API, if any helper is needed.
- Whether callback-group storage belongs on the node or stays purely caller-owned.
- The precise policy for in-flight callbacks during deactivate and cleanup.

---

Validation
----------

- [ ] Callback group creation is idempotent per component name.
- [ ] Different component names receive distinct groups when requested.
- [ ] Component constructors pass callback groups to ROS resource creation.
- [ ] Concurrent lifecycle transitions fail with the expected typed error.
- [ ] Component activation state remains coherent across threads.
- [ ] Deactivate prevents new gated callbacks while respecting in-flight work.

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

- [ ] Multi-threaded use has a documented, test-backed contract.
- [ ] Callback groups are easier to wire without hiding ROS 2 semantics.
- [ ] Existing lifecycle guarantees remain intact.
