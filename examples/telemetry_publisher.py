"""Demonstrates configure-time resource acquisition vs activate-time sampling behavior.

Unlike the minimal examples, this example makes the lifecycle contract explicit at each stage:
``_on_configure`` acquires long-lived resources (ROS publisher via super(), sensor handle);
``_on_activate`` starts runtime behavior (timer); ``_on_deactivate`` suspends sampling while keeping
the sensor handle intact; ``_on_cleanup`` releases the sensor handle before the framework destroys
the ROS publisher via ``_release_resources``.

Single idea: a simulated telemetry sensor that publishes ``Float64`` sine-wave samples, with all
four hooks overridden to show the configure/activate/deactivate/cleanup layers explicitly.

Drive it::

    ros2 lifecycle set /telemetry_node configure
    ros2 lifecycle set /telemetry_node activate
    # Observe data: ros2 topic echo /telemetry
    ros2 lifecycle set /telemetry_node deactivate
    ros2 lifecycle set /telemetry_node cleanup

Expected output::

    [before configure]
                 ros2 topic list:  /telemetry not present

    [configure]  [INFO] [telemetry_pub] publisher created on '/telemetry'
                 [INFO] [telemetry_pub] sensor handle acquired
                 ros2 topic list:  /telemetry appears  (publisher created by framework)
                 data flow:        none  (sampling timer not started yet)

    [activate]   [INFO] [telemetry_pub] sampling started
                 data flow:        /telemetry publishes at 1 Hz

    [while active]
                 [INFO] [telemetry_pub] sample 0: 0.0000  (value is sin(N * 0.1); repeats every second)
                 [INFO] [telemetry_pub] sample 1: 0.0998

    [deactivate] [INFO] [telemetry_pub] sampling paused — sensor handle retained
                 ros2 topic list:  /telemetry still present  (publisher and sensor handle both retained)
                 data flow:        stopped

    [cleanup]    [INFO] [telemetry_pub] sensor handle released
                 ros2 topic list:  /telemetry disappears  (publisher released by framework via _release_resources)

    [shutdown]   same teardown as cleanup; node disappears from ros2 node list
"""

from __future__ import annotations

import math

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.timer import Timer
from std_msgs.msg import Float64

from lifecore_ros2 import LifecycleComponentNode, LifecyclePublisherComponent

_TELEMETRY_QOS = QoSProfile(depth=5, reliability=ReliabilityPolicy.BEST_EFFORT)


class LifecycleTelemetryPublisher(LifecyclePublisherComponent[Float64]):
    """Simulates a sensor that publishes sine-wave telemetry while active."""

    def __init__(self) -> None:
        super().__init__(
            name="telemetry_pub",
            topic_name="/telemetry",
            msg_type=Float64,
            qos_profile=_TELEMETRY_QOS,
        )
        self._timer: Timer | None = None
        self._sensor_ready: bool = False
        self._sequence: int = 0

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        result = super()._on_configure(state)  # creates the ROS publisher
        if result != TransitionCallbackReturn.SUCCESS:
            return result
        self._sensor_ready = True
        self._sequence = 0
        self.node.get_logger().info(f"[{self.name}] sensor handle acquired")
        return TransitionCallbackReturn.SUCCESS

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        # why: timer is runtime behavior — created here (not in _on_configure) so it only runs while active.
        self._timer = self.node.create_timer(1.0, self._sample)
        self.node.get_logger().info(f"[{self.name}] sampling started")
        return TransitionCallbackReturn.SUCCESS

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        if self._timer is not None:
            self._timer.cancel()
            self.node.destroy_timer(self._timer)
            self._timer = None
        self.node.get_logger().info(f"[{self.name}] sampling paused — sensor handle retained")
        return TransitionCallbackReturn.SUCCESS

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._sensor_ready = False
        self._sequence = 0
        self.node.get_logger().info(f"[{self.name}] sensor handle released")
        return super()._on_cleanup(state)

    def _sample(self) -> None:
        msg = Float64()
        msg.data = math.sin(self._sequence * 0.1)
        self._sequence += 1
        # publish() is gated by @when_active on the parent; the timer lifetime further ensures this.
        self.publish(msg)
        self.node.get_logger().info(f"[{self.name}] sample {self._sequence - 1}: {msg.data:.4f}")


class TelemetryNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("telemetry_node")
        self.add_component(LifecycleTelemetryPublisher())


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init(args=["--ros-args", "--log-level", "telemetry_node:=debug"])

    node = TelemetryNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        node.get_logger().info("Telemetry node ready — configure and activate to start sampling")
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
