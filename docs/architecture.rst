Architecture
============

Overview
--------

lifecore_ros2 provides a structured way to build ROS 2 lifecycle nodes using composable components.

The current architecture is centered on two layers:

- a lifecycle-aware core in src/lifecore_ros2/core
- reusable topic-oriented components in src/lifecore_ros2/components

Lifecycle Design
----------------

The repository follows native ROS 2 lifecycle semantics.
ComposedLifecycleNode registers each component as a managed entity and relies on the underlying lifecycle node behavior to propagate transitions.

LifecycleComponent remains intentionally small:

- it is a managed entity
- it knows its parent node
- it exposes explicit lifecycle hooks
- it avoids introducing a parallel hidden state machine

Topic Components
----------------

Topic-oriented components should follow these rules:

- create ROS publishers and subscriptions during configure
- gate publication or message handling with activation state
- release ROS resources during cleanup

This keeps runtime behavior explicit and consistent with ROS 2 lifecycle expectations.

Lifecycle Invariants
--------------------

The following invariants are binding for all ``LifecycleComponent`` subclasses.

**configure**
  Allocate ROS resources: create publishers, subscriptions, timers.
  Do not enable runtime behavior. Do not set ``_is_active``.

**activate**
  Enable runtime behavior. Start publishing, accept message callbacks.
  Must call ``super()._on_activate(state)`` to set ``_is_active = True``.
  Methods decorated with ``@when_active`` will not execute until this flag is set.
  Do not allocate new ROS resources here.

**deactivate**
  Disable runtime behavior. Stop publishing, ignore incoming messages.
  Must call ``super()._on_deactivate(state)`` to clear ``_is_active``.
  Do not release ROS resources here — that is cleanup's responsibility.

**cleanup**
  Release all ROS resources allocated during configure.
  ``_release_resources()`` is not called automatically by the base class.
  Subclasses must call it explicitly inside their ``_on_cleanup`` override.

**shutdown / error**
  ``_release_resources()`` is called automatically. No override needed for most subclasses.

**No parallel lifecycle**
  No component may introduce an internal state machine that diverges from or shadows
  the node lifecycle. ``_is_active`` is the only lifecycle-adjacent flag. It is
  managed exclusively through ``_on_activate`` and ``_on_deactivate`` super() calls.

**Activation gating**
  ``PublisherComponent.publish()`` raises ``RuntimeError`` when inactive.
  ``SubscriberComponent`` silently drops incoming messages when inactive.
  Both behaviors are intentional and consistent with explicit activation semantics.
