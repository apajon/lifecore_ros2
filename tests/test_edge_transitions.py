"""Edge-case and invalid lifecycle transition tests.

Covers transitions that violate the expected lifecycle ordering or repeat
a transition without the required intermediate step.  Two test classes:

- ``TestEdgeTransitionsDirect`` — direct calls to component hooks (unit level).
- ``TestEdgeTransitionsIntegration`` — node-level via ``trigger_*`` with a
  spinning executor that exercises the rclpy state machine.

Note on rclpy Jazzy behavior:
    Invalid lifecycle transitions (e.g. activate from unconfigured) raise
    ``rclpy._rclpy_pybind11.RCLError`` rather than returning
    ``TransitionCallbackReturn.ERROR``.  The tests use ``pytest.raises``
    to assert this.
"""

from __future__ import annotations

import threading
from unittest.mock import MagicMock, patch

import pytest
from rclpy._rclpy_pybind11 import RCLError
from rclpy.executors import SingleThreadedExecutor
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.core import LifecycleComponent, LifecycleComponentNode
from lifecore_ros2.core.exceptions import InvalidLifecycleTransitionError

# ---------------------------------------------------------------------------
# Instrumented components
# ---------------------------------------------------------------------------

DUMMY_STATE = LifecycleState(state_id=0, label="test")


class ActivationTrackingComponent(LifecycleComponent):
    """Minimal component for tracking _is_active through transitions."""

    pass


class RecordingComponent(LifecycleComponent):
    """Records hook calls and can inject failures on a specific hook."""

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
def node():
    n = LifecycleComponentNode("edge_test_node")
    yield n
    n.destroy_node()


@pytest.fixture()
def spinning_node():
    """LifecycleComponentNode with a background SingleThreadedExecutor."""
    node = LifecycleComponentNode("edge_integration_node")
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    yield node

    executor.shutdown()
    node.destroy_node()
    spin_thread.join(timeout=5.0)


# ===========================================================================
# Direct hook calls (unit level)
# ===========================================================================


class TestEdgeTransitionsDirect:
    """Direct calls to component hooks bypass the rclpy state machine.

    These tests guard the strict contract enforced for direct component hooks.
    """

    # -- 1. Activate before configure (direct) ----------------------------

    def test_activate_before_configure_direct(self, node: LifecycleComponentNode) -> None:
        # Regression: direct activate once succeeded before configure.
        # Expected: direct invalid order is rejected with a typed boundary error.
        comp = ActivationTrackingComponent("act_no_cfg")
        node.add_component(comp)

        assert comp.is_active is False
        with pytest.raises(InvalidLifecycleTransitionError, match="cannot 'activate' from 'unconfigured'"):
            comp.on_activate(DUMMY_STATE)
        assert comp.is_active is False

    def test_activate_before_configure_direct_logs_actionable_context(self, node: LifecycleComponentNode) -> None:
        comp = ActivationTrackingComponent("act_no_cfg_log")
        node.add_component(comp)

        mock_logger = MagicMock()
        with patch.object(comp, "_resolve_logger", return_value=mock_logger):
            with pytest.raises(InvalidLifecycleTransitionError):
                comp.on_activate(DUMMY_STATE)

        error_msg = mock_logger.error.call_args[0][0]
        assert "attempted='activate'" in error_msg
        assert "current_state='unconfigured'" in error_msg
        assert "reason='component is not configured'" in error_msg

    # -- 2. Cleanup before configure (direct) ------------------------------

    def test_cleanup_before_configure_direct(self, node: LifecycleComponentNode) -> None:
        # Regression: direct cleanup once succeeded on an unconfigured component.
        # Expected: direct invalid order is rejected with a typed boundary error.
        comp = ActivationTrackingComponent("cleanup_no_cfg")
        node.add_component(comp)

        with pytest.raises(InvalidLifecycleTransitionError, match="cannot 'cleanup' from 'unconfigured'"):
            comp.on_cleanup(DUMMY_STATE)

    # -- 3. Repeated configure (direct) ------------------------------------

    def test_configure_twice_direct(self, node: LifecycleComponentNode) -> None:
        # Regression: direct repeated configure once ran twice.
        # Expected: second configure is rejected until cleanup releases the component.
        comp = RecordingComponent("cfg_twice")
        node.add_component(comp)

        result1 = comp.on_configure(DUMMY_STATE)

        assert result1 == TransitionCallbackReturn.SUCCESS
        with pytest.raises(InvalidLifecycleTransitionError, match="cannot 'configure' from 'inactive'"):
            comp.on_configure(DUMMY_STATE)
        assert comp.calls == ["configure"]

    # -- 4. Deactivate without prior activate (direct) ---------------------

    def test_deactivate_without_activate_direct(self, node: LifecycleComponentNode) -> None:
        # Regression: direct deactivate once succeeded from inactive state.
        # Expected: direct invalid order is rejected with a typed boundary error.
        comp = ActivationTrackingComponent("deact_no_act")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        assert comp.is_active is False

        with pytest.raises(InvalidLifecycleTransitionError, match="cannot 'deactivate' from 'inactive'"):
            comp.on_deactivate(DUMMY_STATE)
        assert comp.is_active is False

    # -- 5. Activate → activate without deactivate (direct) ----------------

    def test_activate_twice_without_deactivate_direct(self, node: LifecycleComponentNode) -> None:
        # Regression: direct repeated activate once succeeded twice.
        # Expected: second activate is rejected while already active.
        comp = ActivationTrackingComponent("act_twice")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.is_active is True

        with pytest.raises(InvalidLifecycleTransitionError, match="cannot 'activate' from 'active'"):
            comp.on_activate(DUMMY_STATE)
        assert comp.is_active is True

    # -- 6. Cleanup resets activation flag ---------------------------------

    def test_cleanup_clears_is_active(self, node: LifecycleComponentNode) -> None:
        # Regression: direct cleanup once succeeded while the component was active.
        # Expected: cleanup must be rejected until deactivate succeeds.
        comp = ActivationTrackingComponent("cleanup_active")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.is_active is True

        with pytest.raises(InvalidLifecycleTransitionError, match="cannot 'cleanup' from 'active'"):
            comp.on_cleanup(DUMMY_STATE)
        assert comp.is_active is True


