"""Tests for lifecycle hook propagation through the guard decorator."""

from __future__ import annotations

import pytest
from rclpy.lifecycle import TransitionCallbackReturn

from lifecore_ros2.core import LifecycleComponentNode
from tests.helpers.lifecycle import (
    TEST_STATE,
    FakeLifecycleComponent,
    assert_component_active,
    assert_component_inactive,
    assert_contract_state,
    assert_hook_order,
    assert_transition_success,
)

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
        comp = FakeLifecycleComponent("rec")
        node.add_component(comp)

        assert_transition_success(comp, "configure", comp.on_configure(TEST_STATE))
        assert_transition_success(comp, "activate", comp.on_activate(TEST_STATE))
        assert_transition_success(comp, "deactivate", comp.on_deactivate(TEST_STATE))
        assert_transition_success(comp, "cleanup", comp.on_cleanup(TEST_STATE))

        assert_hook_order(comp, ["configure", "activate", "deactivate", "cleanup"])

    def test_configure_failure_returns_failure(self, node: LifecycleComponentNode) -> None:
        comp = FakeLifecycleComponent("fail_cfg", fail_on="configure")
        node.add_component(comp)

        result = comp.on_configure(TEST_STATE)
        assert result == TransitionCallbackReturn.FAILURE
        assert_hook_order(comp, ["configure"])

    def test_guard_catches_exception_returns_error(self, node: LifecycleComponentNode) -> None:
        comp = FakeLifecycleComponent("crasher", raise_on="configure", exception=RuntimeError("boom"))
        node.add_component(comp)

        result = comp.on_configure(TEST_STATE)
        assert result == TransitionCallbackReturn.ERROR
        assert_hook_order(comp, ["configure"])

    def test_activate_deactivate_cycle(self, node: LifecycleComponentNode) -> None:
        comp = FakeLifecycleComponent("cycle")
        node.add_component(comp)

        assert_transition_success(comp, "configure", comp.on_configure(TEST_STATE))
        assert_transition_success(comp, "activate", comp.on_activate(TEST_STATE))
        assert_transition_success(comp, "deactivate", comp.on_deactivate(TEST_STATE))
        assert_transition_success(comp, "activate", comp.on_activate(TEST_STATE))
        assert_transition_success(comp, "deactivate", comp.on_deactivate(TEST_STATE))
        assert_transition_success(comp, "cleanup", comp.on_cleanup(TEST_STATE))

        assert_hook_order(comp, ["configure", "activate", "deactivate", "activate", "deactivate", "cleanup"])


# ---------------------------------------------------------------------------
# 5.2b  _is_active flag at each transition step
# ---------------------------------------------------------------------------


class TestLifecycleComponentActivation:
    def test_is_active_false_after_configure(self, node: LifecycleComponentNode) -> None:
        comp = FakeLifecycleComponent("track")
        node.add_component(comp)

        assert_transition_success(comp, "configure", comp.on_configure(TEST_STATE))
        assert_contract_state(comp, "inactive")

    def test_is_active_true_after_activate(self, node: LifecycleComponentNode) -> None:
        comp = FakeLifecycleComponent("track")
        node.add_component(comp)

        assert_transition_success(comp, "configure", comp.on_configure(TEST_STATE))
        assert_transition_success(comp, "activate", comp.on_activate(TEST_STATE))
        assert_component_active(comp)

    def test_is_active_false_after_deactivate(self, node: LifecycleComponentNode) -> None:
        comp = FakeLifecycleComponent("track")
        node.add_component(comp)

        assert_transition_success(comp, "configure", comp.on_configure(TEST_STATE))
        assert_transition_success(comp, "activate", comp.on_activate(TEST_STATE))
        assert_transition_success(comp, "deactivate", comp.on_deactivate(TEST_STATE))
        assert_component_inactive(comp)

    def test_is_active_false_after_cleanup(self, node: LifecycleComponentNode) -> None:
        comp = FakeLifecycleComponent("track")
        node.add_component(comp)

        assert_transition_success(comp, "configure", comp.on_configure(TEST_STATE))
        assert_transition_success(comp, "activate", comp.on_activate(TEST_STATE))
        assert_transition_success(comp, "deactivate", comp.on_deactivate(TEST_STATE))
        assert_transition_success(comp, "cleanup", comp.on_cleanup(TEST_STATE))
        assert_contract_state(comp, "unconfigured")

    def test_release_resources_clears_is_active(self, node: LifecycleComponentNode) -> None:
        comp = FakeLifecycleComponent("track")
        node.add_component(comp)

        assert_transition_success(comp, "configure", comp.on_configure(TEST_STATE))
        assert_transition_success(comp, "activate", comp.on_activate(TEST_STATE))
        assert_component_active(comp)

        comp._release_resources()
        assert comp.is_active is False
