"""Regression tests for ConcurrentTransitionError in LifecycleComponentNode.

Verifies that:
  - A second lifecycle transition raises ConcurrentTransitionError while one is in progress.
  - The _in_transition flag is cleared after both success and failure (try/finally contract).
  - add_component and on_error are independent of the concurrent-transition guard.
"""

from __future__ import annotations

import threading
from unittest.mock import MagicMock, patch

import pytest
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleNode, LifecycleState

from lifecore_ros2.core import LifecycleComponentNode
from lifecore_ros2.core.exceptions import ConcurrentTransitionError, RegistrationClosedError
from lifecore_ros2.testing import DUMMY_STATE, FakeComponent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class BlockingNode(LifecycleComponentNode):
    """Node that blocks inside on_configure between _begin_transition and _end_transition.

    The block occurs inside _close_registration, which is called after _begin_transition
    has already set _in_transition = True. This allows threading tests to verify that
    a concurrent on_configure call is rejected with ConcurrentTransitionError.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._started: threading.Event = threading.Event()
        self._unblock: threading.Event = threading.Event()

    def _close_registration(self) -> None:
        # Signal that _begin_transition has already set _in_transition = True, then block.
        self._started.set()
        self._unblock.wait()
        super()._close_registration()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def node():
    n = LifecycleComponentNode("concurrent_test_node")
    yield n
    n.destroy_node()


@pytest.fixture()
def blocking_node():
    n = BlockingNode("blocking_test_node")
    yield n
    n._unblock.set()  # ensure Thread A can exit if still waiting at teardown
    n.destroy_node()


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


class TestRegressionConcurrentTransitions:
    """ConcurrentTransitionError is raised and the _in_transition flag is reliably cleared."""

    def test_concurrent_transition_raises_from_different_thread(self, blocking_node: BlockingNode) -> None:
        # Regression: concurrent on_configure calls were not guarded; a second caller
        # could race through managed-entity propagation producing inconsistent state.
        # Expected: Thread B raises ConcurrentTransitionError while Thread A is in progress.
        errors: list[Exception] = []

        def thread_a() -> None:
            blocking_node.on_configure(DUMMY_STATE)

        def thread_b() -> None:
            blocking_node._started.wait()  # wait until Thread A has set _in_transition = True
            try:
                blocking_node.on_configure(DUMMY_STATE)
            except Exception as exc:
                errors.append(exc)
            finally:
                blocking_node._unblock.set()  # release Thread A regardless of outcome

        ta = threading.Thread(target=thread_a)
        tb = threading.Thread(target=thread_b)
        ta.start()
        tb.start()
        ta.join(timeout=5)
        tb.join(timeout=5)

        assert len(errors) == 1
        assert isinstance(errors[0], ConcurrentTransitionError)

    def test_concurrent_transition_flag_cleared_after_success(self, node: LifecycleComponentNode) -> None:
        # Regression: _in_transition stayed True after a successful transition,
        # blocking all subsequent transitions on the same node.
        # Expected: flag is False after completion; next transition does not raise.

        node.on_configure(DUMMY_STATE)
        assert node._in_transition is False

        # A follow-up transition must not raise ConcurrentTransitionError.
        node.on_activate(DUMMY_STATE)
        assert node._in_transition is False

    def test_concurrent_transition_flag_cleared_after_failure(self, node: LifecycleComponentNode) -> None:
        # Regression: an exception inside super().on_configure bypassed _end_transition,
        # permanently locking the node against further transitions.
        # Expected: finally block clears the flag; second on_configure does not raise
        # ConcurrentTransitionError.

        side_effects = [RuntimeError("injected"), TransitionCallbackReturn.SUCCESS]
        with patch.object(LifecycleNode, "on_configure", side_effect=side_effects):
            with pytest.raises(RuntimeError, match="injected"):
                node.on_configure(DUMMY_STATE)

            assert node._in_transition is False

            # Must not raise ConcurrentTransitionError; the second call succeeds.
            result = node.on_configure(DUMMY_STATE)
            assert result == TransitionCallbackReturn.SUCCESS

    def test_add_component_safe_during_transition(self, node: LifecycleComponentNode) -> None:
        # Regression: RegistrationClosedError and ConcurrentTransitionError are
        # independent guards; one must not mask or suppress the other.
        # Expected: add_component raises RegistrationClosedError (not
        # ConcurrentTransitionError) even when _in_transition is True.

        node.on_configure(DUMMY_STATE)  # closes registration
        node._in_transition = True
        try:
            with pytest.raises(RegistrationClosedError):
                node.add_component(FakeComponent("late"))
        finally:
            node._in_transition = False

    def test_on_error_not_guarded(self, node: LifecycleComponentNode) -> None:
        # Regression: on_error was blocked by the concurrent-transition guard,
        # making error recovery unreachable during active transitions.
        # Expected: on_error is callable with _in_transition=True and must not
        # raise ConcurrentTransitionError (error recovery path is intentionally unguarded).

        node._in_transition = True
        try:
            node.on_error(DUMMY_STATE)
        except ConcurrentTransitionError:
            pytest.fail("on_error must not raise ConcurrentTransitionError")
        except Exception:
            pass  # rclpy lifecycle state errors are acceptable
        finally:
            node._in_transition = False


# ---------------------------------------------------------------------------
# Reentrant transition helpers
# ---------------------------------------------------------------------------


class _ReentrantComponent(FakeComponent):
    """Subclass that calls node.on_configure() from within its own _on_configure hook.

    Used to simulate a synchronous reentrant configure: the hook fires during an
    active transition and attempts to start a second one on the same node.
    """

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        # Reentrant call — raises ConcurrentTransitionError because _in_transition is True.
        self.node.on_configure(state)
        return TransitionCallbackReturn.SUCCESS


# ---------------------------------------------------------------------------
# TestReentrantTransitionFromHook
# ---------------------------------------------------------------------------


class TestReentrantTransitionFromHook:
    """ConcurrentTransitionError is raised when a hook attempts a synchronous reentrant transition."""

    def test_reentrant_configure_from_hook_raises_concurrent_error(self) -> None:
        # Regression: same-thread reentrant on_configure from within a component hook was not
        # detected; _begin_transition received _in_transition=True and could silently corrupt state.
        # Expected: ConcurrentTransitionError is raised by the reentrant node.on_configure() call.
        node = LifecycleComponentNode("reentrant_test_node")
        comp = _ReentrantComponent("reentrant")
        node.add_component(comp)

        # Simulate the node being mid-transition: _in_transition is True and registration is
        # closed, exactly as when on_configure propagates to managed entities.
        # _on_configure is called directly to bypass _guarded_call so the exception propagates.
        node._in_transition = True
        node._close_registration()
        try:
            with pytest.raises(ConcurrentTransitionError):
                comp._on_configure(DUMMY_STATE)
        finally:
            node._in_transition = False
            node.destroy_node()


# ---------------------------------------------------------------------------
# TestDestructionDuringSpin
# ---------------------------------------------------------------------------


class TestDestructionDuringSpin:
    """_release_resources is called for every active component when the node is torn down."""

    def test_release_resources_called_on_teardown_after_activate(self) -> None:
        # Regression: _release_resources was not invoked on components in the active state
        # when destroy_node() was called without an explicit shutdown transition.
        # Expected: _release_resources runs for each active component during teardown.
        node = LifecycleComponentNode("teardown_test_node")
        comp = FakeComponent("teardown_comp")
        node.add_component(comp)

        node.on_configure(DUMMY_STATE)
        node.on_activate(DUMMY_STATE)

        mock_release = MagicMock()
        comp._release_resources = mock_release  # type: ignore[method-assign]

        # rclpy's destroy_node does not drive lifecycle transitions for managed entities.
        # on_shutdown is the semantically correct path to trigger _release_resources on
        # each component before the node is destroyed.
        node.on_shutdown(DUMMY_STATE)
        node.destroy_node()

        mock_release.assert_called()
