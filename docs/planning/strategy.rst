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

Roadmap thesis
--------------

Sprint numbers encode priority order. The strategic comparison example becomes
Sprint 4 because it is the next proof point before additional library surface.
Some new cards intentionally move ahead of older advanced surfaces when they are
closer to the product differentiator.

Current sprint mapping:

1. Sprint 4: lifecycle comparison example
2. Sprint 5: internal component cascade, the main differentiator
3. Sprint 6-9: runtime consistency and hardening: gating, cleanup, concurrency,
   observability
4. Sprint 10-11: health/status, then lightweight watchdog
5. Sprint 12-14: broader advanced surfaces: policies, parameters, factory
6. Sprint 15+: generated-node tooling; MCP or deeper automation only after the
   runtime and examples prove useful

The project wins when a ROS 2 developer sees the example and thinks: "this would
have prevented lifecycle pain in my own node." It loses if the reaction is only:
"clean, but unnecessary."
