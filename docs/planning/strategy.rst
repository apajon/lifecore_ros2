Strategic cap
=============

This page records the product direction behind the planning backlog. It is a
discussion baseline, not an implementation contract.

---

Positioning
-----------

``lifecore_ros2`` is a Python library for structuring ROS 2 lifecycle nodes
with a component-oriented approach.

Its level is **inside the node**:

::

   [ Launch / better_launch ]
           v
   [ Nav2 / cascade ]
           v
   [ lifecore_ros2 ]
           v
   [ rclpy lifecycle ]

``lifecore_ros2`` is the internal discipline layer that raw ROS 2 lifecycle
primitives do not provide. It is not a system orchestrator, not a launcher, and
not a replacement for native ROS 2 lifecycle semantics.

The short message to test in public material is:

::

   Build predictable ROS 2 nodes.

The longer positioning sentence is:

::

   lifecore_ros2 helps advanced ROS 2 developers build predictable lifecycle
   nodes by structuring the inside of a node around lifecycle-aware components.

---

Problem statement
-----------------

ROS 2 provides lifecycle primitives, but it does not prescribe an internal node
structure. In real projects this often leaves lifecycle behavior scattered
across callbacks, resources, flags, and shutdown paths.

The recurring failure modes are:

- callbacks active too early
- lifecycle ignored or used inconsistently
- duplicated activation flags and cleanup logic
- shutdown behavior that depends on incidental code order
- non-deterministic component interactions
- debugging that requires reading the full node class

The implicit need is high, but the market maturity is low. The project is ahead
of an explicit demand, which means concrete examples matter more than abstract
claims.

---

Strategic value
---------------

The value proposition is:

::

   structure + determinism + internal robustness

The primary differentiator is internal lifecycle orchestration of components
inside one node. That should remain separate from multi-node orchestration,
process restart, launch files, and lifecycle managers.

What ``lifecore_ros2`` should make obvious:

- components are lifecycle-aware managed entities
- callback behavior is activation-gated
- resource ownership follows configure / activate / deactivate / cleanup
- component ordering can become explicit and deterministic
- health and diagnostics can be read before any recovery behavior is attempted

---

Strategic boundaries
--------------------

Do not expand into these areas until a concrete user need forces the discussion:

- multi-node orchestration
- automatic process restart
- dynamic graph orchestration
- task scheduling
- direct AI or MCP integration inside the runtime library
- plugin loading or config-driven applications before the core API proves it

These may become tooling or companion-repository concerns later. They should not
move into the core library prematurely.

After Sprint 13, the same boundary applies to new attractive ideas: EventBus,
ECS, StateStore, Codegen, DSLs, diagnostics, and advanced tooling may become
separate modules, companion work, or research tracks. They must not
automatically become part of ``lifecore_ros2``.

The future distributed typed state model belongs to a separate ``lifecore_state``
track. Lifecycle drives systems; systems modify state; state is the source of
truth; events describe what happened; ROS 2 exposes what must leave the process.

---

Adoption sequence
-----------------

The near-term adoption sequence is:

1. build one strong comparison example
2. update README positioning around the comparison
3. publish only after the example makes the value obvious

The comparison format is:

::

   1. plain ROS 2 node
   2. classic ROS 2 lifecycle node
   3. lifecore_ros2 component-oriented lifecycle node

The preferred use case is a sensor watchdog node with a subscriber, publisher,
and timer. It should show that plain ROS 2 is simple but fragile, classic
lifecycle code is controlled but verbose, and ``lifecore_ros2`` is structured
without hiding lifecycle semantics.

---

Roadmap thesis after Sprint 14
------------------------------

Sprint 14 completed the planning-alignment pass after the current core planning
window. Future priority is
location-neutral: a sprint may target core, companion, docs, architecture,
tooling, DX, external modules, or research. Priority is based on risk reduction,
adoption leverage, architectural clarification, and strategic sequencing, not on
whether the sprint changes the ``lifecore_ros2`` package.

Recommended mapping:

1. Sprint 15: companion adoption examples.
2. Sprint 16: test ergonomics and diagnostics polish.
3. Sprint 17: ``lifecore_state`` architecture RFC.
4. Sprint 18: ``lifecore_state_msgs`` ABI prototype, conditional on Sprint 17.
5. Sprint 19: minimal factory and registry, conditional on repeated real pain.
6. Sprint 20+: tooling and generated nodes, conditional on stable conventions.

The historical factory and tooling cards that once held Sprint 14 and Sprint 15
numbering are no longer default next steps. Factory and tooling should follow
proven adoption, stable conventions, and clear state architecture boundaries.

The project wins when a ROS 2 developer sees the example and thinks: "this would
have prevented lifecycle pain in my own node." It loses if the reaction is only:
"clean, but unnecessary."
