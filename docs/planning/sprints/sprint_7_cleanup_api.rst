Sprint 7 - Cleanup and ownership API
====================================

**Objective.** Make resource ownership and cleanup behavior boringly clear
before concurrency, health, or watchdog behavior depend on it.

**Deliverable.** Components have consistent cleanup semantics, and docs explain
which resources are owned by the component versus borrowed from the application.

---

Scope
-----

Audit and refine cleanup behavior for:

- publisher components
- subscriber components
- timer components
- service server components
- service client components
- custom ``LifecycleComponent`` subclasses in examples

Clarify:

- resources created in configure are released in cleanup
- deactivation gates runtime behavior but does not necessarily destroy ROS resources
- borrowed resources such as callback groups remain application-owned
- shutdown is not the only release path a component should rely on

Decisions already made
----------------------

- Configure owns ROS resource creation.
- Cleanup owns release of resources created by the component.
- Deactivate changes runtime behavior; it is not the normal resource-destruction
  mechanism.
- Borrowed resources remain borrowed and must not be destroyed by components.

To decide during sprint planning
--------------------------------

- Whether cleanup needs shared helper utilities or only documentation/tests.
- The exact idempotency contract for each component type.
- Which cleanup guarantees should be public docstrings versus architecture docs.

---

Validation
----------

- [ ] Cleanup releases owned ROS handles for each component type.
- [ ] Deactivate gates behavior without over-cleaning resources.
- [ ] Cleanup remains idempotent where the current contract requires it.
- [ ] Borrowed callback groups are not cleared or destroyed by components.

---

Success signal
--------------

- [ ] A user can answer "who owns this resource?" from the component docs.
- [ ] Concurrency and health planning can assume cleanup behavior is explicit and tested.
