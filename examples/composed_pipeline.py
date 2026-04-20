"""Demonstrates lifecycle composition with three sibling components inside one node.

Single idea: a source, a relay, and a sink compose inside one ``LifecycleComponentNode``.
All three transition together; data flow is fully gated by activation state.

The relay (``MovingAverageRelay``) extends ``LifecycleComponent`` directly, owning both a
raw ROS subscription and a raw ROS publisher.  This makes explicit what the framework's
pre-built topic components do internally — and shows that any pair of ROS resources can
live together in a single component.

Topology::

    SineSource  ──/pipeline/raw──►  MovingAverageRelay  ──/pipeline/avg──►  LoggingSink

Drive it::

    ros2 lifecycle set /pipeline_node configure
    ros2 lifecycle set /pipeline_node activate
    # Observe averaged values: ros2 topic echo /pipeline/avg
    ros2 lifecycle set /pipeline_node deactivate
    ros2 lifecycle set /pipeline_node activate   # resumes from an empty window
    ros2 lifecycle set /pipeline_node cleanup

Expected output per transition::

    [before configure]
                 ros2 topic list:  /pipeline/raw and /pipeline/avg not present

    [configure]  [INFO] [pipeline_node] [source] publisher created on '/pipeline/raw'
                 [INFO] [pipeline_node] [relay]  subscription on '/pipeline/raw', publisher on '/pipeline/avg'
                 [INFO] [pipeline_node] [sink]   subscription created on '/pipeline/avg'
                 ros2 topic list:  /pipeline/raw and /pipeline/avg now present
                 data flow:        none  (source timer not started; relay callback gated by @when_active)

    [activate]   [INFO] [pipeline_node] [source] sampling started
                 (relay and sink have no activate log — base _on_activate returns SUCCESS silently)
                 data flow:        /pipeline/raw at 1 Hz → relay 5-sample window → /pipeline/avg

    [while active]
                 [INFO] [pipeline_node] [sink]   avg=<value>  (once per sample at 1 Hz; builds toward steady state)

    [deactivate] [INFO] [pipeline_node] [source] sampling paused
                 [INFO] [pipeline_node] [relay]  moving-average buffer cleared
                 ros2 topic list:  /pipeline/raw and /pipeline/avg still present  (resources retained)
                 data flow:        stopped; any residual relay messages silently dropped

    [reactivate] [INFO] [pipeline_node] [source] sampling started
                 data flow:        resumes from an empty window; average builds from scratch

    [cleanup]    [INFO] [pipeline_node] [relay]  subscription and publisher released
                 ros2 topic list:  /pipeline/raw and /pipeline/avg disappear
                 (source and sink ROS resources released automatically by the framework)

    [shutdown]   same teardown as cleanup; node disappears from ros2 node list
"""

from __future__ import annotations

import math
from collections import deque

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.publisher import Publisher
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.subscription import Subscription
from rclpy.timer import Timer
from std_msgs.msg import Float64

from lifecore_ros2 import (
    LifecycleComponent,
    LifecycleComponentNode,
    LifecyclePublisherComponent,
    LifecycleSubscriberComponent,
    when_active,
)

_SOURCE_TOPIC = "/pipeline/raw"
_AVG_TOPIC = "/pipeline/avg"
_PIPELINE_QOS = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
_SAMPLE_PERIOD = 1.0  # seconds between source emissions
_WINDOW_SIZE = 5  # number of samples in the moving-average window


