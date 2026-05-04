from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from rclpy.callback_groups import CallbackGroup
from rclpy.client import Client
from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.qos import QoSProfile
from rclpy.task import Future

from lifecore_ros2.core.exceptions import ComponentNotConfiguredError
from lifecore_ros2.core.lifecycle_component import when_active

from .service_component import ServiceComponent


class LifecycleServiceClientComponent[SrvT](ServiceComponent[SrvT]):
    """Service client component that creates a ROS client and gates calls through the lifecycle.

    The client is created on configure and destroyed automatically on cleanup.
    Outbound calls (``call``, ``call_async``, ``wait_for_service``) raise ``RuntimeError``
    while the component is inactive.

    Note:
        Futures from ``call_async`` are not cancelled on deactivate; the application owns them.

    Owns:
        - The ROS ``Client`` instance (created on configure, released automatically on cleanup).

    Does not own:
        - The service name, service type, or QoS profile (inherited from ``ServiceComponent``).
        - The callback group — it is borrowed from the application; lifetime is owned by the caller.
        - The node or lifecycle state transitions.
        - Activation state management (handled by the framework).

    Override points:
        - This class is usable directly without subclassing.
        - Override ``_on_configure`` for additional setup; call ``super()._on_configure(state)`` first.
        - Do not override ``call``, ``call_async``, or ``wait_for_service``.
    """

    def __init__(
        self,
        name: str,
        service_name: str,
        srv_type: type[SrvT] | None = None,
        *,
        qos_profile: QoSProfile | None = None,
        callback_group: CallbackGroup | None = None,
        dependencies: Sequence[str] = (),
        priority: int = 0,
    ) -> None:
        """Initialize the lifecycle service client component.

        Args:
            name: Unique name for this component within the node.
            service_name: ROS service name to call.
            srv_type: ROS service type. Optional when the concrete subclass parameterizes
                the generic base (e.g. ``LifecycleServiceClientComponent[MySrv]``); see
                :class:`~lifecore_ros2.components.service_component.ServiceComponent`
                for resolution rules.
            qos_profile: QoS profile for the client. ``None`` selects
                ``qos_profile_services_default``.
            callback_group: Optional CallbackGroup borrowed from the application and
                forwarded to ``create_client`` on configure. Lifetime is owned by the
                caller; the component never destroys it. ``None`` selects the node
                default group.
            dependencies: Names of other components that must be transitioned before
                this one. Forwarded to ``LifecycleComponent``.
            priority: Tie-breaking ordering hint when dependencies do not impose a
                strict order. Forwarded to ``LifecycleComponent``.
        """
        super().__init__(
            name=name,
            service_name=service_name,
            srv_type=srv_type,
            qos_profile=qos_profile,
            callback_group=callback_group,
            dependencies=dependencies,
            priority=priority,
        )
        self._client: Client | None = None  # type: ignore[type-arg]  # rclpy Client is not generic

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Extension point. Calls super if overridden; creates the ROS client.

        Override in subclasses for additional setup. Call ``super()._on_configure(state)`` first.
        """
        kwargs: dict[str, Any] = {"callback_group": self._callback_group}
        if self.qos_profile is not None:
            kwargs["qos_profile"] = self.qos_profile
        self._client = self.node.create_client(self.srv_type, self.service_name, **kwargs)
        self.node.get_logger().info(f"[{self.name}] client created for '{self.service_name}'")
        return TransitionCallbackReturn.SUCCESS

    @when_active
    def call(self, request: Any, timeout_service: float | None = None, timeout_call: float | None = None) -> Any:
        """Call the service synchronously. Raises ``RuntimeError`` if not active.

        Args:
            request: The service request object.
            timeout_service: Optional timeout in seconds to wait for the service to become
                available before sending the request. Raises ``TimeoutError`` if the service
                does not become available in time.
            timeout_call: Optional timeout in seconds for the synchronous call itself.
                ``None`` waits indefinitely for the response.

        Returns:
            The service response object.

        Raises:
            RuntimeError: if the component is not active.
            ComponentNotConfiguredError: if the component has not been configured.
            TimeoutError: if ``timeout_service`` is specified and the service is not available.
        """
        if self._client is None:
            raise ComponentNotConfiguredError(f"Client '{self.name}' is not configured")
        if timeout_service is not None and not self._client.wait_for_service(timeout_sec=timeout_service):
            raise TimeoutError(f"[{self.name}] service '{self.service_name}' not available after {timeout_service}s")
        return self._client.call(request, timeout_sec=timeout_call)

    @when_active
    def call_async(self, request: Any, timeout_service: float | None = None) -> Future:  # type: ignore[type-arg]  # rclpy Future is not generic
        """Call the service asynchronously. Raises ``RuntimeError`` if not active.

        Note:
            Futures are not cancelled on deactivate; the application owns them.

        Args:
            request: The service request object.
            timeout_service: Optional timeout in seconds to wait for the service to become
                available before submitting the request. Raises ``TimeoutError`` if the
                service does not become available in time.

        Returns:
            A ``Future`` that resolves to the service response.

        Raises:
            RuntimeError: if the component is not active.
            ComponentNotConfiguredError: if the component has not been configured.
            TimeoutError: if ``timeout_service`` is specified and the service is not available.
        """
        if self._client is None:
            raise ComponentNotConfiguredError(f"Client '{self.name}' is not configured")
        if timeout_service is not None and not self._client.wait_for_service(timeout_sec=timeout_service):
            raise TimeoutError(f"[{self.name}] service '{self.service_name}' not available after {timeout_service}s")
        return self._client.call_async(request)

    @when_active
    def wait_for_service(self, timeout: float | None = None) -> bool:
        """Wait for the service to become available. Raises ``RuntimeError`` if not active.

        Args:
            timeout: Optional timeout in seconds. ``None`` waits indefinitely.

        Returns:
            ``True`` if the service is available; ``False`` if the timeout elapsed.

        Raises:
            RuntimeError: if the component is not active.
            ComponentNotConfiguredError: if the component has not been configured.
        """
        if self._client is None:
            raise ComponentNotConfiguredError(f"Client '{self.name}' is not configured")
        return self._client.wait_for_service(timeout_sec=timeout)

    def _release_resources(self) -> None:
        """Extension point. Override to release additional resources; call ``super()._release_resources()`` last."""
        if self._client is not None:
            self.node.destroy_client(self._client)
            self._client = None
        super()._release_resources()
