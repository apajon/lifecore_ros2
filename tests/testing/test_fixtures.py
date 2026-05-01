from __future__ import annotations

from lifecore_ros2.testing import FakeComponent, NodeWithComponents


def test_lifecycle_node_fixture_creates_node(lifecycle_node_fixture) -> None:
    assert lifecycle_node_fixture.get_name() == "lifecore_test_node"


def test_node_with_components_registers_standard_fakes(node_with_components: NodeWithComponents) -> None:
    names = {component.name for component in node_with_components.node.components}

    assert names == {
        "fake_component",
        "fake_publisher",
        "fake_subscriber",
        "fake_timer",
        "fake_service",
        "fake_client",
    }
    assert isinstance(node_with_components.component, FakeComponent)
