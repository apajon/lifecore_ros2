from __future__ import annotations

from abc import ABC

from rclpy.callback_groups import CallbackGroup
from rclpy.qos import QoSProfile

from lifecore_ros2.core._iface_type import _resolve_iface_type
from lifecore_ros2.core.lifecycle_component import LifecycleComponent


class ServiceComponent[SrvT](LifecycleComponent, ABC):
    """Intermediate base class for lifecycle-aware service server and client components.

    Owns:
        - The service name, service type, and QoS profile shared by server and client subclasses.

    Does not own:
        - The ROS ``Service`` or ``Client`` objects — those belong to concrete subclasses.
        - Any lifecycle hook logic — concrete subclasses provide ``_on_configure``,
          ``_on_cleanup``, and ``_release_resources`` implementations.
        - The callback group — it is borrowed from the application and forwarded to the core.

    Override points:
        - Not intended to be subclassed directly outside the framework.
        - Subclass ``LifecycleServiceServerComponent`` or ``LifecycleServiceClientComponent`` instead.
    """

    def __init__(
        self,
        name: str,
        service_name: str,
        srv_type: type[SrvT] | None = None,
        *,
        qos_profile: QoSProfile | None = None,
        callback_group: CallbackGroup | None = None,
    ) -> None:
        """Initialize the service component.

        Args:
            name: Unique name for this component within the node.
            service_name: ROS service name used by the server or client subclass.
            srv_type: ROS service type. Optional when the concrete subclass parameterizes
                the generic base (e.g. ``LifecycleServiceServerComponent[MySrv]``); in that
                case the type is inferred from the generic argument. Must be supplied when
                the generic base is not parameterized. If both are supplied, they must agree.
            qos_profile: QoS profile for the service. ``None`` lets rclpy select
                ``qos_profile_services_default`` (the standard service default).
            callback_group: Optional CallbackGroup borrowed from the application and
                forwarded to the underlying service or client. Lifetime is owned by the
                caller; the component never destroys it. ``None`` selects the node default
                group.

        Raises:
            TypeError: if ``srv_type`` cannot be resolved (neither passed nor inferred
                from the generic parameter), or if the explicit value conflicts with the
                inferred one.
        """
        super().__init__(name=name, callback_group=callback_group)
        self._service_name = service_name
        self._srv_type: type[SrvT] = _resolve_iface_type(
            type(self),
            base=ServiceComponent,
            explicit=srv_type,
            interface_kind="srv_type",
        )
        self._qos_profile = qos_profile

    @property
    def service_name(self) -> str:
        return self._service_name

    @property
    def srv_type(self) -> type[SrvT]:
        return self._srv_type

    @property
    def qos_profile(self) -> QoSProfile | None:
        return self._qos_profile
