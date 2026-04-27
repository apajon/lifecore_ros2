"""Tests for LifecycleSubscriberComponent and LifecyclePublisherComponent behavior."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from rclpy.callback_groups import CallbackGroup
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState
from rclpy.qos import QoSProfile

from lifecore_ros2.components import LifecyclePublisherComponent, LifecycleSubscriberComponent, LifecycleTimerComponent
from lifecore_ros2.core import LifecycleComponentNode

# ---------------------------------------------------------------------------
# Concrete subclasses for testing
# ---------------------------------------------------------------------------


class StubSubscriber(LifecycleSubscriberComponent[Any]):
    def __init__(self, name: str = "test_sub") -> None:
        super().__init__(name=name, topic_name="/test_topic", msg_type=MagicMock, qos_profile=10)
        self.received: list[Any] = []

    def on_message(self, msg: Any) -> None:
        self.received.append(msg)


class StubPublisher(LifecyclePublisherComponent[Any]):
    def __init__(self, name: str = "test_pub") -> None:
        super().__init__(name=name, topic_name="/test_topic", msg_type=MagicMock, qos_profile=10)


class StubTimer(LifecycleTimerComponent):
    def __init__(self, name: str = "test_timer", period: float = 0.1) -> None:
        super().__init__(name=name, period=period)
        self.ticks: int = 0

    def on_tick(self) -> None:
        self.ticks += 1


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


DUMMY_STATE = LifecycleState(state_id=0, label="test")


@pytest.fixture()
def node():
    n = LifecycleComponentNode("topic_test_node")
    yield n
    n.destroy_node()


@pytest.fixture(autouse=True)
def mock_topic_factories(node: LifecycleComponentNode):
    with (
        patch.object(node, "create_publisher", return_value=MagicMock()),
        patch.object(node, "destroy_publisher", return_value=None),
        patch.object(node, "create_subscription", return_value=MagicMock()),
        patch.object(node, "destroy_subscription", return_value=None),
        patch.object(node, "create_timer", return_value=MagicMock()),
        patch.object(node, "destroy_timer", return_value=None),
    ):
        yield


# ---------------------------------------------------------------------------
# 5.3  LifecycleSubscriberComponent
# ---------------------------------------------------------------------------


class TestSubscriberComponent:
    def test_inactive_messages_ignored(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber()
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        # not activated yet → messages should be dropped
        sub._on_message_wrapper("hello")

        assert sub.received == []

    def test_active_messages_received(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber()
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)

        sub._on_message_wrapper("hello")
        assert sub.received == ["hello"]

    def test_deactivate_stops_processing(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber()
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub.on_deactivate(DUMMY_STATE)

        sub._on_message_wrapper("dropped")
        assert sub.received == []

    def test_cleanup_resets_active(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber()
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub.on_deactivate(DUMMY_STATE)
        sub.on_cleanup(DUMMY_STATE)

        assert not sub.is_active
        assert sub._subscription is None


# ---------------------------------------------------------------------------
# 5.3  LifecyclePublisherComponent
# ---------------------------------------------------------------------------


class TestPublisherComponent:
    def test_publish_before_configure_raises(self) -> None:
        pub = StubPublisher()
        # not attached to any node, not configured, not active
        with pytest.raises(RuntimeError, match="not active"):
            pub.publish(MagicMock())

    def test_publish_when_inactive_raises(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher()
        node.add_component(pub)

        # Manually set publisher to simulate successful configure without real ROS msg type
        pub._publisher = MagicMock()
        pub._is_active = False

        with pytest.raises(RuntimeError, match="not active"):
            pub.publish(MagicMock())

    def test_publish_when_active_succeeds(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher()
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)

        # The publisher object is real but topic is mock → just verify no exception
        pub._publisher = MagicMock()
        pub.publish(MagicMock())
        pub._publisher.publish.assert_called_once()

    def test_cleanup_resets_publisher(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher()
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        pub.on_deactivate(DUMMY_STATE)
        pub.on_cleanup(DUMMY_STATE)

        assert not pub.is_active
        assert pub._publisher is None


# ---------------------------------------------------------------------------
# Fix 3 — qos_profile typing coherence
# ---------------------------------------------------------------------------


class TestRegressionQoSTyping:
    """QoS profile parameter must accept both int and QoSProfile objects."""

    def test_subscriber_accepts_int_qos(self) -> None:
        # Regression: qos_profile was typed as int only in subclass __init__,
        # despite TopicComponent accepting QoSProfile | int.
        # Expected: int value is accepted without error.
        sub = StubSubscriber()
        assert sub.qos_profile == 10

    def test_subscriber_accepts_qos_profile_object(self) -> None:
        # Regression: passing a QoSProfile object raised or was mistyped.
        # Expected: QoSProfile object is stored correctly.
        qos = QoSProfile(depth=10)
        sub = _QoSSubscriber(qos_profile=qos)
        assert sub.qos_profile is qos

    def test_publisher_accepts_int_qos(self) -> None:
        # Regression: qos_profile was typed as int only in subclass __init__.
        # Expected: int value is accepted without error.
        pub = StubPublisher()
        assert pub.qos_profile == 10

    def test_publisher_accepts_qos_profile_object(self) -> None:
        # Regression: passing a QoSProfile object raised or was mistyped.
        # Expected: QoSProfile object is stored correctly.
        qos = QoSProfile(depth=10)
        pub = _QoSPublisher(qos_profile=qos)
        assert pub.qos_profile is qos


# ---------------------------------------------------------------------------
# Helpers for QoS typing tests
# ---------------------------------------------------------------------------


class _QoSSubscriber(LifecycleSubscriberComponent[Any]):
    """Subscriber stub that accepts a custom qos_profile."""

    def __init__(self, qos_profile: QoSProfile | int = 10) -> None:
        super().__init__(
            name="qos_sub",
            topic_name="/qos_test",
            msg_type=MagicMock,
            qos_profile=qos_profile,
        )

    def on_message(self, msg: Any) -> None:
        pass


class _QoSPublisher(LifecyclePublisherComponent[Any]):
    """Publisher stub that accepts a custom qos_profile."""

    def __init__(self, qos_profile: QoSProfile | int = 10) -> None:
        super().__init__(
            name="qos_pub",
            topic_name="/qos_test",
            msg_type=MagicMock,
            qos_profile=qos_profile,
        )


# ---------------------------------------------------------------------------
# 5.3b  TopicComponent property stability across lifecycle
# ---------------------------------------------------------------------------


class TestTopicComponentProperties:
    def test_properties_stable_across_full_lifecycle(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher("prop_pub")
        node.add_component(pub)

        expected_topic = "/test_topic"
        expected_qos = 10

        # Before any transition
        assert pub.topic_name == expected_topic
        assert pub.msg_type is MagicMock
        assert pub.qos_profile == expected_qos

        pub.on_configure(DUMMY_STATE)
        assert pub.topic_name == expected_topic
        assert pub.msg_type is MagicMock
        assert pub.qos_profile == expected_qos

        pub.on_activate(DUMMY_STATE)
        assert pub.topic_name == expected_topic
        assert pub.msg_type is MagicMock
        assert pub.qos_profile == expected_qos

        pub.on_deactivate(DUMMY_STATE)
        assert pub.topic_name == expected_topic
        assert pub.msg_type is MagicMock
        assert pub.qos_profile == expected_qos

        pub.on_cleanup(DUMMY_STATE)
        assert pub.topic_name == expected_topic
        assert pub.msg_type is MagicMock
        assert pub.qos_profile == expected_qos


# ---------------------------------------------------------------------------
# 5.3c  Publisher nominal full cycle
# ---------------------------------------------------------------------------


class TestPublisherNominalCycle:
    def test_configure_creates_publisher(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher("nom_pub")
        node.add_component(pub)

        with patch.object(node, "create_publisher", return_value=MagicMock()) as mock_create:
            result = pub.on_configure(DUMMY_STATE)
            assert result == TransitionCallbackReturn.SUCCESS
            assert pub._publisher is not None
            mock_create.assert_called_once()

    def test_activate_enables_publish(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher("nom_pub")
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        result = pub.on_activate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert pub.is_active is True

        # Replace real publisher with mock to avoid ROS transport
        pub._publisher = MagicMock()
        msg = MagicMock()
        pub.publish(msg)
        pub._publisher.publish.assert_called_once_with(msg)

    def test_deactivate_blocks_publish(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher("nom_pub")
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        result = pub.on_deactivate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert pub.is_active is False

    def test_cleanup_releases_publisher(self, node: LifecycleComponentNode) -> None:
        pub = StubPublisher("nom_pub")
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        pub.on_deactivate(DUMMY_STATE)
        result = pub.on_cleanup(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert pub._publisher is None


# ---------------------------------------------------------------------------
# 5.3d  Subscriber nominal full cycle
# ---------------------------------------------------------------------------


class TestSubscriberNominalCycle:
    def test_configure_creates_subscription(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber("nom_sub")
        node.add_component(sub)

        with patch.object(node, "create_subscription", return_value=MagicMock()) as mock_create:
            result = sub.on_configure(DUMMY_STATE)
            assert result == TransitionCallbackReturn.SUCCESS
            assert sub._subscription is not None
            mock_create.assert_called_once()

    def test_activate_enables_message_processing(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber("nom_sub")
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        result = sub.on_activate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert sub.is_active is True

        sub._on_message_wrapper("test_msg")
        assert sub.received == ["test_msg"]

    def test_deactivate_blocks_message_processing(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber("nom_sub")
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub._on_message_wrapper("before")

        result = sub.on_deactivate(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert sub.is_active is False

        sub._on_message_wrapper("after")
        assert sub.received == ["before"]

    def test_cleanup_releases_subscription(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber("nom_sub")
        node.add_component(sub)

        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub.on_deactivate(DUMMY_STATE)
        result = sub.on_cleanup(DUMMY_STATE)
        assert result == TransitionCallbackReturn.SUCCESS
        assert sub._subscription is None


# ---------------------------------------------------------------------------
# Helpers for callback_group tests
# ---------------------------------------------------------------------------


class _CbPublisher(LifecyclePublisherComponent[Any]):
    """Publisher stub that accepts a custom callback_group."""

    def __init__(self, callback_group: CallbackGroup | None = None) -> None:
        super().__init__(
            name="cb_pub",
            topic_name="/cb_test",
            msg_type=MagicMock,
            qos_profile=10,
            callback_group=callback_group,
        )


class _CbSubscriber(LifecycleSubscriberComponent[Any]):
    """Subscriber stub that accepts a custom callback_group."""

    def __init__(self, callback_group: CallbackGroup | None = None) -> None:
        super().__init__(
            name="cb_sub",
            topic_name="/cb_test",
            msg_type=MagicMock,
            qos_profile=10,
            callback_group=callback_group,
        )

    def on_message(self, msg: Any) -> None:
        pass


# ---------------------------------------------------------------------------
# callback_group propagation
# ---------------------------------------------------------------------------


class TestCallbackGroupPropagation:
    def test_publisher_default_callback_group_is_none(self, node: LifecycleComponentNode) -> None:
        pub = _CbPublisher()
        node.add_component(pub)

        assert pub.callback_group is None

        pub.on_configure(DUMMY_STATE)

        assert cast(MagicMock, node.create_publisher).call_args.kwargs["callback_group"] is None

    def test_publisher_callback_group_propagated_to_create_publisher(self, node: LifecycleComponentNode) -> None:
        cg = MagicMock(spec=CallbackGroup)
        pub = _CbPublisher(callback_group=cg)
        node.add_component(pub)

        assert pub.callback_group is cg

        pub.on_configure(DUMMY_STATE)

        assert cast(MagicMock, node.create_publisher).call_args.kwargs["callback_group"] is cg

    def test_subscriber_default_callback_group_is_none(self, node: LifecycleComponentNode) -> None:
        sub = _CbSubscriber()
        node.add_component(sub)

        assert sub.callback_group is None

        sub.on_configure(DUMMY_STATE)

        assert cast(MagicMock, node.create_subscription).call_args.kwargs["callback_group"] is None

    def test_subscriber_callback_group_propagated_to_create_subscription(self, node: LifecycleComponentNode) -> None:
        cg = MagicMock(spec=CallbackGroup)
        sub = _CbSubscriber(callback_group=cg)
        node.add_component(sub)

        assert sub.callback_group is cg

        sub.on_configure(DUMMY_STATE)

        assert cast(MagicMock, node.create_subscription).call_args.kwargs["callback_group"] is cg

    def test_callback_group_persists_across_cleanup(self, node: LifecycleComponentNode) -> None:
        cg = MagicMock(spec=CallbackGroup)
        pub = _CbPublisher(callback_group=cg)
        node.add_component(pub)

        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        pub.on_deactivate(DUMMY_STATE)
        pub.on_cleanup(DUMMY_STATE)

        # Option B: _callback_group is borrowed and never cleared; it must survive cleanup.
        assert pub.callback_group is cg
        assert pub._callback_group is cg

    def test_callback_group_keyword_only(self) -> None:
        cg = MagicMock(spec=CallbackGroup)
        # callback_group is keyword-only; passing it positionally must raise TypeError.
        positional_args: tuple[Any, ...] = ("kw_pub", "/cb_test", MagicMock, 10, cg)
        with pytest.raises(TypeError):
            LifecyclePublisherComponent(*positional_args)


# ---------------------------------------------------------------------------
# 5.3e  LifecycleTimerComponent
# ---------------------------------------------------------------------------


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
# 5.3f  LifecycleTimerComponent — autostart and explicit controls
# ---------------------------------------------------------------------------


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
        from lifecore_ros2.core import ComponentNotConfiguredError

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

        from lifecore_ros2.core import ComponentNotConfiguredError

        with pytest.raises(ComponentNotConfiguredError):
            timer.start()
        with pytest.raises(ComponentNotConfiguredError):
            timer.stop()
        with pytest.raises(ComponentNotConfiguredError):
            timer.reset()
