Sprint 9 - Minimal observability
================================

Status:
  Archived / Completed

Completed in:
  Unknown

Outcome:
  See sprint body.

Follow-ups:
  See docs/planning/backlog.rst if applicable.


**Objective.** Add structured logging and lifecycle tracing for industrial
debugging.

**Deliverable.** Lifecycle behavior is debuggable without print statements.

---

Decisions already made
----------------------

- Observability stays lightweight and rclpy-native.
- Lifecycle diagnostics should be available through structured logs before any
  external metrics or tracing integration is considered.
- Detailed hook and gating information belongs at debug level; transition
  summaries may use a higher level if they remain useful.

Scope
-----

Structured logging
^^^^^^^^^^^^^^^^^^

Standardize lifecycle logs for:

- node transition start and completion
- component hook execution and result
- activation gating decisions
- hook failure and invalid transition diagnostics

Component timing
^^^^^^^^^^^^^^^^

Optionally measure hook duration and include it in debug-level logs.

Last error and transition history
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Deferred during sprint planning:

- last component error → Sprint 10 as a ``HealthStatus`` field.
- transition history → backlog, `issue #14 <https://github.com/apajon/lifecore_ros2/issues/14>`_.

Decisions made during sprint planning
--------------------------------------

- **Hook timing (Option B):** timing is measured and logged only when the logger
  is at DEBUG level. No flag, no extra API surface. Zero overhead in production.
- **last-error surface:** out of scope for this sprint. Planned for Sprint 10 as
  a field of the ``HealthStatus`` value object.
- **transition-history surface:** out of scope and not planned. Candidate for a
  future sprint if a concrete use case arises. Tracked in the backlog (GitHub
  issue). Logging-only remains the contract for this sprint.

---

Delivered — *2026-05-08*
------------------------

- Structured ``DEBUG`` log before each component hook: ``component=``, ``hook=``, ``action='start'``.
- Structured ``DEBUG`` log after each component hook: ``component=``, ``hook=``, ``result=``, ``duration_ms=``.
  Duration is always emitted in the hook-end message; logging-level filtering controls
  whether it appears in production (Option B — no flag, no extra API).
- ``DEBUG`` log before ``_release_resources``: ``component=``, ``action='release_resources'``.
- Node-level ``DEBUG`` before each transition propagation: ``transition=``, ``component_count=``.
- Node-level ``INFO`` after each successful transition: ``transition=``, ``result='SUCCESS'``.
- Node-level ``WARNING`` before ``error_processing`` propagation; ``INFO`` on success, ``ERROR`` on non-SUCCESS.
- Standardized activation-gating drop: ``component=``, ``method=``, ``action='dropped'``, ``reason='not_active'``.
- 15 regression tests in ``tests/core/test_observability.py`` asserting field presence
  without brittle full-message matching.
- No new public API surface. Observability is purely log-based.

---

Validation
----------

- [x] Transition logs include target state and component count.
- [x] Hook logs include component name, hook name, result, and duration when enabled.
- [x] Gating logs include action and allowed/denied outcome.
- [ ] Last error is captured and cleared according to the contract. *(deferred to Sprint 10)*
- [ ] Transition history, if added, is bounded and deterministic. *(deferred to backlog)*

---

Risks and mitigation
--------------------

**Risk: noisy logs.** Keep detailed messages at debug level and reserve info for
transition summaries.

**Risk: observability becomes a dependency magnet.** Keep the core rclpy-only;
external metrics/tracing adapters stay application code.

---

Dependencies
------------

- Requires: Sprint 2 error handling.
- Requires: Sprint 3 testing helpers.
- Benefits from: Sprint 6 gating consistency.

---

Scope boundaries
----------------

In scope:

- structured logs
- optional hook timing

Out of scope (deferred):

- last error read-only surface (Sprint 10)
- transition history (backlog, issue #14)
- OpenTelemetry runtime dependency
- Prometheus exporters
- distributed tracing
- custom visualization tools

---

Success signal
--------------

- [x] A lifecycle failure can be diagnosed from logs and read-only state.
- [x] Observability stays lightweight and ROS 2 native.
- [x] Tests assert important log fields without brittle full-message matching.
