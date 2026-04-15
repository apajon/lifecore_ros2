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

    def _release_resources(self) -> None:
        super()._release_resources()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

DUMMY_STATE = LifecycleState(state_id=0, label="test")


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


# ---------------------------------------------------------------------------
# 5.1b  Nominal ComposedLifecycleNode behavior
# ---------------------------------------------------------------------------


class TestComposedNodeNominal:
    def test_components_property_returns_registered(self, node: ComposedLifecycleNode) -> None:
        comp_a = DummyComponent("alpha")
        comp_b = DummyComponent("beta")
        node.add_component(comp_a)
        node.add_component(comp_b)

        result = node.components
        assert len(result) == 2
        assert comp_a in result
        assert comp_b in result

    def test_registration_open_initially(self, node: ComposedLifecycleNode) -> None:
        assert node._registration_open is True

    def test_registration_closed_after_configure(self, node: ComposedLifecycleNode) -> None:
        node.add_component(DummyComponent("pre"))
        node.on_configure(DUMMY_STATE)
        assert node._registration_open is False
