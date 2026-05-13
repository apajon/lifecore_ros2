Sprint 10 - Health status API
=============================

Status:
  Archived / Completed

Completed in:
  Unknown

Outcome:
  See sprint body.

Follow-ups:
  See docs/planning/backlog.rst if applicable.


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

Decisions finalised during sprint planning
------------------------------------------

- **Python type shape:** ``@dataclass(frozen=True)`` from stdlib — no new PyPI
  dependencies. ``HealthStatus`` is immutable and hashable, enabling direct
  equality assertions in tests.
- **Level names:** ``UNKNOWN | OK | DEGRADED | ERROR``.
  ``UNKNOWN`` = not yet configured. ``OK`` = last transition succeeded.
  ``DEGRADED`` = hook returned ``FAILURE`` (controlled). ``ERROR`` = exception
  captured by ``_guarded_call``. ``STALE`` is a watchdog concern, not a core level.
- **API scope:** component-level + node-level aggregation. ``node.health`` returns
  the worst-severity ``HealthStatus`` across all registered components.

---

Scope boundaries
----------------

In scope:

- component-level health/status reporting
- node-level aggregation: ``LifecycleComponentNode.health`` (worst-of across components)
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

- [x] A watchdog can be designed as a consumer of health, not as a hidden part
  of every component.
- [x] The API improves observability without making recovery promises.

---

Delivery
--------

*Shipped in v0.10.0 (2026-05-08)*

- ``src/lifecore_ros2/core/health.py`` — ``HealthLevel``, ``HealthStatus``,
  ``HEALTH_UNKNOWN``.
- ``LifecycleComponent.health`` property — updated by ``_guarded_call`` and each
  ``on_*`` handler.
- ``LifecycleComponentNode.health`` property — worst-of aggregation.
- ``HealthStatus`` and ``HealthLevel`` exported from ``lifecore_ros2``.
- 30 regression tests in ``tests/core/test_health.py``.
- Example: ``examples/minimal_health_status.py``.
