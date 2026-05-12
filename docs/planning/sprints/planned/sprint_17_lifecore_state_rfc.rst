Sprint 17 - lifecore_state architecture RFC
===========================================

**Track.** State Architecture / Research.

**Branch.** ``sprint/17-lifecore-state-rfc``.

**Priority.** P2 - separate future architecture.

**Objective.** Decide the future ``lifecore_state`` architecture before coding
runtime or message packages.

Context
-------

The future model should be treated as a distributed typed state space or semantic
synchronized state model, not as a generic industrial I/O bus hidden inside
``lifecore_ros2``.

Concepts to evaluate include ``StateField``, ``StateRegistry``,
``StateDescriptor``, ``StateQuality``, ``StateSnapshot``, ``StateDelta``,
``StateProjection``, ``StateMirror``, ``StatePublisher``, ``StateSubscriber``,
and ``StateBridge``.

Questions to decide
-------------------

- Public name: ``lifecore_state`` or ``lifecore_io``.
- Package split: ``lifecore_state_msgs``, ``lifecore_state_core``, and
  ``lifecore_state_ros``.
- Separation between description, state, and command.
- Required quality, sequence, and ``description_version`` fields.
- Timestamp strategy: source timestamp per value and/or publication timestamp
  per batch.
- Identity strategy: ``id``, ``uuid``, ``key``, path-derived deterministic
  identity, future ``config_uuid`` or external id.
- Projection model: registry-scoped synchronization or state-space projection.
- Policies for unknown signals, missing signals, type mismatches, and stale data.
- Relationship with lifecycle core, EventBus ideas, lightweight ECS ideas, and
  structured fast-access memory.

Explicit limits
---------------

- No hard real-time loop.
- No full ECS framework.
- No replacement for ROS 2 topics or services.
- No state-store concepts hidden inside ``lifecore_ros2``.

Acceptance criteria
-------------------

- [ ] An RFC document exists.
- [ ] Boundaries between ``lifecore_ros2`` and ``lifecore_state`` are clear.
- [ ] Go/no-go for implementation is explicit.
- [ ] Architectural risks are listed.
- [ ] Public names are provisionally stabilized.
