"""Regression tests for LifecyclePublisherComponent lifecycle and activation gating.

Coverage map (this file):
    TestPublisherComponent    — activation gating (outbound raises while inactive)
    TestPublisherNominalCycle — configure / activate / deactivate / cleanup lifecycle

See also:
    tests/components/test_components.py — QoS typing, property stability, and callback_group propagation
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from rclpy.lifecycle import TransitionCallbackReturn

from lifecore_ros2.core import LifecycleComponentNode
from tests.components._topic_stubs import DUMMY_STATE, StubPublisher

# ---------------------------------------------------------------------------
# Publisher activation gating
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestPublisherComponent:
    def test_publish_before_configure_raises(self) -> None:
        pub = StubPublisher()
        # not attached to any node, not configured, not active
        with pytest.raises(RuntimeError, match="not active"):
            pub.publish(MagicMock())

    def test_publish_when_inactive_raises(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher()
        node.add_component(pub)

        # Manually set publisher to simulate successful configure without real ROS msg type
        pub._publisher = MagicMock()
        pub._is_active = False

        with pytest.raises(RuntimeError, match="not active"):
            pub.publish(MagicMock())

    def test_publish_when_active_succeeds(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher()
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)

        # The publisher object is real but topic is mock → just verify no exception
        pub._publisher = MagicMock()
        pub.publish(MagicMock())
        pub._publisher.publish.assert_called_once()

    def test_cleanup_resets_publisher(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher()
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        pub.on_deactivate(DUMMY_STATE)
        pub.on_cleanup(DUMMY_STATE)

        assert not pub.is_active
        assert pub._publisher is None


# ---------------------------------------------------------------------------
# Publisher nominal lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestPublisherNominalCycle:
    def test_configure_creates_publisher(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher("nom_pub")
        node.add_component(pub)

        with patch.object(node, "create_publisher", return_value=MagicMock()) as mock_create:
            result = pub.on_configure(DUMMY_STATE)
            assert result == TransitionCallbackReturn.SUCCESS
            assert pub._publisher is not None
            mock_create.assert_called_once()

    def test_activate_enables_publish(self, node: LifecycleComponentNode) -> None:
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

    def test_deactivate_blocks_publish(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher("nom_pub")
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        result = pub.on_deactivate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert pub.is_active is False

    def test_cleanup_releases_publisher(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher("nom_pub")
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        pub.on_deactivate(DUMMY_STATE)
        result = pub.on_cleanup(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert pub._publisher is None
