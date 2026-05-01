"""Shared stubs and fixtures for topic component tests.

Fixtures are loaded for tests/components via the local conftest module.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from lifecore_ros2.components import LifecyclePublisherComponent, LifecycleSubscriberComponent, LifecycleTimerComponent
from lifecore_ros2.core import LifecycleComponentNode
from lifecore_ros2.testing import DUMMY_STATE as DUMMY_STATE

# ---------------------------------------------------------------------------
# Shared constant
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Concrete subclasses for testing
# ---------------------------------------------------------------------------


class StubSubscriber(LifecycleSubscriberComponent[Any]):
    def __init__(self, name: str = "test_sub") -> None:
        super().__init__(name=name, topic_name="/test_topic", msg_type=MagicMock, qos_profile=10)
        self.received: list[Any] = []

    def on_message(self, msg: Any) -> None:
        self.received.append(msg)


class StubPublisher(LifecyclePublisherComponent[Any]):
    def __init__(self, name: str = "test_pub") -> None:
        super().__init__(name=name, topic_name="/test_topic", msg_type=MagicMock, qos_profile=10)


class StubTimer(LifecycleTimerComponent):
    def __init__(self, name: str = "test_timer", period: float = 0.1) -> None:
        super().__init__(name=name, period=period)
        self.ticks: int = 0

    def on_tick(self) -> None:
        self.ticks += 1


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def node() -> Generator[LifecycleComponentNode, None, None]:
    n = LifecycleComponentNode("topic_test_node")
    yield n
    n.destroy_node()


@pytest.fixture()
def mock_topic_factories(node: LifecycleComponentNode) -> Generator[None, None, None]:
    """Patch node topic/timer factory methods so no real ROS endpoints are created."""
    with (
        patch.object(node, "create_publisher", return_value=MagicMock()),
        patch.object(node, "destroy_publisher", return_value=None),
        patch.object(node, "create_subscription", return_value=MagicMock()),
        patch.object(node, "destroy_subscription", return_value=None),
        patch.object(node, "create_timer", return_value=MagicMock()),
        patch.object(node, "destroy_timer", return_value=None),
    ):
        yield