class SineSource(LifecyclePublisherComponent[Float64]):
    """Emits a sine-wave sequence on ``/pipeline/raw`` at 1 Hz while active.

    Uses ``LifecyclePublisherComponent``: the ROS publisher is created by the framework
    on configure; the timer (runtime behavior) is created on activate only.
    """

    def __init__(self) -> None:
        super().__init__(
            name="source",
            topic_name=_SOURCE_TOPIC,
            msg_type=Float64,
            qos_profile=_PIPELINE_QOS,
        )
        self._timer: Timer | None = None
        self._sequence: int = 0

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        # why: timer is runtime behavior — created here (not in _on_configure)
        # so sampling only runs while active.
        self._timer = self.node.create_timer(_SAMPLE_PERIOD, self._emit)
        self.node.get_logger().info(f"[{self.name}] sampling started")
        return TransitionCallbackReturn.SUCCESS

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        if self._timer is not None:
            self._timer.cancel()
            self.node.destroy_timer(self._timer)
            self._timer = None
        self.node.get_logger().info(f"[{self.name}] sampling paused")
        return TransitionCallbackReturn.SUCCESS

    def _emit(self) -> None:
        msg = Float64()
        msg.data = math.sin(self._sequence * 0.1)
        self._sequence += 1
        self.publish(msg)  # @when_active gating inherited from LifecyclePublisherComponent


class MovingAverageRelay(LifecycleComponent):
    """Subscribes to ``/pipeline/raw``, computes a windowed average, publishes on ``/pipeline/avg``.

    Owns both a raw ROS subscription and a raw ROS publisher.  Extends ``LifecycleComponent``
    directly — no pre-built topic component — to illustrate how any pair of ROS resources
    can live together inside one component.

    The moving-average buffer is cleared on deactivate so that reactivation always starts
    from an empty window.  This follows the lifecycle contract: deactivate suspends behavior
    without preserving stale intermediate state into the next active period.
    """

    def __init__(self) -> None:
        super().__init__(name="relay")
        self._subscription: Subscription | None = None  # type: ignore[type-arg]  # rclpy Subscription is not generic
        self._publisher: Publisher | None = None  # type: ignore[type-arg]  # rclpy Publisher is not generic
        self._buffer: deque[float] = deque(maxlen=_WINDOW_SIZE)

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Extension point. Creates both the subscription and publisher on configure."""
        self._subscription = self.node.create_subscription(
            Float64,
            _SOURCE_TOPIC,
            self._relay_message,
            _PIPELINE_QOS,
        )
        self._publisher = self.node.create_publisher(Float64, _AVG_TOPIC, _PIPELINE_QOS)
        self.node.get_logger().info(f"[{self.name}] subscription on '{_SOURCE_TOPIC}', publisher on '{_AVG_TOPIC}'")
        return TransitionCallbackReturn.SUCCESS

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        # why: clearing the buffer on deactivate matches "deactivate suspends behavior";
        # stale samples from a previous active window would silently bias the first average
        # after reactivation.
        self._buffer.clear()
        self.node.get_logger().info(f"[{self.name}] moving-average buffer cleared")
        return TransitionCallbackReturn.SUCCESS

    @when_active(when_not_active=None)
    def _relay_message(self, msg: Float64) -> None:
        """Subscription callback; silently dropped while inactive via ``@when_active``."""
        self._buffer.append(msg.data)
        avg = sum(self._buffer) / len(self._buffer)
        out = Float64()
        out.data = avg
        if self._publisher is not None:
            self._publisher.publish(out)  # type: ignore[arg-type]  # rclpy Publisher.publish accepts Any

    def _release_resources(self) -> None:
        """Extension point. Releases subscription and publisher; call ``super()._release_resources()`` last."""
        if self._subscription is not None:
            self.node.destroy_subscription(self._subscription)
            self._subscription = None
        if self._publisher is not None:
            self.node.destroy_publisher(self._publisher)
            self._publisher = None
        self._buffer.clear()
        self.node.get_logger().info(f"[{self.name}] subscription and publisher released")
        super()._release_resources()


class LoggingSink(LifecycleSubscriberComponent[Float64]):
    """Logs averaged values received on ``/pipeline/avg`` while active."""

    def __init__(self) -> None:
        super().__init__(
            name="sink",
            topic_name=_AVG_TOPIC,
            msg_type=Float64,
            qos_profile=_PIPELINE_QOS,
        )

    def on_message(self, msg: Float64) -> None:
        """Log each averaged value received from the relay."""
        self.node.get_logger().info(f"[{self.name}] avg={msg.data:.4f}")


class PipelineNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("pipeline_node")
        self.add_component(SineSource())
        self.add_component(MovingAverageRelay())
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
