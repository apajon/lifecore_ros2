"""Regression tests for Sprint 9 structured lifecycle logging.

Assertions target field presence (component=, hook=, result=, duration_ms=,
transition=, action=) rather than exact message strings so that minor wording
changes do not break these tests.
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from lifecore_ros2.core import LifecycleComponent, LifecycleComponentNode
from lifecore_ros2.core.lifecycle_component import when_active
from lifecore_ros2.testing import DUMMY_STATE, FailingComponent, FakeComponent
from lifecore_ros2.testing.helpers import collect_logs, expect_log

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_COMPONENT_LOGGER = logging.getLogger("lifecore_ros2.core.lifecycle_component")


def _capture_component_logs(fn: object) -> list[str]:
    """Run *fn* and return DEBUG+ log messages from the component logger."""
    _COMPONENT_LOGGER.setLevel(logging.DEBUG)
    return collect_logs(_COMPONENT_LOGGER, fn)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Component-level hook logging (unattached — uses Python stdlib logger)
# ---------------------------------------------------------------------------


class TestComponentHookDebugLogs:
    def test_start_debug_emitted(self) -> None:
        comp = FakeComponent("c1")
        logs = _capture_component_logs(lambda: comp.on_configure(DUMMY_STATE))

        msg = expect_log(logs, r"action='start'")
        assert "component='c1'" in msg
        assert "hook='on_configure'" in msg

    def test_end_debug_has_result_and_duration(self) -> None:
        comp = FakeComponent("c2")
        logs = _capture_component_logs(lambda: comp.on_configure(DUMMY_STATE))

        msg = expect_log(logs, r"result='SUCCESS'")
        assert "component='c2'" in msg
        assert "hook='on_configure'" in msg
        assert "duration_ms=" in msg

    def test_hook_failure_result_logged(self) -> None:
        comp = FakeComponent("c3", fail_at_hook="configure")
        logs = _capture_component_logs(lambda: comp.on_configure(DUMMY_STATE))

        msg = expect_log(logs, r"result='FAILURE'")
        assert "component='c3'" in msg

    def test_hook_exception_error_not_duplicated(self) -> None:
        comp = FailingComponent("c4", fail_at_hook="_on_configure", exception=RuntimeError("boom"))
        logs = _capture_component_logs(lambda: comp.on_configure(DUMMY_STATE))

        error_logs = [m for m in logs if "boom" in m or "LifecycleHookError" in m or "raised RuntimeError" in m]
        # The error is captured once by _guarded_call — not duplicated
        assert len([m for m in error_logs if "raised RuntimeError" in m]) == 1

    def test_withdrawn_component_emits_no_debug(self) -> None:
        node = LifecycleComponentNode("obs_withdrawn_node")
        comp = FakeComponent("wd")
        node.add_component(comp)
        node.remove_component("wd")

        logs = _capture_component_logs(lambda: comp.on_configure(DUMMY_STATE))
        assert not any("component='wd'" in m for m in logs)
        node.destroy_node()

    def test_release_resources_debug_emitted(self) -> None:
        comp = FakeComponent("c5")
        comp.on_configure(DUMMY_STATE)
        logs = _capture_component_logs(lambda: comp.on_cleanup(DUMMY_STATE))

        msg = expect_log(logs, r"action='release_resources'")
        assert "component='c5'" in msg


# ---------------------------------------------------------------------------
# @when_active no-op activation gating log
# ---------------------------------------------------------------------------


class _GatedComponent(LifecycleComponent):
    def __init__(self) -> None:
        super().__init__("gated")

    @when_active(when_not_active=None)
    def do_work(self) -> None:
        pass  # pragma: no cover


class TestWhenActiveDroppedLog:
    def test_dropped_debug_has_required_fields(self) -> None:
        comp = _GatedComponent()
        # Component is inactive (never activated) — do_work is a silent no-op.
        logs = _capture_component_logs(comp.do_work)

        msg = expect_log(logs, r"action='dropped'")
        assert "component='gated'" in msg
        assert "method='do_work'" in msg
        assert "reason='not_active'" in msg


# ---------------------------------------------------------------------------
# Node-level transition logging (mocked rclpy logger)
# ---------------------------------------------------------------------------


@pytest.fixture()
def node_with_comp() -> tuple[LifecycleComponentNode, FakeComponent]:
    n = LifecycleComponentNode("obs_node")
    c = FakeComponent("nc")
    n.add_component(c)
    return n, c


class TestNodeTransitionInfoLog:
    def test_configure_info_on_success(self, node_with_comp: tuple[LifecycleComponentNode, FakeComponent]) -> None:
        node, _ = node_with_comp
        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            node.on_configure(DUMMY_STATE)
        node.destroy_node()

        info_msgs = [call.args[0] for call in mock_logger.info.call_args_list]
        assert any("transition='configure'" in m and "result='SUCCESS'" in m for m in info_msgs)

    def test_configure_debug_before_propagation(
        self, node_with_comp: tuple[LifecycleComponentNode, FakeComponent]
    ) -> None:
        node, _ = node_with_comp
        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            node.on_configure(DUMMY_STATE)
        node.destroy_node()

        debug_msgs = [call.args[0] for call in mock_logger.debug.call_args_list]
        assert any("transition='configure'" in m and "component_count=" in m for m in debug_msgs)

    def test_activate_info_on_success(self) -> None:
        node = LifecycleComponentNode("obs_act_node")
        node.add_component(FakeComponent("a"))
        node.on_configure(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            node.on_activate(DUMMY_STATE)
        node.destroy_node()

        info_msgs = [call.args[0] for call in mock_logger.info.call_args_list]
        assert any("transition='activate'" in m and "result='SUCCESS'" in m for m in info_msgs)

    def test_deactivate_info_on_success(self) -> None:
        node = LifecycleComponentNode("obs_deact_node")
        node.add_component(FakeComponent("d"))
        node.on_configure(DUMMY_STATE)
        node.on_activate(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            node.on_deactivate(DUMMY_STATE)
        node.destroy_node()

        info_msgs = [call.args[0] for call in mock_logger.info.call_args_list]
        assert any("transition='deactivate'" in m and "result='SUCCESS'" in m for m in info_msgs)

    def test_cleanup_info_on_success(self) -> None:
        node = LifecycleComponentNode("obs_cleanup_node")
        node.add_component(FakeComponent("cl"))
        node.on_configure(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            node.on_cleanup(DUMMY_STATE)
        node.destroy_node()

        info_msgs = [call.args[0] for call in mock_logger.info.call_args_list]
        assert any("transition='cleanup'" in m and "result='SUCCESS'" in m for m in info_msgs)

    def test_shutdown_info_on_success(self) -> None:
        node = LifecycleComponentNode("obs_shutdown_node")
        node.add_component(FakeComponent("sh"))

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            node.on_shutdown(DUMMY_STATE)
        node.destroy_node()

        info_msgs = [call.args[0] for call in mock_logger.info.call_args_list]
        assert any("transition='shutdown'" in m and "result='SUCCESS'" in m for m in info_msgs)

    def test_error_warning_emitted(self) -> None:
        node = LifecycleComponentNode("obs_err_node")
        node.add_component(FakeComponent("e"))
        node.on_configure(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            node.on_error(DUMMY_STATE)
        node.destroy_node()

        warn_msgs = [call.args[0] for call in mock_logger.warning.call_args_list]
        assert any("transition='error_processing'" in m and "component_count=" in m for m in warn_msgs)

    def test_error_info_on_success(self) -> None:
        node = LifecycleComponentNode("obs_err_ok_node")
        node.add_component(FakeComponent("eo"))
        node.on_configure(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            node.on_error(DUMMY_STATE)
        node.destroy_node()

        info_msgs = [call.args[0] for call in mock_logger.info.call_args_list]
        assert any("transition='error_processing'" in m and "result='SUCCESS'" in m for m in info_msgs)
