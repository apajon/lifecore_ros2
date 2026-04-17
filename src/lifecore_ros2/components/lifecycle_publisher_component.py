from __future__ import annotations

from typing import Any

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.publisher import Publisher
from rclpy.qos import QoSProfile

from lifecore_ros2.core.lifecycle_component import when_active

from .topic_component import TopicComponent


class LifecyclePublisherComponent(TopicComponent):
    """Publisher component that creates and gates a ROS publisher through the lifecycle.

    Owns:
        - The ROS ``Publisher`` instance (created on configure, released on cleanup).
        - ``publish``: the activation-gated publication method.

    Does not own:
        - The topic name, message type, or QoS profile (inherited from ``TopicComponent``).
        - The node or lifecycle state transitions.

    Override points:
        - This class is usable directly without subclassing.
        - Override ``_on_configure`` for additional setup; call ``super()._on_configure(state)`` first.
        - Override ``_on_cleanup`` for additional teardown; call ``super()._on_cleanup(state)``
          and ``_release_resources()`` explicitly.
        - Do not override ``publish``.
    """

    def __init__(
        self,
        name: str,
        topic_name: str,
        msg_type: type[Any],
        qos_profile: QoSProfile | int = 10,
    ) -> None:
        super().__init__(
            name=name,
            topic_name=topic_name,
            msg_type=msg_type,
            qos_profile=qos_profile,
        )
        self._publisher: Publisher | None = None

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        super()._on_configure(state)

        self._publisher = self.node.create_publisher(
            self.msg_type,
            self.topic_name,
            self.qos_profile,
        )
        self.node.get_logger().info(f"[{self.name}] publisher created on '{self.topic_name}'")
        return TransitionCallbackReturn.SUCCESS

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return super()._on_activate(state)

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return super()._on_deactivate(state)

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        super()._on_cleanup(state)
        self._release_resources()
        return TransitionCallbackReturn.SUCCESS

    @when_active
    def publish(self, msg: Any) -> None:
        """Publish a message. Raises ``RuntimeError`` if not active."""
        if self._publisher is None:
            raise RuntimeError(f"Publisher '{self.name}' is not configured")
        self._publisher.publish(msg)

    def _release_resources(self) -> None:
        if self._publisher is not None:
            self.node.destroy_publisher(self._publisher)
            self._publisher = None
        super()._release_resources()
