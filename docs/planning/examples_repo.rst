Companion examples repository
=============================

Planning for the ``lifecore_ros2_examples`` companion repository.

This file records planning context for the companion repository at
``apajon/lifecore_ros2_examples``.

Status note
-----------

This page is planning context for the companion repository, not the current
core sprint index. The initial sensor watchdog comparison baseline is already
shipped in the companion repo; the adoption follow-up is archived in
:doc:`sprints/archived/sprint_15_companion_adoption`.

Bootstrap status: the repository exists and the initial foundation lives on the
``bootstrap/repo-foundation`` branch. Since ``lifecore_ros2`` is published on PyPI,
the companion repository should resolve the core dependency from PyPI by default.

---

Purpose
-------

Host **concrete, scenario-driven examples** that demonstrate lifecore_ros2
patterns under conditions too applied, too multi-file, or too workflow-oriented
to belong in the core repo's ``examples/`` directory.

The core repo keeps simple/minimal examples that teach one library abstraction
at a time. The companion repo owns concrete examples that show how those
abstractions work together in realistic ROS 2 scenarios.

---

Repository identity
-------------------

- **Name**: ``lifecore_ros2_examples``
- **Owner**: ``apajon`` (same GitHub owner as ``lifecore_ros2``)
- **License**: Apache-2.0 (matches core)
- **Python / ROS baseline**: tracks the core library — Python 3.12+, ROS 2 Jazzy
- **Versioning**: independent of the core library version. The companion repo follows the core release cadence but does not pin a coupled version number.

Rejected name alternatives:

- ``lifecore_ros2_demos`` — "demos" reads as throwaway; we want examples that are followable and re-usable as scaffolding.
- ``lifecore_examples`` — drops the ``_ros2`` qualifier; risks confusion if a non-ROS variant ever exists.
- ``lifecore_ros2_recipes`` — implies a cookbook format that constrains structure prematurely.

---

Scope boundary — what belongs here vs. in core
-----------------------------------------------

An example belongs in **lifecore_ros2_examples** (companion repo) if **any** of the following is true:

1. it depends on third-party ROS packages beyond ``rclpy`` and ``std_msgs``
2. it uses domain-specific message types (``sensor_msgs``, ``geometry_msgs``, custom ``.msg``)
3. it spans more than one ROS node or launch file
4. it teaches an applied pattern (sensor fusion, watchdog comparison,
   supervisor, diagnostics aggregation) rather than a single core abstraction

