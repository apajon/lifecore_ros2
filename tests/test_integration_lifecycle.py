"""Integration tests for lifecycle transition propagation with a running executor.

Separation rationale:
- Unit tests (test_lifecycle.py, test_core.py) call component hooks directly.
- These tests use trigger_* on the *node* to drive the rclpy lifecycle state
  machine end-to-end, with a SingleThreadedExecutor spinning in a background
  thread — matching real runtime conditions.
"""

from __future__ import annotations

import threading

import pytest
from rclpy.executors import SingleThreadedExecutor
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.core import ComposedLifecycleNode, LifecycleComponent

# ---------------------------------------------------------------------------
# Instrumented component
# ---------------------------------------------------------------------------


class RecordingComponent(LifecycleComponent):
    """Records lifecycle hook invocations for integration assertions."""

    def __init__(self, name: str, *, fail_on: str | None = None) -> None:
        super().__init__(name)
        self.calls: list[str] = []
        self._fail_on = fail_on

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.calls.append("configure")
        if self._fail_on == "configure":
            return TransitionCallbackReturn.FAILURE
        return TransitionCallbackReturn.SUCCESS

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.calls.append("activate")
        if self._fail_on == "activate":
            return TransitionCallbackReturn.FAILURE
        return TransitionCallbackReturn.SUCCESS

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.calls.append("deactivate")
        if self._fail_on == "deactivate":
            return TransitionCallbackReturn.FAILURE
        return TransitionCallbackReturn.SUCCESS

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.calls.append("cleanup")
        if self._fail_on == "cleanup":
            return TransitionCallbackReturn.FAILURE
        return TransitionCallbackReturn.SUCCESS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def spinning_node():
    """ComposedLifecycleNode with a background SingleThreadedExecutor."""
    node = ComposedLifecycleNode("integration_test_node")
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    yield node

    executor.shutdown()
    node.destroy_node()
    spin_thread.join(timeout=5.0)


# ---------------------------------------------------------------------------
# Transition propagation via trigger_*
# ---------------------------------------------------------------------------


class TestIntegrationTransitionPropagation:
    """trigger_* on the node must propagate to all registered components."""

    def test_configure_propagates_to_all_components(self, spinning_node: ComposedLifecycleNode) -> None:
        comp_a = RecordingComponent("prop_a")
        comp_b = RecordingComponent("prop_b")
        spinning_node.add_component(comp_a)
        spinning_node.add_component(comp_b)

        result = spinning_node.trigger_configure()

        assert result == TransitionCallbackReturn.SUCCESS
        assert "configure" in comp_a.calls
        assert "configure" in comp_b.calls

    def test_activate_propagates_after_configure(self, spinning_node: ComposedLifecycleNode) -> None:
        comp = RecordingComponent("act")
        spinning_node.add_component(comp)

        spinning_node.trigger_configure()
        result = spinning_node.trigger_activate()

        assert result == TransitionCallbackReturn.SUCCESS
        assert comp.calls == ["configure", "activate"]

    def test_full_cycle_propagation(self, spinning_node: ComposedLifecycleNode) -> None:
        comp = RecordingComponent("full_cycle")
        spinning_node.add_component(comp)

        assert spinning_node.trigger_configure() == TransitionCallbackReturn.SUCCESS
        assert spinning_node.trigger_activate() == TransitionCallbackReturn.SUCCESS
        assert spinning_node.trigger_deactivate() == TransitionCallbackReturn.SUCCESS
        assert spinning_node.trigger_cleanup() == TransitionCallbackReturn.SUCCESS

        assert comp.calls == ["configure", "activate", "deactivate", "cleanup"]

    def test_activate_deactivate_repeat_cycle(self, spinning_node: ComposedLifecycleNode) -> None:
        comp = RecordingComponent("repeat")
        spinning_node.add_component(comp)

        spinning_node.trigger_configure()
        spinning_node.trigger_activate()
        spinning_node.trigger_deactivate()
        spinning_node.trigger_activate()
        spinning_node.trigger_deactivate()
        spinning_node.trigger_cleanup()

        assert comp.calls == [
            "configure",
            "activate",
            "deactivate",
            "activate",
            "deactivate",
            "cleanup",
        ]

    def test_shutdown_from_unconfigured_does_not_propagate(self, spinning_node: ComposedLifecycleNode) -> None:
        # rclpy does not propagate on_shutdown to managed entities when the
        # node transitions directly from unconfigured to finalized.
        comp = RecordingComponent("shutdown_unc")
        spinning_node.add_component(comp)

        result = spinning_node.trigger_shutdown()

        assert result == TransitionCallbackReturn.SUCCESS
        assert "shutdown" not in comp.calls

    def test_shutdown_from_inactive_does_not_propagate_to_entities(self, spinning_node: ComposedLifecycleNode) -> None:
        # rclpy does not propagate on_shutdown to managed entities even from
        # the inactive state.  The node's own on_shutdown runs (closing
        # registration), but entity-level propagation is skipped.
        comp = RecordingComponent("shutdown_inact")
        spinning_node.add_component(comp)

        spinning_node.trigger_configure()
        result = spinning_node.trigger_shutdown()

        assert result == TransitionCallbackReturn.SUCCESS
        assert "shutdown" not in comp.calls


# ---------------------------------------------------------------------------
# Registration guard under runtime conditions
# ---------------------------------------------------------------------------


class TestIntegrationRegistrationGuard:
    """Registration guard must hold when transitions are driven by trigger_*."""

    def test_registration_closed_after_trigger_configure(self, spinning_node: ComposedLifecycleNode) -> None:
        # Registration: still possible before first transition
        comp = RecordingComponent("pre_cfg")
        spinning_node.add_component(comp)

        spinning_node.trigger_configure()

        # Guard: registration must be closed after trigger_configure
        assert not spinning_node._registration_open
        with pytest.raises(RuntimeError, match="lifecycle transitions have already started"):
            spinning_node.add_component(RecordingComponent("late_cfg"))

    def test_registration_closed_after_trigger_shutdown(self, spinning_node: ComposedLifecycleNode) -> None:
        spinning_node.trigger_shutdown()

        assert not spinning_node._registration_open
        with pytest.raises(RuntimeError, match="lifecycle transitions have already started"):
            spinning_node.add_component(RecordingComponent("late_shut"))


# ---------------------------------------------------------------------------
# Multiple components
# ---------------------------------------------------------------------------


class TestIntegrationMultipleComponents:
    """All registered components receive every propagated transition."""

    def test_three_components_configure_activate(self, spinning_node: ComposedLifecycleNode) -> None:
        comps = [RecordingComponent(f"multi_{i}") for i in range(3)]
        spinning_node.add_components(comps)

        spinning_node.trigger_configure()
        spinning_node.trigger_activate()

        for comp in comps:
            assert comp.calls == ["configure", "activate"]

    def test_component_failure_prevents_transition(self, spinning_node: ComposedLifecycleNode) -> None:
        good = RecordingComponent("good")
        bad = RecordingComponent("bad", fail_on="configure")
        spinning_node.add_component(good)
        spinning_node.add_component(bad)

        result = spinning_node.trigger_configure()

        # rclpy treats FAILURE from a managed entity as an overall failure;
        # the node should stay in the unconfigured state.
        assert result == TransitionCallbackReturn.FAILURE
