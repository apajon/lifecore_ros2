Sprint 10 - Health status API
=============================

**Objective.** Expose component health without introducing recovery behavior.

**Deliverable.** Applications can ask a component or node for a small, stable
health/status value.

---

Decisions already made
----------------------

- Health is read-only in the first version.
- Health reports state; it does not perform recovery.
- The first value should stay small: a level plus a human-readable reason is the
  intended shape.
- Node-level aggregation is optional and must remain obvious if included.
- ``last_error`` from Sprint 9 observability is integrated as a field of
  ``HealthStatus`` rather than as a standalone property. A component that has
  faulted exposes the error reason through its health level and reason field.

To decide during sprint planning
--------------------------------

- Exact Python type shape: dataclass, enum-backed value object, or another small
  representation.
- Exact level names and whether ``stale`` is a core level or a watchdog concern.
- Whether the first API is component-only or also exposed through the node.

---

Scope boundaries
----------------

In scope:

- component-level health/status reporting
- optional node-level aggregation if it stays obvious
- status values that help debugging and tests
- ``last_error`` as a field of the health value object (level + human-readable reason)

Out of scope:

- automatic restart
- lifecycle transition requests
- ROS diagnostics integration
- distributed health across multiple nodes

---

Success signal
--------------

- [ ] A watchdog can be designed as a consumer of health, not as a hidden part
  of every component.
- [ ] The API improves observability without making recovery promises.
