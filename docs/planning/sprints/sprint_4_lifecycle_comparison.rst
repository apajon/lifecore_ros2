Sprint 4 - Lifecycle comparison example
=======================================

**Objective.** Prove the value proposition with one concrete example before
adding more framework surface.

**Deliverable.** A reader can compare plain ROS 2, classic ROS 2 lifecycle, and
``lifecore_ros2`` in the same sensor watchdog scenario.

---

Scope
-----

Create ``examples/lifecycle_comparison/`` in the core repository with three
implementations of the same node:

1. plain ROS 2 node
2. classic ROS 2 lifecycle node
3. ``lifecore_ros2`` component-oriented lifecycle node

The scenario should include:

- one subscriber receiving sensor samples
- one publisher emitting watchdog/status output
- one timer checking freshness
- activation behavior that is visible in logs or tests
- cleanup behavior that releases ROS resources explicitly

Decisions already made
----------------------

- The comparison belongs in the core repository first, not in the companion
  examples repository.
- The first scenario is a single-node sensor watchdog, because it exercises the
  lifecycle boundary without requiring domain-specific dependencies.
- The example must compare structure and lifecycle behavior, not performance or
  launch orchestration.

To decide during sprint planning
--------------------------------

- Exact message types and topic names.
- Whether the watchdog output is a status topic, logs, or both.
- How much shared helper code is acceptable between the three variants.

---

Why this sprint comes first
---------------------------

The market need is implicit. A strong comparison example is the clearest way to
show that the library is not just cleaner code, but safer lifecycle structure.

The example should make these tradeoffs visible:

- plain ROS 2 is simple but easy to make active too early
- classic lifecycle is controlled but verbose
- ``lifecore_ros2`` keeps lifecycle semantics native while reducing internal
  lifecycle sprawl

---

Validation
----------

- [ ] Smoke import all three example modules.
- [ ] Verify the ``lifecore_ros2`` variant gates subscriber and timer behavior
  while inactive.
- [ ] Verify the plain and classic variants remain runnable documentation, not
  regression mirrors.
- [ ] Document expected commands and log signals.

---

Scope boundaries
----------------

In scope:

- one scenario, three implementations
- dependency-light example suitable for the core repo
- README/docs link after the example is real

Out of scope:

- domain-specific message packages
- multi-node orchestration
- launch-file tutorials
- companion-repo migration before the core comparison is useful

---

Success signal
--------------

- [ ] A new reader understands the project value in under 30 seconds by reading
  or running the comparison.
- [ ] The example supports the message "build predictable ROS 2 nodes".
- [ ] The example does not imply that ``lifecore_ros2`` is a launcher,
  lifecycle manager, or multi-node orchestrator.
