from __future__ import annotations

from abc import ABC
from collections.abc import Sequence

from rclpy.callback_groups import CallbackGroup
from rclpy.qos import QoSProfile

from lifecore_ros2.core._iface_type import _resolve_iface_type
from lifecore_ros2.core.lifecycle_component import LifecycleComponent


class TopicComponent[MsgT](LifecycleComponent, ABC):
    """Intermediate base class for lifecycle-aware topic publisher and subscriber components.

    Owns:
        - The topic name, message type, and QoS profile shared by publisher and subscriber subclasses.

    Does not own:
        - The ROS publisher or subscription objects — those belong to concrete subclasses.
        - Any lifecycle hook logic — concrete subclasses provide ``_on_configure``,
          ``_on_cleanup``, and ``_release_resources`` implementations.
        - The callback group — it is borrowed from the application and forwarded to the core.

    Override points:
        - Not intended to be subclassed directly outside the framework.
        - Subclass ``LifecyclePublisherComponent`` or ``LifecycleSubscriberComponent`` instead.
    """

    def __init__(
        self,
        name: str,
        topic_name: str,
        msg_type: type[MsgT] | None = None,
        qos_profile: QoSProfile | int = 10,
        *,
        callback_group: CallbackGroup | None = None,
        dependencies: Sequence[str] = (),
        priority: int = 0,
    ) -> None:
        """Initialize the topic component.

        Args:
            name: Unique name for this component within the node.
            topic_name: ROS topic name used by the publisher or subscriber subclass.
            msg_type: ROS message type for the topic. Optional when the concrete
                subclass parameterizes the generic base (e.g.
                ``LifecycleSubscriberComponent[String]``); in that case the type
                is inferred from the generic argument. Must be supplied when the
                generic base is not parameterized. If both are supplied, they
                must agree.
            qos_profile: QoS profile or depth (default 10).
            callback_group: Optional CallbackGroup borrowed from the application and
                forwarded to the underlying publisher or subscription. Lifetime is owned
                by the caller; the component never destroys it. ``None`` selects the
                node default group.
            dependencies: Names of other components that must be transitioned before
                this one. Forwarded to ``LifecycleComponent``.
            priority: Tie-breaking ordering hint when dependencies do not impose a
                strict order. Forwarded to ``LifecycleComponent``.

        Raises:
            TypeError: if ``msg_type`` cannot be resolved (neither passed nor
                inferred from the generic parameter), or if the explicit value
                conflicts with the inferred one.
        """
        super().__init__(name=name, callback_group=callback_group, dependencies=dependencies, priority=priority)
        self._topic_name = topic_name
        self._msg_type: type[MsgT] = _resolve_iface_type(
            type(self),
            base=TopicComponent,
            explicit=msg_type,
            interface_kind="msg_type",
        )
        self._qos_profile = qos_profile

    @property
    def topic_name(self) -> str:
        return self._topic_name

    @property
    def msg_type(self) -> type[MsgT]:
        return self._msg_type

    @property
    def qos_profile(self) -> QoSProfile | int:
        return self._qos_profile
