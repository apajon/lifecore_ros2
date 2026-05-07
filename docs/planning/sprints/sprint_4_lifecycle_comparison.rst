Sprint 4 - Lifecycle comparison example
=======================================

**Objective.** Prove the value proposition with one concrete example before
adding more library surface.

**Deliverable.** A reader can compare plain ROS 2, classic ROS 2 lifecycle, and
``lifecore_ros2`` in the same sensor watchdog scenario.

---

Scope
-----

Create ``lifecore_ros2_examples/examples/lifecycle_comparison/`` in the
companion examples repository with three implementations of the same node:

1. plain ROS 2 node
2. classic ROS 2 lifecycle node
3. ``lifecore_ros2`` component-oriented lifecycle node

The scenario should include:

- one subscriber receiving sensor samples
- one publisher emitting watchdog/status output
- one timer checking freshness
- activation behavior that is visible in logs or tests
- cleanup behavior that releases ROS resources explicitly

The scenario is named ``sensor_watchdog``. It receives sensor values on
``/sensor/value`` with ``std_msgs/msg/Float64`` and publishes watchdog status on
``/sensor/status`` with ``std_msgs/msg/String``. Status changes should be visible
both on the status topic and in logs.

Target tree
-----------

::

   lifecore_ros2_examples/
   `-- examples/
       `-- lifecycle_comparison/
           |-- README.md
           |-- sensor_value_publisher_node.py
           |-- ros2_plain/
           |   `-- sensor_watchdog_node.py
           |-- ros2_lifecycle_classic/
           |   `-- sensor_watchdog_lifecycle_node.py
           `-- lifecore_ros2/
               `-- sensor_watchdog_lifecore_node.py

Decisions already made
----------------------

- The comparison belongs in the companion examples repository because it is an
  applied, scenario-driven example rather than a minimal library primitive.
- The first scenario is a single-node sensor watchdog, because it exercises the
  lifecycle boundary without requiring domain-specific dependencies.
- The example must compare structure and lifecycle behavior, not performance or
  launch orchestration.

Sprint decisions
----------------

- Use ``std_msgs/msg/Float64`` for sensor samples on ``/sensor/value``.
- Use ``std_msgs/msg/String`` for watchdog status on ``/sensor/status``.
- Emit watchdog status through both topic publication and logs.
- Keep each implementation autonomous. Do not use shared helper code between
  the three variants, because the point of the example is to compare structure.
- Add one minimal plain ROS 2 sensor publisher node as a shared runtime stimulus
  for all three watchdog variants. This node is not shared implementation code;
  it only publishes ``std_msgs/msg/Float64`` samples on ``/sensor/value`` so the
  examples can be run and tested consistently.
- Use runtime ROS 2 tests where lifecycle behavior depends on real publishers,
  subscribers, timers, spin, transitions, and cleanup.

Lifecycle behavior contract
---------------------------

Configure:

- Plain ROS 2 has no lifecycle configure transition. It creates the subscriber,
  publisher, and timer immediately in ``__init__``.
- Classic lifecycle creates the subscriber, lifecycle publisher, and timer in
  ``on_configure``.
- ``lifecore_ros2`` creates resources through the component-oriented lifecycle
  model during configure.

Activate:

- Plain ROS 2 starts active immediately and logs that behavior explicitly.
- Classic lifecycle activates its publisher and allows watchdog status output.
- ``lifecore_ros2`` activates the relevant components; subscriber handling,
  timer checks, and status publication become effective only after activation.

Deactivate:

- Plain ROS 2 has no native deactivation path.
- Classic lifecycle deactivates publication and gates watchdog behavior while
  inactive.
- ``lifecore_ros2`` gates subscriber handling, timer checks, and status
  publication while inactive.

Cleanup:

- Classic lifecycle explicitly destroys or releases the subscriber, publisher,
  and timer created during configure.
- ``lifecore_ros2`` releases the same resources through component cleanup.
- Plain ROS 2 relies on ``destroy_node()`` during shutdown.

Shutdown:

- All variants should terminate cleanly without leaving active timers,
  publishers, or subscriptions behind.
- Lifecycle variants should not add recovery or orchestration behavior.

Error:

- Keep error handling minimal and observable with clear logs.
- Do not introduce custom state machines, retry loops, or recovery flows.

Execution plan
--------------

