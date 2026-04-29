"""Demonstrates a ``LifecycleServiceClientComponent`` with activation-gated outbound calls.

Single idea: the ROS client is created by the framework in ``_on_configure``; ``call()`` and
``call_async()`` raise ``RuntimeError`` while the component is inactive.  The node exposes a
``trigger()`` helper that drives an outbound Trigger call once active.

Drive it::

    ros2 lifecycle set /service_client_node configure
    ros2 lifecycle set /service_client_node activate
    # Node calls /trigger automatically; a server (e.g. minimal_service_server) must be running
    ros2 lifecycle set /service_client_node deactivate

Expected output::

    [before configure]
                 ros2 service list:  no /trigger client registered by this node

    [configure]  [INFO] [trigger_client] client created for '/trigger'
                 ros2 service list:  /trigger client appears

    [activate]   (no component log — base _on_activate returns SUCCESS silently)
                 node:               trigger() is safe to call; raises RuntimeError if called before this point

    [trigger()]  [INFO] Trigger response: success=True, message='ok'  (if server is available)
                 or raises TimeoutError if server is not available within 2.0 s

    [deactivate] (no component log — base _on_deactivate returns SUCCESS silently)
                 trigger():          raises RuntimeError (component inactive)

    [cleanup]    client destroyed implicitly via _release_resources
                 ros2 service list:  /trigger client disappears

    [shutdown]   same teardown as cleanup; node disappears from ros2 node list
"""

from __future__ import annotations

from std_srvs.srv import Trigger

from lifecore_ros2 import LifecycleComponentNode, LifecycleServiceClientComponent


class ServiceClientNode(LifecycleComponentNode):
    """Minimal application node that hosts a single lifecycle-gated Trigger client.

    The ``trigger()`` method is safe to call only while the node is active; calling it
    before ``activate`` (or after ``deactivate``) raises ``RuntimeError``.
    """

    def __init__(self) -> None:
        super().__init__("service_client_node")
        self._client: LifecycleServiceClientComponent[Trigger] = LifecycleServiceClientComponent(
            name="trigger_client",
            service_name="/trigger",
            srv_type=Trigger,
        )
        self.add_component(self._client)

    def trigger(self) -> None:
        """Call the /trigger service and log the response.

        Raises:
            RuntimeError: if the component is not active.
            TimeoutError: if the service is not available within 2.0 seconds.
        """
        response: Trigger.Response = self._client.call(Trigger.Request(), timeout_service=2.0)
        self.get_logger().info(f"Trigger response: success={response.success}, message='{response.message}'")


def main() -> None:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init(args=["--ros-args", "--log-level", "service_client_node:=debug"])

    node = ServiceClientNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        node.get_logger().info("Service client node ready (configure + activate, then call node.trigger())")
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
