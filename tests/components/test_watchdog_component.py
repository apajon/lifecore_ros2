"""Regression tests for LifecycleWatchdogComponent (Sprint 11).

Coverage:
    AC1  — DEGRADED health triggers WARN log with component name and reason.
    AC2  — ERROR health triggers ERROR log including last_error.
    AC3  — Persistent non-OK level beyond stale_threshold triggers STALE WARN.
    AC4  — Polling runs only while active (activation gating via _on_timer_wrapper).
    AC5  — Watchdog never calls lifecycle transition methods (read-only).
    AC6  — LifecycleComponentNode accepted as target; node.health read correctly.
    AC7  — Public import: ``from lifecore_ros2 import LifecycleWatchdogComponent``.
    AC8  — Covered by examples/minimal_watchdog.py.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from rclpy.clock import ClockType
from rclpy.time import Time

import lifecore_ros2
from lifecore_ros2.components import LifecycleWatchdogComponent
from lifecore_ros2.core import HealthLevel, HealthStatus, LifecycleComponentNode
from lifecore_ros2.testing import DUMMY_STATE, FakeComponent

# ---------------------------------------------------------------------------
# AC7 — Public import
# ---------------------------------------------------------------------------


class TestPublicImport:
    """LifecycleWatchdogComponent is importable directly from lifecore_ros2."""

    def test_importable_from_top_level(self) -> None:
        assert hasattr(lifecore_ros2, "LifecycleWatchdogComponent")
        assert lifecore_ros2.LifecycleWatchdogComponent is LifecycleWatchdogComponent

    def test_in_all(self) -> None:
        assert "LifecycleWatchdogComponent" in lifecore_ros2.__all__


# ---------------------------------------------------------------------------
# Constructor validation
# ---------------------------------------------------------------------------


class TestConstructorValidation:
    """Invalid constructor arguments raise ValueError before any node is attached."""

    def test_stale_threshold_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="stale_threshold must be > 0"):
            LifecycleWatchdogComponent("w", [], poll_period=1.0, stale_threshold=0.0)

    def test_stale_threshold_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="stale_threshold must be > 0"):
            LifecycleWatchdogComponent("w", [], poll_period=1.0, stale_threshold=-1.0)

    def test_poll_period_zero_raises(self) -> None:
        # Delegated to LifecycleTimerComponent
        with pytest.raises(ValueError, match="must be > 0"):
            LifecycleWatchdogComponent("w", [], poll_period=0.0, stale_threshold=5.0)

    def test_stale_threshold_property(self) -> None:
        watchdog = LifecycleWatchdogComponent("w", [], poll_period=1.0, stale_threshold=10.0)
        assert watchdog.stale_threshold == 10.0


# ---------------------------------------------------------------------------
# Configure initialises watch states
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestConfigure:
    """_on_configure initialises per-target tracking state."""

    def test_configure_creates_watch_state_per_target(self, node: LifecycleComponentNode) -> None:
        comp_a = FakeComponent("a")
        comp_b = FakeComponent("b")
        node.add_component(comp_a)
        node.add_component(comp_b)
        watchdog = LifecycleWatchdogComponent("watchdog", [comp_a, comp_b], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)

        watchdog.on_configure(DUMMY_STATE)

        assert id(comp_a) in watchdog._watch_states
        assert id(comp_b) in watchdog._watch_states

    def test_configure_captures_initial_health_level(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        # Force DEGRADED health after configure
        comp._health = HealthStatus(level=HealthLevel.DEGRADED, reason="pre-existing fault")

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)

        assert watchdog._watch_states[id(comp)].last_level == HealthLevel.DEGRADED

    def test_empty_targets_configure_succeeds(self, node: LifecycleComponentNode) -> None:
        from rclpy.lifecycle import TransitionCallbackReturn

        watchdog = LifecycleWatchdogComponent("watchdog", [], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)

        result = watchdog.on_configure(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        assert watchdog._watch_states == {}


# ---------------------------------------------------------------------------
# AC1 — DEGRADED → WARN log
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestDegradedLogging:
    """AC1: DEGRADED health level triggers a WARN log on each tick."""

    def test_degraded_logs_warn_with_reason(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        comp._health = HealthStatus(level=HealthLevel.DEGRADED, reason="hardware fault")

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog.on_tick()

        assert mock_logger.warn.call_count >= 1
        warn_message = mock_logger.warn.call_args_list[0][0][0]
        assert "sensor" in warn_message
        assert "DEGRADED" in warn_message
        assert "hardware fault" in warn_message

    def test_ok_health_does_not_log_warn(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)  # health = OK

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog.on_tick()

        mock_logger.warn.assert_not_called()
        mock_logger.error.assert_not_called()

    def test_unknown_health_is_silent(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        # health stays UNKNOWN — component never configured

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog.on_tick()

        mock_logger.warn.assert_not_called()
        mock_logger.error.assert_not_called()


# ---------------------------------------------------------------------------
# AC2 — ERROR → ERROR log with last_error
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestErrorLogging:
    """AC2: ERROR health triggers an ERROR log; last_error is included when set."""

    def test_error_logs_error_with_reason(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp._health = HealthStatus(level=HealthLevel.ERROR, reason="sensor crashed")

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog.on_tick()

        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "sensor" in error_message
        assert "ERROR" in error_message
        assert "sensor crashed" in error_message

    def test_error_includes_last_error_when_set(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp._health = HealthStatus(
            level=HealthLevel.ERROR,
            reason="hook failed",
            last_error="[sensor.on_configure] raised RuntimeError: boom",
        )

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog.on_tick()

        error_message = mock_logger.error.call_args[0][0]
        assert "boom" in error_message

    def test_error_omits_last_error_suffix_when_none(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp._health = HealthStatus(level=HealthLevel.ERROR, reason="crash", last_error=None)

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog.on_tick()

        error_message = mock_logger.error.call_args[0][0]
        assert "last_error" not in error_message


# ---------------------------------------------------------------------------
# AC3 — Stale detection
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestStaleness:
    """AC3: DEGRADED/ERROR level persisting beyond stale_threshold triggers a STALE WARN."""

    def test_stale_warn_after_threshold_exceeded(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp._health = HealthStatus(level=HealthLevel.DEGRADED, reason="persistent fault")

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)

        # Simulate time passing beyond the stale threshold.
        # ROS epoch (t=0) with the correct clock type is effectively very far in the
        # past relative to the live node clock, so elapsed >> stale_threshold.
        watchdog._watch_states[id(comp)].last_change_time = Time(nanoseconds=0, clock_type=ClockType.ROS_TIME)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog.on_tick()

        stale_calls = [c for c in mock_logger.warn.call_args_list if "STALE" in c[0][0]]
        assert len(stale_calls) == 1
        assert "degraded" in stale_calls[0][0][0]

    def test_no_stale_warn_below_threshold(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp._health = HealthStatus(level=HealthLevel.DEGRADED, reason="fault")

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)

        # Elapsed time is small — well below the 5 s threshold.
        # (last_change_time was just set by _on_configure; elapsed ≈ 0)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog.on_tick()

        stale_calls = [c for c in mock_logger.warn.call_args_list if "STALE" in c[0][0]]
        assert len(stale_calls) == 0

    def test_stale_resets_when_level_changes_to_ok(self, node: LifecycleComponentNode) -> None:
        """Level change resets last_change_time; stale clock does not carry over."""
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp._health = HealthStatus(level=HealthLevel.DEGRADED, reason="fault")

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)

        # Age the stale clock — ROS epoch with matching clock type ensures elapsed >> stale_threshold.
        watchdog._watch_states[id(comp)].last_change_time = Time(nanoseconds=0, clock_type=ClockType.ROS_TIME)

        # Component recovers to OK
        comp._health = HealthStatus(level=HealthLevel.OK, reason="")

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog.on_tick()

        mock_logger.warn.assert_not_called()
        mock_logger.error.assert_not_called()

    def test_stale_triggered_for_error_level(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp._health = HealthStatus(level=HealthLevel.ERROR, reason="crash")

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)

        watchdog._watch_states[id(comp)].last_change_time = Time(nanoseconds=0, clock_type=ClockType.ROS_TIME)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog.on_tick()

        stale_calls = [c for c in mock_logger.warn.call_args_list if "STALE" in c[0][0]]
        assert len(stale_calls) == 1
        assert "error" in stale_calls[0][0][0]


# ---------------------------------------------------------------------------
# AC4 — Activation gating
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestActivationGating:
    """AC4: Polling (and logging) only occurs while the watchdog is active."""

    def test_tick_dropped_when_not_active(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp._health = HealthStatus(level=HealthLevel.DEGRADED, reason="fault")

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        # Deliberately NOT activating — watchdog is inactive

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog._on_timer_wrapper()  # gated tick: should not reach on_tick

        mock_logger.warn.assert_not_called()
        mock_logger.error.assert_not_called()

    def test_deactivate_stops_polling(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp._health = HealthStatus(level=HealthLevel.DEGRADED, reason="fault")

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)
        watchdog.on_deactivate(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog._on_timer_wrapper()

        mock_logger.warn.assert_not_called()
        mock_logger.error.assert_not_called()


# ---------------------------------------------------------------------------
# AC5 — Read-only: watchdog never triggers lifecycle transitions
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestReadOnly:
    """AC5: The watchdog only reads health; it never calls lifecycle methods."""

    def test_on_tick_does_not_call_lifecycle_methods(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)
        comp._health = HealthStatus(level=HealthLevel.ERROR, reason="crash")

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)

        calls_before = list(comp.calls)
        with patch.object(node, "get_logger", return_value=MagicMock()):
            watchdog.on_tick()

        # No additional lifecycle hook calls recorded on the target
        assert comp.calls == calls_before


# ---------------------------------------------------------------------------
# AC6 — LifecycleComponentNode as target
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestNodeTarget:
    """AC6: Watchdog accepts a LifecycleComponentNode and reads its aggregated health."""

    def test_accepts_node_as_target(self, node: LifecycleComponentNode) -> None:
        # node.health is HEALTH_UNKNOWN (no resolved order yet) → silent
        watchdog = LifecycleWatchdogComponent("watchdog", [node], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(node, "get_logger", return_value=mock_logger):
            watchdog.on_tick()

        # UNKNOWN is silent
        mock_logger.warn.assert_not_called()
        mock_logger.error.assert_not_called()

    def test_node_name_used_in_log(self, node: LifecycleComponentNode) -> None:
        """Node name appears in STALE log when node health is non-OK."""
        # Patch node.health to return DEGRADED
        degraded = HealthStatus(level=HealthLevel.DEGRADED, reason="agg fault")
        watchdog = LifecycleWatchdogComponent("watchdog", [node], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)

        with patch.object(type(node), "health", new_callable=lambda: property(lambda self: degraded)):
            watchdog.on_configure(DUMMY_STATE)
            watchdog.on_activate(DUMMY_STATE)
            watchdog._watch_states[id(node)].last_change_time = Time(nanoseconds=0, clock_type=ClockType.ROS_TIME)

            mock_logger = MagicMock()
            with patch.object(node, "get_logger", return_value=mock_logger):
                watchdog.on_tick()

        node_name = node.get_name()
        all_warn_msgs = " ".join(c[0][0] for c in mock_logger.warn.call_args_list)
        assert node_name in all_warn_msgs


# ---------------------------------------------------------------------------
# Cleanup releases state
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestCleanup:
    """Cleanup clears per-target tracking state."""

    def test_cleanup_clears_watch_states(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("sensor")
        node.add_component(comp)

        watchdog = LifecycleWatchdogComponent("watchdog", [comp], poll_period=0.1, stale_threshold=5.0)
        node.add_component(watchdog)
        watchdog.on_configure(DUMMY_STATE)
        watchdog.on_activate(DUMMY_STATE)
        watchdog.on_deactivate(DUMMY_STATE)
        watchdog.on_cleanup(DUMMY_STATE)

        assert watchdog._watch_states == {}
