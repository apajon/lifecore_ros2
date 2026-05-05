Examples
========

This page is the runtime view of the framework.
Use it once the lifecycle vocabulary is familiar and you want to see how the contract feels in actual nodes and components.

.. raw:: html

   <div class="lifecycle-map">
     <div class="lifecycle-step"><strong>⚙ Configure</strong><p>Each example shows where ROS resources are created and what stays dormant until activation.</p></div>
     <div class="lifecycle-step"><strong>▶ Activate</strong><p>Activation opens message flow, callbacks, or service handling depending on the component type.</p></div>
     <div class="lifecycle-step"><strong>▶ Run</strong><p>Observe the steady-state behavior you actually care about: publish, subscribe, tick, call, relay.</p></div>
     <div class="lifecycle-step lifecycle-step--transition"><strong>🔁 Transition</strong><p>Deactivate and cleanup reveal what remains allocated, what is gated, and what disappears from the graph.</p></div>
     <div class="lifecycle-step"><strong>■ Shutdown</strong><p>The final comparison point is always explicit teardown, never implicit destruction.</p></div>
   </div>

Read these examples before the API reference when you want the lifecycle model in one pass.
They are ordered from the smallest hook surface to full component composition.

If you are new to the repository, run ``minimal_node.py`` first. It shows the native ROS 2
transition flow without adding topic resources or runtime behavior.

Across all examples, the same lifecycle contract holds: ``configure`` creates long-lived ROS
resources, ``activate`` starts behavior, ``deactivate`` stops or gates behavior, and ``cleanup``
releases resources.

.. raw:: html

   <div class="state-box transition">
     <strong>How to read the examples.</strong>
     Do not read them as isolated demos. Read them as the same lifecycle contract replayed through different ROS surfaces: node-only, publisher, subscriber, timer, service server, service client, then multi-component composition.
   </div>

The companion repository also ships a scenario-driven comparison:
`lifecore_ros2_examples sensor watchdog comparison <https://github.com/apajon/lifecore_ros2_examples/blob/main/examples/lifecycle_comparison/README.md>`_.
Use it when you want the same watchdog behavior shown as plain ROS 2, classic lifecycle, and ``lifecore_ros2``. That README includes the shared sensor publisher command, the commands to run each variant, and the expected ``/sensor/status`` and log signals.

Example map
-----------

.. list-table::
   :header-rows: 1
   :widths: 20 26 24 30

   * - Example
     - What it demonstrates
     - When to read it
     - Command to run
   * - `minimal_node.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_node.py>`_
     - Smallest ``LifecycleComponentNode`` plus one explicit component hook.
     - Start here if you want the base transition flow without topic resources.
     - ``uv run python examples/minimal_node.py``
   * - `minimal_state_component.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_state_component.py>`_
     - Lifecycle-managed state with no ROS resource ownership.
     - Read after the node example to see lifecycle management applied to owned state rather than ROS resources.
     - ``uv run python examples/minimal_state_component.py``
   * - `minimal_timer.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_timer.py>`_
     - Standalone ``LifecycleTimerComponent`` with activation-gated ticks.
     - Read before the publisher example to understand timer gating in isolation.
     - ``uv run python examples/minimal_timer.py``
   * - `minimal_publisher.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_publisher.py>`_
     - Framework-owned publisher and timer composing in one node without overrides.
     - Read after the timer example to see two framework components wiring together.
     - ``uv run python examples/minimal_publisher.py``
   * - `minimal_subscriber.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_subscriber.py>`_
     - Activation-gated delivery with a managed subscription.
     - Read when you want to see inactive message drops and subscriber ownership.
     - ``uv run python examples/minimal_subscriber.py``
   * - `minimal_service_server.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_service_server.py>`_
     - ``LifecycleServiceServerComponent`` with activation-gated request handling.
     - Read when you want to see how inactive requests are answered with a default response.
     - ``uv run python examples/minimal_service_server.py``
   * - `minimal_service_client.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_service_client.py>`_
     - ``LifecycleServiceClientComponent`` with activation-gated outbound calls.
     - Read when you want to see how inactive ``call()`` raises and how ``timeout_service`` works.
     - ``uv run python examples/minimal_service_client.py``
   * - `telemetry_publisher.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/telemetry_publisher.py>`_
     - Full ``configure`` / ``activate`` / ``deactivate`` / ``cleanup`` split in one publisher component.
     - Read when you need a concrete pattern for long-lived handles plus runtime behavior.
     - ``uv run python examples/telemetry_publisher.py``
   * - `composed_pipeline.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/composed_pipeline.py>`_
     - Three sibling components transitioning together inside one node without any ordering.
     - Read after the timer example to see three framework components composing in one node.
     - ``uv run python examples/composed_pipeline.py``
   * - `composed_ordered_pipeline.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/composed_ordered_pipeline.py>`_
     - Three sibling components with explicit internal dependencies declared at registration time inside one node.
     - Read after ``composed_pipeline.py`` to see the same shape with dependency-driven ordering kept visible in the node assembly code.
     - ``uv run python examples/composed_ordered_pipeline.py``

