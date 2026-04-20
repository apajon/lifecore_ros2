# lifecore_ros2

lifecore_ros2 is a minimal lifecycle composition library for ROS 2 Jazzy that helps build reusable lifecycle-aware nodes without adding a hidden state machine on top of ROS 2.

## Why this exists

ROS 2 provides a powerful managed-node lifecycle (`configure → active → deactivate → cleanup`). In practice, using it for anything beyond a trivial node leads to recurring problems:

- lifecycle logic gets scattered across monolithic node classes with no clear ownership
- ROS resource setup and teardown (publishers, subscriptions, timers) are easy to make inconsistent — resources allocated in the wrong place or released too late
- runtime gating ("only process messages when active") is hand-rolled differently each time, with no shared, tested pattern
- reusable lifecycle-aware building blocks are awkward in raw `rclpy` because the lifecycle contract is on the node, not on reusable sub-units

lifecore_ros2 solves these four problems with a small, explicit composition layer. It does not replace or extend the ROS 2 lifecycle state machine — it makes the lifecycle contract expressible at the component level.

## What the library provides

A small set of lifecycle-aware building blocks:

| Symbol | Role |
|---|---|
| `LifecycleComponentNode` | Lifecycle node that owns and drives registered `LifecycleComponent` instances |
| `LifecycleComponent` | Abstract base for a lifecycle-aware managed entity |
| `TopicComponent` | Abstract base for topic-oriented components (pub/sub) |
| `LifecyclePublisherComponent` | Lifecycle-gated ROS publisher |
| `LifecycleSubscriberComponent` | Lifecycle-gated ROS subscriber |
| `when_active` | Decorator that guards any method to the active state |
| `LifecoreError` and subclasses | Typed exceptions for boundary violations |

## Design principles

- native ROS 2 lifecycle semantics stay in control — no parallel state machine is introduced
- `LifecycleComponentNode` owns and drives registered `LifecycleComponent` instances as managed entities
- components keep `_on_*` hooks focused and deterministic
- topic-oriented components create ROS resources during configure, gate behavior with activation, and release resources during cleanup
- errors and misuse raise typed exceptions; inbound callbacks drop silently to protect the executor

## Non-goals

- no hidden state machine layered on top of ROS 2 lifecycle
- no full application framework with service orchestration or task scheduling
- no domain-specific components (sensors, actuators, controllers)
- no plugin or dynamic component loading
- no replacement of native ROS 2 lifecycle semantics

See [ROADMAP.md](ROADMAP.md) for the full "out of scope" list and deferred features.

## Prerequisites

- Python 3.12 or newer
- ROS 2 Jazzy installed on the system
- `uv` available in the workspace

`rclpy` is expected to come from the system ROS installation. It is intentionally not declared as a normal PyPI dependency.

## Quickstart

Prepare a ROS 2 Jazzy shell:

```bash
source /opt/ros/jazzy/setup.bash
```

Install development dependencies:

```bash
uv sync --extra dev
```

Validate the installation:

```bash
uv run --extra dev python -m ruff check .
uv run --extra dev python -m ruff format --check .
uv run --extra dev pyright
uv run --extra dev pytest
```

## Minimal example

```python
from lifecore_ros2 import LifecycleComponent, LifecycleComponentNode


class StatusComponent(LifecycleComponent):
    pass  # override _on_configure, _on_activate, etc. as needed


class StatusNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("status_node")
        self.add_component(StatusComponent("status"))
```

Run it:

```bash
source /opt/ros/jazzy/setup.bash
uv run --extra dev python examples/minimal_node.py
```

Then trigger lifecycle transitions from another terminal:

```bash
ros2 lifecycle set /minimal_lifecore_node configure
ros2 lifecycle set /minimal_lifecore_node activate
ros2 lifecycle set /minimal_lifecore_node deactivate
ros2 lifecycle set /minimal_lifecore_node cleanup
```

## Publisher and subscriber examples

Run the publisher and observe activation gating:

```bash
uv run --extra dev python examples/minimal_publisher.py
# in another terminal:
ros2 lifecycle set /publisher_demo_node configure
ros2 lifecycle set /publisher_demo_node activate
ros2 topic echo /chatter
```

Messages appear only after `activate`. Deactivation stops them.

Run the subscriber and observe that messages are dropped before activation:

```bash
uv run --extra dev python examples/minimal_subscriber.py
# configure but do not yet activate:
ros2 lifecycle set /demo_node configure
ros2 topic pub --once /chatter std_msgs/msg/String "{data: 'before activate'}"
# no Received: log appears — then activate:
ros2 lifecycle set /demo_node activate
ros2 topic pub --once /chatter std_msgs/msg/String "{data: 'after activate'}"
```

## Public API overview

All exported symbols and their stability levels are documented in [ROADMAP.md](ROADMAP.md#public-api-and-extension-model).

The extension model uses four buckets defined in the architecture docs:
- public API (direct use by application code)
- protected extension points (`_on_*` hooks — override in subclasses)
- framework-controlled entry points (`on_*` — sealed with `@final` on components)
- framework-internal (`_attach`, `_guarded_call`, etc. — not for user code)

## Current limitations

- the public API is in the `0.x` series — experimental stability level; minor bumps may include breaking changes
- no multi-component composed example yet (deferred to post-first-release)
- no companion examples repository yet

## License

This project is licensed under the Apache-2.0 License — see [LICENSE](LICENSE).

## Documentation

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
