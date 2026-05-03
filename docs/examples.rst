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
   * - `minimal_publisher.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_publisher.py>`_
     - Framework-owned publisher plus component-owned timer.
     - Read after the node example to see ``configure`` versus ``activate`` for publishing.
     - ``uv run python examples/minimal_publisher.py``
   * - `minimal_subscriber.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_subscriber.py>`_
     - Activation-gated delivery with a managed subscription.
     - Read when you want to see inactive message drops and subscriber ownership.
     - ``uv run python examples/minimal_subscriber.py``
   * - `minimal_timer.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_timer.py>`_
     - Standalone ``LifecycleTimerComponent`` with activation-gated ticks.
     - Read when you want a periodic callback whose firing is bound to lifecycle state.
     - ``uv run python examples/minimal_timer.py``
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
     - Three sibling components transitioning together inside one node.
     - Read last to see composition, raw ROS resource ownership, and reactivation behavior.
     - ``uv run python examples/composed_pipeline.py``

After launching an example, drive it with ``ros2 lifecycle set /<node_name> configure``, then
``activate``, ``deactivate``, and ``cleanup``. Each module docstring includes the expected output
for those transitions, so you can compare logs and graph changes without reading the code first.

Suggested reading path
----------------------

- Start with ``minimal_node.py`` for the smallest ownership boundary.
- Move to publisher, subscriber, and timer examples to see activation gating on long-lived ROS resources.
- Continue with service server and client examples to compare inbound versus outbound gating behavior.
- Finish with ``telemetry_publisher.py`` and ``composed_pipeline.py`` for full lifecycle separation across multiple responsibilities.

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

Minimal Publisher
-----------------

Source: `examples/minimal_publisher.py <https://github.com/apajon/lifecore_ros2/blob/main/examples/minimal_publisher.py>`_

What it demonstrates
~~~~~~~~~~~~~~~~~~~~

A ``LifecyclePublisherComponent`` where the framework owns the ROS publisher and the component owns
the runtime timer.

What to look for
~~~~~~~~~~~~~~~~

- ``configure`` creates the publisher on ``/chatter``.
- The node owns one publisher component; the timer belongs to that component, not to the node.
- ``activate`` starts the timer; ``deactivate`` stops it while the publisher stays available.
- ``cleanup`` removes the publisher, so ``/chatter`` disappears from the graph.

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

Three sibling components inside one ``LifecycleComponentNode``: a source, a relay, and a sink that
transition together through the native ROS 2 lifecycle.

What to look for
~~~~~~~~~~~~~~~~

- ``configure`` creates both pipeline topics and wires all three components.
- The node owns three sibling components; the relay shows direct ownership of both a raw subscription and a raw publisher.
- ``activate`` enables end-to-end flow, and ``deactivate`` stops flow for the whole pipeline.
- The relay clears its buffer on ``deactivate``; ``cleanup`` releases raw ROS resources and removes both topics.
