"""Tests for SubscriberComponent and PublisherComponent behavior."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from rclpy.lifecycle.node import LifecycleState
from rclpy.qos import QoSProfile

from lifecore_ros2.components import PublisherComponent, SubscriberComponent
from lifecore_ros2.core import ComposedLifecycleNode

# ---------------------------------------------------------------------------
# Concrete subclasses for testing
# ---------------------------------------------------------------------------


class StubSubscriber(SubscriberComponent):
    def __init__(self, name: str = "test_sub") -> None:
        super().__init__(name=name, topic_name="/test_topic", msg_type=MagicMock, qos_profile=10)
        self.received: list[Any] = []

    def on_message(self, msg: Any) -> None:
        self.received.append(msg)


class StubPublisher(PublisherComponent):
    def __init__(self, name: str = "test_pub") -> None:
        super().__init__(name=name, topic_name="/test_topic", msg_type=MagicMock, qos_profile=10)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


DUMMY_STATE = LifecycleState(state_id=0, label="test")


@pytest.fixture()
def node():
    n = ComposedLifecycleNode("topic_test_node")
    yield n
    n.destroy_node()


# ---------------------------------------------------------------------------
# 5.3  SubscriberComponent
# ---------------------------------------------------------------------------


class TestSubscriberComponent:
    def test_inactive_messages_ignored(self, node: ComposedLifecycleNode) -> None:
        sub = StubSubscriber()
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        # not activated yet → messages should be dropped
        sub._on_message_wrapper("hello")

        assert sub.received == []

    def test_active_messages_received(self, node: ComposedLifecycleNode) -> None:
        sub = StubSubscriber()
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)

        sub._on_message_wrapper("hello")
        assert sub.received == ["hello"]

    def test_deactivate_stops_processing(self, node: ComposedLifecycleNode) -> None:
        sub = StubSubscriber()
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub.on_deactivate(DUMMY_STATE)

        sub._on_message_wrapper("dropped")
        assert sub.received == []

    def test_cleanup_resets_active(self, node: ComposedLifecycleNode) -> None:
        sub = StubSubscriber()
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub.on_cleanup(DUMMY_STATE)

        assert not sub.is_active
        assert sub._subscription is None


# ---------------------------------------------------------------------------
# 5.3  PublisherComponent
# ---------------------------------------------------------------------------


class TestPublisherComponent:
    def test_publish_before_configure_raises(self) -> None:
        pub = StubPublisher()
        # not attached to any node, not configured, not active
        with pytest.raises(RuntimeError, match="not active"):
            pub.publish(MagicMock())

    def test_publish_when_inactive_raises(self, node: ComposedLifecycleNode) -> None:
        pub = StubPublisher()
        node.add_component(pub)

        # Manually set publisher to simulate successful configure without real ROS msg type
        pub._publisher = MagicMock()
        pub._is_active = False

        with pytest.raises(RuntimeError, match="not active"):
            pub.publish(MagicMock())

    def test_publish_when_active_succeeds(self, node: ComposedLifecycleNode) -> None:
        pub = StubPublisher()
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)

        # The publisher object is real but topic is mock → just verify no exception
        pub._publisher = MagicMock()
        pub.publish(MagicMock())
        pub._publisher.publish.assert_called_once()

    def test_cleanup_resets_publisher(self, node: ComposedLifecycleNode) -> None:
        pub = StubPublisher()
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        pub.on_cleanup(DUMMY_STATE)

        assert not pub.is_active
        assert pub._publisher is None


# ---------------------------------------------------------------------------
# Fix 3 — qos_profile typing coherence
# ---------------------------------------------------------------------------


class TestRegressionQoSTyping:
    """QoS profile parameter must accept both int and QoSProfile objects."""

    def test_subscriber_accepts_int_qos(self) -> None:
        # Regression: qos_profile was typed as int only in subclass __init__,
        # despite TopicComponent accepting QoSProfile | int.
        # Expected: int value is accepted without error.
        sub = StubSubscriber()
        assert sub.qos_profile == 10

    def test_subscriber_accepts_qos_profile_object(self) -> None:
        # Regression: passing a QoSProfile object raised or was mistyped.
        # Expected: QoSProfile object is stored correctly.
        qos = QoSProfile(depth=10)
        sub = _QoSSubscriber(qos_profile=qos)
        assert sub.qos_profile is qos

    def test_publisher_accepts_int_qos(self) -> None:
        # Regression: qos_profile was typed as int only in subclass __init__.
        # Expected: int value is accepted without error.
        pub = StubPublisher()
        assert pub.qos_profile == 10

    def test_publisher_accepts_qos_profile_object(self) -> None:
        # Regression: passing a QoSProfile object raised or was mistyped.
        # Expected: QoSProfile object is stored correctly.
        qos = QoSProfile(depth=10)
        pub = _QoSPublisher(qos_profile=qos)
        assert pub.qos_profile is qos


# ---------------------------------------------------------------------------
# Helpers for QoS typing tests
# ---------------------------------------------------------------------------


class _QoSSubscriber(SubscriberComponent):
    """Subscriber stub that accepts a custom qos_profile."""

    def __init__(self, qos_profile: QoSProfile | int = 10) -> None:
        super().__init__(
            name="qos_sub",
            topic_name="/qos_test",
            msg_type=MagicMock,
            qos_profile=qos_profile,
        )

    def on_message(self, msg: Any) -> None:
        pass


class _QoSPublisher(PublisherComponent):
    """Publisher stub that accepts a custom qos_profile."""

    def __init__(self, qos_profile: QoSProfile | int = 10) -> None:
        super().__init__(
            name="qos_pub",
            topic_name="/qos_test",
            msg_type=MagicMock,
            qos_profile=qos_profile,
        )
