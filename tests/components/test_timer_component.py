"""Regression tests for LifecycleTimerComponent lifecycle, activation gating, and controls.

Coverage map (this file):
    TestTimerComponent — configure / activate / deactivate / cleanup / period / callback_group / gating
    TestTimerControls  — autostart, start, stop, reset, error paths

See also:
    tests/components/test_components.py — callback_group propagation for publisher and subscriber
"""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from rclpy.callback_groups import CallbackGroup
from rclpy.lifecycle import TransitionCallbackReturn

from lifecore_ros2.components import LifecycleTimerComponent
from lifecore_ros2.core import ComponentNotConfiguredError, LifecycleComponentNode
from tests.components._topic_stubs import DUMMY_STATE, StubTimer

# ---------------------------------------------------------------------------
# Timer lifecycle and activation gating
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestTimerComponent:
    def test_inactive_ticks_ignored(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer()
        node.add_component(timer)

        timer.on_configure(DUMMY_STATE)
        # not activated yet → ticks should be dropped
        timer._on_timer_wrapper()

        assert timer.ticks == 0

    def test_active_ticks_routed_to_on_tick(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer()
        node.add_component(timer)

        timer.on_configure(DUMMY_STATE)
        timer.on_activate(DUMMY_STATE)

        timer._on_timer_wrapper()
        timer._on_timer_wrapper()
        assert timer.ticks == 2

    def test_deactivate_stops_ticks(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer()
        node.add_component(timer)

        timer.on_configure(DUMMY_STATE)
        timer.on_activate(DUMMY_STATE)
        timer._on_timer_wrapper()
        timer.on_deactivate(DUMMY_STATE)

        timer._on_timer_wrapper()
        assert timer.ticks == 1

    def test_cleanup_destroys_timer(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer()
        node.add_component(timer)

        timer.on_configure(DUMMY_STATE)
        timer.on_activate(DUMMY_STATE)
        timer.on_deactivate(DUMMY_STATE)
        result = timer.on_cleanup(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        assert not timer.is_active
        assert timer._timer is None

    def test_configure_creates_timer_with_period(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer(period=0.25)
        node.add_component(timer)

        with patch.object(node, "create_timer", return_value=MagicMock()) as mock_create:
            result = timer.on_configure(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        assert timer._timer is not None
        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args
        assert args[0] == 0.25  # period_sec
        assert args[1] == timer._on_timer_wrapper
        assert kwargs["callback_group"] is None

    def test_period_accepts_duration(self) -> None:
        from rclpy.duration import Duration

        timer = StubTimer(period=Duration(seconds=0, nanoseconds=500_000_000))  # type: ignore[arg-type]
        assert timer.period_sec == 0.5

    def test_non_positive_period_raises(self) -> None:
        with pytest.raises(ValueError, match="must be > 0"):
            StubTimer(period=0.0)
        with pytest.raises(ValueError, match="must be > 0"):
            StubTimer(period=-1.0)

    def test_callback_group_propagated_to_create_timer(self, node: LifecycleComponentNode) -> None:
        cg = MagicMock(spec=CallbackGroup)

        class _CbTimer(LifecycleTimerComponent):
            def on_tick(self) -> None: ...

        timer = _CbTimer(name="cb_timer", period=0.1, callback_group=cg)
        node.add_component(timer)

        timer.on_configure(DUMMY_STATE)

        assert cast(MagicMock, node.create_timer).call_args.kwargs["callback_group"] is cg

    def test_user_exception_in_on_tick_does_not_propagate(self, node: LifecycleComponentNode) -> None:
        class _BadTimer(LifecycleTimerComponent):
            def on_tick(self) -> None:
                raise RuntimeError("boom")

        timer = _BadTimer(name="bad_timer", period=0.1)
        node.add_component(timer)
        timer.on_configure(DUMMY_STATE)
        timer.on_activate(DUMMY_STATE)

        # Rule C (inbound): the wrapper must swallow user exceptions.
        timer._on_timer_wrapper()

    def test_callback_group_keyword_only(self) -> None:
        cg = MagicMock(spec=CallbackGroup)
        positional_args: tuple[Any, ...] = ("kw_timer", 1.0, cg)
        with pytest.raises(TypeError):
            LifecycleTimerComponent(*positional_args)  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# Timer controls: autostart, start, stop, reset
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestTimerControls:
    def test_autostart_true_leaves_timer_running(self, node: LifecycleComponentNode) -> None:
        fake_timer = MagicMock()
        fake_timer.is_canceled.return_value = False
        with patch.object(node, "create_timer", return_value=fake_timer) as mock_create:
            timer = StubTimer()
            node.add_component(timer)
            timer.on_configure(DUMMY_STATE)

        assert mock_create.call_args.kwargs["autostart"] is True
        assert timer.is_running is True

    def test_autostart_false_creates_canceled_timer(self, node: LifecycleComponentNode) -> None:
        fake_timer = MagicMock()
        # rclpy's create_timer(autostart=False) yields a canceled timer.
        fake_timer.is_canceled.return_value = True

        class _ManualTimer(LifecycleTimerComponent):
            def on_tick(self) -> None: ...

        with patch.object(node, "create_timer", return_value=fake_timer) as mock_create:
            timer = _ManualTimer(name="manual_timer", period=0.1, autostart=False)
            node.add_component(timer)
            timer.on_configure(DUMMY_STATE)

        assert mock_create.call_args.kwargs["autostart"] is False
        assert timer.autostart is False
        assert timer.is_running is False

    def test_start_resumes_canceled_timer(self, node: LifecycleComponentNode) -> None:
        fake_timer = MagicMock()
        fake_timer.is_canceled.return_value = True

        class _ManualTimer(LifecycleTimerComponent):
            def on_tick(self) -> None: ...

        with patch.object(node, "create_timer", return_value=fake_timer):
            timer = _ManualTimer(name="manual_timer", period=0.1, autostart=False)
            node.add_component(timer)
            timer.on_configure(DUMMY_STATE)
            fake_timer.cancel.reset_mock()

            timer.start()

        fake_timer.reset.assert_called_once()

    def test_start_is_noop_when_already_running(self, node: LifecycleComponentNode) -> None:
        fake_timer = MagicMock()
        fake_timer.is_canceled.return_value = False
        with patch.object(node, "create_timer", return_value=fake_timer):
            timer = StubTimer()
            node.add_component(timer)
            timer.on_configure(DUMMY_STATE)

            timer.start()

        fake_timer.reset.assert_not_called()

    def test_stop_cancels_timer(self, node: LifecycleComponentNode) -> None:
        fake_timer = MagicMock()
        fake_timer.is_canceled.return_value = False
        with patch.object(node, "create_timer", return_value=fake_timer):
            timer = StubTimer()
            node.add_component(timer)
            timer.on_configure(DUMMY_STATE)

            timer.stop()

        fake_timer.cancel.assert_called_once()

    def test_reset_restarts_timer(self, node: LifecycleComponentNode) -> None:
        fake_timer = MagicMock()
        fake_timer.is_canceled.return_value = False
        with patch.object(node, "create_timer", return_value=fake_timer):
            timer = StubTimer()
            node.add_component(timer)
            timer.on_configure(DUMMY_STATE)

            timer.reset()

        fake_timer.reset.assert_called_once()

    def test_controls_raise_when_not_configured(self) -> None:
        timer = StubTimer()

        with pytest.raises(ComponentNotConfiguredError):
            timer.start()
        with pytest.raises(ComponentNotConfiguredError):
            timer.stop()
        with pytest.raises(ComponentNotConfiguredError):
            timer.reset()

    def test_controls_raise_after_cleanup(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer()
        node.add_component(timer)
        timer.on_configure(DUMMY_STATE)
        timer.on_cleanup(DUMMY_STATE)

        with pytest.raises(ComponentNotConfiguredError):
            timer.start()
        with pytest.raises(ComponentNotConfiguredError):
            timer.stop()
        with pytest.raises(ComponentNotConfiguredError):
            timer.reset()