After launching an example, drive it with ``ros2 lifecycle set /<node_name> configure``, then
``activate``, ``deactivate``, and ``cleanup``. Each module docstring includes the expected output
for those transitions, so you can compare logs and graph changes without reading the code first.

Suggested reading path
----------------------

- Start with ``minimal_node.py`` for the smallest ownership boundary.
- Continue with ``minimal_state_component.py`` to see lifecycle management applied to owned state with no ROS resources.
- Move to timer, publisher, and subscriber examples to see activation gating on long-lived ROS resources.
- Continue with service server and client examples to compare inbound versus outbound gating behavior.
- Finish with ``telemetry_publisher.py``, ``composed_pipeline.py``, and ``composed_ordered_pipeline.py`` for full lifecycle separation across multiple responsibilities.
- Read ``composed_ordered_pipeline.py`` after ``telemetry_publisher.py`` to see how ``dependencies`` declared at ``add_component(...)`` impose a guaranteed transition order across independently managed components.

Companion Comparison
--------------------

After the bundled examples, use the `sensor watchdog comparison in lifecore_ros2_examples <https://github.com/apajon/lifecore_ros2_examples/blob/main/examples/lifecycle_comparison/README.md>`_
when you want one applied walkthrough that compares plain ROS 2, classic lifecycle, and ``lifecore_ros2`` on the same watchdog node.
That companion README is the source of truth for its run commands, lifecycle transition commands, and expected ``/sensor/status`` and log signals.

Minimal Node
------------

Source: `examples/minimal_node.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_node.py>`_

What it demonstrates
~~~~~~~~~~~~~~~~~~~~

The smallest managed setup: one ``LifecycleComponentNode`` owns one ``LifecycleComponent`` with only
``_on_configure`` overridden.

What to look for
~~~~~~~~~~~~~~~~

- ``configure`` runs the component hook explicitly and nothing else.
- The node owns the component; the component does not manage node lifetime.
- ``activate`` and ``deactivate`` succeed with the native silent base behavior.
- No topics or ROS resources are created, retained, or released in this example.

Minimal State Component
-----------------------

Source: `examples/minimal_state_component.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_state_component.py>`_

What it demonstrates
~~~~~~~~~~~~~~~~~~~~

A ``LifecycleComponent`` that owns lifecycle-managed state with no ROS resource ownership.
The node calls ``update()`` on the component after each activation to demonstrate external mutation.

What to look for
~~~~~~~~~~~~~~~~

- ``configure`` resets the counter to ``0``; cleanup, shutdown, and error also reset it.
- ``deactivate`` preserves the counter so accumulated state survives a deactivate / re-activate cycle.
- The component owns its state; the node calls ``update()`` — the component does not push state outward.
- No publishers, subscriptions, or timers are created; the lifecycle contract is purely about state.

Minimal Timer
-------------

Source: `examples/minimal_timer.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_timer.py>`_

What it demonstrates
~~~~~~~~~~~~~~~~~~~~

A standalone ``LifecycleTimerComponent`` where the framework owns the ROS timer and ticks are
routed to ``on_tick`` only while the component is active.

What to look for
~~~~~~~~~~~~~~~~

- ``configure`` creates the ROS timer with the configured period; ticks fire but are silently dropped.
- ``activate`` opens the gate so each tick reaches ``on_tick``; ``deactivate`` closes it again without destroying the timer.
- ``cleanup`` lets the framework cancel and destroy the timer through ``_release_resources``.
- The component never owns a publisher or subscription, so the example isolates the timer contract on its own.

Minimal Publisher
-----------------

Source: `examples/minimal_publisher.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_publisher.py>`_

What it demonstrates
~~~~~~~~~~~~~~~~~~~~

A ``LifecyclePublisherComponent`` and a ``LifecycleTimerComponent`` composing in one node.
The framework owns both the ROS publisher and the ROS timer; activation gating is handled
entirely without overrides.

What to look for
~~~~~~~~~~~~~~~~

- ``configure`` creates both the publisher on ``/chatter`` and the timer.
- ``PublisherTimer`` receives ``PeriodicPublisher`` at construction and calls ``emit_next()`` in ``on_tick`` — no overrides needed.
- ``activate`` enables ticks and publication; ``deactivate`` gates both without any ``_on_deactivate`` override.
- ``cleanup`` releases the publisher and timer automatically through the framework.

Minimal Subscriber
------------------

Source: `examples/minimal_subscriber.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_subscriber.py>`_

What it demonstrates
~~~~~~~~~~~~~~~~~~~~

