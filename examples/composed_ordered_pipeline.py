"""Three framework components with explicit dependencies inside one lifecycle node.

Demonstrates: timer, publisher, and subscriber components composed with
``dependencies`` declared at the registration site — not in each component's
constructor — so ordering intent is visible at a single glance in the node.

Dependency graph::

    publisher <── timer
    publisher <── sink

The publisher is always configured first because both timer and sink depend on
it.  Activation and cleanup propagate in dependency order automatically — no
``_on_activate`` or ``_on_deactivate`` overrides needed anywhere.

Drive it::

    ros2 lifecycle set /ordered_pipeline_node configure
    ros2 lifecycle set /ordered_pipeline_node activate
    ros2 lifecycle set /ordered_pipeline_node deactivate
    ros2 lifecycle set /ordered_pipeline_node cleanup
"""

from __future__ import annotations

import math

from std_msgs.msg import Float64

from lifecore_ros2 import (
    LifecycleComponentNode,
    LifecyclePublisherComponent,
    LifecycleSubscriberComponent,
    LifecycleTimerComponent,
)

_TOPIC = "/ordered/raw"
_PERIOD = 1.0


class SinePublisher(LifecyclePublisherComponent[Float64]):
    """Publishes a sine-wave sequence on ``/ordered/raw``."""

    def __init__(self, *, name: str) -> None:
        super().__init__(name=name, topic_name=_TOPIC, msg_type=Float64)
        self._sequence: int = 0

    def emit_next(self) -> None:
        """Publish one sine sample and advance the sequence counter."""
        msg = Float64()
        msg.data = math.sin(self._sequence * 0.1)
        self._sequence += 1
        self.publish(msg)


class SineTimer(LifecycleTimerComponent):
    """Drives ``SinePublisher`` at 1 Hz while active."""

    def __init__(self, *, name: str, source: SinePublisher) -> None:
        super().__init__(name=name, period=_PERIOD)
        self._source = source

    def on_tick(self) -> None:
        self._source.emit_next()


class LoggingSink(LifecycleSubscriberComponent[Float64]):
    """Logs values received on ``/ordered/raw``."""

    def __init__(self, *, name: str) -> None:
        super().__init__(name=name, topic_name=_TOPIC, msg_type=Float64)

    def on_message(self, msg: Float64) -> None:
        self.node.get_logger().info(f"[{self.name}] value={msg.data:.4f}")


class OrderedPipelineNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("ordered_pipeline_node")
        publisher = SinePublisher(name="publisher")
        timer = SineTimer(name="timer", source=publisher)
        sink = LoggingSink(name="sink")
        # Ordering intent is declared here, at the assembly site.
        # Registration order is intentionally scrambled to confirm that
        # dependencies -- not registration order -- drive the transition sequence.
        self.add_component(sink, dependencies=("publisher",))
        self.add_component(timer, dependencies=("publisher",))
        self.add_component(publisher)


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init()

    node = OrderedPipelineNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        node.get_logger().info("Ordered pipeline node ready -- configure and activate to start")
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
