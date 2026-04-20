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
LifecycleComponentNode registers each component as a managed entity and relies on the underlying lifecycle node behavior to propagate transitions.

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
  Do not call ``super()._on_activate(state)`` — the framework sets ``_is_active = True``
  automatically after the hook returns SUCCESS.
  Do not allocate new ROS resources here.

**deactivate**
  Disable runtime behavior. Stop publishing, ignore incoming messages.
  ``_is_active`` is cleared to ``False`` only after ``_on_deactivate`` returns SUCCESS.
  A FAILURE or ERROR result leaves ``_is_active`` unchanged — the component stays active.
  Do not release ROS resources here — that is cleanup's responsibility.

**cleanup**
  Release all ROS resources allocated during configure.
  ``_release_resources()`` is called automatically by the framework after ``_on_cleanup`` returns.
  No explicit call is needed in the override.

**shutdown / error**
  ``_release_resources()`` is called automatically. No override needed for most subclasses.

**No parallel lifecycle**
  No component may introduce an internal state machine that diverges from or shadows
  the node lifecycle. ``_is_active`` is the only lifecycle-adjacent flag. It is
  managed exclusively through ``_on_activate`` and ``_on_deactivate`` super() calls.

**Activation gating**
  ``LifecyclePublisherComponent.publish()`` raises ``RuntimeError`` when inactive.
  ``LifecycleSubscriberComponent`` silently drops incoming messages when inactive.
  Both behaviors are intentional and consistent with explicit activation semantics.

Member Convention
-----------------

Every class in ``lifecore_ros2`` assigns each method and attribute to exactly one
of four buckets. This is the authoritative guide for contributors and subclassers.

**Bucket 1 — Public API**
  Stable surface for direct use by application code. No leading underscore.
  Included in ``__all__`` at module level. Examples: ``name``, ``is_active``,
  ``add_component``, ``publish``, ``on_message``.

**Bucket 2 — Protected extension points**
  Override in subclasses; never call directly from application code. Single leading
  underscore. Docstring starts with ``Extension point.`` Examples: ``_on_configure``,
  ``_on_activate``, ``_on_deactivate``, ``_on_cleanup``, ``_on_shutdown``, ``_on_error``,
  ``_release_resources``. Rendered in API docs.

**Bucket 3 — Framework-controlled entry points**
  Implement the ``rclpy`` ``ManagedEntity`` / ``LifecycleNode`` protocol. Decorated with
  ``@typing.final`` on ``LifecycleComponent`` so pyright catches accidental overrides.
  On ``LifecycleComponentNode``, ``on_configure`` and ``on_shutdown`` are not sealed because
  application nodes legitimately call ``super()`` inside them; those carry an explicit
  "override with super" contract in their docstring. Examples: ``LifecycleComponent.on_configure``,
  ``on_activate``, ``on_deactivate``, ``on_cleanup``, ``on_shutdown``, ``on_error``.

**Bucket 4 — Framework-internal**
  Implementation details with no user contract. Single leading underscore. Docstring starts
  with ``Framework-internal. Do not call from user code.`` Excluded from API docs.
  Examples: ``_attach``, ``_detach``, ``_guarded_call``, ``_safe_release_resources``,
  ``_resolve_logger``, ``_close_registration``, ``_on_message_wrapper``.

When adding a new method, assign it to one bucket before writing the docstring.
