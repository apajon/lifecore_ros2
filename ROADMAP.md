# Roadmap

## First public release — v0.1.0

### Included

**Core API**
- `ComposedLifecycleNode` — lifecycle node that orchestrates registered components as native ROS 2 managed entities
- `LifecycleComponent` — abstract base class for lifecycle-aware components, propagates transitions through `_on_configure`, `_on_activate`, `_on_deactivate`, `_on_cleanup`, `_on_shutdown`
- `TopicComponent` — abstract base class for topic-oriented components; allocates ROS pub/sub during configure, releases during cleanup
- `PublisherComponent` — publishes messages gated by activation state
- `SubscriberComponent` — processes incoming messages gated by activation state
- `when_active` — decorator that guards component methods to the active state

**Examples**
- `examples/minimal_node.py` — minimal composed lifecycle node
- `examples/minimal_publisher.py` — lifecycle-gated publisher
- `examples/minimal_subscriber.py` — lifecycle-gated subscriber

**Documentation**
- Getting started guide, architecture overview, API reference, examples walkthrough
- Sphinx-buildable docs under `docs/`

**Quality baseline**
- Ruff formatting and linting, Pyright static checks, pytest suite covering nominal transitions, activation gating, and resource handling

---

### Intentionally deferred

- Multi-component composed example (two or more components in a single node)
- Companion examples repository (`lifecore_ros2_examples`)
- Visual demo assets (terminal recording or GIF)
- `CONTRIBUTING.md` and GitHub issue templates
- Advanced patterns, anti-patterns, and migration docs
- FAQ section

---

### Out of scope for the core library

- Full application framework with service orchestration or task scheduling
- Hidden parallel state machine layered on top of ROS 2 lifecycle
- Domain-specific components (sensors, actuators, controllers)
- Plugin or dynamic component loading system
- Replacement of native ROS 2 lifecycle semantics

---

## After v0.1.0

- Multi-component and concrete real-world examples
- Companion examples repository
- Richer architecture diagrams and migration guide
- Extended edge-case test coverage
