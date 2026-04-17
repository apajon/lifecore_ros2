"""Double activate/deactivate edge case tests.

Validates that repeated or redundant lifecycle transitions produce
correct ``_is_active`` state and expected hook invocations.
"""

from __future__ import annotations

import pytest
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.core import LifecycleComponent, LifecycleComponentNode
from lifecore_ros2.core.lifecycle_component import when_active

DUMMY_STATE = LifecycleState(state_id=0, label="test")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def node():
    n = LifecycleComponentNode("double_transition_node")
    yield n
    n.destroy_node()


# ---------------------------------------------------------------------------
# Instrumented component
# ---------------------------------------------------------------------------


class RecordingComponent(LifecycleComponent):
    """Records hook calls and supports injected failures."""

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
# Double activate
# ---------------------------------------------------------------------------


class TestDoubleActivate:
    """Calling on_activate twice without an intervening on_deactivate."""

    def test_double_activate_calls_hook_twice(self, node: LifecycleComponentNode) -> None:
        # Regression: a second activate must still call the hook (ROS 2 node
        # may trigger transitions in unexpected orders during error recovery).
        # Expected: both calls go through; _is_active remains True.
        comp = RecordingComponent("dbl_act")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        result1 = comp.on_activate(DUMMY_STATE)
        result2 = comp.on_activate(DUMMY_STATE)

        assert result1 == TransitionCallbackReturn.SUCCESS
        assert result2 == TransitionCallbackReturn.SUCCESS
        assert comp.is_active is True
        assert comp.calls.count("activate") == 2

    def test_double_activate_second_fails_stays_active(self, node: LifecycleComponentNode) -> None:
        # Regression: if the second activate fails, _is_active must still
        # reflect the first successful activation.
        # Expected: _is_active remains True after failed second activate.
        comp = RecordingComponent("dbl_act_fail")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.is_active is True

        # Inject failure for second activate
        comp._fail_on = "activate"
        result = comp.on_activate(DUMMY_STATE)

        assert result == TransitionCallbackReturn.FAILURE
        assert comp.is_active is True  # first activation still holds


# ---------------------------------------------------------------------------
# Double deactivate
# ---------------------------------------------------------------------------


class TestDoubleDeactivate:
    """Calling on_deactivate twice without an intervening on_activate."""

    def test_double_deactivate_calls_hook_twice(self, node: LifecycleComponentNode) -> None:
        # Regression: a second deactivate call must still invoke the hook.
        # Expected: both calls succeed; _is_active remains False.
        comp = RecordingComponent("dbl_deact")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_deactivate(DUMMY_STATE)
        assert comp.is_active is False

        result = comp.on_deactivate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert comp.is_active is False
        assert comp.calls.count("deactivate") == 2

    def test_deactivate_without_prior_activate(self, node: LifecycleComponentNode) -> None:
        # Guard: calling deactivate on a configured-but-never-activated component.
        # Expected: hook runs, _is_active stays False.
        comp = RecordingComponent("cold_deact")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        assert comp.is_active is False

        result = comp.on_deactivate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert comp.is_active is False
        assert "deactivate" in comp.calls


# ---------------------------------------------------------------------------
# Rapid activate-deactivate cycles
# ---------------------------------------------------------------------------


class TestRapidActivateDeactivateCycles:
    """Many activate/deactivate transitions in sequence."""

    def test_many_cycles_is_active_consistent(self, node: LifecycleComponentNode) -> None:
        # Guard: _is_active must correctly track state through many cycles.
        comp = RecordingComponent("rapid")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)

        cycles = 20
        for _ in range(cycles):
            comp.on_activate(DUMMY_STATE)
            assert comp.is_active is True
            comp.on_deactivate(DUMMY_STATE)
            assert comp.is_active is False

        assert comp.calls.count("activate") == cycles
        assert comp.calls.count("deactivate") == cycles

    def test_failed_deactivate_keeps_active(self, node: LifecycleComponentNode) -> None:
        # Regression: a failed deactivate must NOT clear _is_active.
        # Expected: _is_active remains True after FAILURE from on_deactivate.
        comp = RecordingComponent("fail_deact", fail_on="deactivate")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.is_active is True

        result = comp.on_deactivate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.FAILURE
        assert comp.is_active is True  # not cleared on failure


# ---------------------------------------------------------------------------
# Activate-deactivate-reactivate cycle
# ---------------------------------------------------------------------------


class TestReactivation:
    """Validates activate → deactivate → activate restores full functionality."""

    def test_reactivate_restores_is_active(self, node: LifecycleComponentNode) -> None:
        # Guard: after a full deactivate→reactivate cycle, _is_active must be True
        # and hooks must all be called.
        comp = RecordingComponent("react")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.is_active is True

        comp.on_deactivate(DUMMY_STATE)
        assert comp.is_active is False

        comp.on_activate(DUMMY_STATE)
        assert comp.is_active is True
        assert comp.calls == ["configure", "activate", "deactivate", "activate"]

    def test_reactivate_gated_method_works(self, node: LifecycleComponentNode) -> None:
        # Guard: @when_active-gated methods must work after reactivation.
        comp = _GatedComponent("gated_react")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.gated_action() == "ok"

        comp.on_deactivate(DUMMY_STATE)
        with pytest.raises(RuntimeError, match="not active"):
            comp.gated_action()

        comp.on_activate(DUMMY_STATE)
        assert comp.gated_action() == "ok"