A ``LifecycleSubscriberComponent`` where delivery is gated by lifecycle state instead of being
embedded directly in the node.

What to look for
~~~~~~~~~~~~~~~~

- ``configure`` creates the subscription on ``/chatter``.
- The node owns one subscriber component; ``on_message`` is the component contract.
- ``activate`` allows delivery; ``deactivate`` silently drops messages by design.
- ``cleanup`` releases the subscription and removes the topic from the subscriber graph.

Minimal Service Server
----------------------

Source: `examples/minimal_service_server.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_service_server.py>`_

What it demonstrates
~~~~~~~~~~~~~~~~~~~~

A ``LifecycleServiceServerComponent`` where the framework owns the ROS service and request
handling is gated by lifecycle state through ``on_service_request``.

What to look for
~~~~~~~~~~~~~~~~

- ``configure`` creates the ROS service on ``/trigger``; the service appears in ``ros2 service list``.
- ``activate`` opens the gate so each request reaches ``on_service_request``.
- ``deactivate`` does not destroy the service: incoming requests get a default-constructed response with ``success=False`` and ``message="component inactive"``, and a warning is logged.
- ``cleanup`` destroys the service through ``_release_resources``.

Minimal Service Client
----------------------

Source: `examples/minimal_service_client.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_service_client.py>`_

What it demonstrates
~~~~~~~~~~~~~~~~~~~~

A ``LifecycleServiceClientComponent`` where the framework owns the ROS client and outbound
``call()`` / ``call_async()`` are gated by lifecycle state.

What to look for
~~~~~~~~~~~~~~~~

- ``configure`` creates the ROS client for ``/trigger``; no calls are issued yet.
- ``activate`` makes ``call()``, ``call_async()``, and ``wait_for_service()`` safe to invoke.
- ``call(..., timeout_service=...)`` waits for the service to become available and raises ``TimeoutError`` if it does not appear in time.
- ``deactivate`` makes new calls raise ``RuntimeError``; futures already returned by ``call_async()`` are not cancelled and remain owned by the application.
- ``cleanup`` destroys the client through ``_release_resources``.

Telemetry Publisher
-------------------

Source: `examples/telemetry_publisher.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/telemetry_publisher.py>`_

What it demonstrates
~~~~~~~~~~~~~~~~~~~~

A publisher component with all four hooks overridden to separate ROS resources, runtime behavior,
and non-ROS handles.

What to look for
~~~~~~~~~~~~~~~~

- ``configure`` acquires both the ROS publisher and the simulated sensor handle.
- One component owns the publisher, timer, and sensor handle as a single lifecycle unit.
- ``activate`` starts sampling; ``deactivate`` pauses it without releasing the sensor handle.
- ``cleanup`` releases the sensor handle and then lets the framework release the publisher.

Composed Pipeline
-----------------

Source: `examples/composed_pipeline.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/composed_pipeline.py>`_

What it demonstrates
~~~~~~~~~~~~~~~~~~~~

Three framework components — a timer, a publisher, and a subscriber — inside one
``LifecycleComponentNode``.  All three configure, activate, deactivate, and clean up
together through the native ROS 2 lifecycle.  No activation overrides needed.

What to look for
~~~~~~~~~~~~~~~~

- ``configure`` creates the publisher and subscription, and starts the timer in a ready (not firing) state.
- The node wires ``SineTimer`` to ``SinePublisher`` by passing the publisher at construction — no ``get_component`` call needed.
- ``activate`` enables end-to-end flow; ``deactivate`` gates all three components without any manual ``_on_deactivate`` override.
- ``cleanup`` releases the publisher, timer, and subscription automatically through the framework.

Composed Ordered Pipeline
-------------------------

Source: `examples/composed_ordered_pipeline.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/composed_ordered_pipeline.py>`_

What it demonstrates
~~~~~~~~~~~~~~~~~~~~

A timer, publisher, and subscriber component wired with explicit ``dependencies``
declared at ``add_component(...)`` so the framework resolves transition order
from those declarations, not from registration order. No ``_on_activate`` or
``_on_deactivate`` overrides are needed — the framework gates each component
automatically.

What to look for
~~~~~~~~~~~~~~~~

- Components are registered in a deliberately scrambled order (sink first, timer
  second, publisher last). Dependencies are declared at the registration site,
  so ordering intent is visible where the node is assembled. Publisher is
  configured first because both timer and sink depend on it.
- ``SineTimer`` holds a direct reference to ``SinePublisher`` and calls
  ``emit_next()`` in ``on_tick`` — no raw ``create_timer`` or ``create_publisher``
  call appears anywhere in the example.
- ``SineTimer`` and ``LoggingSink`` do not expose pass-through ordering kwargs in
  their constructors; ``dependencies`` stay on the node side of the composition boundary.
- ``deactivate`` and ``cleanup`` propagate in reverse dependency order: timer
  and sink before publisher.
