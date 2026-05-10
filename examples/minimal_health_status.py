"""Demonstrates how ``LifecycleComponent.health`` reflects lifecycle transitions in real time.

Single idea: a watchdog can read ``node.health`` or individual ``component.health``
to observe the worst-case state without accessing component internals.

Two components are registered:

- ``sensor`` — activate hook returns ``FAILURE`` (→ ``DEGRADED``); cleanup hook raises
  a ``RuntimeError`` so ``last_error`` is populated (→ ``ERROR``).
- ``heartbeat`` — always succeeds; shows the ``OK`` → ``UNKNOWN`` path via cleanup.

Registration order places ``sensor`` before ``heartbeat``.  Activate propagates forward
(sensor first), so propagation stops at ``sensor`` before ``heartbeat`` is reached.
Cleanup propagates in reverse (heartbeat first), so ``heartbeat`` resets to ``UNKNOWN``
before ``sensor`` raises.

Drive it::

    ros2 lifecycle set /health_status_demo_node configure
    ros2 lifecycle set /health_status_demo_node activate
    ros2 lifecycle set /health_status_demo_node cleanup
    ros2 lifecycle set /health_status_demo_node shutdown

Expected output::

    [startup]    sensor.health=unknown  heartbeat.health=unknown  node.health=unknown

    [configure]  [INFO] [health_status_demo_node] [configure] sensor.health=ok  last_error=None
                 [INFO] [health_status_demo_node] [configure] heartbeat.health=ok  last_error=None
                 [INFO] [health_status_demo_node] [configure] node.health=ok

    [activate]   [INFO] [health_status_demo_node] [activate] sensor.health=degraded  last_error=None
                 [INFO] [health_status_demo_node] [activate] heartbeat.health=ok  last_error=None
                 [INFO] [health_status_demo_node] [activate] node.health=degraded

    [cleanup]    [INFO] [health_status_demo_node] [cleanup] sensor.health=error
                         last_error=[sensor.on_cleanup] raised RuntimeError: simulated hardware fault
                 [INFO] [health_status_demo_node] [cleanup] heartbeat.health=unknown  last_error=None
                 [INFO] [health_status_demo_node] [cleanup] node.health=error
"""

from __future__ import annotations

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn

from lifecore_ros2.core import LifecycleComponent, LifecycleComponentNode


class SensorComponent(LifecycleComponent):
    """Simulates a sensor that activates with degraded performance and faults on cleanup.

    Deliberately returns ``FAILURE`` from ``_on_activate`` to demonstrate ``DEGRADED``
    health and node-level worst-of aggregation.  Raises in ``_on_cleanup`` to demonstrate
    that uncaught hook exceptions set ``health.level`` to ``ERROR`` and populate
    ``health.last_error`` with the hook name and exception message.
    """

    def __init__(self) -> None:
        super().__init__("sensor")

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.node.get_logger().info(f"[{self.name}] configured")
        return TransitionCallbackReturn.SUCCESS

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.node.get_logger().info(f"[{self.name}] activate returning FAILURE — health will be DEGRADED")
        return TransitionCallbackReturn.FAILURE

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        raise RuntimeError("simulated hardware fault")


class HeartbeatComponent(LifecycleComponent):
    """Always-healthy component; shows the OK → UNKNOWN reset path through cleanup."""

    def __init__(self) -> None:
        super().__init__("heartbeat")

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.node.get_logger().info(f"[{self.name}] configured")
        return TransitionCallbackReturn.SUCCESS

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.node.get_logger().info(f"[{self.name}] cleaned up — health will reset to UNKNOWN")
        return TransitionCallbackReturn.SUCCESS


class HealthStatusDemoNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("health_status_demo_node")
        self._sensor = SensorComponent()
        self._heartbeat = HeartbeatComponent()
        # sensor registered first: activate propagation stops at sensor (forward),
        # cleanup starts at heartbeat (reverse).
        self.add_component(self._sensor)
        self.add_component(self._heartbeat)

    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        result = super().on_configure(state)
        self._log_health("configure")
        return result

    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        result = super().on_activate(state)
        self._log_health("activate")
        return result

    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        result = super().on_cleanup(state)
        self._log_health("cleanup")
        return result

    def _log_health(self, stage: str) -> None:
        log = self.get_logger()
        sensor = self._sensor.health
        heartbeat = self._heartbeat.health
        log.info(f"[{stage}] sensor.health={sensor.level.value}  last_error={sensor.last_error}")
        log.info(f"[{stage}] heartbeat.health={heartbeat.level.value}  last_error={heartbeat.last_error}")
        log.info(f"[{stage}] node.health={self.health.level.value}")


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init(args=["--ros-args", "--log-level", "health_status_demo_node:=debug"])

    node = HealthStatusDemoNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    sensor = node._sensor.health  # noqa: SLF001
    heartbeat = node._heartbeat.health  # noqa: SLF001
    node.get_logger().info(
        f"Health status demo ready — "
        f"sensor.health={sensor.level.value}  heartbeat.health={heartbeat.level.value}  "
        f"node.health={node.health.level.value}"
    )

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
