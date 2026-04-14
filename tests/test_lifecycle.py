"""Tests for lifecycle hook propagation through the guard decorator."""

from __future__ import annotations

import pytest
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.core import ComposedLifecycleNode, LifecycleComponent

# ---------------------------------------------------------------------------
# Instrumented component that records which hooks were called
# ---------------------------------------------------------------------------


class RecordingComponent(LifecycleComponent):
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

    def _release_resources(self) -> None:
        super()._release_resources()


class CrashingComponent(LifecycleComponent):
    """Component that raises during _on_configure to test the guard."""

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        raise RuntimeError("boom")

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


@pytest.fixture()
def node():
    n = ComposedLifecycleNode("lifecycle_test_node")
    yield n
    n.destroy_node()


DUMMY_STATE = LifecycleState(state_id=0, label="test")


# ---------------------------------------------------------------------------
# 5.2  Tests lifecycle
# ---------------------------------------------------------------------------


class TestLifecycleHooks:
    def test_hooks_called_in_order(self, node: ComposedLifecycleNode) -> None:
        comp = RecordingComponent("rec")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_deactivate(DUMMY_STATE)
        comp.on_cleanup(DUMMY_STATE)

        assert comp.calls == ["configure", "activate", "deactivate", "cleanup"]

    def test_configure_failure_returns_failure(self, node: ComposedLifecycleNode) -> None:
        comp = RecordingComponent("fail_cfg", fail_on="configure")
        node.add_component(comp)

        result = comp.on_configure(DUMMY_STATE)
        assert result == TransitionCallbackReturn.FAILURE

    def test_guard_catches_exception_returns_error(self, node: ComposedLifecycleNode) -> None:
        comp = CrashingComponent("crasher")
        node.add_component(comp)

        result = comp.on_configure(DUMMY_STATE)
        assert result == TransitionCallbackReturn.ERROR

    def test_activate_deactivate_cycle(self, node: ComposedLifecycleNode) -> None:
        comp = RecordingComponent("cycle")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_deactivate(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_deactivate(DUMMY_STATE)
        comp.on_cleanup(DUMMY_STATE)

        assert comp.calls == ["configure", "activate", "deactivate", "activate", "deactivate", "cleanup"]
