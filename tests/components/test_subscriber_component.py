"""Regression tests for LifecycleSubscriberComponent lifecycle and activation gating.

Coverage map (this file):
    TestSubscriberComponent    — activation gating (inbound message drop while inactive)
    TestSubscriberNominalCycle — configure / activate / deactivate / cleanup lifecycle

See also:
    tests/components/test_components.py — QoS typing, property stability, and callback_group propagation
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from rclpy.lifecycle import TransitionCallbackReturn

from lifecore_ros2.core import LifecycleComponentNode
from tests.components._topic_stubs import DUMMY_STATE, StubSubscriber

# ---------------------------------------------------------------------------
# Subscriber activation gating
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestSubscriberComponent:
    def test_inactive_messages_ignored(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber()
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        # not activated yet → messages should be dropped
        sub._on_message_wrapper("hello")

        assert sub.received == []

    def test_active_messages_received(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber()
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)

        sub._on_message_wrapper("hello")
        assert sub.received == ["hello"]

    def test_deactivate_stops_processing(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber()
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub.on_deactivate(DUMMY_STATE)

        sub._on_message_wrapper("dropped")
        assert sub.received == []

    def test_cleanup_resets_active(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber()
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub.on_deactivate(DUMMY_STATE)
        sub.on_cleanup(DUMMY_STATE)

        assert not sub.is_active
        assert sub._subscription is None


# ---------------------------------------------------------------------------
# Subscriber nominal lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestSubscriberNominalCycle:
    def test_configure_creates_subscription(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber("nom_sub")
        node.add_component(sub)

        with patch.object(node, "create_subscription", return_value=MagicMock()) as mock_create:
            result = sub.on_configure(DUMMY_STATE)
            assert result == TransitionCallbackReturn.SUCCESS
            assert sub._subscription is not None
            mock_create.assert_called_once()

    def test_activate_enables_message_processing(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber("nom_sub")
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        result = sub.on_activate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert sub.is_active is True

        sub._on_message_wrapper("test_msg")
        assert sub.received == ["test_msg"]

    def test_deactivate_blocks_message_processing(self, node: LifecycleComponentNode) -> None:
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

    def test_cleanup_releases_subscription(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber("nom_sub")
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub.on_deactivate(DUMMY_STATE)
        result = sub.on_cleanup(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert sub._subscription is None
