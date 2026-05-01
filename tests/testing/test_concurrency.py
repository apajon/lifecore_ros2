from __future__ import annotations

import threading

import pytest
from rclpy.lifecycle import TransitionCallbackReturn

from lifecore_ros2.testing import assert_no_race, barrier_hook, spawn_transition_thread
from lifecore_ros2.testing.fakes import DUMMY_STATE


class _TriggerRecorder:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def trigger_configure(self) -> TransitionCallbackReturn:
        self.calls.append("configure")
        return TransitionCallbackReturn.SUCCESS

    def trigger_activate(self) -> TransitionCallbackReturn:
        self.calls.append("activate")
        return TransitionCallbackReturn.SUCCESS

    def trigger_deactivate(self) -> TransitionCallbackReturn:
        self.calls.append("deactivate")
        return TransitionCallbackReturn.SUCCESS

    def trigger_cleanup(self) -> TransitionCallbackReturn:
        self.calls.append("cleanup")
        return TransitionCallbackReturn.SUCCESS

    def trigger_shutdown(self) -> TransitionCallbackReturn:
        self.calls.append("shutdown")
        return TransitionCallbackReturn.SUCCESS


def test_spawn_transition_thread_runs_transition() -> None:
    node = _TriggerRecorder()

    result = spawn_transition_thread(node, "configure")

    assert result.join(timeout=1.0) == TransitionCallbackReturn.SUCCESS
    assert node.calls == ["configure"]


def test_spawn_transition_thread_rejects_unknown_transition() -> None:
    with pytest.raises(ValueError, match="Unknown lifecycle transition"):
        spawn_transition_thread(_TriggerRecorder(), "missing")


def test_assert_no_race_runs_test_repeatedly() -> None:
    calls: list[int] = []

    assert_no_race(lambda: calls.append(1), attempts=3)

    assert calls == [1, 1, 1]


def test_barrier_hook_blocks_until_released() -> None:
    barrier = threading.Barrier(2)
    hook = barrier_hook(barrier)
    results: list[TransitionCallbackReturn] = []

    thread = threading.Thread(target=lambda: results.append(hook(DUMMY_STATE)))
    thread.start()
    barrier.wait(timeout=1.0)
    thread.join(timeout=1.0)

    assert results == [TransitionCallbackReturn.SUCCESS]
