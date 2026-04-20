"""Demonstrates a ``LifecycleSubscriberComponent`` with activation-gated message delivery.

Single idea: the ROS subscription is created on configure; messages are silently dropped by the
framework when the component is inactive and delivered to ``on_message`` only when active.

Drive it::

    ros2 lifecycle set /demo_node configure
    ros2 lifecycle set /demo_node activate
    # In a separate terminal: ros2 topic pub /chatter std_msgs/msg/String "{data: 'hi'}"
    ros2 lifecycle set /demo_node deactivate

Expected output::

    [configure]  [INFO] [echo_sub] subscription created on '/chatter'
    [activate]   (no component log — base _on_activate returns SUCCESS silently)
    [message]    [INFO] Received: hi
    [deactivate] (no component log — messages after this point are silently dropped)
"""

from __future__ import annotations

from std_msgs.msg import String

from lifecore_ros2 import LifecycleComponentNode, LifecycleSubscriberComponent


class EchoSubscriber(LifecycleSubscriberComponent[String]):
    def __init__(self) -> None:
        super().__init__(
            name="echo_sub",
            topic_name="/chatter",
            msg_type=String,
            qos_profile=10,
        )

    def on_message(self, msg: String) -> None:
        """Handle an incoming message while the component is active.

        This is the public application-callback contract (Bucket-1: intentionally public).
        Called only while active; messages arriving before activate or after deactivate
        are silently dropped by the framework.
        """
        self.node.get_logger().info(f"Received: {msg.data}")


class DemoNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("demo_node")
        self.add_component(EchoSubscriber())


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init(args=["--ros-args", "--log-level", "demo_node:=debug"])

    node = DemoNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        node.get_logger().info("Subscriber demo node ready (configure + activate to process /chatter)")
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
