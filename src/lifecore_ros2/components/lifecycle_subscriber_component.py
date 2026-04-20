from __future__ import annotations

from abc import abstractmethod
from typing import final

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.qos import QoSProfile
from rclpy.subscription import Subscription

from lifecore_ros2.core.lifecycle_component import when_active

from .topic_component import TopicComponent


class LifecycleSubscriberComponent[MsgT](TopicComponent[MsgT]):
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
        msg_type: type[MsgT],
        qos_profile: QoSProfile | int = 10,
    ) -> None:
        super().__init__(
            name=name,
            topic_name=topic_name,
            msg_type=msg_type,
            qos_profile=qos_profile,
        )
        self._subscription: Subscription | None = None  # type: ignore[type-arg]  # rclpy Subscription is not generic

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Extension point. Creates the ROS subscription.

        Override in subclasses for additional setup. Call ``super()._on_configure(state)`` first.
        """
        self._subscription = self.node.create_subscription(
            self.msg_type,
            self.topic_name,
            self._on_message_wrapper,
            self.qos_profile,
        )
        self.node.get_logger().info(f"[{self.name}] subscription created on '{self.topic_name}'")
        return TransitionCallbackReturn.SUCCESS

    @final
    @when_active(when_not_active=None)
    def _on_message_wrapper(self, msg: MsgT) -> None:
        """Framework-internal. Do not call from user code."""
        try:
            self.on_message(msg)
        except Exception as exc:
            # Rule C (inbound): never propagate user exceptions into the rclpy executor.
            # Log the error and drop the message silently.
            self._resolve_logger().error(f"[{self._name}.on_message] {type(exc).__name__}: {exc}")

    @abstractmethod
    def on_message(self, msg: MsgT) -> None:
        """Extension point. Implement to handle incoming messages while active.

        This is the subscriber callback contract. Unlike the ``_on_*`` lifecycle hooks,
        ``on_message`` is intentionally public because it defines application behavior,
        not framework behavior. It is only called while the component is active.
        """
        raise NotImplementedError("on_message must be implemented by LifecycleSubscriberComponent subclasses")

    def _release_resources(self) -> None:
        """Extension point. Override to release additional resources; call ``super()._release_resources()`` last."""
        if self._subscription is not None:
            self.node.destroy_subscription(self._subscription)
            self._subscription = None
        super()._release_resources()
