from __future__ import annotations

from abc import ABC
from typing import Any

from rclpy.qos import QoSProfile

from lifecore_ros2.core.lifecycle_component import LifecycleComponent


class TopicComponent(LifecycleComponent, ABC):
    """Base class for lifecycle-aware topic components."""

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
