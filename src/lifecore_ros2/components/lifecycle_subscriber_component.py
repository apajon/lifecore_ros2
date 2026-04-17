from __future__ import annotations

from abc import abstractmethod
from typing import Any

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.qos import QoSProfile
from rclpy.subscription import Subscription

from lifecore_ros2.core.lifecycle_component import when_active

from .topic_component import TopicComponent


class LifecycleSubscriberComponent(TopicComponent):
    """Subscriber component that creates a ROS subscription and gates message delivery through the lifecycle.

    The subscription is created on configure and destroyed automatically on cleanup.
    Incoming messages are silently dropped while the component is inactive,
    and routed to ``on_message`` when active.

    Owns:
        - The ROS ``Subscription`` instance (created on configure, released automatically on cleanup).
        - ``_on_message_wrapper``: the ``@when_active``-gated internal callback.

    Does not own:
        - The topic name, message type, or QoS profile (inherited from ``TopicComponent``).
        - The node or lifecycle state transitions.
        - Activation state management (handled by the framework).

    Override points:
        - ``on_message``: implement to handle incoming messages. Called only while active.
        - Override ``_on_configure`` only for additional setup; call ``super()._on_configure(state)`` first.
        - Do not override ``_on_message_wrapper``.
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
        self._subscription: Subscription | None = None

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._subscription = self.node.create_subscription(
            self.msg_type,
            self.topic_name,
            self._on_message_wrapper,
            self.qos_profile,
        )
        self.node.get_logger().info(f"[{self.name}] subscription created on '{self.topic_name}'")
        return TransitionCallbackReturn.SUCCESS

    @when_active(when_not_active=None)
    def _on_message_wrapper(self, msg: Any) -> None:
        self.on_message(msg)

    @abstractmethod
    def on_message(self, msg: Any) -> None:
        """Handle an incoming message while the component is active."""
        raise NotImplementedError("on_message must be implemented by LifecycleSubscriberComponent subclasses")

    def _release_resources(self) -> None:
        if self._subscription is not None:
            self.node.destroy_subscription(self._subscription)
            self._subscription = None
        super()._release_resources()
