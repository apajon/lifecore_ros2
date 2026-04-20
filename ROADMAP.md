# Roadmap

## First public release — 0.x series

### Included

**Core API**
- `LifecycleComponentNode` — lifecycle node that owns and drives registered `LifecycleComponent` instances as native ROS 2 managed entities
- `LifecycleComponent` — abstract base class for lifecycle-aware components, propagates transitions through `_on_configure`, `_on_activate`, `_on_deactivate`, `_on_cleanup`, `_on_shutdown`
- `TopicComponent` — abstract base class for topic-oriented components; allocates ROS pub/sub during configure, releases during cleanup
- `LifecyclePublisherComponent` — publishes messages gated by activation state
- `LifecycleSubscriberComponent` — processes incoming messages gated by activation state
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

## Companion examples repository

**Name**: `lifecore_ros2_examples` — owner `apajon`, Apache-2.0, tracks Python 3.12+ /
ROS 2 Jazzy, follows core release cadence without coupling its version number.

**Why a separate repo**: keeps the core library abstract and dependency-light. Applied,
domain-flavored, or multi-node examples have a clearly-signposted home that does not
dilute the core API surface.

**Scope boundary** (contributor exclusion test): an example belongs in the companion
repo if it depends on third-party ROS packages beyond `rclpy` and `std_msgs`, uses
domain-specific message types, spans more than one ROS node, or teaches an applied
pattern rather than a single core abstraction. Otherwise it belongs in `examples/`
in this repo.

**Initial categories**:
- *Sensor-pipeline composition* — multi-publisher / fan-in topologies
- *Lifecycle-aware diagnostics* — `/diagnostics` integration and inter-component health
- *Multi-node orchestration patterns* — supervisor and launch-coordinated lifecycle nodes

**First concrete example**: a sensor-fusion pipeline (two heterogeneous simulated sensors,
one fusion component owning two subscriptions and one publisher, one logging subscriber).
Teaches activation gating across a fan-in topology, configure-time sensor-handle
acquisition, the warm-up window with inbound-drop semantics, and state reset on
deactivate.

**Rejected name alternatives**: `lifecore_ros2_demos` (reads as throwaway),
`lifecore_examples` (drops the ROS qualifier), `lifecore_ros2_recipes` (constrains
structure prematurely).

Full plan: see `ROADMAP_lifecore_ros2_examples.md` and
`TODO_lifecore_ros2_examples.md` (planning artifacts in this repo until the companion
repository is created, then moved into it).

---

## Public API and extension model

### Public API — exported symbols

The following symbols are exported from `lifecore_ros2` and form the public API:

| Symbol | Kind | Role |
|---|---|---|
| `LifecycleComponentNode` | class | Owns and drives registered LifecycleComponent instances |
| `LifecycleComponent` | abstract class | Base for all lifecycle-aware components |
| `TopicComponent` | abstract class | Base for topic-oriented components |
| `LifecyclePublisherComponent` | concrete class | Lifecycle-gated ROS publisher |
| `LifecycleSubscriberComponent` | abstract class | Lifecycle-gated ROS subscriber |
| `when_active` | decorator | Guards a method to the active state |
| `LifecoreError` | exception | Base class for all framework boundary violations |
| `RegistrationClosedError` | exception | Raised by `add_component` after first lifecycle transition |
| `DuplicateComponentError` | exception | Raised by `add_component` when a name is already registered |
| `ComponentNotAttachedError` | exception | Raised when `.node` is accessed on a detached component |
| `ComponentNotConfiguredError` | exception | Raised by `publish()` before `_on_configure` has run |

### Naming decision record (3.1)

- `ComposedLifecycleNode` renamed to `LifecycleComponentNode` to name the class after what it owns and drives.
- `PublisherComponent` renamed to `LifecyclePublisherComponent` for explicit lifecycle intent at call sites.
- `SubscriberComponent` renamed to `LifecycleSubscriberComponent` for naming consistency with publisher.
- `LifecycleComponent` and `TopicComponent` kept unchanged.

