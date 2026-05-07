Migration from Raw rclpy
========================

This page shows a single before/after comparison: a subscriber node written with raw ``rclpy``
rewritten using lifecore_ros2. The goal is to make the composition benefit concrete.

The before example represents common rclpy usage. The after example uses
``LifecycleComponentNode`` and ``LifecycleSubscriberComponent``.

Before: raw rclpy lifecycle node
---------------------------------

A typical raw rclpy lifecycle subscriber node looks like this:

.. code-block:: python

    from rclpy.lifecycle import LifecycleNode, LifecycleState, TransitionCallbackReturn
    from std_msgs.msg import String


    class ChatterNode(LifecycleNode):
        def __init__(self) -> None:
            super().__init__("chatter_node")
            self._sub = None
            self._active = False

        def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
            self._sub = self.create_subscription(String, "/chatter", self._on_msg, 10)
            return TransitionCallbackReturn.SUCCESS

        def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
            self._active = True
            return super().on_activate(state)

        def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
            self._active = False
            return super().on_deactivate(state)

        def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
            self.destroy_subscription(self._sub)
            self._sub = None
            return TransitionCallbackReturn.SUCCESS

        def _on_msg(self, msg: String) -> None:
            if not self._active:
                return
            self.get_logger().info(f"Received: {msg.data}")

Problems with this pattern at scale:

- ``_active``, ``_sub``, and ``_on_msg`` are all mixed into the node class.
  Adding a second subscriber doubles the noise.
- ``_active`` is a hand-rolled flag that shadows the lifecycle state but is not
  connected to it. A missed ``super()`` call or an exception in a hook desynchronises it.
  ``lifecore_ros2`` removes both failure modes: activation gating is owned by the
    library, and uncaught hook exceptions are wrapped in
  :class:`~lifecore_ros2.LifecycleHookError`, mapped to
  ``TransitionCallbackReturn.ERROR``, and routed through rclpy's native
  ``ErrorProcessing`` (see :doc:`design_notes/error_handling_contract`).
- Cleanup logic (``destroy_subscription``) is duplicated in every node that needs it.
- There is no reusable unit — the subscriber behavior is coupled to this specific node.

After: lifecore_ros2
--------------------

The same behavior expressed with ``LifecycleSubscriberComponent``:

.. code-block:: python

    from lifecore_ros2 import LifecycleComponentNode, LifecycleSubscriberComponent
    from std_msgs.msg import String


    class ChatterSubscriber(LifecycleSubscriberComponent[String]):
        def __init__(self) -> None:
            super().__init__(
                name="chatter_sub",
                topic_name="/chatter",
                qos_profile=10,
            )

        def on_message(self, msg: String) -> None:
            self.node.get_logger().info(f"Received: {msg.data}")


    class ChatterNode(LifecycleComponentNode):
        def __init__(self) -> None:
            super().__init__("chatter_node")
            self.add_component(ChatterSubscriber())

What changed:

- ``_active`` is gone. The library tracks activation state via ``_is_active`` and drops
  inbound messages automatically when the component is not active.
- ``_sub`` creation and destruction are handled by ``TopicComponent._on_configure`` and
  ``_release_resources``. No explicit ``destroy_subscription`` call needed.
- ``ChatterSubscriber`` is reusable. Any node can attach it via ``add_component``.
- The node class contains only composition logic: which components it owns.

What stays the same:

- lifecycle transitions are still ``configure → activate → deactivate → cleanup``
- ``ros2 lifecycle set`` commands work identically
- rclpy controls the lifecycle state machine — lifecore_ros2 only propagates transitions
  to components

Running the equivalent example
-------------------------------

The ``examples/minimal_subscriber.py`` file in the repository demonstrates this pattern.
Run it with:

.. code-block:: bash

    source /opt/ros/jazzy/setup.bash
    uv run --extra dev python examples/minimal_subscriber.py

See :doc:`examples` for the full walkthrough.
