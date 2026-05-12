"""Demonstrates ``LifecycleParameterComponent`` for lifecycle-aware parameter ownership.

Single idea: a node owns two parameters through a ``LifecycleParameterComponent``.

- ``sensor_params.gain`` — ``ACTIVE`` mutability: runtime writes are accepted only while
  the component is active. The validation hook rejects non-positive values.
- ``sensor_params.mode`` — ``STATIC`` mutability: declared at configure and frozen
  for the duration of the node's lifetime.

Parameter definitions (registered before configure) persist across cleanup/reconfigure
cycles. The ROS 2 parameters themselves are declared on the node during configure and
are NOT undeclared during cleanup — a subsequent configure reuses the existing values.

Drive it::

    ros2 lifecycle set /parameter_demo_node configure
    ros2 lifecycle set /parameter_demo_node activate

    # Accepted (component is active, value is positive):
    ros2 param set /parameter_demo_node sensor_params.gain 5.0
    #   -> [INFO] sensor_params: gain updated -> 5.0

    # Rejected (component is active, value is not positive):
    ros2 param set /parameter_demo_node sensor_params.gain -1.0

    # Rejected (static parameter, never writable at runtime):
    ros2 param set /parameter_demo_node sensor_params.mode raw

    ros2 lifecycle set /parameter_demo_node deactivate

    # Rejected (component is inactive):
    ros2 param set /parameter_demo_node sensor_params.gain 3.0

    ros2 lifecycle set /parameter_demo_node cleanup
    ros2 lifecycle set /parameter_demo_node configure
    # sensor_params.gain and sensor_params.mode are restored from the node's memory.

Expected output::

    [configure]  [INFO] sensor_params: parameter 'sensor_params.gain' declared (default=1.0)
                        [INFO] sensor_params: parameter 'sensor_params.mode' declared (default='filtered')

    [activate]   timer logs the current values every second:
                 [INFO] gain=1.0  mode='filtered'

    [param set sensor_params.gain 5.0]
                 [INFO] sensor_params: gain updated -> 5.0

    [deactivate] [INFO] gain=5.0  mode='filtered'  (final log before timer stops ticking)

    [cleanup]    definitions preserved; runtime values cleared

    [reconfigure]
                 [INFO] sensor_params: using existing parameter 'sensor_params.gain'  (value=5.0 retained)
"""

from __future__ import annotations

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.parameter import Parameter

from lifecore_ros2 import (
    LifecycleComponentNode,
    LifecycleParameterComponent,
    LifecycleTimerComponent,
    ParameterMutability,
)


class SensorParameters(LifecycleParameterComponent):
    """Owns the two tunable parameters for the sensor pipeline.

    ``gain`` is writable while active and must be strictly positive.
    ``mode`` is fixed for the full configure/active/deactivate span.
    """

    def __init__(self) -> None:
        super().__init__("sensor_params")
        self.declare_lifecycle_parameter("gain", 1.0, mutability=ParameterMutability.ACTIVE)
        self.declare_lifecycle_parameter("mode", "filtered", mutability=ParameterMutability.STATIC)

    def validate_parameter_update(self, name: str, old_value: object, new_value: object) -> str | None:
        if name == "gain" and isinstance(new_value, float) and new_value <= 0:
            return f"gain must be positive, got {new_value}"
        return None

    def on_post_set_owned_parameters(self, parameters: list[Parameter]) -> None:
        for parameter in parameters:
            local_name = parameter.name.removeprefix(f"{self.name}.")
            self.node.get_logger().info(f"[{self.name}] {local_name} updated -> {parameter.value}")


class StatusTimer(LifecycleTimerComponent):
    """Logs current parameter values every second while active."""

    def __init__(self, params: SensorParameters) -> None:
        super().__init__(name="status_timer", period=1.0)
        self._params = params

    def on_tick(self) -> None:
        gain = self._params.get_parameter_value("gain")
        mode = self._params.get_parameter_value("mode")
        self.node.get_logger().info(f"gain={gain}  mode={mode!r}")


class ParameterDemoNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("parameter_demo_node")
        params = SensorParameters()
        self.add_component(params, priority=10)
        self.add_component(StatusTimer(params))

    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        result = super().on_configure(state)
        if result == TransitionCallbackReturn.SUCCESS:
            self.get_logger().info("configured — parameters declared on node")
        return result


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init()

    node = ParameterDemoNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        node.get_logger().info("Parameter demo node ready — trigger lifecycle transitions to observe parameter gating")
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
