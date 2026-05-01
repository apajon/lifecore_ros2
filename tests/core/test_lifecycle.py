"""Tests for lifecycle hook propagation through the guard decorator."""

from __future__ import annotations

import pytest
from rclpy.lifecycle import TransitionCallbackReturn

from lifecore_ros2.core import LifecycleComponentNode
from lifecore_ros2.testing import DUMMY_STATE, FailingComponent, FakeComponent

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def node():
    n = LifecycleComponentNode("lifecycle_test_node")
    yield n
    n.destroy_node()


# ---------------------------------------------------------------------------
# 5.2  Tests lifecycle
# ---------------------------------------------------------------------------


class TestLifecycleHooks:
    def test_hooks_called_in_order(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("rec")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_deactivate(DUMMY_STATE)
        comp.on_cleanup(DUMMY_STATE)

        assert comp.calls == ["configure", "activate", "deactivate", "cleanup"]

    def test_configure_failure_returns_failure(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("fail_cfg", fail_at_hook="configure")
        node.add_component(comp)

        result = comp.on_configure(DUMMY_STATE)
        assert result == TransitionCallbackReturn.FAILURE

    def test_guard_catches_exception_returns_error(self, node: LifecycleComponentNode) -> None:
        comp = FailingComponent("crasher", fail_at_hook="configure", exception=RuntimeError("boom"))
        node.add_component(comp)

        result = comp.on_configure(DUMMY_STATE)
        assert result == TransitionCallbackReturn.ERROR

    def test_activate_deactivate_cycle(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("cycle")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_deactivate(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_deactivate(DUMMY_STATE)
        comp.on_cleanup(DUMMY_STATE)

        assert comp.calls == ["configure", "activate", "deactivate", "activate", "deactivate", "cleanup"]


# ---------------------------------------------------------------------------
# 5.2b  _is_active flag at each transition step
# ---------------------------------------------------------------------------


class TestLifecycleComponentActivation:
    def test_is_active_false_after_configure(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("track")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        assert comp.is_active is False

    def test_is_active_true_after_activate(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("track")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.is_active is True

    def test_is_active_false_after_deactivate(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("track")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_deactivate(DUMMY_STATE)
        assert comp.is_active is False

    def test_is_active_false_after_cleanup(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("track")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_deactivate(DUMMY_STATE)
        comp.on_cleanup(DUMMY_STATE)
        assert comp.is_active is False

    def test_release_resources_clears_is_active(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("track")
        node.add_component(comp)

        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.is_active is True

        comp._release_resources()
        assert comp.is_active is False
