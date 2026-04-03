from __future__ import annotations

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn

from lifecore_ros2.core import ComposedLifecycleNode, LifecycleComponent


class LoggingComponent(LifecycleComponent):
    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        return super()._on_configure(state)

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return super()._on_activate(state)

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return super()._on_deactivate(state)

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        return super()._on_cleanup(state)


class MinimalNode(ComposedLifecycleNode):
    def __init__(self) -> None:
        super().__init__("minimal_lifecore_node")
        self.add_component(LoggingComponent("logger_component"))
        self.get_logger().debug("MinimalNode initialized")

    # def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
    #     self.get_logger().debug(f"[{self.get_name()}] configure")
    #     return TransitionCallbackReturn.SUCCESS


def main() -> None:
    rclpy.init(args=["--ros-args", "--log-level", "minimal_lifecore_node:=debug"])

    node = MinimalNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        node.get_logger().info("Minimal lifecycle node ready")
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
