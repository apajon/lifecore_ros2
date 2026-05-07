"""Regression tests for Sprint 7 _needs_cleanup reset policy.

Verifies that on_cleanup, on_shutdown, and on_error reset _needs_cleanup to False
unconditionally — even when _release_resources() raises an exception.

Coverage:
    TestNeedsCleanupReset — _needs_cleanup = False after failed release attempt
"""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import patch

import pytest
from rclpy.lifecycle import TransitionCallbackReturn

from lifecore_ros2.core import LifecycleComponentNode
from lifecore_ros2.testing import DUMMY_STATE, FakeComponent


@pytest.fixture()
def node() -> Generator[LifecycleComponentNode, None, None]:
    n = LifecycleComponentNode("cleanup_policy_test_node")
    yield n
    n.destroy_node()


class TestNeedsCleanupReset:
    def test_needs_cleanup_false_after_cleanup_when_release_fails(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("release_fail_cleanup")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        assert comp._needs_cleanup is True

        with patch.object(comp, "_release_resources", side_effect=RuntimeError("destroy failed")):
            result = comp.on_cleanup(DUMMY_STATE)

        assert result == TransitionCallbackReturn.ERROR
        assert comp._needs_cleanup is False

    def test_needs_cleanup_false_after_shutdown_when_release_fails(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("release_fail_shutdown")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)

        with patch.object(comp, "_release_resources", side_effect=RuntimeError("destroy failed")):
            result = comp.on_shutdown(DUMMY_STATE)

        assert result == TransitionCallbackReturn.ERROR
        assert comp._needs_cleanup is False

    def test_needs_cleanup_false_after_error_when_release_fails(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("release_fail_error")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)

        with patch.object(comp, "_release_resources", side_effect=RuntimeError("destroy failed")):
            result = comp.on_error(DUMMY_STATE)

        assert result == TransitionCallbackReturn.ERROR
        assert comp._needs_cleanup is False

    def test_transition_result_still_error_when_hook_succeeds_and_release_fails(
        self, node: LifecycleComponentNode
    ) -> None:
        """Release failure propagates into the returned transition result."""
        comp = FakeComponent("result_propagation")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)

        with patch.object(comp, "_release_resources", side_effect=RuntimeError("destroy failed")):
            result = comp.on_cleanup(DUMMY_STATE)

        assert result == TransitionCallbackReturn.ERROR

    def test_needs_cleanup_false_after_successful_cleanup(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("clean_cleanup")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        assert comp._needs_cleanup is True

        result = comp.on_cleanup(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        assert comp._needs_cleanup is False
