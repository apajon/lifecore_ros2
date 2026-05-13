Sprint 11 - Lightweight watchdog
================================

Status:
  Archived / Completed

Completed in:
  Unknown

Outcome:
  See sprint body.

Follow-ups:
  See docs/planning/backlog.rst if applicable.


**Objective.** Observe and report unhealthy component state without dangerous
automatic recovery.

**Deliverable.** A lightweight watchdog pattern or component that consumes the
health/status API and reports actionable state.

---

Decisions already made
----------------------

- observe component health
- report stale, warning, and error states
- log actionable context
- remain separate from process restart and multi-node orchestration

To decide during sprint planning
--------------------------------

- Whether version 1 is a reusable component, an example pattern, or both.
- Whether requesting a lifecycle transition belongs in version 1 or should wait.
- What stale-time configuration is minimal enough for this sprint.

Scope boundaries
----------------

Explicitly out of scope:

- restart a process
- kill a node
- hide failures behind automatic recovery
- coordinate multiple nodes as a system lifecycle manager

---

Success signal
--------------

- [x] Users get better diagnostics without new failure modes.
- [x] The docs clearly separate internal component health from system orchestration.
