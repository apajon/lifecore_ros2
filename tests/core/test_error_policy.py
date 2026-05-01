"""Error policy tests for TODO 3.5.

Covers the four policy rules introduced in 3.5:
  Rule A — Boundary violations raise typed LifecoreError subclasses.
  Rule B — Inside lifecycle hooks: _worst_of aggregation for cleanup/shutdown/error.
  Rule C — Activation gating: on_message exceptions are caught and dropped.
  Rule D — (worst-of ordering for hook + resource-release results).

Coverage added here deliberately avoids duplicating what already exists in
test_failure_propagation.py (guard catches exceptions), test_edge_transitions.py
(invalid transitions), and test_activation_gating.py (publish/subscribe gating).
"""

from __future__ import annotations

import threading
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from rclpy.executors import SingleThreadedExecutor
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

import lifecore_ros2
from lifecore_ros2 import (
    ComponentNotAttachedError,
    ComponentNotConfiguredError,
    DuplicateComponentError,
    InvalidLifecycleTransitionError,
    LifecoreError,
    LifecycleComponent,
    LifecycleComponentNode,
    LifecycleHookError,
    RegistrationClosedError,
)
from lifecore_ros2.components import LifecyclePublisherComponent, LifecycleSubscriberComponent
from lifecore_ros2.core.lifecycle_component import _worst_of
from lifecore_ros2.testing import DUMMY_STATE, FakeComponent

# ---------------------------------------------------------------------------
# Instrumented helpers
# ---------------------------------------------------------------------------


