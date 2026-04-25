# lifecore_ros2

[![CI](https://github.com/apajon/lifecore_ros2/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/apajon/lifecore_ros2/actions/workflows/ci.yml)
[![Docs](https://github.com/apajon/lifecore_ros2/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/apajon/lifecore_ros2/actions/workflows/docs.yml)
[![Release](https://github.com/apajon/lifecore_ros2/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/apajon/lifecore_ros2/actions/workflows/release.yml)
[![License: Apache 2.0](https://img.shields.io/github/license/apajon/lifecore_ros2)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-github--pages-blue)](https://apajon.github.io/lifecore_ros2/)

<!-- Canonical positioning sentence — keep in sync with pyproject.toml project.description. See CONTRIBUTING.md. -->
lifecore_ros2 is a minimal lifecycle composition library for ROS 2 Jazzy — no hidden state machine.

![Composed pipeline lifecycle walk-through: configure creates topics, activate streams data, deactivate stops data flow while topics remain (deactivate ≠ cleanup), cleanup releases resources.](docs/_static/composed_pipeline_demo.gif)

*The `examples/composed_pipeline.py` walk-through highlights the key distinction the library makes explicit: **deactivate ≠ cleanup** — `/pipeline/*` topics persist across deactivate and only disappear on cleanup.*

## Why lifecore_ros2 exists

**Audience.** This library is for teams building modular ROS 2 nodes that need reusable lifecycle-aware components, especially in larger robotics stacks, embedded systems, or runtime-orchestrated applications.

**Problem framing.** ROS 2 provides a powerful managed-node lifecycle (`configure → active → deactivate → cleanup`). In practice, using it for anything beyond a trivial node leads to recurring problems:

- lifecycle logic gets scattered across monolithic node classes with no clear ownership
- ROS resource setup and teardown (publishers, subscriptions, timers) are easy to make inconsistent — resources allocated in the wrong place or released too late
- runtime gating ("only process messages when active") is hand-rolled differently each time, with no shared, tested pattern
- reusable lifecycle-aware building blocks are awkward in raw `rclpy` because the lifecycle contract is on the node, not on reusable sub-units

lifecore_ros2 solves these four problems with a small, explicit composition layer. It does not replace or extend the ROS 2 lifecycle state machine — it makes the lifecycle contract expressible at the component level.

**Non-goals.** It is not a full application framework, not a plugin system, and not a replacement for native ROS 2 lifecycle semantics.

## Architecture at a glance

```mermaid
flowchart LR
    Lifecycle[ROS 2 Lifecycle]
    Node[LifecycleComponentNode]
    Components[LifecycleComponent instances]
    Lifecycle <--> Node
    Node <--> Components
    Lifecycle -. drives .-> Components
```

## What the library provides

A small set of lifecycle-aware building blocks:

| Symbol | Role |
|---|---|
| `LifecycleComponentNode` | Lifecycle node that owns and drives registered `LifecycleComponent` instances |
| `LifecycleComponent` | Base class for a lifecycle-aware managed entity (abstract by convention — override `_on_*` hooks) |
| `TopicComponent` | Base class for topic-oriented components (pub/sub) |
| `LifecyclePublisherComponent` | Lifecycle-gated ROS publisher |
| `LifecycleSubscriberComponent` | Lifecycle-gated ROS subscriber |
| `when_active` | Decorator that guards any method to the active state |
| `LifecoreError` and subclasses | Typed exceptions for boundary violations |

## Design rules and non-goals

The framework stays lifecycle-native, keeps ownership in `LifecycleComponentNode`, and treats component hooks as explicit extension points rather than hidden orchestration.

See [docs/architecture.rst](docs/architecture.rst) for lifecycle design rules, [docs/patterns.rst](docs/patterns.rst) for usage patterns, and [ROADMAP.md](ROADMAP.md) for non-goals and deferred scope.
See [ROADMAP_lifecore_ros2_examples.md](ROADMAP_lifecore_ros2_examples.md) for the companion examples repository plan.
See [CHANGELOG.md](CHANGELOG.md) for shipped changes or the [GitHub Releases](https://github.com/apajon/lifecore_ros2/releases) page for tagged releases.

## Prerequisites

- Python 3.12 or newer
- ROS 2 Jazzy installed on the system
- `uv` available in the workspace

`rclpy` is expected to come from the system ROS installation. It is intentionally not declared as a normal PyPI dependency.

## Quickstart

Clone the repository and enter a ROS 2 Jazzy shell:

```bash
git clone https://github.com/apajon/lifecore_ros2.git
cd lifecore_ros2
source /opt/ros/jazzy/setup.bash
```

Install dependencies and run the canonical shortest-path example:

```bash
uv sync --extra dev
uv run python examples/minimal_subscriber.py
```

From another terminal in the same ROS environment, drive the lifecycle and publish one message:

```bash
ros2 lifecycle set /demo_node configure
ros2 lifecycle set /demo_node activate
ros2 topic pub --once /chatter std_msgs/msg/String "{data: 'hello'}"
```

For the full validation command set, see [docs/getting_started.rst](docs/getting_started.rst). For a lower-level minimal component example, see [examples/minimal_node.py](examples/minimal_node.py).

## Shortest-path example — subscriber

[examples/minimal_subscriber.py](examples/minimal_subscriber.py) is the canonical shortest-path example for activation-gated message delivery.

See [examples/minimal_subscriber.py](examples/minimal_subscriber.py) for the complete runnable file, [docs/api_friction_audit.rst](docs/api_friction_audit.rst) for the regression baseline, and [docs/examples.rst](docs/examples.rst) for the walkthrough.

> Component + node definition: **24 lines** (regression baseline — see
> [`docs/api_friction_audit.rst`](docs/api_friction_audit.rst)).

## Publisher and subscriber examples

Run the publisher and observe activation gating:

```bash
uv run python examples/minimal_publisher.py
# in another terminal:
ros2 lifecycle set /publisher_demo_node configure
ros2 lifecycle set /publisher_demo_node activate
ros2 topic echo /chatter
```

Messages appear only after `activate`. Deactivation stops them.

For the subscriber path, use the quickstart above or the full example walkthrough in [docs/examples.rst](docs/examples.rst).

## Public API overview

All exported symbols and their stability levels are documented in [ROADMAP.md](ROADMAP.md#public-api-and-extension-model).

The extension model and API buckets are defined in [docs/architecture.rst](docs/architecture.rst) and [docs/api.rst](docs/api.rst).

## Current limitations

- the public API is in the `0.x` series — experimental stability level; minor bumps may include breaking changes
- companion examples repository `lifecore_ros2_examples` is *planned — not yet published*; see `ROADMAP.md` for scope and the first applied example (sensor-fusion pipeline)

## License

This project is licensed under the Apache-2.0 License — see [LICENSE](LICENSE).

## Documentation

Documentation: https://apajon.github.io/lifecore_ros2/

Full documentation lives under `docs/` and is built with Sphinx:

```bash
uv sync --extra dev --group docs
uv run --group docs python -m sphinx -b html docs docs/_build/html
```

Key pages:
- `docs/getting_started.rst` — setup and validation commands
- `docs/architecture.rst` — lifecycle design rules, error policy, member conventions
- `docs/patterns.rst` — recommended patterns and anti-patterns
- `docs/migration_from_rclpy.rst` — before/after comparison with raw rclpy
- `docs/api.rst` — generated API reference
- `docs/examples.rst` — example walkthroughs

## Versioning

Versioning uses Conventional Commits and python-semantic-release. Preview the next version:

```bash
uv run --group release semantic-release version --print
```

Release (version commit + tag, skip hosted release if no token):

```bash
uv run --group release semantic-release version --no-vcs-release
git push origin main --follow-tags
```

See [ROADMAP.md](ROADMAP.md#versioning-strategy) for promotion-to-1.0.0 criteria.
