"""Demonstrates composing a ``LifecyclePublisherComponent`` with a ``LifecycleTimerComponent``.

Single idea: two managed entities — one publisher, one timer — registered on the same node.
The publisher owns the ROS publisher; the timer owns the periodic tick. Both are gated by
the framework: ``publish`` raises while inactive, and timer ticks are silently dropped while
inactive. Neither component overrides ``_on_activate`` / ``_on_deactivate`` — activation
gating is handled entirely by the framework.

Drive it::

    ros2 lifecycle set /telemetry_node configure
    ros2 lifecycle set /telemetry_node activate
    # Observe data: ros2 topic echo /telemetry
    ros2 lifecycle set /telemetry_node deactivate
    ros2 lifecycle set /telemetry_node cleanup

Expected output::

    [before configure]
                 ros2 topic list:  /telemetry not present

    [configure]  [INFO] [telemetry_pub]   publisher created on '/telemetry'
                 [INFO] [telemetry_timer] timer created with period 1.0s
                 ros2 topic list:  /telemetry appears  (publisher created by framework)
                 data flow:        none  (ticks gated until activate)

    [activate]   data flow:        /telemetry publishes at 1 Hz

    [while active]
                 [INFO] [telemetry_timer] sample 0: 0.0000  (value is sin(N * 0.1); repeats every second)
                 [INFO] [telemetry_timer] sample 1: 0.0998

    [deactivate] data flow:        ticks dropped silently; publisher and timer retained
                 ros2 topic list:  /telemetry still present

    [cleanup]    ros2 topic list:  /telemetry disappears  (publisher and timer released by framework)

    [shutdown]   same teardown as cleanup; node disappears from ros2 node list
"""

from __future__ import annotations

import math

from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import Float64

from lifecore_ros2 import (
    LifecycleComponentNode,
    LifecyclePublisherComponent,
    LifecycleTimerComponent,
)

_TELEMETRY_QOS = QoSProfile(depth=5, reliability=ReliabilityPolicy.BEST_EFFORT)


class TelemetrySampler(LifecycleTimerComponent):
    """Samples a sine wave on each tick and publishes it via the supplied publisher."""

    def __init__(self, publisher: LifecyclePublisherComponent[Float64]) -> None:
        super().__init__(name="telemetry_timer", period=1.0)
        self._publisher = publisher
        self._sequence: int = 0

    def on_tick(self) -> None:
        msg = Float64()
        msg.data = math.sin(self._sequence * 0.1)
        self._publisher.publish(msg)
        self.node.get_logger().info(f"[{self.name}] sample {self._sequence}: {msg.data:.4f}")
        self._sequence += 1


class TelemetryNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("telemetry_node")
        publisher = LifecyclePublisherComponent[Float64](
            name="telemetry_pub",
            topic_name="/telemetry",
            msg_type=Float64,
            qos_profile=_TELEMETRY_QOS,
        )
        self.add_component(publisher)
        self.add_component(TelemetrySampler(publisher))


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
