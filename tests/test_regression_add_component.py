"""Regression tests for add_component registration guard and atomic rollback."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.core import ComposedLifecycleNode, LifecycleComponent

# ---------------------------------------------------------------------------
# Concrete test component
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

DUMMY_STATE = LifecycleState(state_id=0, label="test")


@pytest.fixture()
def node():
    n = ComposedLifecycleNode("regression_add_node")
    yield n
    n.destroy_node()


# ---------------------------------------------------------------------------
# Fix 1 — Guard add_component after lifecycle transitions
# ---------------------------------------------------------------------------


class TestRegressionRegistrationGuard:
    """Registration must be rejected after the first lifecycle transition."""

    def test_configure_closes_registration(self, node: ComposedLifecycleNode) -> None:
        # Regression: add_component was silently accepted after on_configure,
        # leading to components that never received configure propagation.
        # Expected: RuntimeError prevents late registration.

        # Negative case first: registration works before any transition
        comp_before = DummyComponent("before_configure")
        node.add_component(comp_before)
        assert comp_before.name in [c.name for c in node.components]

        # Trigger lifecycle transition
        node.on_configure(DUMMY_STATE)

        # Positive case: adding after configure must raise
        with pytest.raises(RuntimeError, match="lifecycle transitions have already started"):
            node.add_component(DummyComponent("after_configure"))

    def test_shutdown_closes_registration(self, node: ComposedLifecycleNode) -> None:
        # Regression: add_component was accepted after on_shutdown,
        # leaving orphan components on a shutting-down node.
        # Expected: RuntimeError prevents registration after shutdown.

        # Negative case first: registration works before shutdown
        comp_before = DummyComponent("before_shutdown")
        node.add_component(comp_before)
        assert comp_before.name in [c.name for c in node.components]

        # Trigger shutdown
        node.on_shutdown(DUMMY_STATE)

        # Positive case: adding after shutdown must raise
        with pytest.raises(RuntimeError, match="lifecycle transitions have already started"):
            node.add_component(DummyComponent("after_shutdown"))

    def test_registration_open_flag_initially_true(self, node: ComposedLifecycleNode) -> None:
        # Guard: the flag must default to True for fresh nodes.
        assert node._registration_open is True


# ---------------------------------------------------------------------------
# Fix 2 — Atomic add_component with rollback
# ---------------------------------------------------------------------------


class TestRegressionAtomicAddComponent:
    """add_component must roll back attach on add_managed_entity failure."""

    def test_rollback_detaches_component_on_failure(self, node: ComposedLifecycleNode) -> None:
        # Regression: if add_managed_entity raised, the component stayed
        # attached (_node set) but was never registered in _components,
        # leaving it in a broken state that prevented re-attachment.
        # Expected: _detach() is called, _node is reset to None.

        comp = DummyComponent("rollback_test")

        with patch.object(node, "add_managed_entity", side_effect=RuntimeError("injected")):
            with pytest.raises(RuntimeError, match="injected"):
                node.add_component(comp)

        # After rollback: component must be fully detached
        assert comp._node is None

    def test_rollback_component_not_in_registry(self, node: ComposedLifecycleNode) -> None:
        # Regression: partial registration left ghost entries in _components.
        # Expected: failed component must not appear in the registry.

        comp = DummyComponent("ghost_check")

        with patch.object(node, "add_managed_entity", side_effect=RuntimeError("injected")):
            with pytest.raises(RuntimeError, match="injected"):
                node.add_component(comp)

        assert "ghost_check" not in [c.name for c in node.components]
        assert comp.name not in node._components

    def test_rollback_allows_reattach(self, node: ComposedLifecycleNode) -> None:
        # Regression: after a failed add_component, the component was stuck
        # in "already attached" state and could not be registered elsewhere.
        # Expected: component can be re-added after rollback.

        comp = DummyComponent("reattach_test")

        # First attempt: fail
        with patch.object(node, "add_managed_entity", side_effect=RuntimeError("injected")):
            with pytest.raises(RuntimeError, match="injected"):
                node.add_component(comp)

        # Second attempt: succeed (no monkeypatch → real add_managed_entity)
        node.add_component(comp)
        assert comp._node is node
        assert comp.name in [c.name for c in node.components]
