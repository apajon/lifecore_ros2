# Roadmap

## First public release — 0.x series

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

## After first public release

- Multi-component and concrete real-world examples
- Companion examples repository
- Richer architecture diagrams and migration guide
- Extended edge-case test coverage

---

## Versioning strategy

The project uses [Conventional Commits](https://www.conventionalcommits.org/) and [python-semantic-release](https://python-semantic-release.readthedocs.io/).

**Current status:** version is in the `0.x` series. This signals that the public API is not yet considered stable. Experimental adoption is welcome; breaking changes may still occur on minor bumps.

**Rules in effect:**
- `allow_zero_version = true` — semantic-release stays in `0.x` and does not force a `1.0.0` bump automatically
- `major_on_zero = false` — breaking changes (BREAKING CHANGE commits) increment the minor version while in `0.x`, not the major
- `tag_format = "v{version}"` — tags are prefixed with `v`

**Promotion to `1.0.0`:** will happen only when the public API (`ComposedLifecycleNode`, `LifecycleComponent`, `TopicComponent`, `PublisherComponent`, `SubscriberComponent`, `when_active`) is considered stable enough to defend. This requires a deliberate decision and a `BREAKING CHANGE` or manual bump — it will not happen automatically.
