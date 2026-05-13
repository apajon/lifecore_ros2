"""Demonstrates ``LifecycleParameterObserverComponent`` for lifecycle-aware remote parameter observation.

Single idea: one node observes a parameter owned by a second node.

- ``/publisher_node`` owns ``rate`` (a float) as a regular ROS 2 parameter.
- ``ObserverNode`` registers a watch on ``/publisher_node rate`` before configure.
- During configure, the observer tries to read the initial value. If the remote
  node is not yet present, the watch records ``WatchState.UNKNOWN_NODE`` — configure
  still succeeds.
- While active, live ``/parameter_events`` updates are received and a callback logs
  each change.

The observer never declares, validates, or rejects remote parameters. It only
records what the remote node already accepted.

Drive it (two separate terminals)::

    # Terminal 1 — start the publisher node (owns the parameter):
    ros2 run demo_nodes_py parameter_blackboard

    # Terminal 2 — start the observer demo:
    python examples/minimal_parameter_observer.py
    # Then trigger lifecycle transitions:
    ros2 lifecycle set /observer_demo_node configure
    ros2 lifecycle set /observer_demo_node activate

    # Change the remote parameter and observe the callback log:
    ros2 param set /parameter_blackboard rate 20.0

    ros2 lifecycle set /observer_demo_node deactivate
    # Changes while inactive: snapshot is updated, callback does not fire.
    ros2 param set /parameter_blackboard rate 5.0

    ros2 lifecycle set /observer_demo_node activate
    # callback fires again for subsequent changes:
    ros2 param set /parameter_blackboard rate 30.0

    ros2 lifecycle set /observer_demo_node cleanup
    ros2 lifecycle set /observer_demo_node configure

Expected output::

    [configure]  [INFO] observer: initial '/parameter_blackboard/rate': value_available -> 10.0
                 (or 'unknown_node' when the remote node is absent — configure still succeeds)

    [activate]   [INFO] observer: observed '/parameter_blackboard/rate' changed
                         previous=10.0  new=20.0  source=parameter_event

    [deactivate] snapshot silently updated; callback not fired

    [reconfigure] subscription re-created; initial read retried
"""

from __future__ import annotations

from lifecore_ros2 import LifecycleComponentNode, LifecycleParameterObserverComponent
from lifecore_ros2.components.lifecycle_parameter_observer_component import ObservedParameterEvent


class RateObserver(LifecycleParameterObserverComponent):
    """Observes the ``rate`` parameter on ``/parameter_blackboard``.

    Logs every observed change while active.
    """

    def __init__(self) -> None:
        super().__init__("observer")
        self.watch_parameter(
            node_name="/parameter_blackboard",
            parameter_name="rate",
            read_initial=True,
            callback=self._on_rate_changed,
        )

    def _on_rate_changed(self, event: ObservedParameterEvent) -> None:
        self.node.get_logger().info(
            f"[{self.name}] observed '{event.node_name}/{event.parameter_name}' changed"
            f"  previous={event.previous_value!r}  new={event.value!r}  source={event.source}"
        )


class ObserverDemoNode(LifecycleComponentNode):
    def __init__(self) -> None:
        super().__init__("observer_demo_node")
        self.add_component(RateObserver())


def main() -> None:
    import rclpy
    from rclpy.executors import MultiThreadedExecutor

    rclpy.init()

    node = ObserverDemoNode()
    # MultiThreadedExecutor is recommended: _read_initial_parameter blocks the
    # lifecycle transition thread while waiting for the remote parameter service.
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        node.get_logger().info(
            "Observer demo node ready — trigger lifecycle transitions to observe remote parameter gating"
        )
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