class WorstOfComponent(LifecycleComponent):
    """Component with injectable hook results and a failing _release_resources."""

    def __init__(
        self,
        name: str,
        *,
        hook_return: TransitionCallbackReturn = TransitionCallbackReturn.SUCCESS,
        release_raises: bool = False,
    ) -> None:
        super().__init__(name)
        self._hook_return = hook_return
        self._release_raises = release_raises

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._hook_return

    def _on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._hook_return

    def _on_error(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._hook_return

    def _release_resources(self) -> None:
        if self._release_raises:
            raise RuntimeError("release failed")
        super()._release_resources()


class RaisingSubscriber(LifecycleSubscriberComponent[Any]):
    """Subscriber whose on_message always raises."""

    def __init__(self) -> None:
        super().__init__(
            name="raising_sub",
            topic_name="/test",
            msg_type=MagicMock,
            qos_profile=10,
        )
        self.received: list[Any] = []

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._subscription = MagicMock()
        return TransitionCallbackReturn.SUCCESS

    def on_message(self, msg: Any) -> None:
        raise ValueError("user error in on_message")

    def _release_resources(self) -> None:
        self._subscription = None
        super()._release_resources()


class UnconfiguredPublisher(LifecyclePublisherComponent[Any]):
    """Publisher that skips real ROS calls; used to test pre-configure publish."""

    def __init__(self) -> None:
        super().__init__(
            name="uncfg_pub",
            topic_name="/test",
            msg_type=MagicMock,
            qos_profile=10,
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def node() -> Generator[LifecycleComponentNode, None, None]:
    n = LifecycleComponentNode("error_policy_node")
    yield n
    n.destroy_node()


@pytest.fixture()
def spinning_error_node() -> Generator[LifecycleComponentNode, None, None]:
    n = LifecycleComponentNode("error_policy_integration_node")
    executor = SingleThreadedExecutor()
    executor.add_node(n)
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()
    yield n
    executor.shutdown()
    n.destroy_node()
    spin_thread.join(timeout=5.0)


# ===========================================================================
# Rule A — Typed boundary exceptions
# ===========================================================================


class TestTypedExceptions:
    """Boundary violations raise LifecoreError subclasses that preserve compat."""

    # -- RegistrationClosedError --------------------------------------------

    def test_add_after_configure_raises_registration_closed(self, node: LifecycleComponentNode) -> None:
        # Rule A: adding a component after configure must raise RegistrationClosedError.
        node.on_configure(DUMMY_STATE)
        with pytest.raises(RegistrationClosedError, match="lifecycle transitions have already started"):
            node.add_component(FakeComponent("after_configure"))

    def test_registration_closed_is_runtime_error(self, node: LifecycleComponentNode) -> None:
        # Backward-compat: RegistrationClosedError must be catchable as RuntimeError.
        node.on_configure(DUMMY_STATE)

        dummy = FakeComponent("dummy_rt")
        with pytest.raises(RuntimeError):
            node.add_component(dummy)

    def test_registration_closed_is_lifecore_error(self, node: LifecycleComponentNode) -> None:
        # LifecoreError catches all framework boundary violations.
        node.on_configure(DUMMY_STATE)

        dummy = FakeComponent("dummy_le")
        with pytest.raises(LifecoreError):
            node.add_component(dummy)

    # -- DuplicateComponentError --------------------------------------------

    def test_duplicate_name_raises_duplicate_component_error(self, node: LifecycleComponentNode) -> None:
        # Rule A: registering two components with the same name raises DuplicateComponentError.
        node.add_component(FakeComponent("dup"))
        with pytest.raises(DuplicateComponentError, match="already registered"):
            node.add_component(FakeComponent("dup"))

    def test_duplicate_component_error_is_value_error(self, node: LifecycleComponentNode) -> None:
        # Backward-compat: DuplicateComponentError must be catchable as ValueError.
        node.add_component(FakeComponent("dup_ve"))
        with pytest.raises(ValueError):
            node.add_component(FakeComponent("dup_ve"))

    def test_duplicate_component_error_is_lifecore_error(self, node: LifecycleComponentNode) -> None:
        node.add_component(FakeComponent("dup_lce"))
        with pytest.raises(LifecoreError):
            node.add_component(FakeComponent("dup_lce"))

    # -- ComponentNotAttachedError ------------------------------------------

    def test_node_property_raises_when_detached(self) -> None:
        # Rule A: accessing .node on a detached component raises ComponentNotAttachedError.
        comp = FakeComponent("detached")
        with pytest.raises(ComponentNotAttachedError, match="not attached"):
            _ = comp.node

    def test_not_attached_is_runtime_error(self) -> None:
        comp = FakeComponent("detached_rt")
        with pytest.raises(RuntimeError):
            _ = comp.node

    # -- ComponentNotConfiguredError ----------------------------------------

    def test_publish_before_configure_raises_not_configured(self, node: LifecycleComponentNode) -> None:
        # Rule A: publish() before configure (publisher is None) raises ComponentNotConfiguredError.
        # We need the component attached and active to reach the inner check.
        pub = UnconfiguredPublisher()
        node.add_component(pub)
        # Force active without configure so _publisher stays None
        pub._is_active = True

        with pytest.raises(ComponentNotConfiguredError, match="not configured"):
            pub.publish(MagicMock())

    def test_not_configured_is_runtime_error(self, node: LifecycleComponentNode) -> None:
        pub = UnconfiguredPublisher()
        node.add_component(pub)
        pub._is_active = True

        with pytest.raises(RuntimeError):
            pub.publish(MagicMock())

    def test_not_configured_is_lifecore_error(self, node: LifecycleComponentNode) -> None:
        pub = UnconfiguredPublisher()
        node.add_component(pub)
        pub._is_active = True

        with pytest.raises(LifecoreError):
            pub.publish(MagicMock())

    # -- LifecoreError catch-all --------------------------------------------

    def test_lifecore_error_in_top_level_init(self) -> None:
        # All LifecoreError subclasses are importable from the top-level package.
        assert issubclass(RegistrationClosedError, lifecore_ros2.LifecoreError)
        assert issubclass(DuplicateComponentError, lifecore_ros2.LifecoreError)
        assert issubclass(ComponentNotAttachedError, lifecore_ros2.LifecoreError)
        assert issubclass(ComponentNotConfiguredError, lifecore_ros2.LifecoreError)
        assert issubclass(InvalidLifecycleTransitionError, lifecore_ros2.LifecoreError)


# ===========================================================================
# Rule B / D — _worst_of helper and cleanup/shutdown/error aggregation
# ===========================================================================


class TestWorstOf:
    """_worst_of returns the more severe of two TransitionCallbackReturn values."""

    S = TransitionCallbackReturn.SUCCESS
    F = TransitionCallbackReturn.FAILURE
    E = TransitionCallbackReturn.ERROR

    def test_success_success(self) -> None:
        assert _worst_of(self.S, self.S) == self.S

    def test_failure_success(self) -> None:
        assert _worst_of(self.F, self.S) == self.F

    def test_success_failure(self) -> None:
        assert _worst_of(self.S, self.F) == self.F

    def test_error_success(self) -> None:
        assert _worst_of(self.E, self.S) == self.E

    def test_success_error(self) -> None:
        assert _worst_of(self.S, self.E) == self.E

    def test_error_failure(self) -> None:
        # This is the bug case the previous implementation got wrong:
        # hook=ERROR, release=FAILURE must return ERROR, not FAILURE.
        assert _worst_of(self.E, self.F) == self.E

    def test_failure_error(self) -> None:
        assert _worst_of(self.F, self.E) == self.E


class TestCleanupWorstOfAggregation:
    """on_cleanup / on_shutdown / on_error return _worst_of(hook, release)."""

    def test_cleanup_failure_hook_success_release_returns_failure(self, node: LifecycleComponentNode) -> None:
        # Rule D: hook=FAILURE, release=SUCCESS → FAILURE.
        comp = WorstOfComponent("wof_fail", hook_return=TransitionCallbackReturn.FAILURE)
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)

        result = comp.on_cleanup(DUMMY_STATE)

        assert result == TransitionCallbackReturn.FAILURE

    def test_cleanup_error_hook_success_release_returns_error(self, node: LifecycleComponentNode) -> None:
        # Rule D: hook=ERROR, release=SUCCESS → ERROR.
        comp = WorstOfComponent("wof_err", hook_return=TransitionCallbackReturn.ERROR)
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)

        result = comp.on_cleanup(DUMMY_STATE)

        assert result == TransitionCallbackReturn.ERROR

    def test_cleanup_success_hook_raising_release_returns_error(self, node: LifecycleComponentNode) -> None:
        # Rule D: hook=SUCCESS, release raises → ERROR.
        comp = WorstOfComponent("wof_release_err", hook_return=TransitionCallbackReturn.SUCCESS, release_raises=True)
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)

        result = comp.on_cleanup(DUMMY_STATE)

        assert result == TransitionCallbackReturn.ERROR

    def test_cleanup_failure_hook_does_not_skip_release(self, node: LifecycleComponentNode) -> None:
        # Rule D: _release_resources must run even when the hook returns FAILURE.
        comp = WorstOfComponent("wof_no_skip", hook_return=TransitionCallbackReturn.FAILURE)
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        released = []

        original = comp._release_resources

        def tracked_release() -> None:
            released.append(True)
            original()

        comp._release_resources = tracked_release  # type: ignore[method-assign]

        comp.on_cleanup(DUMMY_STATE)

        assert released, "_release_resources must be called even when hook returns FAILURE"

    def test_shutdown_failure_hook_does_not_skip_release(self, node: LifecycleComponentNode) -> None:
        # Rule D: same guarantee for on_shutdown.
        comp = WorstOfComponent("wof_shut", hook_return=TransitionCallbackReturn.FAILURE)
        node.add_component(comp)
        released = []

        original = comp._release_resources

        def tracked_release() -> None:
            released.append(True)
            original()

        comp._release_resources = tracked_release  # type: ignore[method-assign]

        comp.on_shutdown(DUMMY_STATE)

        assert released

    def test_error_hook_failure_hook_does_not_skip_release(self, node: LifecycleComponentNode) -> None:
        # Rule D: same guarantee for on_error.
        comp = WorstOfComponent("wof_on_error", hook_return=TransitionCallbackReturn.FAILURE)
        node.add_component(comp)
        released = []

        original = comp._release_resources

        def tracked_release() -> None:
            released.append(True)
            original()

        comp._release_resources = tracked_release  # type: ignore[method-assign]

        comp.on_error(DUMMY_STATE)

        assert released