# ---------------------------------------------------------------------------
# when_active gating during double transitions
# ---------------------------------------------------------------------------


class TestGatingConsistencyDuringDoubleTransitions:
    """Validates @when_active gating is consistent at every double-transition step."""

    def test_gated_after_double_activate(self, node: LifecycleComponentNode) -> None:
        # Guard: after two activates, gated method must still work.
        comp = _GatedComponent("gated_dbl_act")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.gated_action() == "ok"

    def test_gated_after_double_deactivate(self, node: LifecycleComponentNode) -> None:
        # Guard: after two deactivates, gated method must still raise.
        comp = _GatedComponent("gated_dbl_deact")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_deactivate(DUMMY_STATE)
        comp.on_deactivate(DUMMY_STATE)

        with pytest.raises(RuntimeError, match="not active"):
            comp.gated_action()

    def test_gated_before_any_activate(self, node: LifecycleComponentNode) -> None:
        # Guard: gated method must raise when component was never activated.
        comp = _GatedComponent("gated_never_act")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        with pytest.raises(RuntimeError, match="not active"):
            comp.gated_action()


# ---------------------------------------------------------------------------
# Release resources idempotency
# ---------------------------------------------------------------------------


class TestReleaseResourcesIdempotency:
    """Validates that _release_resources can be called multiple times safely."""

    def test_double_release_no_error(self, node: LifecycleComponentNode) -> None:
        # Guard: _release_resources must be idempotent — calling it twice
        # must not raise or corrupt state.
        comp = _TrackingReleaseComponent("dbl_release")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.is_active is True

        comp._release_resources()
        comp._release_resources()

        assert comp.is_active is False
        assert comp.release_count == 2

    def test_release_after_cleanup_is_safe(self, node: LifecycleComponentNode) -> None:
        # Guard: cleanup auto-calls _release_resources; a manual call after
        # must be harmless.
        comp = _TrackingReleaseComponent("release_after_cleanup")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_cleanup(DUMMY_STATE)  # auto-calls _release_resources
        assert comp.release_count == 1

        comp._release_resources()  # manual second call
        assert comp.release_count == 2
        assert comp.is_active is False


# ---------------------------------------------------------------------------
# Activate with exception
# ---------------------------------------------------------------------------


class TestActivateWithException:
    """Validates _is_active correctness when hooks raise or return ERROR."""

    def test_activate_exception_keeps_inactive(self, node: LifecycleComponentNode) -> None:
        # Regression: if _on_activate raises, _guarded_call returns ERROR.
        # _is_active must NOT be set to True.
        # Expected: _is_active remains False after exception in activate.
        comp = _CrashingActivateComponent("crash_act")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        result = comp.on_activate(DUMMY_STATE)

        assert result == TransitionCallbackReturn.ERROR
        assert comp.is_active is False

    def test_activate_failure_keeps_inactive(self, node: LifecycleComponentNode) -> None:
        # Guard: explicit FAILURE return from _on_activate must not set _is_active.
        comp = RecordingComponent("fail_act", fail_on="activate")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        result = comp.on_activate(DUMMY_STATE)

        assert result == TransitionCallbackReturn.FAILURE
        assert comp.is_active is False
        assert "activate" in comp.calls


# ---------------------------------------------------------------------------
# Full lifecycle recycle: cleanup → reconfigure → reactivate
# ---------------------------------------------------------------------------


class TestFullLifecycleRecycle:
    """Validates that a component can be fully recycled through cleanup and back."""

    def test_cleanup_reconfigure_reactivate(self, node: LifecycleComponentNode) -> None:
        # Guard: after cleanup (which auto-releases resources), a component
        # must be re-configurable and re-activatable with no leaked state.
        comp = _TrackingReleaseComponent("recycle")
        node.add_component(comp)

        # First cycle
        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.is_active is True

        comp.on_deactivate(DUMMY_STATE)
        comp.on_cleanup(DUMMY_STATE)
        assert comp.is_active is False
        assert comp.release_count == 1

        # Second cycle — must work identically
        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.is_active is True

        comp.on_deactivate(DUMMY_STATE)
        comp.on_cleanup(DUMMY_STATE)
        assert comp.is_active is False
        assert comp.release_count == 2

    def test_gated_method_works_after_recycle(self, node: LifecycleComponentNode) -> None:
        # Guard: @when_active-gated method must work after a full recycle.
        comp = _GatedComponent("gated_recycle")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.gated_action() == "ok"

        comp.on_deactivate(DUMMY_STATE)
        comp.on_cleanup(DUMMY_STATE)

        with pytest.raises(RuntimeError, match="not active"):
            comp.gated_action()

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.gated_action() == "ok"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _GatedComponent(LifecycleComponent):
    """Component with a @when_active-gated method for testing."""

    @when_active
    def gated_action(self) -> str:
        return "ok"


class _TrackingReleaseComponent(LifecycleComponent):
    """Component that counts _release_resources calls."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.release_count: int = 0

    def _release_resources(self) -> None:
        self.release_count += 1
        super()._release_resources()


class _CrashingActivateComponent(LifecycleComponent):
    """Component that raises during _on_activate."""

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        raise RuntimeError("activate crash")
