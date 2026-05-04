"""Three sibling components inside one lifecycle node, transitioning together.

Single idea: a timer, a publisher, and a subscriber register on the same
``LifecycleComponentNode``.  All three configure, activate, deactivate, and
clean up together — no ordering or dependencies required.

No ``_on_activate`` or ``_on_deactivate`` overrides appear anywhere: the
framework gates each component automatically based on its lifecycle state.

Topology::

    SineTimer ──► SinePublisher ──/pipeline/raw──► LoggingSink

Drive it::

    ros2 lifecycle set /pipeline_node configure
    ros2 lifecycle set /pipeline_node activate
    # Observe values: ros2 topic echo /pipeline/raw
    ros2 lifecycle set /pipeline_node deactivate
    ros2 lifecycle set /pipeline_node activate   # resumes from where it paused
    ros2 lifecycle set /pipeline_node cleanup

Expected output per transition::

    [before configure]
                 ros2 topic list:  /pipeline/raw not present

    [configure]  [INFO] [pipeline_node] [source] publisher created on '/pipeline/raw'
                 [INFO] [pipeline_node] [timer]  timer created with period 1.0s
                 [INFO] [pipeline_node] [sink]   subscription created on '/pipeline/raw'
                 ros2 topic list:  /pipeline/raw now present
                 data flow:        none  (ticks gated until activate)

    [activate]   data flow:        /pipeline/raw at 1 Hz delivered to LoggingSink

    [while active]
                 [INFO] [pipeline_node] [sink]   value=0.0000
                 [INFO] [pipeline_node] [sink]   value=0.0998
                 ...

    [deactivate] data flow:        ticks dropped; subscription gated; topics retained

    [reactivate] data flow:        resumes; sequence continues from last counter value

    [cleanup]    ros2 topic list:  /pipeline/raw disappears
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

_TOPIC = "/pipeline/raw"
_PERIOD = 1.0


class SinePublisher(LifecyclePublisherComponent[Float64]):
    """Publishes a sine-wave sequence on ``/pipeline/raw``."""

    def __init__(self) -> None:
        super().__init__(name="source", topic_name=_TOPIC, msg_type=Float64)
        self._sequence: int = 0

    def emit_next(self) -> None:
        """Publish one sine sample and advance the sequence counter."""
        msg = Float64()
        msg.data = math.sin(self._sequence * 0.1)
        self._sequence += 1
        self.publish(msg)


class SineTimer(LifecycleTimerComponent):
    """Drives ``SinePublisher`` at 1 Hz while active."""

    def __init__(self, publisher: SinePublisher) -> None:
        super().__init__(name="timer", period=_PERIOD)
        self._publisher = publisher

    def on_tick(self) -> None:
        self._publisher.emit_next()


class LoggingSink(LifecycleSubscriberComponent[Float64]):
    """Logs values received on ``/pipeline/raw``."""

    def __init__(self) -> None:
        super().__init__(name="sink", topic_name=_TOPIC, msg_type=Float64)

    def on_message(self, msg: Float64) -> None:
        self.node.get_logger().info(f"[{self.name}] value={msg.data:.4f}")


class PipelineNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("pipeline_node")
        publisher = SinePublisher()
        self.add_component(publisher)
        self.add_component(SineTimer(publisher))
        self.add_component(LoggingSink())


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init()

    node = PipelineNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        node.get_logger().info("Pipeline node ready — configure and activate to start the pipeline")
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
