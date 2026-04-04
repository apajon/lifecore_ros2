from __future__ import annotations

from typing import Any

from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.publisher import Publisher

from .topic_component import TopicComponent


class PublisherComponent(TopicComponent):
    """Lifecycle-aware publisher component."""

    def __init__(
        self,
        name: str,
        topic_name: str,
        msg_type: type[Any],
        qos_profile: int = 10,
    ) -> None:
        super().__init__(
            name=name,
            topic_name=topic_name,
            msg_type=msg_type,
            qos_profile=qos_profile,
        )
        self._publisher: Publisher | None = None
        self._is_active = False

    @property
    def is_active(self) -> bool:
        return self._is_active

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
        super()._on_activate(state)
        self._is_active = True
        return TransitionCallbackReturn.SUCCESS

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        super()._on_deactivate(state)
        self._is_active = False
        return TransitionCallbackReturn.SUCCESS

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        super()._on_cleanup(state)

        if self._publisher is not None:
            self.node.destroy_publisher(self._publisher)
            self._publisher = None

        self._is_active = False
        return TransitionCallbackReturn.SUCCESS

    def publish(self, msg: Any) -> None:
        if self._publisher is None:
            raise RuntimeError(f"Publisher '{self.name}' is not configured")

        if not self._is_active:
            raise RuntimeError(f"Publisher '{self.name}' is not active")

        self._publisher.publish(msg)
