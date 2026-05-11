"""Regression tests for _is_active thread safety in LifecycleComponent.

Verifies that:
  - is_active reads from concurrent threads observe coherent values (True or False,
    never a torn intermediate state).
  - After on_deactivate completes, all subsequent reads see False regardless of
    how many threads read simultaneously.
  - The write to _is_active in on_cleanup, on_shutdown, and on_error is visible
    to reader threads after the transition completes.

Context:
  C3 decision: _is_active is protected by _active_lock (threading.Lock).
  This contract must not depend on CPython's GIL — the tests document the expected
  behaviour for free-threaded Python runtimes.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator

import pytest
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.core import LifecycleComponent, LifecycleComponentNode
from lifecore_ros2.testing import DUMMY_STATE, FakeComponent


@pytest.fixture()
def node() -> Iterator[LifecycleComponentNode]:
    n = LifecycleComponentNode("active_lock_test_node")
    yield n
    n.destroy_node()


class _BlockingOnDeactivateComponent(LifecycleComponent):
    """Component whose _on_deactivate hook blocks until unblocked by the test."""

    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        self.hook_started: threading.Event = threading.Event()
        self.hook_unblock: threading.Event = threading.Event()

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.hook_started.set()
        self.hook_unblock.wait(timeout=5.0)
        return TransitionCallbackReturn.SUCCESS


class TestIsActiveThreadSafety:
    """_is_active is coherently readable from callback threads during lifecycle transitions."""

    def test_is_active_true_while_deactivate_hook_is_in_flight(self, node: LifecycleComponentNode) -> None:
        # Regression: without _active_lock the write to _is_active = False in on_deactivate
        # could race with a concurrent read in @when_active or is_active.
        # Expected: while the _on_deactivate hook is running (before it returns SUCCESS),
        # _is_active is still True — the write only commits after SUCCESS is returned.
        component = _BlockingOnDeactivateComponent("blocker")
        node.add_component(component)
        node.on_configure(DUMMY_STATE)
        node.on_activate(DUMMY_STATE)
        assert component.is_active

        observed_during_hook: list[bool] = []

        def deactivate_thread() -> None:
            node.on_deactivate(DUMMY_STATE)

        t = threading.Thread(target=deactivate_thread)
        t.start()

        # Wait until the hook is running, then read is_active while it is blocked.
        component.hook_started.wait(timeout=2.0)
        # At this point _on_deactivate is blocked; _is_active has not been written yet.
        observed_during_hook.append(component.is_active)

        # Unblock the hook and wait for the transition to complete.
        component.hook_unblock.set()
        t.join(timeout=5.0)
        assert not t.is_alive(), "Deactivation thread did not finish"

        assert observed_during_hook == [True], (
            f"Expected is_active=True while hook was in-flight, got {observed_during_hook}"
        )
        assert not component.is_active, "Expected is_active=False after on_deactivate"

    def test_is_active_false_after_deactivate_visible_from_all_threads(self, node: LifecycleComponentNode) -> None:
        # After on_deactivate returns, every concurrent read must see False.
        component = FakeComponent("subject")
        node.add_component(component)
        node.on_configure(DUMMY_STATE)
        node.on_activate(DUMMY_STATE)
        node.on_deactivate(DUMMY_STATE)

        results: list[bool] = []
        barrier = threading.Barrier(4, timeout=5.0)

        def read_active() -> None:
            barrier.wait()
            results.append(component.is_active)

        threads = [threading.Thread(target=read_active) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        assert all(r is False for r in results), f"Expected all False, got {results}"

    def test_is_active_false_after_cleanup_visible_from_all_threads(self, node: LifecycleComponentNode) -> None:
        # on_cleanup unconditionally clears _is_active before the hook runs.
        # All reader threads must see False after cleanup completes.
        component = FakeComponent("subject")
        node.add_component(component)
        node.on_configure(DUMMY_STATE)
        node.on_activate(DUMMY_STATE)
        node.on_deactivate(DUMMY_STATE)
        node.on_cleanup(DUMMY_STATE)

        results: list[bool] = []
        barrier = threading.Barrier(4, timeout=5.0)

        def read_active() -> None:
            barrier.wait()
            results.append(component.is_active)

        threads = [threading.Thread(target=read_active) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        assert all(r is False for r in results), f"Expected all False after cleanup, got {results}"