# ===========================================================================
# Integration tests (node-level via trigger_*)
# ===========================================================================


class TestEdgeTransitionsIntegration:
    """Node-level transitions driven by trigger_* with a spinning executor.

    Invalid transitions are rejected by the rclpy lifecycle state machine,
    returning TransitionCallbackReturn.ERROR without invoking component hooks.
    """

    # -- 1. Activate before configure (integration) ------------------------

    def test_activate_before_configure_integration(self, spinning_node: LifecycleComponentNode) -> None:
        # rclpy state machine raises RCLError for activate from unconfigured state.
        comp = RecordingComponent("act_before_cfg")
        spinning_node.add_component(comp)

        with pytest.raises(RCLError, match="Transition is not registered"):
            spinning_node.trigger_activate()
        # Component hook was never called:
        assert "activate" not in comp.calls

    def test_activate_before_configure_integration_logs_actionable_context(
        self, spinning_node: LifecycleComponentNode
    ) -> None:
        comp = RecordingComponent("act_before_cfg_log")
        spinning_node.add_component(comp)

        mock_logger = MagicMock()
        with patch.object(spinning_node, "get_logger", return_value=mock_logger):
            with pytest.raises(RCLError, match="Transition is not registered"):
                spinning_node.trigger_activate()

        error_msg = mock_logger.error.call_args[0][0]
        assert "attempted='activate'" in error_msg
        assert "current_state='unconfigured'" in error_msg
        assert "act_before_cfg_log" in error_msg

    # -- 2. Cleanup before configure (integration) -------------------------

    def test_cleanup_before_configure_integration(self, spinning_node: LifecycleComponentNode) -> None:
        # rclpy state machine raises RCLError for cleanup from unconfigured state.
        comp = RecordingComponent("cleanup_before_cfg")
        spinning_node.add_component(comp)

        with pytest.raises(RCLError, match="Transition is not registered"):
            spinning_node.trigger_cleanup()
        assert "cleanup" not in comp.calls

    # -- 3a. Repeated configure without cleanup (integration) ---------------

    def test_configure_twice_without_cleanup_integration(self, spinning_node: LifecycleComponentNode) -> None:
        # After configure, the node is in inactive state.  A second configure
        # without cleanup is not a valid rclpy transition.
        comp = RecordingComponent("cfg_twice_no_clean")
        spinning_node.add_component(comp)

        result1 = spinning_node.trigger_configure()
        assert result1 == TransitionCallbackReturn.SUCCESS

        # rclpy raises: node is in inactive state, not unconfigured.
        with pytest.raises(RCLError, match="Transition is not registered"):
            spinning_node.trigger_configure()
        # Component configure was only invoked once:
        assert comp.calls.count("configure") == 1

    # -- 3b. Valid re-configure via cleanup (integration) -------------------

    def test_reconfigure_via_cleanup_integration(self, spinning_node: LifecycleComponentNode) -> None:
        # The valid re-configure path: configure → cleanup → configure.
        comp = RecordingComponent("reconfigure")
        spinning_node.add_component(comp)

        assert spinning_node.trigger_configure() == TransitionCallbackReturn.SUCCESS
        assert spinning_node.trigger_cleanup() == TransitionCallbackReturn.SUCCESS
        assert spinning_node.trigger_configure() == TransitionCallbackReturn.SUCCESS

        assert comp.calls == ["configure", "cleanup", "configure"]

    # -- 4. Repeated activate (integration) ---------------------------------

    def test_activate_twice_integration(self, spinning_node: LifecycleComponentNode) -> None:
        # rclpy raises RCLError for the second activate when node is already active.
        comp = RecordingComponent("act_twice")
        spinning_node.add_component(comp)

        spinning_node.trigger_configure()
        result1 = spinning_node.trigger_activate()
        assert result1 == TransitionCallbackReturn.SUCCESS

        with pytest.raises(RCLError, match="Transition is not registered"):
            spinning_node.trigger_activate()
        # Hook was only invoked once:
        assert comp.calls.count("activate") == 1

    # -- 5. Deactivate without active state (integration) -------------------

    def test_deactivate_from_inactive_integration(self, spinning_node: LifecycleComponentNode) -> None:
        # rclpy raises RCLError for deactivate when the node is inactive (after configure).
        comp = RecordingComponent("deact_inact")
        spinning_node.add_component(comp)

        spinning_node.trigger_configure()

        with pytest.raises(RCLError, match="Transition is not registered"):
            spinning_node.trigger_deactivate()
        assert "deactivate" not in comp.calls

    # -- 6. Cleanup after partial initialization failure --------------------

    def test_cleanup_after_partial_configure_failure(self, spinning_node: LifecycleComponentNode) -> None:
        # One component is set to fail configure.  The overall transition
        # returns FAILURE and the node stays in unconfigured state.
        # rclpy may or may not propagate to all entities before aggregating;
        # the key invariant is: the node can be re-configured after failure.
        comp_a = RecordingComponent("partial_ok")
        comp_b = RecordingComponent("partial_fail", fail_on="configure")
        spinning_node.add_component(comp_a)
        spinning_node.add_component(comp_b)

        result = spinning_node.trigger_configure()
        assert result == TransitionCallbackReturn.FAILURE

        # No cleanup was propagated:
        assert "cleanup" not in comp_a.calls
        assert "cleanup" not in comp_b.calls

        # Node is back to unconfigured; a new configure is valid:
        comp_b._fail_on = None
        result2 = spinning_node.trigger_configure()
        assert result2 == TransitionCallbackReturn.SUCCESS

    # -- 7. Deactivate from unconfigured (integration) ---------------------

    def test_deactivate_from_unconfigured_integration(self, spinning_node: LifecycleComponentNode) -> None:
        # rclpy raises RCLError for deactivate from unconfigured state.
        comp = RecordingComponent("deact_uncfg")
        spinning_node.add_component(comp)

        with pytest.raises(RCLError, match="Transition is not registered"):
            spinning_node.trigger_deactivate()
        assert "deactivate" not in comp.calls

    # -- 8. Full invalid sequence: activate → cleanup (integration) --------

    def test_cleanup_from_active_state_integration(self, spinning_node: LifecycleComponentNode) -> None:
        # rclpy raises RCLError for cleanup from active state; must deactivate first.
        comp = RecordingComponent("cleanup_active")
        spinning_node.add_component(comp)

        spinning_node.trigger_configure()
        spinning_node.trigger_activate()

        with pytest.raises(RCLError, match="Transition is not registered"):
            spinning_node.trigger_cleanup()
        assert "cleanup" not in comp.calls
