"""Demonstrates the minimal hook surface of a ``LifecycleComponent`` inside a ``LifecycleComponentNode``.

Single idea: an explicit ``_on_configure`` override that logs the transition and returns SUCCESS,
showing the smallest possible hook contract.

Drive it::

    ros2 lifecycle set /minimal_lifecore_node configure
    ros2 lifecycle set /minimal_lifecore_node activate
    ros2 lifecycle set /minimal_lifecore_node deactivate
    ros2 lifecycle set /minimal_lifecore_node cleanup
    ros2 lifecycle set /minimal_lifecore_node shutdown

Expected output::

    [configure]  [INFO] [logger_component] on_configure called
    [activate]   (no component log — base _on_activate returns SUCCESS silently)
    [deactivate] (no component log — base _on_deactivate returns SUCCESS silently)
    [cleanup]    (no component log — base _on_cleanup returns SUCCESS silently)
    [shutdown]   (no component log — base _on_shutdown returns SUCCESS silently)
"""

from __future__ import annotations

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn

from lifecore_ros2.core import LifecycleComponent, LifecycleComponentNode


class LoggingComponent(LifecycleComponent):
    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.node.get_logger().info(f"[{self.name}] on_configure called")
        return TransitionCallbackReturn.SUCCESS


class MinimalNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("minimal_lifecore_node")
        self.add_component(LoggingComponent("logger_component"))
        self.get_logger().debug("MinimalNode initialized")


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

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
