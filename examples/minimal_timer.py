"""Demonstrates a standalone ``LifecycleTimerComponent``.

Single idea: a timer component creates the ROS timer in ``_on_configure``; ticks are gated by the
lifecycle and only routed to ``on_tick`` while active. Inactive ticks are silently dropped.

Drive it::

    ros2 lifecycle set /timer_demo_node configure
    ros2 lifecycle set /timer_demo_node activate
    ros2 lifecycle set /timer_demo_node deactivate
    ros2 lifecycle set /timer_demo_node cleanup

Expected output::

    [configure]  [INFO] [heartbeat] timer created with period 1.0s
                 data flow:        none  (ticks dropped while inactive)

    [activate]   data flow:        on_tick called every second

    [while active]
                 [INFO] [heartbeat] tick #0  (repeats every second)

    [deactivate] data flow:        ticks dropped again; timer object retained

    [cleanup]    data flow:        timer destroyed by framework via _release_resources

    [shutdown]   same teardown as cleanup; node disappears from ros2 node list
"""

from __future__ import annotations

from lifecore_ros2 import LifecycleComponentNode, LifecycleTimerComponent


class Heartbeat(LifecycleTimerComponent):
    """Logs a heartbeat tick every second while active."""

    def __init__(self) -> None:
        super().__init__(name="heartbeat", period=1.0)
        self._counter: int = 0

    def on_tick(self) -> None:
        self.node.get_logger().info(f"[{self.name}] tick #{self._counter}")
        self._counter += 1


class TimerDemoNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("timer_demo_node")
        self.add_component(Heartbeat())


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init(args=["--ros-args", "--log-level", "timer_demo_node:=debug"])

    node = TimerDemoNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        node.get_logger().info("Timer demo node ready — trigger lifecycle transitions to start ticking")
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
