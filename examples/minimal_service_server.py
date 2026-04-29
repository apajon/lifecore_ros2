"""Demonstrates a ``LifecycleServiceServerComponent`` with activation-gated request handling.

Single idea: the ROS service is created by the framework in ``_on_configure``; requests are handled
by ``on_service_request`` only while the component is active.  When inactive, the framework logs a
warning and returns a default response with ``success=False``.

Drive it::

    ros2 lifecycle set /service_server_node configure
    ros2 lifecycle set /service_server_node activate
    # In a separate terminal: ros2 service call /trigger std_srvs/srv/Trigger
    ros2 lifecycle set /service_server_node deactivate

Expected output::

    [before configure]
                 ros2 service list:  /trigger not present

    [configure]  [INFO] [trigger_server] service created on '/trigger'
                 ros2 service list:  /trigger appears  (service created by framework)
                 requests:           returned with success=False, message='component inactive'

    [activate]   (no component log — base _on_activate returns SUCCESS silently)
                 requests:           on_service_request handles; responds success=True, message='ok'

    [message]    [INFO] [trigger_server] received request  (once per call, while active)

    [deactivate] (no component log — base _on_deactivate returns SUCCESS silently)
                 requests:           [WARN] [trigger_server] request received while inactive on '/trigger'; returning default response

    [cleanup]    [INFO] [trigger_server] service destroyed  (implicit, via _release_resources)
                 ros2 service list:  /trigger disappears

    [shutdown]   same teardown as cleanup; node disappears from ros2 node list
"""

from __future__ import annotations

from typing import Any

from std_srvs.srv import Trigger

from lifecore_ros2 import LifecycleComponentNode, LifecycleServiceServerComponent


class TriggerServer(LifecycleServiceServerComponent[Trigger]):
    """Handles Trigger service calls on /trigger while active."""

    def __init__(self) -> None:
        super().__init__(
            name="trigger_server",
            service_name="/trigger",
            srv_type=Trigger,
        )

    def on_service_request(self, request: Any, response: Any) -> Any:
        """Respond to a Trigger call with success while the component is active.

        Args:
            request: The incoming ``Trigger.Request`` (empty).
            response: A default-constructed ``Trigger.Response`` to fill in.

        Returns:
            The filled-in response with ``success=True`` and ``message='ok'``.
        """
        self.node.get_logger().info(f"[{self.name}] received request")
        response.success = True
        response.message = "ok"
        return response


class ServiceServerNode(LifecycleComponentNode):
    """Minimal application node that hosts a single lifecycle-gated Trigger server."""

    def __init__(self) -> None:
        super().__init__("service_server_node")
        self.add_component(TriggerServer())


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init(args=["--ros-args", "--log-level", "service_server_node:=debug"])

    node = ServiceServerNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        node.get_logger().info("Service server node ready (configure + activate to serve /trigger)")
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
