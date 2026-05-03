FAQ
===

Short answers to the questions that come up most often when evaluating
``lifecore_ros2``.

Why not use the ROS 2 lifecycle directly?
-----------------------------------------

You can, and for a trivial node that is the right choice. ``lifecore_ros2`` exists
because, once a lifecycle node grows beyond a few responsibilities, the native
lifecycle contract lives only on the node. There is no first-class place to express
"this sub-unit is lifecycle-aware" without hand-rolling it every time.

The library does not replace or extend the ROS 2 lifecycle state machine. It makes the
same contract expressible at the *component* level, so that ROS resource setup and
teardown, and the "only act while active" rule, are applied consistently across
reusable building blocks.

How is this different from writing a custom state machine?
----------------------------------------------------------

It is not a state machine. ``LifecycleComponentNode`` is a ROS 2 lifecycle node and
``LifecycleComponent`` instances are driven by its transitions. Transitions,
transition names, and return codes stay those of ``rclpy.lifecycle``. The framework
adds composition, activation gating, and typed boundary errors — nothing else. There
is no parallel state model, no hidden transitions, and no orchestration layer.

Why components, and not just bigger nodes?
------------------------------------------

A lifecycle node that directly owns publishers, subscriptions, timers, and domain
logic tends to blur two concerns: *when* a resource exists and *what* it does.
Components separate those concerns. ``TopicComponent`` owns the ROS resource across
configure/cleanup. ``LifecyclePublisherComponent``, ``LifecycleSubscriberComponent``,
and ``LifecycleTimerComponent`` additionally gate runtime behavior on activation.
``ServiceComponent`` mirrors that pattern for ROS services, with
``LifecycleServiceServerComponent`` and ``LifecycleServiceClientComponent`` gating
request handling and outbound calls on activation. Application code composes these
components inside a ``LifecycleComponentNode`` and keeps each ``_on_*`` hook focused.

What belongs in this repository and what belongs in an application repository?
------------------------------------------------------------------------------

This repository ships reusable, lifecycle-native primitives only:
``LifecycleComponentNode``, ``LifecycleComponent``, ``TopicComponent``, the
publisher/subscriber/timer components, ``ServiceComponent`` and the service
server/client components, ``when_active``, and typed errors. Domain-specific
components, multi-node topologies, ``/diagnostics`` integrations, and applied
examples belong in application repositories — or in the companion
``lifecore_ros2_examples`` repository for teaching examples that depend on more than
``rclpy`` and ``std_msgs``.

See ``ROADMAP.md`` at the repository root for the full "out of scope" list.

What is the current API stability level?
----------------------------------------

The public API is in the ``0.x`` series — experimental stability. Package metadata
uses ``Development Status :: 3 - Alpha`` to reflect API stability, not lack of
usability. Minor version bumps may include breaking changes. The surface is
deliberately small to keep that risk contained. Promotion to ``1.0.0`` will happen
only once the API is judged stable based on real usage feedback.