An example belongs in **lifecore_ros2/examples/** (core repo) if **all** of the following are true:

1. it depends only on ``rclpy`` and ``std_msgs``
2. it fits in a single Python file
3. it teaches exactly one core abstraction or one lifecycle invariant
4. its expected log output can be documented in the module docstring

**Contributor exclusion test.** When in doubt, the example goes to the companion repo.

---

Example categories (initial outline)
------------------------------------

Some applied examples may take conceptual inspiration from MIT's `Underactuated Robotics`_
materials, especially when choosing dynamics, estimation, control, or robotics-system scenarios.
Those materials are inspiration for example design only; the companion repository does not vendor,
mirror, or reproduce their content.

.. _Underactuated Robotics: https://underactuated.mit.edu/

Strategic comparison bridge
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The strategic comparison example belongs in the companion examples repository:

::

   lifecore_ros2_examples/examples/lifecycle_comparison/

It compares one sensor watchdog node implemented as:

1. plain ROS 2
2. classic ROS 2 lifecycle
3. ``lifecore_ros2``

The comparison stays dependency-light, but it is still a concrete scenario: it
uses multiple autonomous files plus a shared runtime sensor publisher to compare
the same behavior across implementations. That makes it a better fit for
``lifecore_ros2_examples`` than for the core repo's minimal ``examples/``
directory.

Applied examples — after the comparison baseline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These examples are candidates for later applied validation after the lifecycle
comparison has proven the basic value proposition. They should start in the
companion examples repository unless they teach exactly one core abstraction in
one minimal file.

- **io_gateway_node** — I/O transformation with Pub, Sub, Timer, Service + stateful processing. Teaches component coordination and gating.
- **robot_state_monitor** — Health aggregation from multiple subscribers. Teaches composition, partial failure, state queries.
- **command_gateway** — Service request validation and dispatch to client. Teaches validation hooks, error handling, async patterns.
- **minimal_supervised_node** — Multiple components with supervised error recovery. Teaches rollback, partial activation, orchestration.

Sensor-pipeline composition
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Multi-publisher / multi-subscriber pipelines with a fan-in or fan-out shape.
Teaches activation gating across a topology, configure-time resource acquisition for simulated or real sensor handles, and how ``LifecycleComponent`` composition scales past the minimal examples already shown in the core repo.

Lifecycle-aware diagnostics
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Components that publish to ``/diagnostics``, react to lifecycle transitions of *other* nodes, or aggregate health signals from sibling components. Teaches inter-component contracts, ``_on_error`` semantics, and graceful deactivation under partial failure.

Multi-node orchestration patterns
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Two or more ``LifecycleComponentNode`` processes coordinated by an external supervisor or launch file. Teaches the boundary between intra-node composition (the core library's job) and inter-node orchestration (explicitly out of scope for the core library).

---

Later applied companion example — sensor-fusion pipeline
--------------------------------------------------------

**Working title**: ``sensor_fusion_pipeline.py`` (or split across a small package)

This remains a later applied companion-repo example after the lifecycle
comparison example has made the basic value proposition obvious.

Topology
^^^^^^^^

- two ``LifecyclePublisherComponent`` instances simulating heterogeneous sensors (e.g. IMU-shaped at 100 Hz, GPS-shaped at 10 Hz) on distinct topics
- one fusion ``LifecycleComponent`` subscribing to both, applying a trivial weighted average, publishing the fused estimate
- one ``LifecycleSubscriberComponent`` consuming the fused topic for logging

Lifecycle teaching axis
^^^^^^^^^^^^^^^^^^^^^^^

- **configure**: each sensor allocates its publisher; fusion node allocates two subscriptions and one publisher; downstream subscriber allocates one subscription
- **activate**: timers start on each sensor; fusion node begins emitting only after both inputs have been observed at least once (demonstrates inbound-drop policy during the warm-up window without raising)
- **deactivate**: sensor timers stop; fusion node clears its rolling state to prevent stale-data bias on reactivation; subscriptions remain allocated
- **cleanup**: all ROS resources released; simulated sensor handles released

What it proves
^^^^^^^^^^^^^^

- a fan-in topology with independent activation timing
- a ``LifecycleComponent`` that owns *more than two* ROS resources
- explicit handling of the "warm-up" window where one input is active but its peer has not yet delivered

---

Repository structure (planned)
------------------------------

::

   lifecore_ros2_examples/
   ├── README.md
   ├── LICENSE
   ├── pyproject.toml                # depends on the published lifecore_ros2 package
   ├── examples/
   │   ├── lifecycle_comparison/
   │   │   ├── README.md
   │   │   ├── sensor_value_publisher_node.py
   │   │   ├── ros2_plain/
   │   │   ├── ros2_lifecycle_classic/
   │   │   └── lifecore_ros2/
   │   ├── sensor_fusion/
   │   │   ├── __init__.py
   │   │   └── sensor_fusion_pipeline.py
   │   └── ...                       # one folder per applied scenario
   ├── tests/                        # smoke tests only, not a regression mirror
   └── docs/                         # optional, may stay README-only initially

The layout remains planning-oriented, but the repository now exists and uses
this structure as its baseline.

---

Out of scope
------------

- replacing or duplicating the core regression test suite
- providing production-grade reference architectures
- packaging examples for PyPI distribution
- maintaining backward compatibility for example APIs across versions
- hosting documentation that contradicts or supersedes the core docs

---

Coupling to core releases
--------------------------

- the companion repo depends on the published ``lifecore_ros2`` package by default
- local editable overrides remain a developer workflow for testing examples against unreleased core changes
- breaking core API changes update the pin; the companion repo does **not** gate core releases
- the core repo's release process never blocks on companion-repo state

---

Implementation phases
---------------------

Strategic comparison baseline — shipped; Sprint 15 polish completed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [x] Build ``lifecore_ros2_examples/examples/lifecycle_comparison/``.
- [x] Keep it dependency-light while still treating it as a concrete comparison
  scenario.
- [x] Include the shared plain ROS 2 sensor publisher as an external runtime
  stimulus for all watchdog variants.
- [x] Complete the ``lifecore_ros2`` variant.
- [x] Add runtime tests that exercise publication, activation gating,
   deactivation gating, and cleanup behavior.
- [x] Document and test inactive runtime misuse as lifecycle gating behavior,
   not as a new exception policy.
- [x] Clarify that public component hooks such as ``on_message`` and
   ``on_tick`` stay explicit while lifecycle gating remains framework-managed.
- [x] Update core README/docs before broad public announcement.

The adoption-polish follow-up is archived in
:doc:`sprints/archived/sprint_15_companion_adoption`. The sprint passed the
companion repository validation gate on 2026-05-13.

Applied validation phase (after the comparison baseline)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After the lifecycle comparison exists, additional concrete examples should be
validated in ``lifecore_ros2_examples/examples/`` by default:

- Companion examples are scenario-shaped but still dependency-light where
   possible: io_gateway_node, command_gateway, etc.
- They validate the API and reveal friction
- They guide future design work without replacing the comparison example as the primary adoption proof
- Only one-file, one-abstraction teaching examples should be added to the core
   repo first

Phase 0 — Repository bootstrap
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [x] Create ``apajon/lifecore_ros2_examples`` on GitHub
- [x] Add ``LICENSE`` (Apache-2.0)
- [x] Add ``README.md`` with positioning, scope boundary, install, and link back to core
- [x] Add ``pyproject.toml``: Python 3.12+, local editable ``lifecore_ros2`` source, dev extras (ruff, pyright, pytest)
- [x] Add ``.gitignore``, ``.editorconfig``, ``.pre-commit-config.yaml`` aligned with core
- [x] Add a manual-only quality workflow (``workflow_dispatch``; no broad ``push`` trigger)

Phase 1 — Next applied example: sensor-fusion pipeline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Context.** Concrete examples are validated in the companion repo by default.
The core repo remains reserved for small, dependency-light examples that teach
one library abstraction at a time.

This later example focuses on **sensor-fusion pipeline** — fan-in multi-sensor integration:
- [ ] Two simulated heterogeneous sensors as ``LifecyclePublisherComponent`` instances
- [ ] Fusion ``LifecycleComponent`` with two subscriptions and one publisher
- [ ] Downstream ``LifecycleSubscriberComponent`` for logging
- [ ] Module docstring with teaching axis, CLI commands, expected log output
- [ ] Demonstrate the warm-up window with explicit inbound-drop behavior
- [ ] Demonstrate state reset on deactivate (rolling-average buffer cleared)
- [ ] Add ``examples/sensor_fusion/README.md`` explaining the topology

Phase 2 — Quality gates
^^^^^^^^^^^^^^^^^^^^^^^

- [x] CI workflow: ``ruff check``, ``ruff format --check``, ``pyright``, ``pytest``
- [x] Smoke test that imports each example module without invoking ``rclpy.spin``
- [x] Document validation commands in the repo ``README.md``
- [ ] Confirm install-from-scratch on a clean ROS 2 Jazzy environment

Phase 3 — Signposting back to core
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [x] Update ``lifecore_ros2/README.md`` to link to the live companion repo URL
- [x] Update ``lifecore_ros2/docs/examples.rst`` to link to the live companion repo URL
- [ ] Move planning artifacts from core repo into the companion repo
- [x] Update ``lifecore_ros2/ROADMAP.md`` to mark the companion repo as published

Phase 4 — Second example (post-Phase-3)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [ ] Choose between *lifecycle-aware diagnostics* and *multi-node orchestration* based on user feedback
- [ ] Apply the same module-docstring discipline (one teaching axis, expected output)
- [ ] Avoid expanding into a domain platform — each example remains followable in isolation

---

Non-goals
---------

Do not add to this list:

- a regression test suite mirroring the core repo
- production-grade reference architectures
- a PyPI package
- documentation that supersedes the core docs
- backward-compatibility guarantees for example APIs across versions
