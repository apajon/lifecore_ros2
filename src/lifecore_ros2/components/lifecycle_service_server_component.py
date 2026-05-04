from __future__ import annotations

from abc import abstractmethod
from collections.abc import Sequence
from typing import Any, final

from rclpy.callback_groups import CallbackGroup
from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.qos import QoSProfile
from rclpy.service import Service

from .service_component import ServiceComponent


class LifecycleServiceServerComponent[SrvT](ServiceComponent[SrvT]):
    """Service server component that creates a ROS service and gates request handling through the lifecycle.

    The service is created on configure and destroyed automatically on cleanup.
    Incoming requests while the component is inactive are not silently dropped:
    a warning is logged and a default-constructed response is returned, optionally
    annotated with diagnostic fields (``success=False``, ``message="component inactive"``).

    Owns:
        - The ROS ``Service`` instance (created on configure, released automatically on cleanup).
        - ``_on_request_wrapper``: the framework-internal callback registered with rclpy.

    Does not own:
        - The service name, service type, or QoS profile (inherited from ``ServiceComponent``).
        - The callback group — it is borrowed from the application; lifetime is owned by the caller.
        - The node or lifecycle state transitions.
        - Activation state management (handled by the framework).

    Override points:
        - ``on_service_request``: implement to handle incoming requests while active.
        - Override ``_on_configure`` only for additional setup; call ``super()._on_configure(state)`` first.
        - Do not override ``_on_request_wrapper``.
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
        """Initialize the lifecycle service server component.

        Args:
            name: Unique name for this component within the node.
            service_name: ROS service name to serve.
            srv_type: ROS service type. Optional when the concrete subclass parameterizes
                the generic base (e.g. ``LifecycleServiceServerComponent[MySrv]``); see
                :class:`~lifecore_ros2.components.service_component.ServiceComponent`
                for resolution rules.
            qos_profile: QoS profile for the service. ``None`` selects
                ``qos_profile_services_default``.
            callback_group: Optional CallbackGroup borrowed from the application and
                forwarded to ``create_service`` on configure. Lifetime is owned by the
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
        self._service: Service | None = None  # type: ignore[type-arg]  # rclpy Service is not generic

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Extension point. Calls super if overridden; creates the ROS service.

        Override in subclasses for additional setup. Call ``super()._on_configure(state)`` first.
        """
        kwargs: dict[str, Any] = {"callback_group": self._callback_group}
        if self.qos_profile is not None:
            kwargs["qos_profile"] = self.qos_profile
        self._service = self.node.create_service(
            self.srv_type,
            self.service_name,
            self._on_request_wrapper,
            **kwargs,
        )
        self.node.get_logger().info(f"[{self.name}] service created on '{self.service_name}'")
        return TransitionCallbackReturn.SUCCESS

    @final
    def _on_request_wrapper(self, request: Any, response: Any) -> Any:
        """Framework-internal. Do not call from user code.

        Handles the rclpy ``(request, response) -> response`` callback contract.
        While inactive: logs a warning and returns a default-constructed response
        with diagnostic annotations if supported. While active: delegates to
        ``on_service_request`` and never propagates exceptions into the rclpy executor.
        """
        if not self._is_active:
            self._resolve_logger().warning(
                f"[{self._name}] request received while inactive on '{self._service_name}'; returning default response"
            )
            # Annotate the default response with diagnostic fields when available.
            if hasattr(response, "success") and isinstance(response.success, bool):
                response.success = False
            if hasattr(response, "message") and isinstance(response.message, str):
                response.message = "component inactive"
            return response

        try:
            result = self.on_service_request(request, response)
            # on_service_request follows rclpy convention: fill in response and return it.
            return result if result is not None else response
        except Exception as exc:
            # Rule C (inbound): never propagate user exceptions into the rclpy executor.
            self._resolve_logger().error(f"[{self._name}.on_service_request] {type(exc).__name__}: {exc}")
            return response

    @abstractmethod
    def on_service_request(self, request: Any, response: Any) -> Any:
        """Extension point. Implement to handle incoming service requests while active.

        Follows the rclpy service callback convention: fill in ``response`` fields
        and return it. Called only while the component is active.

        Args:
            request: The incoming service request object.
            response: A default-constructed response object to fill in.

        Returns:
            The filled-in response object.
        """
        raise NotImplementedError(
            "on_service_request must be implemented by LifecycleServiceServerComponent subclasses"
        )

    def _release_resources(self) -> None:
        """Extension point. Override to release additional resources; call ``super()._release_resources()`` last."""
        if self._service is not None:
            self.node.destroy_service(self._service)
            self._service = None
        super()._release_resources()
