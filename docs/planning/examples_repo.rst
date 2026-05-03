Companion examples repository
=============================

Planning for the ``lifecore_ros2_examples`` companion repository.

This file records planning context for the companion repository at
``apajon/lifecore_ros2_examples``.

Bootstrap status: the repository exists and the initial foundation lives on the
``bootstrap/repo-foundation`` branch. Since ``lifecore_ros2`` is published on PyPI,
the companion repository should resolve the core dependency from PyPI by default.

---

Purpose
-------

Host **applied, scenario-driven examples** that demonstrate lifecore_ros2 patterns under conditions too domain-flavored or too multi-node to belong in the core repo's ``examples/`` directory.

The companion repo should amplify the core repo's strongest examples. It should
not become the place where the basic value proposition is first proven.

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
4. it teaches an applied pattern (sensor fusion, supervisor, diagnostics aggregation) rather than a single core abstraction

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

The next strategic example should be built in the core repo first:

::

   examples/lifecycle_comparison/

It compares one sensor watchdog node implemented as:

1. plain ROS 2
2. classic ROS 2 lifecycle
3. ``lifecore_ros2``

The companion repo can later host a richer version if the scenario needs
domain-specific messages, multiple nodes, launch files, or applied diagnostics.
Until then, the core repo owns the proof that ``lifecore_ros2`` makes a single
node more predictable without hiding ROS 2 lifecycle semantics.

Applied examples — after Sprint 4
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These examples are candidates for later applied validation after the lifecycle comparison has proven the basic value proposition. They may be developed in the core repo first if they stay dependency-light, then moved to or expanded in the companion repo.

- **io_gateway_node** — I/O transformation with Pub, Sub, Timer, Service + stateful processing. Teaches component coordination and gating.
- **robot_state_monitor** — Health aggregation from multiple subscribers. Teaches composition, partial failure, state queries.
- **command_gateway** — Service request validation and dispatch to client. Teaches validation hooks, error handling, async patterns.
- **minimal_supervised_node** — Multiple components with supervised error recovery. Teaches rollback, partial activation, orchestration.

Sensor-pipeline composition
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Multi-publisher / multi-subscriber pipelines with a fan-in or fan-out shape.
Teaches activation gating across a topology, configure-time resource acquisition for simulated or real sensor handles, and how ``LifecycleComponent`` composition scales past the three-component pipeline already shown in the core repo.

Lifecycle-aware diagnostics
^^^^^^^^^^^^^^^^^^^^^^^^^^

Components that publish to ``/diagnostics``, react to lifecycle transitions of *other* nodes, or aggregate health signals from sibling components. Teaches inter-component contracts, ``_on_error`` semantics, and graceful deactivation under partial failure.

Multi-node orchestration patterns
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Two or more ``LifecycleComponentNode`` processes coordinated by an external supervisor or launch file. Teaches the boundary between intra-node composition (the core library's job) and inter-node orchestration (explicitly out of scope for the core library).

---

First applied companion example — sensor-fusion pipeline
--------------------------------------------------------

**Working title**: ``sensor_fusion_pipeline.py`` (or split across a small package)

This remains the first applied companion-repo example after the core comparison
example has made the basic value proposition obvious.

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
   │   ├── sensor_fusion/
   │   │   ├── __init__.py
   │   │   └── sensor_fusion_pipeline.py
   │   └── ...                       # one folder per applied scenario
   ├── tests/                        # smoke tests only, not a regression mirror
   └── docs/                         # optional, may stay README-only initially

Layout is provisional. The first commit will lock it.

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

Strategic prerequisite — Sprint 4 lifecycle comparison in core
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [ ] Build ``lifecore_ros2/examples/lifecycle_comparison/`` first.
- [ ] Keep it dependency-light so it belongs in the core repository.
- [ ] Use the companion repo only for an extended applied version if needed.
- [ ] Update core README/docs before broad public announcement.

Applied validation phase (after Sprint 4)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After the lifecycle comparison exists, additional dependency-light examples can be validated in the core ``examples/`` directory:

- Core examples are simple but real: io_gateway_node, command_gateway, etc.
- They validate the API and reveal friction
- They guide future design work without replacing the comparison example as the primary adoption proof
- Once proven, they can be ported or extended in the companion repo

Phase 0 — Repository bootstrap
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [x] Create ``apajon/lifecore_ros2_examples`` on GitHub
- [x] Add ``LICENSE`` (Apache-2.0)
- [x] Add ``README.md`` with positioning, scope boundary, install, and link back to core
- [x] Add ``pyproject.toml``: Python 3.12+, local editable ``lifecore_ros2`` source, dev extras (ruff, pyright, pytest)
- [x] Add ``.gitignore``, ``.editorconfig``, ``.pre-commit-config.yaml`` aligned with core
- [x] Add a manual-only quality workflow (``workflow_dispatch``; no broad ``push`` trigger)

Phase 1 — First applied example: sensor-fusion pipeline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Context.** Core examples are validated in the core repo when they stay small and dependency-light. This phase extends them with domain-specific, multi-node, or complex scenarios that belong in the companion repo.

First example focuses on **sensor-fusion pipeline** — fan-in multi-sensor integration:
- [ ] Two simulated heterogeneous sensors as ``LifecyclePublisherComponent`` instances
- [ ] Fusion ``LifecycleComponent`` with two subscriptions and one publisher
- [ ] Downstream ``LifecycleSubscriberComponent`` for logging
- [ ] Module docstring with teaching axis, CLI commands, expected log output
- [ ] Demonstrate the warm-up window with explicit inbound-drop behavior
- [ ] Demonstrate state reset on deactivate (rolling-average buffer cleared)
- [ ] Add ``examples/sensor_fusion/README.md`` explaining the topology

Phase 2 — Quality gates
^^^^^^^^^^^^^^^^^^^^^^

- [x] CI workflow: ``ruff check``, ``ruff format --check``, ``pyright``, ``pytest``
- [ ] Smoke test that imports each example module without invoking ``rclpy.spin``
- [x] Document validation commands in the repo ``README.md``
- [ ] Confirm install-from-scratch on a clean ROS 2 Jazzy environment

Phase 3 — Signposting back to core
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [ ] Update ``lifecore_ros2/README.md`` to link to the live companion repo URL
- [ ] Update ``lifecore_ros2/docs/examples.rst`` to link to the live companion repo URL
- [ ] Move planning artifacts from core repo into the companion repo
- [ ] Update ``lifecore_ros2/ROADMAP.md`` to mark the companion repo as published

Phase 4 — Second example (post-Phase-3)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [ ] Choose between *lifecycle-aware diagnostics* and *multi-node orchestration* based on user feedback
- [ ] Apply the same module-docstring discipline (one teaching axis, expected output)
- [ ] Avoid expanding into a domain framework — each example remains followable in isolation

---

Non-goals
---------

Do not add to this list:

- a regression test suite mirroring the core repo
- production-grade reference architectures
- a PyPI package
- documentation that supersedes the core docs
- backward-compatibility guarantees for example APIs across versions
