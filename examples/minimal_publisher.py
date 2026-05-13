"""Demonstrates two framework components composing inside one lifecycle node.

Single idea: a ``LifecyclePublisherComponent`` and a ``LifecycleTimerComponent``
register on the same node.  The framework owns both the ROS publisher and the
ROS timer; both are gated by activation state without any ``_on_activate`` or
``_on_deactivate`` overrides.

Drive it::

    ros2 lifecycle set /publisher_demo_node configure
    ros2 lifecycle set /publisher_demo_node activate
    ros2 lifecycle set /publisher_demo_node deactivate
    ros2 lifecycle set /publisher_demo_node cleanup

Expected output per transition::

    [before configure]
                 ros2 topic list:  /chatter not present

    [configure]  [INFO] [periodic_pub] publisher created on '/chatter'
                 [INFO] [pub_timer]    timer created with period 1.0s
                 ros2 topic list:  /chatter appears  (publisher created by framework)
                 data flow:        none  (ticks gated until activate)

    [activate]   data flow:        /chatter publishes at 1 Hz

    [while active]
                 [INFO] [periodic_pub] published on [/chatter]: 'hello #0'  (repeats every second)

    [deactivate] data flow:        ticks dropped; publisher retained
                 ros2 topic list:  /chatter still present

    [cleanup]    ros2 topic list:  /chatter disappears  (publisher released by framework)
"""

from __future__ import annotations

from std_msgs.msg import String

from lifecore_ros2 import LifecycleComponentNode, LifecyclePublisherComponent, LifecycleTimerComponent


class PeriodicPublisher(LifecyclePublisherComponent[String]):
    """Publishes incrementing ``hello #N`` messages on ``/chatter``."""

    def __init__(self) -> None:
        super().__init__(name="periodic_pub", topic_name="/chatter", msg_type=String)
        self._counter: int = 0

    def emit_next(self) -> None:
        """Publish one message and increment the counter.

        This is the application-facing publish step used by the timer example;
        the framework still owns publisher creation and lifecycle gating.
        """
        msg = String()
        msg.data = f"hello #{self._counter}"
        self._counter += 1
        self.publish(msg)
        self.node.get_logger().info(f"[{self.name}] published on [{self.topic_name}]: {msg.data!r}")


class PublisherTimer(LifecycleTimerComponent):
    """Drives ``PeriodicPublisher`` at 1 Hz while active."""

    def __init__(self, publisher: PeriodicPublisher) -> None:
        super().__init__(name="pub_timer", period=1.0)
        self._publisher = publisher

    def on_tick(self) -> None:
        """Handle one timer tick while active by delegating to ``emit_next``.

        ``on_tick`` remains the public timer hook; this example keeps publish
        logic in the publisher component so the timer stays orchestration-only.
        """
        self._publisher.emit_next()


class PublisherDemoNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("publisher_demo_node")
        publisher = PeriodicPublisher()
        self.add_component(publisher)
        self.add_component(PublisherTimer(publisher))


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init()

    node = PublisherDemoNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        node.get_logger().info("Publisher demo node ready — trigger lifecycle transitions to publish")
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
