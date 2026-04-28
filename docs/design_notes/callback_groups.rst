Callback groups and concurrency utilities
===========================================

**Status**: Design note (pre-implementation placeholder).

**Purpose**: Define framework support for callback group management and lifecycle-aware concurrency patterns.

---

Background
----------

Currently, applications must manually create and assign ``CallbackGroup`` instances via ``node.create_callback_group()``. As component counts grow and callback sequencing matters, the framework could offer:

- Scoped callback group creation per component
- Activation-gating for callbacks (prevent execution while inactive)
- Multi-threaded executor coordination patterns

This design note reserves the decision space to avoid ad-hoc threading solutions.

---

Key questions
--------------

1. **Scoped creation**: Should ``LifecycleComponentNode`` offer a helper like ``create_callback_group_for_component(name)`` that creates and tracks groups?
2. **Activation gating**: Should timers, subscriptions, and service handlers automatically respect component activation state, or remain application-controlled?
3. **Executor binding**: Should components declare preferred callback group types (exclusive, reentrant, mutually-exclusive), or is that application-level?
4. **Coordination**: For multi-threaded executors, what are the thread-safety guarantees? (Currently: single-threaded via RLock on registration.)

---

Scope boundaries
----------------

- **In-scope**: Helpers for common patterns (group-per-component, callback gating)
- **Out-of-scope**: Custom executor or executor pool management (deferred; see ROS 2 executor abstraction)
- **Out-of-scope**: Automatic executor selection or multi-threaded by default (deferred)

---

Success criteria
----------------

- [ ] Write a design: scoped callback group API and its usage examples
- [ ] Document the activation gating pattern (if applicable)
- [ ] Define concurrency guarantees for components in different callback groups
- [ ] Verify against the concurrency contract (see :doc:`../architecture`)

---

Related backlog items
---------------------

- Ownership & threading (concurrency model)
- Execution and timing (callback duration tracking)
- Component state and health (callback performance metrics)
