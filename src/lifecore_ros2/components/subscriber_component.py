from __future__ import annotations

from abc import abstractmethod
from typing import Any

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.qos import QoSProfile
from rclpy.subscription import Subscription

from .topic_component import TopicComponent


class SubscriberComponent(TopicComponent):
    """Lifecycle-aware subscriber component.

    The ROS subscription is created during configure.
    Incoming messages are ignored while the component is inactive.
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
        self._is_active = False

    @property
    def is_active(self) -> bool:
        return self._is_active

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        super()._on_configure(state)

        self._subscription = self.node.create_subscription(
            self.msg_type,
            self.topic_name,
            self._on_message_wrapper,
            self.qos_profile,
        )
        self.node.get_logger().info(f"[{self.name}] subscription created on '{self.topic_name}'")
        return TransitionCallbackReturn.SUCCESS

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        super()._on_activate(state)
        self._is_active = True
        return TransitionCallbackReturn.SUCCESS

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        super()._on_deactivate(state)
        self._is_active = False
        return TransitionCallbackReturn.SUCCESS

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        super()._on_cleanup(state)
        self._release_resources()
        return TransitionCallbackReturn.SUCCESS

    def _on_message_wrapper(self, msg: Any) -> None:
        if not self._is_active:
            return
        self.on_message(msg)

    @abstractmethod
    def on_message(self, msg: Any) -> None:
        """Handle an incoming message while the component is active."""
        raise NotImplementedError("on_message must be implemented by SubscriberComponent subclasses")

    def _release_resources(self) -> None:
        if self._subscription is not None:
            self.node.destroy_subscription(self._subscription)
            self._subscription = None
        self._is_active = False