### Intended subclassing hooks

These `_on_*` methods are the intended extension points. They are `abstractmethod` where enforcement is required; otherwise they have a safe default:

| Hook | Where | Abstract | Notes |
|---|---|---|---|
| `_on_configure(state)` | `LifecycleComponent` and subclasses | no (default: SUCCESS) | Allocate ROS resources here |
| `_on_activate(state)` | `LifecycleComponent` and subclasses | no (default: SUCCESS) | Enable runtime behavior |
| `_on_deactivate(state)` | `LifecycleComponent` and subclasses | no (default: SUCCESS) | Disable runtime behavior |
| `_on_cleanup(state)` | `LifecycleComponent` and subclasses | no (default: SUCCESS) | Release resources; override to call `_release_resources` in subclasses |
| `_on_shutdown(state)` | `LifecycleComponent` | no (default: SUCCESS) | Calls `_release_resources`; override if needed |
| `_on_error(state)` | `LifecycleComponent` | no (default: SUCCESS) | Calls `_release_resources`; override if needed |
| `_release_resources()` | `LifecycleComponent` and subclasses | no (default: no-op) | Release all allocated ROS resources; override in each subclass |
| `on_message(msg)` | `LifecycleSubscriberComponent` | yes | Handle incoming messages while active |

**Do not override** the native `on_configure`, `on_activate`, `on_deactivate`, `on_cleanup`, `on_shutdown`, `on_error` methods directly. These are owned by ROS 2 `ManagedEntity` and delegate to the `_on_*` hooks after applying the lifecycle guard.

### Internal helpers — not part of the public API

The following are internal and subject to change without notice:

- `_LoggerLike` — internal protocol for logger duck-typing
- `_LifecycleHook` — internal type alias
- `_SENTINEL` — internal sentinel value for `when_active`
- `_attach()` / `_detach()` on `LifecycleComponent` — registration lifecycle managed by `LifecycleComponentNode.add_component()`; do not call directly
- `_guarded_call` — wraps `_on_*` hooks with error handling and return-value normalisation
- `_safe_release_resources` — exception-safe wrapper around `_release_resources`
- `_close_registration` on `LifecycleComponentNode` — closes `add_component` gate on first transition
- `_on_message_wrapper` on `LifecycleSubscriberComponent` — framework dispatch method; sealed with `@final`

### Stability statement

All public API symbols are in the `0.x` series and carry an **experimental** stability level:
- The class hierarchy and hook names are considered stable in intent and will not change without a minor version bump and a changelog entry.
- The `_on_*` hook signatures (`state: LifecycleState`) are stable and will not change before `1.0.0` without a `BREAKING CHANGE` commit.
- Internal helpers (`_`-prefixed or not exported) may change in any release.

---

## Versioning strategy

The project uses [Conventional Commits](https://www.conventionalcommits.org/) and [python-semantic-release](https://python-semantic-release.readthedocs.io/).

**Current status:** version is in the `0.x` series. This signals that the public API is not yet considered stable. Experimental adoption is welcome; breaking changes may still occur on minor bumps.

**Rules in effect:**
- `allow_zero_version = true` — semantic-release stays in `0.x` and does not force a `1.0.0` bump automatically
- `major_on_zero = false` — breaking changes (BREAKING CHANGE commits) increment the minor version while in `0.x`, not the major
- `tag_format = "v{version}"` — tags are prefixed with `v`

**Promotion to `1.0.0`:** will happen only when the public API (`LifecycleComponentNode`, `LifecycleComponent`, `TopicComponent`, `LifecyclePublisherComponent`, `LifecycleSubscriberComponent`, `when_active`) is considered stable enough to defend. This requires a deliberate decision and a `BREAKING CHANGE` or manual bump — it will not happen automatically.
