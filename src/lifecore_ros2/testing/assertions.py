from __future__ import annotations

from collections.abc import Sequence

import std_msgs.msg
import std_srvs.srv

from lifecore_ros2.core import LifecycleComponentNode

from .fakes import (
    DUMMY_STATE,
    FakeClientComponent,
    FakeComponent,
    FakePublisherComponent,
    FakeServiceComponent,
    FakeSubscriberComponent,
    FakeTimerComponent,
)

ActivationGatedFake = (
    FakePublisherComponent | FakeSubscriberComponent | FakeTimerComponent | FakeServiceComponent | FakeClientComponent
)


def assert_component_state(node: LifecycleComponentNode, name: str, expected_state: str) -> None:
    """Assert the lifecycle contract state of a component registered on a node."""
    component = node.get_component(name)
    actual_state = component._contract_state()  # pyright: ignore[reportPrivateUsage]
    assert actual_state == expected_state, f"Expected component '{name}' to be {expected_state}, got {actual_state}"


def assert_transition_order(log: Sequence[str] | FakeComponent, expected_order: Sequence[str]) -> None:
    """Assert recorded lifecycle hook order."""
    actual_order = log.calls if isinstance(log, FakeComponent) else list(log)
    assert actual_order == list(expected_order), (
        f"Expected transition order {list(expected_order)}, got {actual_order}"
    )


def assert_activation_gated(component: ActivationGatedFake) -> None:
    """Assert activation gating for the built-in fake component families."""
    if isinstance(component, FakePublisherComponent):
        _assert_publisher_gated(component)
        return
    if isinstance(component, FakeSubscriberComponent):
        _assert_subscriber_gated(component)
        return
    if isinstance(component, FakeTimerComponent):
        _assert_timer_gated(component)
        return
    if isinstance(component, FakeServiceComponent):
        _assert_service_gated(component)
        return
    _assert_client_gated(component)


def _assert_publisher_gated(component: FakePublisherComponent) -> None:
    message = std_msgs.msg.String()
    message.data = "hello"
    component.on_configure(DUMMY_STATE)
    try:
        component.publish(message)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected inactive publisher to reject publish()")

    component.on_activate(DUMMY_STATE)
    component.publish(message)
    assert component.published_messages == [message]


def _assert_subscriber_gated(component: FakeSubscriberComponent) -> None:
    message = std_msgs.msg.String()
    message.data = "hello"
    component.on_configure(DUMMY_STATE)
    component.receive(message)
    assert component.received_messages == []

    component.on_activate(DUMMY_STATE)
    component.receive(message)
    assert component.received_messages == [message]


def _assert_timer_gated(component: FakeTimerComponent) -> None:
    component.on_configure(DUMMY_STATE)
    component.tick()
    assert component.ticks == 0

    component.on_activate(DUMMY_STATE)
    component.tick()
    assert component.ticks == 1


def _assert_service_gated(component: FakeServiceComponent) -> None:
    request = std_srvs.srv.Trigger.Request()
    inactive_response = std_srvs.srv.Trigger.Response()
    component.on_configure(DUMMY_STATE)
    response = component._on_request_wrapper(request, inactive_response)  # pyright: ignore[reportPrivateUsage]
    assert response.success is False
    assert component.requests == []

    component.on_activate(DUMMY_STATE)
    active_response = component._on_request_wrapper(  # pyright: ignore[reportPrivateUsage]
        request,
        std_srvs.srv.Trigger.Response(),
    )
    assert active_response.success is True
    assert component.requests == [request]


def _assert_client_gated(component: FakeClientComponent) -> None:
    request = std_srvs.srv.Trigger.Request()
    component.on_configure(DUMMY_STATE)
    try:
        component.call(request)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected inactive client to reject call()")

    component.on_activate(DUMMY_STATE)
    response = component.call(request)
    assert response.success is True
    assert component.requests == [request]
