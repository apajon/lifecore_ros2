"""Demonstrates a ``LifecycleComponent`` that owns lifecycle-managed state without owning ROS resources.

Single idea: lifecycle management applies to domain state, not only to ROS resources.
The counter resets on configure, cleanup, shutdown, and error; it is preserved across deactivate
so accumulated state survives a deactivate / re-activate cycle.

Note: the state reset in ``_on_configure``, ``_on_cleanup``, ``_on_shutdown``, and ``_on_error``
is a choice made by ``CounterStateComponent``, not a framework rule.

Drive it::

    ros2 lifecycle set /state_component_demo_node configure
    ros2 lifecycle set /state_component_demo_node activate
    ros2 lifecycle set /state_component_demo_node deactivate
    ros2 lifecycle set /state_component_demo_node activate
    ros2 lifecycle set /state_component_demo_node cleanup
    ros2 lifecycle set /state_component_demo_node shutdown

Expected output::

    [configure]  [INFO] [counter_state] configured, count reset to 0

    [activate]   [INFO] [counter_state] count updated to 1
                 count: 1  (node calls update(1) after activation)

    [deactivate] [INFO] [counter_state] deactivated, count preserved at 1
                 count: 1  (deactivation does not reset — state available for re-activation)

    [activate]   [INFO] [counter_state] count updated to 2  (re-activation accumulates)
                 count: 2

    [cleanup]    [INFO] [counter_state] cleaned up, count reset to 0
                 count: 0

    [shutdown]   [INFO] [counter_state] shutdown, count reset to 0
                 count: 0
"""

from __future__ import annotations

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn

from lifecore_ros2.core import LifecycleComponent, LifecycleComponentNode


class CounterStateComponent(LifecycleComponent):
    """Owns an integer counter as lifecycle-managed state with no ROS resources.

    The count resets on configure, cleanup, shutdown, and error.
    Deactivation preserves the count so accumulated state survives a deactivate / re-activate cycle.
    """

    def __init__(self) -> None:
        super().__init__("counter_state")
        self._count: int = 0

    @property
    def count(self) -> int:
        """Current counter value."""
        return self._count

    def update(self, delta: int = 1) -> None:
        self._count += delta
        self.node.get_logger().info(f"[{self.name}] count updated to {self._count}")

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._count = 0
        self.node.get_logger().info(f"[{self.name}] configured, count reset to 0")
        return TransitionCallbackReturn.SUCCESS

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.node.get_logger().info(f"[{self.name}] deactivated, count preserved at {self._count}")
        return TransitionCallbackReturn.SUCCESS

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._count = 0
        self.node.get_logger().info(f"[{self.name}] cleaned up, count reset to 0")
        return TransitionCallbackReturn.SUCCESS

    def _on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._count = 0
        self.node.get_logger().info(f"[{self.name}] shutdown, count reset to 0")
        return TransitionCallbackReturn.SUCCESS

    def _on_error(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._count = 0
        self.node.get_logger().info(f"[{self.name}] error, count reset to 0")
        return TransitionCallbackReturn.SUCCESS


class StateComponentDemoNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("state_component_demo_node")
        self._counter = CounterStateComponent()
        self.add_component(self._counter)

    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        result = super().on_activate(state)
        if result == TransitionCallbackReturn.SUCCESS:
            self._counter.update(1)
        return result


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init(args=["--ros-args", "--log-level", "state_component_demo_node:=debug"])

    node = StateComponentDemoNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        node.get_logger().info("State component demo node ready — trigger lifecycle transitions to observe state")
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
