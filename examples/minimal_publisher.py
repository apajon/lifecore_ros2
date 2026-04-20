from __future__ import annotations

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.timer import Timer
from std_msgs.msg import String

from lifecore_ros2 import LifecycleComponentNode, LifecyclePublisherComponent


class PeriodicPublisher(LifecyclePublisherComponent[String]):
    """Publishes a String message on /chatter every second while active."""

    def __init__(self) -> None:
        super().__init__(
            name="periodic_pub",
            topic_name="/chatter",
            msg_type=String,
            qos_profile=10,
        )
        self._timer: Timer | None = None
        self._counter: int = 0

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._timer = self.node.create_timer(1.0, self._tick)
        self.node.get_logger().info(f"[{self.name}] timer started")
        return TransitionCallbackReturn.SUCCESS

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        if self._timer is not None:
            self._timer.cancel()
            self.node.destroy_timer(self._timer)
            self._timer = None
        self.node.get_logger().info(f"[{self.name}] timer stopped")
        return TransitionCallbackReturn.SUCCESS

    def _tick(self) -> None:
        msg = String()
        msg.data = f"hello #{self._counter}"
        self.publish(msg)
        self.node.get_logger().info(f"[{self.name}] published on [{self.topic_name}]: {msg.data!r}")
        self._counter += 1


class PublisherDemoNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("publisher_demo_node")
        self.add_component(PeriodicPublisher())


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init(args=["--ros-args", "--log-level", "publisher_demo_node:=debug"])

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
