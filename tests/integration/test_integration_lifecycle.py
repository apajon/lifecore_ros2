"""Integration tests for lifecycle transition propagation with a running executor.

Separation rationale:
- Unit tests (test_lifecycle.py, test_core.py) call component hooks directly.
- These tests use trigger_* on the *node* to drive the rclpy lifecycle state
  machine end-to-end, with a SingleThreadedExecutor spinning in a background
  thread — matching real runtime conditions.
"""

from __future__ import annotations

import threading
from typing import Any
from unittest.mock import MagicMock

import pytest
from rclpy.executors import SingleThreadedExecutor
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.components import LifecyclePublisherComponent, LifecycleSubscriberComponent
from lifecore_ros2.core import LifecycleComponentNode
from lifecore_ros2.testing import FakeComponent


class _NoShutdownRecordingComponent(FakeComponent):
    """Fake component variant that preserves the old shutdown-blind test helper behavior."""

    def _on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        return TransitionCallbackReturn.SUCCESS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def spinning_node():
    """LifecycleComponentNode with a background SingleThreadedExecutor."""
    node = LifecycleComponentNode("integration_test_node")
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

    def test_configure_propagates_to_all_components(self, spinning_node: LifecycleComponentNode) -> None:
        comp_a = FakeComponent("prop_a")
        comp_b = FakeComponent("prop_b")
        spinning_node.add_component(comp_a)
        spinning_node.add_component(comp_b)

        result = spinning_node.trigger_configure()

        assert result == TransitionCallbackReturn.SUCCESS
        assert "configure" in comp_a.calls
        assert "configure" in comp_b.calls

    def test_activate_propagates_after_configure(self, spinning_node: LifecycleComponentNode) -> None:
        comp = FakeComponent("act")
        spinning_node.add_component(comp)

        spinning_node.trigger_configure()
        result = spinning_node.trigger_activate()

        assert result == TransitionCallbackReturn.SUCCESS
        assert comp.calls == ["configure", "activate"]

    def test_full_cycle_propagation(self, spinning_node: LifecycleComponentNode) -> None:
        comp = FakeComponent("full_cycle")
        spinning_node.add_component(comp)

        assert spinning_node.trigger_configure() == TransitionCallbackReturn.SUCCESS
        assert spinning_node.trigger_activate() == TransitionCallbackReturn.SUCCESS
        assert spinning_node.trigger_deactivate() == TransitionCallbackReturn.SUCCESS
        assert spinning_node.trigger_cleanup() == TransitionCallbackReturn.SUCCESS

        assert comp.calls == ["configure", "activate", "deactivate", "cleanup"]

    def test_activate_deactivate_repeat_cycle(self, spinning_node: LifecycleComponentNode) -> None:
        comp = FakeComponent("repeat")
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

    def test_shutdown_from_unconfigured_does_not_propagate(self, spinning_node: LifecycleComponentNode) -> None:
        # rclpy does not propagate on_shutdown to managed entities when the
        # node transitions directly from unconfigured to finalized.
        comp = _NoShutdownRecordingComponent("shutdown_unc")
        spinning_node.add_component(comp)

        result = spinning_node.trigger_shutdown()

        assert result == TransitionCallbackReturn.SUCCESS
        assert "shutdown" not in comp.calls

    def test_shutdown_from_inactive_does_not_propagate_to_entities(
        self, spinning_node: LifecycleComponentNode
    ) -> None:
        # rclpy does not propagate on_shutdown to managed entities even from
        # the inactive state.  The node's own on_shutdown runs (closing
        # registration), but entity-level propagation is skipped.
        comp = _NoShutdownRecordingComponent("shutdown_inact")
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

    def test_registration_closed_after_trigger_configure(self, spinning_node: LifecycleComponentNode) -> None:
        # Registration: still possible before first transition
        comp = FakeComponent("pre_cfg")
        spinning_node.add_component(comp)

        spinning_node.trigger_configure()

        # Guard: registration must be closed after trigger_configure
        assert not spinning_node._registration_open
        with pytest.raises(RuntimeError, match="lifecycle transitions have already started"):
            spinning_node.add_component(FakeComponent("late_cfg"))

    def test_registration_closed_after_trigger_shutdown(self, spinning_node: LifecycleComponentNode) -> None:
        spinning_node.trigger_shutdown()

        assert not spinning_node._registration_open
        with pytest.raises(RuntimeError, match="lifecycle transitions have already started"):
            spinning_node.add_component(FakeComponent("late_shut"))


