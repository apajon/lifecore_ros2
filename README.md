# lifecore_ros2

A composable lifecycle framework for ROS 2.

## What It Is

lifecore_ros2 provides a small set of lifecycle-aware building blocks for composing ROS 2 Jazzy nodes from reusable components.

The current public surface exposes:
- ComposedLifecycleNode
- LifecycleComponent
- TopicComponent
- PublisherComponent
- SubscriberComponent

## Design Principles

The repository is built around a few explicit rules:
- native ROS 2 lifecycle semantics stay in control
- ComposedLifecycleNode orchestrates components and registers them as managed entities
- components keep their _on_* hooks focused and deterministic
- topic-oriented components create ROS resources during configure, gate behavior with activation, and release resources during cleanup
- no parallel hidden state machine is introduced on top of ROS 2 lifecycle

## Prerequisites

- Python 3.12 or newer
- ROS 2 Jazzy installed on the system
- uv available in the workspace

The project expects rclpy to come from the system ROS installation. It is intentionally not declared as a normal PyPI dependency.

## Quickstart

Prepare a ROS 2 Jazzy shell first:

```bash
source /opt/ros/jazzy/setup.bash
```

Install development dependencies:

```bash
uv sync --extra dev
```

Install the documentation toolchain as well:

```bash
uv sync --extra dev --group docs
```

Common validation commands:

```bash
uv run --extra dev python -m ruff check .
uv run --extra dev python -m ruff format --check .
uv run --extra dev pyright
uv run --extra dev pytest
```

Build the documentation:

```bash
uv run --group docs python -m sphinx -b html docs docs/_build/html
```

## Examples

The repository currently includes:
- examples/minimal_node.py for a minimal composed lifecycle node with a simple component
- examples/minimal_subscriber.py for a lifecycle-aware subscriber component example
- examples/minimal_publisher.py for a lifecycle-aware publisher component example

## Minimal Example

Run the minimal lifecycle node:

```bash
source /opt/ros/jazzy/setup.bash
uv run --extra dev python examples/minimal_node.py
```

In another terminal, inspect and trigger lifecycle transitions:

```bash
source /opt/ros/jazzy/setup.bash
ros2 lifecycle nodes
ros2 lifecycle set /minimal_lifecore_node configure
ros2 lifecycle set /minimal_lifecore_node activate
ros2 lifecycle set /minimal_lifecore_node deactivate
ros2 lifecycle set /minimal_lifecore_node cleanup
```

What to expect:
- the node appears in `ros2 lifecycle nodes`
- configure allocates component resources
- activate enables runtime behavior
- deactivate gates runtime behavior
- cleanup releases component resources

### Publisher Walkthrough

Run the publisher example:

```bash
source /opt/ros/jazzy/setup.bash
uv run --extra dev python examples/minimal_publisher.py
```

In another terminal, activate the node and observe published messages:

```bash
source /opt/ros/jazzy/setup.bash
ros2 lifecycle set /publisher_demo_node configure
ros2 lifecycle set /publisher_demo_node activate
ros2 topic echo /chatter
```

Then deactivate to stop the flow:

```bash
ros2 lifecycle set /publisher_demo_node deactivate
```

What to expect:
- messages are published only while the node is active
- deactivation stops publication immediately
- publication outside activation is guarded by `PublisherComponent.publish()`

## Documentation

The Sphinx documentation lives under docs/ and currently includes:
- docs/getting_started.rst for setup and validation commands
- docs/architecture.rst for lifecycle and component design rules
- docs/api.rst for generated API reference
- docs/examples.rst for example-oriented entry points

## Current Status

The project is in early development, with a working V0 baseline:
- core lifecycle primitives and topic-oriented components are implemented
- minimal node, subscriber, and publisher examples are available
- a focused pytest suite validates core behavior (19 passing tests)

## Roadmap

Near-term focus:
- keep improving runnable examples and ergonomics
- extend docs with richer usage patterns
- prepare release/versioning validation tasks

See TODO.md for the full roadmap.