# ===========================================================================
# Rule C — on_message exception wrapping
# ===========================================================================


class TestOnMessageExceptionWrapping:
    """Exceptions in on_message are caught by the framework and dropped silently."""

    def test_on_message_exception_does_not_propagate(self, node: LifecycleComponentNode) -> None:
        # Rule C: an exception raised inside on_message must never escape _on_message_wrapper.
        # Expected: no exception raised at the wrapper boundary.
        sub = RaisingSubscriber()
        node.add_component(sub)
        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)

        # Must not raise.
        sub._on_message_wrapper("any_message")

    def test_on_message_exception_is_logged_at_error_level(self, node: LifecycleComponentNode) -> None:
        # Rule C: the error must be visible in logs for diagnosis.
        # Expected: logger.error is called with information about the exception.
        sub = RaisingSubscriber()
        node.add_component(sub)
        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)

        mock_logger = MagicMock()
        with patch.object(sub, "_resolve_logger", return_value=mock_logger):
            sub._on_message_wrapper("msg")

        mock_logger.error.assert_called_once()
        error_msg: str = mock_logger.error.call_args[0][0]
        assert "on_message" in error_msg
        assert "ValueError" in error_msg

    def test_on_message_exception_does_not_affect_subsequent_messages(self, node: LifecycleComponentNode) -> None:
        # Rule C: after a failing message, the subscriber must remain functional.
        # (The component stays active; subsequent deliveries are still gated normally.)
        sub = RaisingSubscriber()
        node.add_component(sub)
        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)

        assert sub.is_active
        sub._on_message_wrapper("msg1")
        # Component must still be active — one bad message must not break state.
        assert sub.is_active
        sub._on_message_wrapper("msg2")
        assert sub.is_active


# ===========================================================================
# Sprint 2 error-handling contract — log content, propagation, and idempotence
# ===========================================================================


