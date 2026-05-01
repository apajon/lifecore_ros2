Mental Model
============

.. raw:: html

   <div class="lifecycle-signature">
     <svg class="lifecycle-signature__mark" viewBox="0 0 96 96" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
       <circle cx="48" cy="48" r="30" stroke="currentColor" stroke-width="12" stroke-linecap="round" stroke-dasharray="96 20"/>
       <path d="M48 12a36 36 0 0 1 25.46 10.54" stroke="#7C3AED" stroke-width="12" stroke-linecap="round"/>
       <path d="M79.82 64.5A36 36 0 0 1 48 84" stroke="#7C3AED" stroke-width="12" stroke-linecap="round" stroke-dasharray="22 16"/>
     </svg>
     <div>
       <p class="lifecycle-signature__eyebrow">Lifecycle interface</p>
       <p class="lifecycle-signature__title">Core lifecycle for modular robotics systems</p>
       <p class="lifecycle-signature__text">The framework stays readable when each concept is tied to an explicit lifecycle phase.</p>
     </div>
   </div>

Read this page before the API reference.
It describes the intended mental model of the framework.

Lifecycle Flow
--------------

.. raw:: html

   <div class="lifecycle-map">
     <div class="lifecycle-step"><strong>⚙ Configure</strong><p>Components create ROS-facing resources in configure hooks, not in their constructor.</p></div>
     <div class="lifecycle-step"><strong>▶ Activate</strong><p>Runtime behavior becomes live only when the node activates managed entities.</p></div>
     <div class="lifecycle-step"><strong>▶ Run</strong><p>Publish, subscribe, call services, and tick timers only while the active state is explicit.</p></div>
     <div class="lifecycle-step lifecycle-step--transition"><strong>🔁 Transition</strong><p>The node owns transition propagation, so components do not invent a second control plane.</p></div>
     <div class="lifecycle-step"><strong>■ Shutdown</strong><p>Cleanup and shutdown release resources and leave no hidden runtime state behind.</p></div>
   </div>

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

.. raw:: html

   <div class="state-box">
     <strong>State contract.</strong>
     The lifecycle is the interface: resource creation belongs to configure, runtime work belongs to active states, and teardown belongs to cleanup and shutdown.
   </div>

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
