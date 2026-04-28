# CHANGELOG

## First public release — v0.4.0

`lifecore_ros2` v0.4.0 is the first public release of the library. It establishes a small,
predictable surface for composing lifecycle-aware ROS 2 nodes without layering a hidden state
machine on top of native ROS 2 lifecycle semantics.

This section is the project's permanent first-release statement. Subsequent versioned entries
are appended below the `version list` marker by `python-semantic-release` and are not edited
by hand. The live scope boundary is tracked in [ROADMAP.md](ROADMAP.md); this section is a
snapshot at the time of the first public release.

### What this release provides

**Public API** (re-exported from `lifecore_ros2`):

- `LifecycleComponentNode` — lifecycle node that owns and drives registered components as
  native ROS 2 managed entities.
- `LifecycleComponent` — base class for lifecycle-aware components (abstract by convention);
  propagates transitions through `_on_configure`, `_on_activate`, `_on_deactivate`,
  `_on_cleanup`, `_on_shutdown`, `_on_error`.
- `TopicComponent` — base class for topic-oriented components; allocates ROS pub/sub
  during configure, releases during cleanup.
- `LifecyclePublisherComponent` — generic publisher (`[MsgT]`) gated by activation state.
- `LifecycleSubscriberComponent` — generic subscriber (`[MsgT]`) whose `on_message` callback
  is gated by activation state.
- `when_active` — decorator that guards component methods on activation state.
- `LifecoreError` and the typed boundary-violation subclasses `RegistrationClosedError`,
  `DuplicateComponentError`, `ComponentNotAttachedError`, `ComponentNotConfiguredError`.

**Examples**: `examples/minimal_node.py`, `examples/minimal_publisher.py`,
`examples/minimal_subscriber.py`, `examples/telemetry_publisher.py`.

**Documentation**: getting-started guide, architecture overview, recommended patterns and
anti-patterns, migration notes from raw `rclpy`, and a Sphinx-buildable API reference under
[docs/](docs/).

**Quality baseline**: Ruff formatting and linting, Pyright in strict mode for the core
package, and a pytest suite covering nominal transitions, edge transitions, activation
gating, failure propagation, and resource handling.

### What this release does not provide yet

- Companion examples repository (`lifecore_ros2_examples`).
- Visual demo asset (terminal recording or GIF).
- Extended FAQ section.
- Advanced patterns beyond the recommended/anti-pattern pairs already documented.

### Supported baseline

- Python 3.12 or newer.
- ROS 2 Jazzy.
- `rclpy` is required at runtime and is expected to come from the system ROS installation;
  it is intentionally not declared as a PyPI dependency.

### Known limitations

- `composed_pipeline.py` demonstrates multi-component composition inside a single node;
  multi-node or domain-specific examples live in the planned companion repository.
- The `MsgT` type parameter on topic components is unbounded by design — no stable ROS 2
  message base class is exported by `rosidl` to constrain it without coupling.
- No companion examples repository, visual asset, or FAQ ships with this release.
- Lifecycle observability beyond standard `rclpy` logging (e.g. `/diagnostics` integration)
  is out of scope for the core library.

<!-- version list -->

## Unreleased

### Documentation

- **iface-type-inference**: Mark issue [#1](https://github.com/apajon/lifecore_ros2/issues/1)
  as shipped in the API friction audit, document the generic-only topic-component
  form in `docs/patterns.rst`, and close `TODO_adoption_hardening.md §2`
  for PR [#4](https://github.com/apajon/lifecore_ros2/pull/4).

## v0.4.0 (2026-04-22)

### Bug Fixes

- **docs**: Correct stale automodule paths in api.rst
  ([`a2d9e51`](https://github.com/apajon/lifecore_ros2/commit/a2d9e5199cbdcb9dcce3499da1e18375d0a5e244))

- **typing**: Resolve 82 pyright errors blocking CI
  ([`0d49a82`](https://github.com/apajon/lifecore_ros2/commit/0d49a827e4858ba7719952e80341ab90dea25168))

- **typing**: Suppress remaining 8 pyright errors on mock publisher attributes
  ([`4ebb1a3`](https://github.com/apajon/lifecore_ros2/commit/4ebb1a36ba37ed2dacdbe1bcbda29245ef6b2211))

### Chores

- Mark release workflow rehearsal as done in TODO
  ([`5d0f6dd`](https://github.com/apajon/lifecore_ros2/commit/5d0f6dd3e8edf11152b1b6c7b0e19ab676f0f4de))

- Mark TODO_2 sections 5.1 and 5.2 as done with decision records
  ([`4bb431d`](https://github.com/apajon/lifecore_ros2/commit/4bb431d772a1e91b6909359518ffd4734684fe14))

- Mark §7.3 visual asset complete in TODO_2.md
  ([`13e86c6`](https://github.com/apajon/lifecore_ros2/commit/13e86c6348f2b17ac2144b9671964d57cdd961e3))

- **copilot**: Add MemPalace and architecture guard agents
  ([`fe1c3cd`](https://github.com/apajon/lifecore_ros2/commit/fe1c3cde82a7699f784cad87418c2d54e49a183f))

- **github**: Add structured issue templates
  ([`96fb65c`](https://github.com/apajon/lifecore_ros2/commit/96fb65cf5f37a51b5ffb1d7a7a81b3fd94a0f74f))

- **gitignore**: Ignore local ros2 jazzy interface dumps
  ([`9884539`](https://github.com/apajon/lifecore_ros2/commit/9884539273db75909ad9a4abf29cfe6f6e2a7a7c))

- **packaging**: Drop unused deps, PEP 639 license, add classifiers and URLs
  ([`a6280fd`](https://github.com/apajon/lifecore_ros2/commit/a6280fd9b530ad370d7afd350cafca1781de4ad3))

- **release**: Record 3.3 decision in TODO_2.md
  ([`397c3e3`](https://github.com/apajon/lifecore_ros2/commit/397c3e327a9ca271dff6a6a3b2ca1d7eaba3354e))

- **todo**: Align release flow notes with v0.3.0 shipped and v0.4.0 upcoming
  ([`7a0b3fa`](https://github.com/apajon/lifecore_ros2/commit/7a0b3fa212f46f17d5e0479ba0a726b344501cee))

- **todo**: Fix semantic-release dry-run command in §6.7