class TestContractLogFormat:
    """Log records on hook exception and invalid return match the documented contract format."""

    def test_exception_log_contains_component_name_hook_name_and_exception(self, node: LifecycleComponentNode) -> None:
        # Contract: _guarded_call logs ERROR carrying the component name, the hook name
        # ("on_configure", not "_on_configure"), the exception type, and the original message.
        class _Crashing(LifecycleComponent):
            def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
                raise RuntimeError("boom")

        comp = _Crashing("crash_log_comp")
        node.add_component(comp)

        mock_logger = MagicMock()
        with patch.object(comp, "_resolve_logger", return_value=mock_logger):
            comp.on_configure(DUMMY_STATE)

        # First error call is the structured hook-error message; second is the traceback.
        assert mock_logger.error.call_count >= 1
        first_msg: str = mock_logger.error.call_args_list[0][0][0]
        assert "crash_log_comp" in first_msg
        assert "on_configure" in first_msg
        assert "RuntimeError" in first_msg
        assert "boom" in first_msg

    def test_invalid_return_log_contains_type_repr_and_expected_return_type(
        self, node: LifecycleComponentNode
    ) -> None:
        # Contract: invalid return value logs component name, hook name, type name, repr,
        # and the phrase "TransitionCallbackReturn" to indicate what was expected.
        class _BadReturn(LifecycleComponent):
            def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
                return 42  # type: ignore[return-value]

        comp = _BadReturn("bad_return_log_comp")
        node.add_component(comp)

        mock_logger = MagicMock()
        with patch.object(comp, "_resolve_logger", return_value=mock_logger):
            comp.on_configure(DUMMY_STATE)

        mock_logger.error.assert_called_once()
        msg: str = mock_logger.error.call_args[0][0]
        assert "bad_return_log_comp" in msg
        assert "on_configure" in msg
        assert "int" in msg
        assert "42" in msg
        assert "TransitionCallbackReturn" in msg


class TestLifecycleHookErrorContract:
    """LifecycleHookError is used for internal logging only; it never propagates to the caller."""

    def test_hook_exception_does_not_propagate_to_caller(self, node: LifecycleComponentNode) -> None:
        # Contract: _guarded_call absorbs exceptions, returns ERROR, and never re-raises.
        # The caller of on_configure must never receive any exception.
        class _Crashing(LifecycleComponent):
            def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
                raise RuntimeError("boom")

        comp = _Crashing("no_leak_comp")
        node.add_component(comp)

        result = comp.on_configure(DUMMY_STATE)  # must not raise

        assert result == TransitionCallbackReturn.ERROR

    def test_lifecycle_hook_error_importable_and_correct_hierarchy(self) -> None:
        # Contract: LifecycleHookError is exported from the top-level package and is
        # a subclass of both LifecoreError (framework catch-all) and RuntimeError (compat).
        assert issubclass(LifecycleHookError, LifecoreError)
        assert issubclass(LifecycleHookError, RuntimeError)


class TestOnErrorInvocationCount:
    """_on_error is driven exactly once by rclpy; the framework must not synthesize an extra call."""

    def test_on_error_invoked_exactly_once_after_configure_exception(
        self, spinning_error_node: LifecycleComponentNode
    ) -> None:
        # Contract: when _on_configure raises, _guarded_call returns ERROR.
        # rclpy then drives the ERROR_PROCESSING transition which calls on_error on managed
        # entities exactly once.  A count of 2 would indicate the framework also synthesized
        # a second call — which is forbidden by the contract.
        error_calls: list[int] = []

        class _CountingError(LifecycleComponent):
            def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
                raise RuntimeError("boom")

            def _on_error(self, state: LifecycleState) -> TransitionCallbackReturn:
                error_calls.append(1)
                return TransitionCallbackReturn.SUCCESS

        comp = _CountingError("count_err_comp")
        spinning_error_node.add_component(comp)

        spinning_error_node.trigger_configure()

        assert len(error_calls) == 1


class TestDoubleReleaseAfterOnError:
    """_release_resources idempotence guarantees no crash on a second release after the on_error path."""

    def test_second_release_after_on_error_is_a_noop(self, node: LifecycleComponentNode) -> None:
        # Contract: on_error calls _release_resources once (inside on_error).
        # A subsequent on_shutdown must not raise and must not trigger a second increment
        # when the implementation follows the idempotency rule (check-then-release).
        release_count: list[int] = []

        class _IdempotentRelease(LifecycleComponent):
            def __init__(self) -> None:
                super().__init__("idem_comp")
                self._resource: object | None = object()

            def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
                self._resource = object()
                return TransitionCallbackReturn.SUCCESS

            def _release_resources(self) -> None:
                if self._resource is not None:
                    release_count.append(1)
                    self._resource = None
                super()._release_resources()

        comp = _IdempotentRelease()
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)

        # on_error path: calls _on_error then _release_resources.
        comp.on_error(DUMMY_STATE)
        assert len(release_count) == 1

        # Subsequent on_shutdown must not raise and must not double-release.
        comp.on_shutdown(DUMMY_STATE)  # must not raise
        assert len(release_count) == 1  # idempotent: no second increment
