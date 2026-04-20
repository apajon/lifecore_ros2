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
