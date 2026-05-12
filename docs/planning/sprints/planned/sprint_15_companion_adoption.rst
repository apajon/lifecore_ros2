Sprint 15 - Companion adoption examples
=======================================

**Track.** Companion / Adoption.

**Branch.** ``sprint/15-companion-adoption``.

**Priority.** P1 - usage proof and adoption.

**Objective.** Strengthen proof of value with concrete, readable, testable
examples.

Scope
-----

- Audit the companion repository when available in the workspace.
- Identify the strongest lifecycle comparison example.
- Strengthen the comparative lifecycle example.
- Cover active publication, inactive publication blocking, activation gating,
  deactivation gating, cleanup, and expected errors in runtime tests.
- Explain why ``lifecore_ros2`` helps compared with manual ``rclpy`` lifecycle
  code.
- Add links from ``README.md`` and ``ROADMAP.md`` when the example is ready.

Non-goals
---------

- No new core abstraction just to make an example shorter.
- No dependency-heavy showcase unless the scenario requires it.

Acceptance criteria
-------------------

- [ ] A new user can understand the value by reading and running one example.
- [ ] The example does not require knowing the full internal architecture.
- [ ] The example demonstrates less boilerplate, cleaner transitions, clearer
  errors, safer activation/deactivation, and deterministic cleanup.
