"""Regression tests for QoS typing, TopicComponent property stability, and callback_group propagation.

Coverage map (this file):
    TestRegressionQoSTyping      — qos_profile accepts int and QoSProfile for publisher and subscriber
    TestTopicComponentProperties — property values stable across the full lifecycle
    TestCallbackGroupPropagation — callback_group forwarded correctly to ROS factory calls

See also:
    tests/components/test_publisher_component.py — LifecyclePublisherComponent lifecycle and activation gating
    tests/components/test_subscriber_component.py — LifecycleSubscriberComponent lifecycle and activation gating
    tests/components/test_timer_component.py      — LifecycleTimerComponent lifecycle, controls, and activation gating
"""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from rclpy.callback_groups import CallbackGroup
from rclpy.qos import QoSProfile

from lifecore_ros2.components import LifecyclePublisherComponent, LifecycleSubscriberComponent
from lifecore_ros2.core import LifecycleComponentNode
from tests.components._topic_stubs import DUMMY_STATE, StubPublisher, StubSubscriber

# ---------------------------------------------------------------------------
# Local helpers
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
# QoS typing regression
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
# TopicComponent property stability
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
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


@pytest.mark.usefixtures("mock_topic_factories")
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
# dependencies / priority pass-through — topic component family
# ---------------------------------------------------------------------------


class TestDependenciesAndPriorityTopicFamily:
    """Regression: dependencies and priority must be accepted and stored by publisher/subscriber."""

    def test_publisher_accepts_dependencies_and_priority(self) -> None:
        pub = LifecyclePublisherComponent[Any](
            name="dep_pub",
            topic_name="/dep_test",
            msg_type=MagicMock,
            dependencies=("other",),
            priority=3,
        )
        assert pub._dependencies == ("other",)
        assert pub._priority == 3

    def test_subscriber_accepts_dependencies_and_priority(self) -> None:
        class _MinimalSub(LifecycleSubscriberComponent[Any]):
            def on_message(self, msg: Any) -> None:
                pass

        sub = _MinimalSub(
            name="dep_sub",
            topic_name="/dep_test",
            msg_type=MagicMock,
            dependencies=("source",),
            priority=1,
        )
        assert sub._dependencies == ("source",)
        assert sub._priority == 1

    def test_defaults_are_empty_and_zero(self) -> None:
        pub = StubPublisher()
        assert pub._dependencies == ()
        assert pub._priority == 0
