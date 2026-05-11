"""Demonstrates ``LifecycleWatchdogComponent`` observing a degraded sensor.

Two components are registered on the node:

- ``watchdog`` (priority=10) — activates *before* the sensor because it has the
  higher priority. Polls ``sensor.health`` every second. Stale threshold is 5 s.
- ``sensor`` (priority=0) — activates second; its ``_on_activate`` returns ``FAILURE``
  (→ health ``DEGRADED``). Propagation stops here; the *watchdog is already active*.

After ``ros2 lifecycle set /minimal_watchdog_node activate`` the watchdog timer fires
every second and logs a WARN for the degraded sensor. After 5 s it adds a STALE WARN.

Drive it::

    ros2 run lifecore_ros2 minimal_watchdog &  # or: python -m lifecore_ros2.examples.minimal_watchdog
    ros2 lifecycle set /minimal_watchdog_node configure
    ros2 lifecycle set /minimal_watchdog_node activate

Expected output (repeating every ~1 s)::

    [WARN]  [minimal_watchdog_node]: [watchdog] sensor DEGRADED: activate hook returned FAILURE

After ~5 s::

    [WARN]  [minimal_watchdog_node]: [watchdog] sensor STALE: level=degraded for 5.0s (threshold=5.0s)

Note: ``ros2 lifecycle set activate`` returns FAILURE (because sensor failed to activate),
but the watchdog component is already active and continues polling.
"""

from __future__ import annotations

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn

from lifecore_ros2 import LifecycleComponentNode, LifecycleWatchdogComponent
from lifecore_ros2.core import LifecycleComponent


class SensorComponent(LifecycleComponent):
    """Sensor that fails to activate, producing a persistent DEGRADED health state.

    Returning ``FAILURE`` from ``_on_activate`` is enough — the framework sets
    ``health.level`` to ``DEGRADED`` automatically.
    """

    def __init__(self) -> None:
        super().__init__("sensor")

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.node.get_logger().info(f"[{self.name}] configured")
        return TransitionCallbackReturn.SUCCESS

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.node.get_logger().info(f"[{self.name}] activate returning FAILURE — health will be DEGRADED")
        return TransitionCallbackReturn.FAILURE


class MinimalWatchdogNode(LifecycleComponentNode):
    """Node with a degraded sensor observed by a lifecycle watchdog.

    The watchdog has higher ``priority`` than the sensor so it is activated first
    in the forward propagation pass. When the sensor then fails to activate, the
    watchdog is already active and will start polling on its next timer tick.
    """

    def __init__(self) -> None:
        super().__init__("minimal_watchdog_node")
        self._sensor = SensorComponent()
        self._watchdog = LifecycleWatchdogComponent(
            name="watchdog",
            targets=[self._sensor],
            poll_period=1.0,
            stale_threshold=5.0,
            priority=10,  # activate before sensor (priority 0)
        )
        self.add_component(self._sensor)
        self.add_component(self._watchdog)


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init()
    node = MinimalWatchdogNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    node.get_logger().info(
        "Minimal watchdog node ready — "
        "drive it with: ros2 lifecycle set /minimal_watchdog_node configure && "
        "ros2 lifecycle set /minimal_watchdog_node activate"
    )
    try:
        executor.spin()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
