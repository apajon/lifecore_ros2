# Roadmap — `lifecore_ros2_examples`

Planning artifact for the companion examples repository of `lifecore_ros2`.
This file lives inside the core repo until the companion repository is created.
At that point it will move to `apajon/lifecore_ros2_examples` and be removed from here.

---

## Purpose

Host **applied, scenario-driven examples** that demonstrate `lifecore_ros2` patterns under
conditions too domain-flavored or too multi-node to belong in the core repo's `examples/`
directory.

---

## Repository identity

- **Name**: `lifecore_ros2_examples`
- **Owner**: `apajon` (same GitHub owner as `lifecore_ros2`)
- **License**: Apache-2.0 (matches core)
- **Python / ROS baseline**: tracks the core library — Python 3.12+, ROS 2 Jazzy
- **Versioning**: independent of the core library version. The companion repo follows the
  core release cadence but does not pin a coupled version number.

### Rejected name alternatives

- `lifecore_ros2_demos` — "demos" reads as throwaway; we want examples that are followable
  and re-usable as scaffolding.
- `lifecore_examples` — drops the `_ros2` qualifier; risks confusion if a non-ROS variant
  ever exists.
- `lifecore_ros2_recipes` — implies a cookbook format that constrains structure prematurely.

---

## Scope boundary — what belongs here vs. in core

An example belongs in **`lifecore_ros2_examples`** (companion repo) if **any** of the
following is true:

1. it depends on third-party ROS packages beyond `rclpy` and `std_msgs`
2. it uses domain-specific message types (`sensor_msgs`, `geometry_msgs`, custom `.msg`)
3. it spans more than one ROS node or launch file
4. it teaches an applied pattern (sensor fusion, supervisor, diagnostics aggregation)
   rather than a single core abstraction

An example belongs in **`lifecore_ros2/examples/`** (core repo) if **all** of the
following are true:

1. it depends only on `rclpy` and `std_msgs`
2. it fits in a single Python file
3. it teaches exactly one core abstraction or one lifecycle invariant
4. its expected log output can be documented in the module docstring

This rule is the contributor-facing exclusion test. When in doubt, the example goes to
the companion repo.

---

## Example categories (initial outline)

### 1. Sensor-pipeline composition

Multi-publisher / multi-subscriber pipelines with a fan-in or fan-out shape.
Teaches activation gating across a topology, configure-time resource acquisition for
simulated or real sensor handles, and how `LifecycleComponent` composition scales past
the three-component pipeline already shown in the core repo.

### 2. Lifecycle-aware diagnostics

Components that publish to `/diagnostics`, react to lifecycle transitions of *other*
nodes, or aggregate health signals from sibling components. Teaches inter-component
contracts, `_on_error` semantics, and graceful deactivation under partial failure.

### 3. Multi-node orchestration patterns

Two or more `LifecycleComponentNode` processes coordinated by an external supervisor or
launch file. Teaches the boundary between intra-node composition (the core library's job)
and inter-node orchestration (explicitly out of scope for the core library).

---

## First concrete example — sensor-fusion pipeline

**Working title**: `sensor_fusion_pipeline.py` (or split across a small package)

**Topology**
- two `LifecyclePublisherComponent` instances simulating heterogeneous sensors
  (e.g. IMU-shaped at 100 Hz, GPS-shaped at 10 Hz) on distinct topics
- one fusion `LifecycleComponent` subscribing to both, applying a trivial weighted
  average, publishing the fused estimate
- one `LifecycleSubscriberComponent` consuming the fused topic for logging

**Lifecycle teaching axis**
- **configure**: each sensor allocates its publisher; fusion node allocates two
  subscriptions and one publisher; downstream subscriber allocates one subscription
- **activate**: timers start on each sensor; fusion node begins emitting only after
  both inputs have been observed at least once (demonstrates inbound-drop policy
  during the warm-up window without raising)
- **deactivate**: sensor timers stop; fusion node clears its rolling state to prevent
  stale-data bias on reactivation; subscriptions remain allocated
- **cleanup**: all ROS resources released; simulated sensor handles released

**What it proves that current core examples do not**
- a fan-in topology with independent activation timing
- a `LifecycleComponent` that owns *more than two* ROS resources
- explicit handling of the "warm-up" window where one input is active but its peer
  has not yet delivered

---

## Repository structure (planned, not normative)

```
lifecore_ros2_examples/
├── README.md
├── LICENSE
├── pyproject.toml                # depends on lifecore_ros2 from PyPI
├── examples/
│   ├── sensor_fusion/
│   │   ├── __init__.py
│   │   └── sensor_fusion_pipeline.py
│   └── ...                       # one folder per applied scenario
├── tests/                        # smoke tests only, not a regression mirror
└── docs/                         # optional, may stay README-only initially
```

Layout is provisional. The first commit will lock it.

---

## Out of scope for the companion repo

- replacing or duplicating the core regression test suite
- providing production-grade reference architectures
- packaging examples for PyPI distribution
- maintaining backward compatibility for example APIs across versions
- hosting documentation that contradicts or supersedes the core docs

---

## Coupling to core releases

- the companion repo pins `lifecore_ros2 >= <current core release>` in its
  `pyproject.toml`
- breaking core API changes update the pin; the companion repo does **not** gate core
  releases
- the core repo's release process never blocks on companion-repo state
