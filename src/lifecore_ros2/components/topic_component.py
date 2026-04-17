from __future__ import annotations

from abc import ABC
from typing import Any

from rclpy.qos import QoSProfile

from lifecore_ros2.core.lifecycle_component import LifecycleComponent


class TopicComponent(LifecycleComponent, ABC):
    """Intermediate base class for lifecycle-aware topic publisher and subscriber components.

    Owns:
        - The topic name, message type, and QoS profile shared by publisher and subscriber subclasses.

    Does not own:
        - The ROS publisher or subscription objects — those belong to concrete subclasses.
        - Any lifecycle hook logic — concrete subclasses provide ``_on_configure``,
          ``_on_cleanup``, and ``_release_resources`` implementations.

    Override points:
        - Not intended to be subclassed directly outside the framework.
        - Subclass ``LifecyclePublisherComponent`` or ``LifecycleSubscriberComponent`` instead.
    """

    def __init__(
        self,
        name: str,
        topic_name: str,
        msg_type: type[Any],
        qos_profile: QoSProfile | int = 10,
    ) -> None:
        super().__init__(name=name)
        self._topic_name = topic_name
        self._msg_type = msg_type
        self._qos_profile = qos_profile

    @property
    def topic_name(self) -> str:
        return self._topic_name

    @property
    def msg_type(self) -> type[Any]:
        return self._msg_type

    @property
    def qos_profile(self) -> QoSProfile | int:
        return self._qos_profile
