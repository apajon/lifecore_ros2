"""Strict activation gating tests for TODO 2.5.

Verifies that publisher and subscriber behavior is properly gated by
activation state, and that the ``@when_active`` decorator enforces the
correct semantics in all lifecycle phases.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.components import LifecyclePublisherComponent, LifecycleSubscriberComponent
from lifecore_ros2.core import LifecycleComponentNode
from lifecore_ros2.core.activation_gating import require_active
from lifecore_ros2.core.lifecycle_component import LifecycleComponent, when_active
from lifecore_ros2.testing import DUMMY_STATE

# ---------------------------------------------------------------------------
# Dummy state for direct hook invocations
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# TestRequireActivePrimitive
# ---------------------------------------------------------------------------


class TestRequireActivePrimitive:
    """Unit tests for the shared ``require_active`` primitive in activation_gating.py."""

    def test_raises_when_inactive(self) -> None:
        # Regression: primitive must raise RuntimeError when is_active is False.
        # Expected: RuntimeError with component name in message.
        with pytest.raises(RuntimeError, match="Component 'my_comp' is not active"):
            require_active(False, component_name="my_comp")

    def test_returns_none_when_active(self) -> None:
        # Guard: primitive must return cleanly when is_active is True.
        result = require_active(True, component_name="my_comp")
        assert result is None

    def test_error_message_contains_component_name(self) -> None:
        # Regression: error message must embed the component name for diagnosis.
        with pytest.raises(RuntimeError, match="sensor_node"):
            require_active(False, component_name="sensor_node")

    def test_error_is_runtime_error_not_subclass(self) -> None:
        # Guard: callers catching RuntimeError must not need to know about subclasses.
        with pytest.raises(RuntimeError) as exc_info:
            require_active(False, component_name="x")
        assert type(exc_info.value) is RuntimeError


# ---------------------------------------------------------------------------


class GatedPublisher(LifecyclePublisherComponent[Any]):
    """Publisher that bypasses real ROS transport in configure."""

    def __init__(self, name: str = "gated_pub") -> None:
        super().__init__(name=name, topic_name="/gating_test", msg_type=MagicMock, qos_profile=10)
        self.publish_count: int = 0

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        # Skip real create_publisher — inject a mock instead.
        self._publisher = MagicMock()
        return TransitionCallbackReturn.SUCCESS

    def _release_resources(self) -> None:
        self._publisher = None
        super()._release_resources()


class GatedSubscriber(LifecycleSubscriberComponent[Any]):
    """Subscriber that records received messages without real ROS transport."""

    def __init__(self, name: str = "gated_sub") -> None:
        super().__init__(name=name, topic_name="/gating_test", msg_type=MagicMock, qos_profile=10)
        self.received: list[Any] = []

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        # Skip real create_subscription — no transport needed.
        self._subscription = MagicMock()
        return TransitionCallbackReturn.SUCCESS

    def on_message(self, msg: Any) -> None:
        self.received.append(msg)

    def _release_resources(self) -> None:
        self._subscription = None
        super()._release_resources()


# ---------------------------------------------------------------------------
# Minimal component for testing @when_active decorator variants
# ---------------------------------------------------------------------------


class DecoratorTestComponent(LifecycleComponent):
    """Minimal component for testing @when_active variants."""

    @when_active
    def gated_default(self) -> str:
        return "executed"

    @when_active(when_not_active=None)
    def gated_silent(self) -> str:
        return "executed"

    @when_active(when_not_active=lambda: "fallback")
    def gated_callable(self) -> str:
        return "executed"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def node() -> Generator[LifecycleComponentNode, None, None]:
    n = LifecycleComponentNode("gating_test_node")
    yield n
    n.destroy_node()


@pytest.fixture()
def pub(node: LifecycleComponentNode) -> GatedPublisher:
    p = GatedPublisher()
    node.add_component(p)
    return p


@pytest.fixture()
def sub(node: LifecycleComponentNode) -> GatedSubscriber:
    s = GatedSubscriber()
    node.add_component(s)
    return s


@pytest.fixture()
def decorator_comp(node: LifecycleComponentNode) -> DecoratorTestComponent:
    c = DecoratorTestComponent(name="decorator_test")
    node.add_component(c)
    return c


# ---------------------------------------------------------------------------
# TestPublisherActivationGating
# ---------------------------------------------------------------------------


class TestPublisherActivationGating:
    """Verify publish() raises RuntimeError in every inactive lifecycle phase."""

    def test_publish_rejected_before_configure(self, pub: GatedPublisher) -> None:
        # Regression: publish() must be gated before any transition.
        # Expected: RuntimeError because _is_active is False.
        assert not pub.is_active
        with pytest.raises(RuntimeError, match="not active"):
            pub.publish(MagicMock())

    def test_publish_rejected_after_configure_before_activate(self, pub: GatedPublisher) -> None:
        # Regression: configure alone must not enable publish.
        # Expected: RuntimeError — configured but not yet activated.
        pub.on_configure(DUMMY_STATE)

        assert not pub.is_active
        with pytest.raises(RuntimeError, match="not active"):
            pub.publish(MagicMock())

    def test_publish_rejected_after_deactivate(self, pub: GatedPublisher) -> None:
        # Regression: deactivate must re-gate publish.
        # Expected: RuntimeError after deactivation.
        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        pub.on_deactivate(DUMMY_STATE)

        assert not pub.is_active
        with pytest.raises(RuntimeError, match="not active"):
            pub.publish(MagicMock())

    def test_publish_rejected_after_cleanup(self, pub: GatedPublisher) -> None:
        # Regression: cleanup must clear activation state.
        # Expected: RuntimeError after cleanup.
        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        pub.on_deactivate(DUMMY_STATE)
        pub.on_cleanup(DUMMY_STATE)

        assert not pub.is_active
        with pytest.raises(RuntimeError, match="not active"):
            pub.publish(MagicMock())

    def test_publish_allowed_when_active(self, pub: GatedPublisher) -> None:
        # Guard: publish must succeed in the active phase.
        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)

        assert pub.is_active
        pub.publish(MagicMock())
        pub._publisher.publish.assert_called_once()  # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue]


# ---------------------------------------------------------------------------
# TestSubscriberActivationGating
# ---------------------------------------------------------------------------


class TestSubscriberActivationGating:
    """Verify _on_message_wrapper silently drops messages in every inactive phase."""

    def test_subscriber_drops_messages_before_configure(self, sub: GatedSubscriber) -> None:
        # Regression: messages arriving before configure must be silently dropped.
        # Expected: on_message is not called, received list stays empty.
        assert not sub.is_active
        result = sub._on_message_wrapper("early_msg")

        assert result is None
        assert sub.received == []

    def test_subscriber_drops_messages_after_configure_before_activate(self, sub: GatedSubscriber) -> None:
        # Regression: configure alone must not enable message processing.
        # Expected: message silently dropped.
        sub.on_configure(DUMMY_STATE)

        assert not sub.is_active
        result = sub._on_message_wrapper("configured_msg")

        assert result is None
        assert sub.received == []

    def test_subscriber_drops_messages_after_deactivate(self, sub: GatedSubscriber) -> None:
        # Regression: deactivate must re-gate message processing.
        # Expected: message silently dropped after deactivation.
        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub.on_deactivate(DUMMY_STATE)

        assert not sub.is_active
        result = sub._on_message_wrapper("late_msg")

        assert result is None
        assert sub.received == []

    def test_subscriber_drops_messages_after_cleanup(self, sub: GatedSubscriber) -> None:
        # Regression: cleanup must clear activation state.
        # Expected: message silently dropped after cleanup.
        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub.on_deactivate(DUMMY_STATE)
        sub.on_cleanup(DUMMY_STATE)

        assert not sub.is_active
        result = sub._on_message_wrapper("cleaned_msg")

        assert result is None
        assert sub.received == []

    def test_subscriber_processes_messages_when_active(self, sub: GatedSubscriber) -> None:
        # Guard: messages must be forwarded to on_message when active.
        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)

        assert sub.is_active
        sub._on_message_wrapper("hello")

        assert sub.received == ["hello"]


# ---------------------------------------------------------------------------
# TestReactivationResumption
# ---------------------------------------------------------------------------


class TestReactivationResumption:
    """Verify behavior resumes correctly after configure→activate→deactivate→activate."""

    def test_reactivation_resumes_publish(self, pub: GatedPublisher) -> None:
        # Regression: second activation must re-enable publish.
        # Expected: publish works → blocked → works again.
        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)

        # First activation: publish succeeds.
        pub.publish(MagicMock())
        assert pub._publisher.publish.call_count == 1  # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue]

        # Deactivate: publish blocked.
        pub.on_deactivate(DUMMY_STATE)
        assert not pub.is_active
        with pytest.raises(RuntimeError, match="not active"):
            pub.publish(MagicMock())

        # Reactivate: publish resumes.
        pub.on_activate(DUMMY_STATE)
        assert pub.is_active
        pub.publish(MagicMock())
        assert pub._publisher.publish.call_count == 2  # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue]

    def test_reactivation_resumes_subscriber(self, sub: GatedSubscriber) -> None:
        # Regression: second activation must re-enable message processing.
        # Expected: on_message called → ignored → called again.
        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)

        # First activation: message processed.
        sub._on_message_wrapper("msg_1")
        assert sub.received == ["msg_1"]

        # Deactivate: message dropped.
        sub.on_deactivate(DUMMY_STATE)
        assert not sub.is_active
        sub._on_message_wrapper("msg_2")
        assert "msg_2" not in sub.received

        # Reactivate: message processed.
        sub.on_activate(DUMMY_STATE)
        assert sub.is_active
        sub._on_message_wrapper("msg_3")
        assert sub.received == ["msg_1", "msg_3"]

    def test_multiple_reactivation_cycles(self, pub: GatedPublisher) -> None:
        # Guard: repeated activate/deactivate cycles must not leak state.
        pub.on_configure(DUMMY_STATE)

        for _i in range(3):
            pub.on_activate(DUMMY_STATE)
            assert pub.is_active
            pub.publish(MagicMock())

            pub.on_deactivate(DUMMY_STATE)
            assert not pub.is_active
            with pytest.raises(RuntimeError, match="not active"):
                pub.publish(MagicMock())

        assert pub._publisher.publish.call_count == 3  # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue]


# ---------------------------------------------------------------------------
# TestWhenActiveDecorator
# ---------------------------------------------------------------------------


class TestWhenActiveDecorator:
    """Test @when_active decorator variants directly on a minimal component."""

    # -- default: raises RuntimeError ------------------------------------

    def test_default_raises_when_inactive(self, decorator_comp: DecoratorTestComponent) -> None:
        # Regression: default @when_active must raise RuntimeError when inactive.
        # Expected: RuntimeError with component name in message.
        assert not decorator_comp.is_active
        with pytest.raises(RuntimeError, match="not active"):
            decorator_comp.gated_default()

    def test_default_executes_when_active(self, decorator_comp: DecoratorTestComponent) -> None:
        # Guard: default @when_active must execute the method when active.
        decorator_comp.on_configure(DUMMY_STATE)
        decorator_comp.on_activate(DUMMY_STATE)

        assert decorator_comp.is_active
        result = decorator_comp.gated_default()
        assert result == "executed"

    # -- when_not_active=None: silent no-op ------------------------------

    def test_silent_noop_returns_none_when_inactive(self, decorator_comp: DecoratorTestComponent) -> None:
        # Regression: when_not_active=None must return None silently.
        # Expected: no exception, return value is None.
        assert not decorator_comp.is_active
        result = decorator_comp.gated_silent()
        assert result is None

    def test_silent_noop_executes_when_active(self, decorator_comp: DecoratorTestComponent) -> None:
        # Guard: when_not_active=None must still execute the method when active.
        decorator_comp.on_configure(DUMMY_STATE)
        decorator_comp.on_activate(DUMMY_STATE)

        assert decorator_comp.is_active
        result = decorator_comp.gated_silent()
        assert result == "executed"

    # -- when_not_active=callable: custom fallback -----------------------

    def test_callable_invoked_when_inactive(self, decorator_comp: DecoratorTestComponent) -> None:
        # Regression: custom callable must be invoked when component is inactive.
        # Expected: callable runs, method returns None (not the callable's return value).
        assert not decorator_comp.is_active
        result = decorator_comp.gated_callable()
        # The decorator calls the callable then returns None.
        assert result is None

    def test_callable_not_invoked_when_active(self, decorator_comp: DecoratorTestComponent) -> None:
        # Guard: custom callable must NOT be invoked when active — method runs instead.
        decorator_comp.on_configure(DUMMY_STATE)
        decorator_comp.on_activate(DUMMY_STATE)

        assert decorator_comp.is_active
        result = decorator_comp.gated_callable()
        assert result == "executed"

    # -- verifying the custom callable is actually called ----------------

    def test_callable_side_effect_observed(self, node: LifecycleComponentNode) -> None:
        # Guard: prove the custom callable is actually executed, not just discarded.
        side_effects: list[str] = []

        class SideEffectComponent(LifecycleComponent):
            @when_active(when_not_active=lambda: side_effects.append("called"))
            def gated(self) -> str:
                return "executed"

            def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
                return super()._on_configure(state)

            def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
                return super()._on_activate(state)

            def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
                return super()._on_deactivate(state)

            def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
                return super()._on_cleanup(state)

            def _release_resources(self) -> None:
                super()._release_resources()

        comp = SideEffectComponent(name="side_effect_test")
        node.add_component(comp)

        assert not comp.is_active
        comp.gated()
        assert side_effects == ["called"]

        # Activate: callable must NOT be invoked.
        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)

        side_effects.clear()
        result = comp.gated()
        assert result == "executed"
        assert side_effects == []


# ---------------------------------------------------------------------------
# TestRequireActiveFacade
# ---------------------------------------------------------------------------


class TestRequireActiveFacade:
    """Test LifecycleComponent.require_active() as a façade over the shared primitive."""

    def test_raises_when_component_inactive(self, decorator_comp: DecoratorTestComponent) -> None:
        # Regression: require_active() must raise when component is not active.
        # Expected: RuntimeError with component name in message.
        assert not decorator_comp.is_active
        with pytest.raises(RuntimeError, match="not active"):
            decorator_comp.require_active()

    def test_returns_none_when_component_active(self, decorator_comp: DecoratorTestComponent) -> None:
        # Guard: require_active() must return cleanly when component is active.
        decorator_comp.on_configure(DUMMY_STATE)
        decorator_comp.on_activate(DUMMY_STATE)

        assert decorator_comp.is_active
        result = decorator_comp.require_active()
        assert result is None

    def test_error_message_contains_component_name(self, decorator_comp: DecoratorTestComponent) -> None:
        # Regression: error message must embed the component name for diagnosis.
        # Expected: "decorator_test" appears in the RuntimeError message.
        with pytest.raises(RuntimeError, match="decorator_test"):
            decorator_comp.require_active()

    def test_require_active_matches_when_active_error_message(self, decorator_comp: DecoratorTestComponent) -> None:
        # Regression: require_active() and @when_active default-raise must produce
        # the same error message, proving they share the same primitive.
        facade_msg: str = ""
        decorator_msg: str = ""

        try:
            decorator_comp.require_active()
        except RuntimeError as exc:
            facade_msg = str(exc)

        try:
            decorator_comp.gated_default()
        except RuntimeError as exc:
            decorator_msg = str(exc)

        assert facade_msg == decorator_msg

    def test_raises_after_deactivate(self, decorator_comp: DecoratorTestComponent) -> None:
        # Regression: deactivate must re-gate require_active().
        decorator_comp.on_configure(DUMMY_STATE)
        decorator_comp.on_activate(DUMMY_STATE)
        decorator_comp.on_deactivate(DUMMY_STATE)

        assert not decorator_comp.is_active
        with pytest.raises(RuntimeError, match="not active"):
            decorator_comp.require_active()