- [x] Step 1 - Create the
  ``lifecore_ros2_examples/examples/lifecycle_comparison/`` tree with a README
  and autonomous directories for the three variants.
- [x] Step 2 - Implement the plain ROS 2 version first, adapting the draft
  ``SensorWatchdogNode`` so it publishes ``WAITING_FOR_FIRST_SAMPLE``, ``OK``,
  and ``STALE`` statuses on a timer and logs the same status transitions.
- [x] Step 3 - Implement a minimal plain ROS 2 sensor publisher node that emits
  ``std_msgs/msg/Float64`` samples on ``/sensor/value``. This node is shared as
  an external runtime driver for the three comparison variants.
- [x] Step 4 - Implement the classic lifecycle version with native ``rclpy``
  lifecycle semantics, keeping resource creation in configure, publication
  activation in activate, runtime gating in deactivate, and explicit release in
  cleanup.
- [x] Step 5 - Implement the ``lifecore_ros2`` version using
  ``LifecycleComponentNode`` and component-oriented lifecycle behavior. The node
  should show the same runtime contract with less lifecycle plumbing in the
  application node.
- [x] Step 6 - Add tests that smoke import all example modules and exercise the
  runtime behavior that matters: status publication, activation gating,
  deactivation gating, and cleanup behavior where it is observable without
  fragile timing.
- [x] Step 7 - Update documentation links after the example is real, including
  commands to run each variant and expected log or topic signals.

Acceptance criteria
-------------------

- The three example modules exist and can be imported.
- The shared plain ROS 2 sensor publisher node exists, can be imported, and
  publishes ``std_msgs/msg/Float64`` samples on ``/sensor/value``.
- The three variants use ``/sensor/value``, ``/sensor/status``,
  ``std_msgs/msg/Float64``, and ``std_msgs/msg/String`` consistently.
- Each variant is autonomous and readable without shared helper modules.
- The plain ROS 2 variant starts receiving, checking, and publishing
  immediately after node startup.
- The classic lifecycle variant creates resources in configure, publishes only
  after activation, gates behavior after deactivation, and releases resources in
  cleanup.
- The ``lifecore_ros2`` variant demonstrates the same lifecycle contract through
  component-oriented structure.
- Runtime tests verify that the ``lifecore_ros2`` variant gates subscriber,
  timer, and publication behavior while inactive.
- Watchdog status is visible on ``/sensor/status`` and in logs.
- The README explains how to run each variant, how to run the shared sensor
  publisher, and which status/log signals to observe.
- The example does not imply that ``lifecore_ros2`` is a launcher, lifecycle
  manager, or multi-node orchestrator.

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

- [x] Smoke import all watchdog modules and the shared sensor publisher module.
- [x] Run runtime ROS 2 tests for the behavior that depends on real publishers,
  subscribers, timers, spin, lifecycle transitions, and cleanup.
- [x] Verify the ``lifecore_ros2`` variant gates subscriber and timer behavior
  while inactive.
- [x] Verify the classic lifecycle variant publishes only after activation and
  gates behavior after deactivation.
- [ ] Verify the plain and classic variants remain runnable documentation, not
  regression mirrors.
- [x] Document expected commands and log signals.

Suggested targeted commands, run from ``lifecore_ros2_examples``:

::

  uv run ruff check examples/lifecycle_comparison tests
  uv run pyright
  uv run pytest tests

Escalate to the full validation gate if implementation touches
``src/lifecore_ros2/`` or changes existing lifecycle semantics:

::

   uv run ruff check .
   uv run pyright
   uv run pytest

---

Scope boundaries
----------------

In scope:

- one scenario, three implementations
- one minimal shared plain ROS 2 sensor publisher used as an external runtime
  stimulus
- dependency-light example suitable for the companion examples repo
- README/docs link after the example is real

Out of scope:

- domain-specific message packages
- multi-node orchestration
- launch-file tutorials
- performance, latency, or CPU benchmarking
- shared helper code that hides structural differences between variants
- public API changes in ``lifecore_ros2`` unless the implementation exposes a
  concrete library gap
- core-repo implementation for this scenario

---

Success signal
--------------

- [ ] A new reader understands the project value in under 30 seconds by reading
  or running the comparison.
- [ ] The example supports the message "build predictable ROS 2 nodes".
- [ ] The example does not imply that ``lifecore_ros2`` is a launcher,
  lifecycle manager, or multi-node orchestrator.
