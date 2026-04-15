"""Tests for SubscriberComponent and PublisherComponent behavior."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from rclpy.lifecycle import TransitionCallbackReturn
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


# ---------------------------------------------------------------------------
# 5.3b  TopicComponent property stability across lifecycle
# ---------------------------------------------------------------------------


class TestTopicComponentProperties:
    def test_properties_stable_across_full_lifecycle(self, node: ComposedLifecycleNode) -> None:
        pub = StubPublisher("prop_pub")
        node.add_component(pub)

        expected_topic = "/test_topic"
        expected_qos = 10

        # Before any transition
        assert pub.topic_name == expected_topic
        assert pub.msg_type is MagicMock
        assert pub.qos_profile == expected_qos

        pub.on_configure(DUMMY_STATE)
        assert pub.topic_name == expected_topic
        assert pub.msg_type is MagicMock
        assert pub.qos_profile == expected_qos

        pub.on_activate(DUMMY_STATE)
        assert pub.topic_name == expected_topic
        assert pub.msg_type is MagicMock
        assert pub.qos_profile == expected_qos

        pub.on_deactivate(DUMMY_STATE)
        assert pub.topic_name == expected_topic
        assert pub.msg_type is MagicMock
        assert pub.qos_profile == expected_qos

        pub.on_cleanup(DUMMY_STATE)
        assert pub.topic_name == expected_topic
        assert pub.msg_type is MagicMock
        assert pub.qos_profile == expected_qos


# ---------------------------------------------------------------------------
# 5.3c  Publisher nominal full cycle
# ---------------------------------------------------------------------------


class TestPublisherNominalCycle:
    def test_configure_creates_publisher(self, node: ComposedLifecycleNode) -> None:
        pub = StubPublisher("nom_pub")
        node.add_component(pub)

        with patch.object(node, "create_publisher", return_value=MagicMock()) as mock_create:
            result = pub.on_configure(DUMMY_STATE)
            assert result == TransitionCallbackReturn.SUCCESS
            assert pub._publisher is not None
            mock_create.assert_called_once()

    def test_activate_enables_publish(self, node: ComposedLifecycleNode) -> None:
        pub = StubPublisher("nom_pub")
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        result = pub.on_activate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert pub.is_active is True

        # Replace real publisher with mock to avoid ROS transport
        pub._publisher = MagicMock()
        msg = MagicMock()
        pub.publish(msg)
        pub._publisher.publish.assert_called_once_with(msg)

    def test_deactivate_blocks_publish(self, node: ComposedLifecycleNode) -> None:
        pub = StubPublisher("nom_pub")
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        result = pub.on_deactivate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert pub.is_active is False

    def test_cleanup_releases_publisher(self, node: ComposedLifecycleNode) -> None:
        pub = StubPublisher("nom_pub")
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        pub.on_deactivate(DUMMY_STATE)
        result = pub.on_cleanup(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert pub._publisher is None


# ---------------------------------------------------------------------------
# 5.3d  Subscriber nominal full cycle
# ---------------------------------------------------------------------------


class TestSubscriberNominalCycle:
    def test_configure_creates_subscription(self, node: ComposedLifecycleNode) -> None:
        sub = StubSubscriber("nom_sub")
        node.add_component(sub)

        with patch.object(node, "create_subscription", return_value=MagicMock()) as mock_create:
            result = sub.on_configure(DUMMY_STATE)
            assert result == TransitionCallbackReturn.SUCCESS
            assert sub._subscription is not None
            mock_create.assert_called_once()

    def test_activate_enables_message_processing(self, node: ComposedLifecycleNode) -> None:
        sub = StubSubscriber("nom_sub")
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        result = sub.on_activate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert sub.is_active is True

        sub._on_message_wrapper("test_msg")
        assert sub.received == ["test_msg"]

    def test_deactivate_blocks_message_processing(self, node: ComposedLifecycleNode) -> None:
        sub = StubSubscriber("nom_sub")
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub._on_message_wrapper("before")

        result = sub.on_deactivate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert sub.is_active is False

        sub._on_message_wrapper("after")
        assert sub.received == ["before"]

    def test_cleanup_releases_subscription(self, node: ComposedLifecycleNode) -> None:
        sub = StubSubscriber("nom_sub")
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub.on_deactivate(DUMMY_STATE)
        result = sub.on_cleanup(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert sub._subscription is None
