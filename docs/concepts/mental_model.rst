Mental Model
============

Read this page before the API reference.
It describes the intended mental model of the framework.

What A Component Is
-------------------

``LifecycleComponent`` is not a ROS node.
It is a managed entity owned by a lifecycle node.

A component does not spin, does not own the executor, and does not define the ROS 2 lifecycle state machine.
Its job is narrower: hold one focused slice of behavior behind explicit lifecycle hooks.

Ownership Model
---------------

``LifecycleComponentNode`` owns components.
The node is the ROS 2 lifecycle node.
Components live inside that node and are registered there.

.. code-block:: text

    LifecycleComponentNode
      ├── LifecyclePublisherComponent
      ├── LifecycleSubscriberComponent
      ├── LifecycleTimerComponent
      ├── LifecycleServiceServerComponent
      ├── LifecycleServiceClientComponent
      └── Custom LifecycleComponent

Think in terms of one lifecycle node coordinating several small managed parts, not one large class doing everything.

Who Drives Transitions
----------------------

The node drives lifecycle transitions.
Configure, activate, deactivate, cleanup, shutdown, and error handling enter through the node.
The node then propagates the transition to each registered component.

This matters because the framework does not create a second control plane.
The lifecycle entry point stays explicit and centralized.

Resource Management Happens In Hooks
------------------------------------

Components create and destroy ROS resources through explicit hooks.

- Create publishers, subscriptions, and similar ROS resources during configure.
- Enable runtime behavior during activate.
- Disable or gate runtime behavior during deactivate.
- Release ROS resources during cleanup.

Do not treat ``__init__`` as the place where runtime ROS resources become live.
The framework is designed so resource lifetime follows lifecycle transitions.

Activation Must Stay Explicit
-----------------------------

Activation state must be explicit and predictable.
If a component is inactive, that fact must be reflected in its behavior.

The framework favors visible gating over implicit background behavior.
When code becomes active or inactive, that change should follow the lifecycle transition directly.

No Hidden State Machine
-----------------------

lifecore_ros2 avoids hidden state machines.
It uses the native ROS 2 lifecycle model and keeps component behavior aligned with it.

Users should not have to reason about a second internal status model to understand whether a component can publish, receive, or hold resources.

Prefer Small Components
-----------------------

Prefer small focused components over large monolithic nodes.

Good components usually own one responsibility:

- one publisher path
- one subscriber path
- one bounded piece of integration logic

This keeps lifecycle behavior readable, testable, and predictable.
If one class starts owning many unrelated resources and rules, the lifecycle model becomes harder to follow.

In practice, the framework works best when the node is the owner and coordinator, and each component stays narrow.
