"""Tests for ComposedLifecycleNode and LifecycleComponent core behavior."""

from __future__ import annotations

import pytest
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.core import ComposedLifecycleNode, LifecycleComponent

# ---------------------------------------------------------------------------
# Concrete test component (satisfies @abstractmethod contract)
# ---------------------------------------------------------------------------


class DummyComponent(LifecycleComponent):
    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        return TransitionCallbackReturn.SUCCESS

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return TransitionCallbackReturn.SUCCESS

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return TransitionCallbackReturn.SUCCESS

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        return TransitionCallbackReturn.SUCCESS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def node():
    n = ComposedLifecycleNode("test_node")
    yield n
    n.destroy_node()


# ---------------------------------------------------------------------------
# 5.1  Tests du core
# ---------------------------------------------------------------------------


class TestAddComponent:
    def test_add_component_registers_managed_entity(self, node: ComposedLifecycleNode) -> None:
        comp = DummyComponent("comp_a")
        node.add_component(comp)

        assert comp.name in [c.name for c in node.components]
        assert comp._node is node

    def test_add_component_duplicate_name_raises(self, node: ComposedLifecycleNode) -> None:
        node.add_component(DummyComponent("dup"))

        with pytest.raises(ValueError, match="already registered"):
            node.add_component(DummyComponent("dup"))

    def test_add_components_bulk(self, node: ComposedLifecycleNode) -> None:
        comps = [DummyComponent("a"), DummyComponent("b"), DummyComponent("c")]
        node.add_components(comps)
        assert len(node.components) == 3


class TestGetComponent:
    def test_get_existing_component(self, node: ComposedLifecycleNode) -> None:
        comp = DummyComponent("findme")
        node.add_component(comp)
        assert node.get_component("findme") is comp

    def test_get_missing_component_raises(self, node: ComposedLifecycleNode) -> None:
        with pytest.raises(KeyError, match="Unknown component"):
            node.get_component("nope")


class TestComponentAttach:
    def test_unattached_component_node_raises(self) -> None:
        comp = DummyComponent("orphan")
        with pytest.raises(RuntimeError, match="not attached"):
            _ = comp.node

    def test_double_attach_raises(self, node: ComposedLifecycleNode) -> None:
        comp = DummyComponent("once")
        comp.attach(node)

        with pytest.raises(RuntimeError, match="already attached"):
            comp.attach(node)
