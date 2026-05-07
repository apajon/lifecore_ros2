from __future__ import annotations

import pytest
import std_msgs.msg
import std_srvs.srv
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.testing import (
    DUMMY_STATE,
    FailingComponent,
    FakeClientComponent,
    FakeComponent,
    FakePublisherComponent,
    FakeServiceComponent,
    FakeSubscriberComponent,
    FakeTimerComponent,
)


class TestFakeComponent:
    def test_records_hook_calls_in_order(self) -> None:
        component = FakeComponent()

        component.on_configure(DUMMY_STATE)
        component.on_activate(DUMMY_STATE)
        component.on_deactivate(DUMMY_STATE)
        component.on_cleanup(DUMMY_STATE)

        assert component.calls == ["configure", "activate", "deactivate", "cleanup"]
        assert component.hook_order == component.calls

    def test_records_state_per_hook(self) -> None:
        component = FakeComponent()

        component.on_configure(DUMMY_STATE)

        assert component.states["configure"] == [DUMMY_STATE]
        assert isinstance(component.states["configure"][0], LifecycleState)

    @pytest.mark.parametrize("hook_name", ["configure", "activate", "deactivate", "cleanup"])
    def test_fail_at_hook_returns_failure(self, hook_name: str) -> None:
        component = FakeComponent(fail_at_hook=hook_name)
        component.on_configure(DUMMY_STATE)
        if hook_name == "configure":
            assert component.calls == ["configure"]
            return
        component.on_activate(DUMMY_STATE)
        if hook_name == "activate":
            assert component.calls == ["configure", "activate"]
            return
        component.on_deactivate(DUMMY_STATE)
        if hook_name == "deactivate":
            assert component.calls == ["configure", "activate", "deactivate"]
            return
        component.on_cleanup(DUMMY_STATE)
        assert component.calls == ["configure", "activate", "deactivate", "cleanup"]

    def test_failing_component_exception_becomes_error(self) -> None:
        component = FailingComponent(fail_at_hook="_on_configure", exception=RuntimeError("boom"))

        result = component.on_configure(DUMMY_STATE)

        assert result == TransitionCallbackReturn.ERROR
        assert component.calls == ["configure"]


class TestFakeTopicComponents:
    def test_fake_publisher_records_published_messages_when_active(self) -> None:
        publisher = FakePublisherComponent()
        message = std_msgs.msg.String()
        message.data = "hello"

        publisher.on_configure(DUMMY_STATE)
        with pytest.raises(RuntimeError, match="not active"):
            publisher.publish(message)

        publisher.on_activate(DUMMY_STATE)
        publisher.publish(message)

        assert publisher.published_messages == [message]

    def test_fake_subscriber_records_received_messages_only_when_active(self) -> None:
        subscriber = FakeSubscriberComponent()
        message = std_msgs.msg.String()
        message.data = "hello"

        subscriber.on_configure(DUMMY_STATE)
        subscriber.receive(message)
        assert subscriber.received_messages == []

        subscriber.on_activate(DUMMY_STATE)
        subscriber.receive(message)
        assert subscriber.received_messages == [message]

    def test_fake_timer_counts_ticks_only_when_active(self) -> None:
        timer = FakeTimerComponent()

        timer.on_configure(DUMMY_STATE)
        timer.tick()
        assert timer.ticks == 0

        timer.on_activate(DUMMY_STATE)
        timer.tick()
        assert timer.ticks == 1


class TestFakeServiceComponents:
    def test_fake_service_returns_inactive_response_until_active(self) -> None:
        service = FakeServiceComponent(message="ready")
        request = std_srvs.srv.Trigger.Request()

        service.on_configure(DUMMY_STATE)
        inactive_response = service._on_request_wrapper(request, std_srvs.srv.Trigger.Response())  # pyright: ignore[reportPrivateUsage]
        assert inactive_response.success is False
        assert service.requests == []

        service.on_activate(DUMMY_STATE)
        active_response = service._on_request_wrapper(request, std_srvs.srv.Trigger.Response())  # pyright: ignore[reportPrivateUsage]
        assert active_response.success is True
        assert active_response.message == "ready"
        assert service.requests == [request]

    def test_fake_client_returns_fixed_response_when_active(self) -> None:
        client = FakeClientComponent(message="ready")
        request = std_srvs.srv.Trigger.Request()

        client.on_configure(DUMMY_STATE)
        with pytest.raises(RuntimeError, match="not active"):
            client.call(request)

        client.on_activate(DUMMY_STATE)
        response = client.call(request)

        assert response.success is True
        assert response.message == "ready"
        assert client.requests == [request]
