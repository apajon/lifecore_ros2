Error handling contract
=======================

**Status**: Design note (pre-implementation placeholder).

**Purpose**: Define error propagation semantics and recovery policies for ``LifecycleComponent`` hooks before they become implicit.

---

Background
----------

Currently, lifecycle hooks (``_on_configure``, ``_on_activate``, etc.) can raise exceptions or return a failure state. The framework propagates these to the node's lifecycle transition result, but the semantics of partial failure, rollback, and sibling component state are not explicit.

This design note anticipates:

- What happens when one component's ``_on_configure`` fails?
- Do sibling components already configured stay in that state, or do we roll back?
- What is the contract for ``_on_error`` vs ``_on_cleanup``?
- Can a component transition directly from ERROR → CONFIGURED without going through CLEANUP?

---

Key questions
--------------

1. **Rollback semantics**: On partial failure during ``configure`` or ``activate``, should the framework attempt to restore previously-configured siblings to their prior state?
2. **Idempotence**: Can a hook assume it is called exactly once, or must it be safe to call multiple times?
3. **Resource cleanup**: Is ``_on_error`` called if ``_on_configure`` fails, or only if a transition into ERROR state is triggered?
4. **Ordering**: If component A fails during ``_on_configure``, which sibling components have already started their ``_on_configure``? (Sequential or parallel?)

---

Success criteria
----------------

- [ ] Write an explicit error propagation matrix: (component state × hook type × exception type) → (framework action, sibling state, next available transition)
- [ ] Document the rollback contract with examples
- [ ] Define when ``_on_error`` is called and what it must not assume
- [ ] Verify the contract against the test suite

---

Related backlog items
---------------------

- Lifecycle policies (ordering)
- Component dependencies (cascading failure)
- Testing utilities (error scenario fixtures)
