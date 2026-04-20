from __future__ import annotations

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.publisher import Publisher
from rclpy.qos import QoSProfile

from lifecore_ros2.core.lifecycle_component import when_active

from .topic_component import TopicComponent


class LifecyclePublisherComponent[MsgT](TopicComponent[MsgT]):
    """Publisher component that creates and gates a ROS publisher through the lifecycle.

    Owns:
        - The ROS ``Publisher`` instance (created on configure, released automatically on cleanup).
        - ``publish``: the activation-gated publication method.

    Does not own:
        - The topic name, message type, or QoS profile (inherited from ``TopicComponent``).
        - The node or lifecycle state transitions.
        - Activation state management (handled by the framework).

    Override points:
        - This class is usable directly without subclassing.
        - Override ``_on_configure`` for additional setup; call ``super()._on_configure(state)`` first.
        - Do not override ``publish``.
    """

    def __init__(
        self,
        name: str,
        topic_name: str,
        msg_type: type[MsgT],
        qos_profile: QoSProfile | int = 10,
    ) -> None:
        super().__init__(
            name=name,
            topic_name=topic_name,
            msg_type=msg_type,
            qos_profile=qos_profile,
        )
        self._publisher: Publisher | None = None  # type: ignore[type-arg]  # rclpy Publisher is not generic

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Extension point. Calls super if overridden; creates the ROS publisher.

        Override in subclasses for additional setup. Call ``super()._on_configure(state)`` first.
        """
        self._publisher = self.node.create_publisher(
            self.msg_type,
            self.topic_name,
            self.qos_profile,
        )
        self.node.get_logger().info(f"[{self.name}] publisher created on '{self.topic_name}'")
        return TransitionCallbackReturn.SUCCESS

    @when_active
    def publish(self, msg: MsgT) -> None:
        """Publish a message. Raises ``RuntimeError`` if not active."""
        if self._publisher is None:
            raise RuntimeError(f"Publisher '{self.name}' is not configured")
        self._publisher.publish(msg)  # type: ignore[arg-type]  # rclpy Publisher.publish accepts Any

    def _release_resources(self) -> None:
        """Extension point. Override to release additional resources; call ``super()._release_resources()`` last."""
        if self._publisher is not None:
            self.node.destroy_publisher(self._publisher)
            self._publisher = None
        super()._release_resources()