# ---------------------------------------------------------------------------
# Multiple components
# ---------------------------------------------------------------------------


class TestIntegrationMultipleComponents:
    """All registered components receive every propagated transition."""

    def test_three_components_configure_activate(self, spinning_node: LifecycleComponentNode) -> None:
        comps = [FakeComponent(f"multi_{i}") for i in range(3)]
        spinning_node.add_components(comps)

        spinning_node.trigger_configure()
        spinning_node.trigger_activate()

        for comp in comps:
            assert comp.calls == ["configure", "activate"]

    def test_component_failure_prevents_transition(self, spinning_node: LifecycleComponentNode) -> None:
        good = FakeComponent("good")
        bad = FakeComponent("bad", fail_at_hook="configure")
        spinning_node.add_component(good)
        spinning_node.add_component(bad)

        result = spinning_node.trigger_configure()

        # rclpy treats FAILURE from a managed entity as an overall failure;
        # the node should stay in the unconfigured state.
        assert result == TransitionCallbackReturn.FAILURE


# ---------------------------------------------------------------------------
# TestIntegrationShutdown
# ---------------------------------------------------------------------------


class TestIntegrationShutdown:
    """trigger_shutdown() from the active state returns SUCCESS."""

    def test_trigger_shutdown_from_active_returns_success(self, spinning_node: LifecycleComponentNode) -> None:
        # Regression: trigger_shutdown from the active state was not covered; a broken
        # transition path could silently return non-SUCCESS without failing any existing test.
        # Expected: trigger_shutdown() returns SUCCESS after configure + activate.
        comp = FakeComponent("shutdown_active")
        spinning_node.add_component(comp)

        spinning_node.trigger_configure()
        spinning_node.trigger_activate()
        result = spinning_node.trigger_shutdown()

        assert result == TransitionCallbackReturn.SUCCESS
        # rclpy propagates on_shutdown to managed entities when the node is in the active
        # state, unlike the unconfigured and inactive states where propagation is skipped
        # (see test_shutdown_from_unconfigured_does_not_propagate and
        # test_shutdown_from_inactive_does_not_propagate_to_entities).
        assert "shutdown" in comp.calls


# ---------------------------------------------------------------------------
# TestIntegrationHeterogeneousComponents
# ---------------------------------------------------------------------------


class TestIntegrationHeterogeneousComponents:
    """configure → activate → deactivate → cleanup propagates correctly to all component types."""

    def test_full_cycle_with_publisher_subscriber_and_plain_component(
        self, spinning_node: LifecycleComponentNode
    ) -> None:
        # Regression: heterogeneous component sets (publisher, subscriber, plain lifecycle)
        # were not tested together; silent propagation failures could skip a specific type.
        # Expected: all three components receive all four transitions; activation and resource state correct.

        class LocalPublisher(LifecyclePublisherComponent[Any]):
            def __init__(self) -> None:
                super().__init__(name="het_pub", topic_name="/het_test", msg_type=MagicMock, qos_profile=10)

            def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
                self._publisher = MagicMock()
                return TransitionCallbackReturn.SUCCESS

            def _release_resources(self) -> None:
                self._publisher = None
                super()._release_resources()

        class LocalSubscriber(LifecycleSubscriberComponent[Any]):
            def __init__(self) -> None:
                super().__init__(name="het_sub", topic_name="/het_test", msg_type=MagicMock, qos_profile=10)

            def on_message(self, msg: Any) -> None:  # required abstract method
                pass

            def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
                self._subscription = MagicMock()
                return TransitionCallbackReturn.SUCCESS

            def _release_resources(self) -> None:
                self._subscription = None
                super()._release_resources()

        pub_comp = LocalPublisher()
        sub_comp = LocalSubscriber()
        rec_comp = FakeComponent("het_rec")
        spinning_node.add_components([pub_comp, sub_comp, rec_comp])

        spinning_node.trigger_configure()
        spinning_node.trigger_activate()

        assert pub_comp.is_active
        assert sub_comp.is_active
        assert rec_comp.is_active

        spinning_node.trigger_deactivate()

        assert not pub_comp.is_active
        assert not sub_comp.is_active
        assert not rec_comp.is_active

        spinning_node.trigger_cleanup()

        # _release_resources is called automatically by on_cleanup; no resource leak.
        assert pub_comp._publisher is None
        assert sub_comp._subscription is None
        assert rec_comp.calls == ["configure", "activate", "deactivate", "cleanup"]
