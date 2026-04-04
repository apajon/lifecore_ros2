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
