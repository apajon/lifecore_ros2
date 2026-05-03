Sprint 9 - Minimal observability
================================

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

Candidate read-only surfaces:

- last component error
- last transition result
- bounded transition history

To decide during sprint planning
--------------------------------

- Exact field names for structured log messages.
- Whether last-error and transition-history surfaces are part of this sprint or
  stay behind logging only.
- The size and ordering of any bounded transition history.

---

Validation
----------

- [ ] Transition logs include target state and component count.
- [ ] Hook logs include component name, hook name, result, and duration when enabled.
- [ ] Gating logs include action and allowed/denied outcome.
- [ ] Last error is captured and cleared according to the contract.
- [ ] Transition history, if added, is bounded and deterministic.

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
- last error / transition history if small and testable

Out of scope:

- OpenTelemetry runtime dependency
- Prometheus exporters
- distributed tracing
- custom visualization tools

---

Success signal
--------------

- [ ] A lifecycle failure can be diagnosed from logs and read-only state.
- [ ] Observability stays lightweight and ROS 2 native.
- [ ] Tests assert important log fields without brittle full-message matching.
