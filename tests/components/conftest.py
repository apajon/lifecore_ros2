from __future__ import annotations

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from lifecore_ros2.core import LifecycleComponentNode


@pytest.fixture()
def node() -> Generator[LifecycleComponentNode, None, None]:
    node_instance = LifecycleComponentNode("component_test_node")
    yield node_instance
    node_instance.destroy_node()


@pytest.fixture()
def mock_topic_factories(node: LifecycleComponentNode) -> Generator[None, None, None]:
    with (
        patch.object(node, "create_publisher", return_value=MagicMock()),
        patch.object(node, "destroy_publisher", return_value=None),
        patch.object(node, "create_subscription", return_value=MagicMock()),
        patch.object(node, "destroy_subscription", return_value=None),
        patch.object(node, "create_timer", return_value=MagicMock()),
        patch.object(node, "destroy_timer", return_value=None),
    ):
        yield


@pytest.fixture()
def mock_svc_factories(node: LifecycleComponentNode) -> Generator[None, None, None]:
    with (
        patch.object(node, "create_service", return_value=MagicMock()),
        patch.object(node, "destroy_service"),
        patch.object(node, "create_client", return_value=MagicMock()),
        patch.object(node, "destroy_client"),
    ):
        yield
