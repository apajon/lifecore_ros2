Examples
========

Read these examples before the API reference when you want the lifecycle model in one pass.
They are ordered from the smallest hook surface to full component composition.

If you are new to the repository, run ``minimal_node.py`` first. It shows the native ROS 2
transition flow without adding topic resources or runtime behavior.

Across all examples, the same lifecycle contract holds: ``configure`` creates long-lived ROS
resources, ``activate`` starts behavior, ``deactivate`` stops or gates behavior, and ``cleanup``
releases resources.

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
