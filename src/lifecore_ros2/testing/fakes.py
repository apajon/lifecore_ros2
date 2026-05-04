from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, cast

import std_msgs.msg
import std_srvs.srv
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.components import (
    LifecyclePublisherComponent,
    LifecycleServiceClientComponent,
    LifecycleServiceServerComponent,
    LifecycleSubscriberComponent,
    LifecycleTimerComponent,
)
from lifecore_ros2.core import LifecycleComponent

DUMMY_STATE = LifecycleState(state_id=0, label="test")

_HOOK_NAMES = frozenset({"configure", "activate", "deactivate", "cleanup", "shutdown", "error"})


def _normalize_hook_name(hook_name: str) -> str:
    normalized = hook_name.removeprefix("_on_")
    if normalized not in _HOOK_NAMES:
        expected = ", ".join(sorted(_HOOK_NAMES))
        raise ValueError(f"Unknown lifecycle hook '{hook_name}', expected one of: {expected}")
    return normalized


class FakeComponent(LifecycleComponent):
    """Minimal lifecycle component that records hook calls and controlled failures."""

    def __init__(
        self,
        name: str = "fake_component",
        *,
        dependencies: Sequence[str] = (),
        priority: int = 0,
        fail_at_hook: str | None = None,
        exception: Exception | None = None,
        failure_return: TransitionCallbackReturn = TransitionCallbackReturn.FAILURE,
    ) -> None:
        """Initialize the fake component.

        Args:
            name: Unique component name.
            dependencies: Names of components this one depends on; forwarded to
                ``LifecycleComponent``.
            priority: Higher value means earlier in the resolved transition order;
                forwarded to ``LifecycleComponent``.
            fail_at_hook: Hook name that should fail. Accepts ``configure`` or
                protected-style names such as ``_on_configure``.
            exception: Optional exception to raise at ``fail_at_hook``. If omitted,
                ``failure_return`` is returned instead.
            failure_return: Transition result returned by the failing hook when
                ``exception`` is not set.
        """
        super().__init__(name=name, dependencies=dependencies, priority=priority)
        self.calls: list[str] = []
        self.states: dict[str, list[LifecycleState]] = {hook_name: [] for hook_name in _HOOK_NAMES}
        self._fail_at_hook = _normalize_hook_name(fail_at_hook) if fail_at_hook is not None else None
        self._exception = exception
        self._failure_return = failure_return

    @property
    def hook_order(self) -> list[str]:
        """Hook names in the order they were called."""
        return list(self.calls)

    def _record(self, hook_name: str, state: LifecycleState) -> TransitionCallbackReturn:
        self.calls.append(hook_name)
        self.states[hook_name].append(state)
        if self._fail_at_hook == hook_name:
            if self._exception is not None:
                raise self._exception
            return self._failure_return
        return TransitionCallbackReturn.SUCCESS

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._record("configure", state)

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._record("activate", state)

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._record("deactivate", state)

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._record("cleanup", state)

    def _on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._record("shutdown", state)

    def _on_error(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._record("error", state)


class FailingComponent(FakeComponent):
    """Fake component that raises from one lifecycle hook by default."""

    def __init__(
        self,
        name: str = "failing_component",
        *,
        fail_at_hook: str = "_on_configure",
        exception: Exception | None = None,
    ) -> None:
        super().__init__(
            name=name,
            fail_at_hook=fail_at_hook,
            exception=exception if exception is not None else RuntimeError("configured lifecycle failure"),
        )


class _RecordingPublisher:
    def __init__(self) -> None:
        self.messages: list[std_msgs.msg.String] = []

    def publish(self, msg: std_msgs.msg.String) -> None:
        self.messages.append(msg)


class FakePublisherComponent(LifecyclePublisherComponent[std_msgs.msg.String]):
    """Publisher fake that records published ``std_msgs.msg.String`` messages."""

    def __init__(self, name: str = "fake_publisher", topic_name: str = "/fake_topic") -> None:
        super().__init__(name=name, topic_name=topic_name, msg_type=std_msgs.msg.String, qos_profile=10)

    @property
    def published_messages(self) -> list[std_msgs.msg.String]:
        if self._publisher is None:
            return []
        return list(cast(_RecordingPublisher, self._publisher).messages)

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._publisher = cast(Any, _RecordingPublisher())
        return TransitionCallbackReturn.SUCCESS

    def _release_resources(self) -> None:
        self._publisher = None
        LifecycleComponent._release_resources(self)


class FakeSubscriberComponent(LifecycleSubscriberComponent[std_msgs.msg.String]):
    """Subscriber fake that records received ``std_msgs.msg.String`` messages."""

    def __init__(self, name: str = "fake_subscriber", topic_name: str = "/fake_topic") -> None:
        super().__init__(name=name, topic_name=topic_name, msg_type=std_msgs.msg.String, qos_profile=10)
        self.received_messages: list[std_msgs.msg.String] = []

    def receive(self, msg: std_msgs.msg.String) -> None:
        """Deliver a message through the activation-gated subscriber wrapper."""
        self._on_message_wrapper(msg)

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._subscription = cast(Any, object())
        return TransitionCallbackReturn.SUCCESS

    def on_message(self, msg: std_msgs.msg.String) -> None:
        self.received_messages.append(msg)

    def _release_resources(self) -> None:
        self._subscription = None
        LifecycleComponent._release_resources(self)


class _ControlledTimer:
    def __init__(self, *, autostart: bool) -> None:
        self._is_canceled = not autostart

    def cancel(self) -> None:
        self._is_canceled = True

    def reset(self) -> None:
        self._is_canceled = False

    def is_canceled(self) -> bool:
        return self._is_canceled


class FakeTimerComponent(LifecycleTimerComponent):
    """Timer fake with manually controlled ticks."""

    def __init__(self, name: str = "fake_timer", period: float = 0.1, *, autostart: bool = True) -> None:
        super().__init__(name=name, period=period, autostart=autostart)
        self.ticks: int = 0

    def tick(self) -> None:
        """Deliver one timer tick through the activation-gated timer wrapper."""
        self._on_timer_wrapper()

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._timer = cast(Any, _ControlledTimer(autostart=self.autostart))
        return TransitionCallbackReturn.SUCCESS

    def on_tick(self) -> None:
        self.ticks += 1

    def _release_resources(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        LifecycleComponent._release_resources(self)


class FakeServiceComponent(LifecycleServiceServerComponent[std_srvs.srv.Trigger]):
    """Trigger service fake that returns a fixed response or raises on demand."""

    def __init__(
        self,
        name: str = "fake_service",
        service_name: str = "/fake_service",
        *,
        success: bool = True,
        message: str = "ok",
        exception: Exception | None = None,
    ) -> None:
        super().__init__(name=name, service_name=service_name, srv_type=std_srvs.srv.Trigger)
        self.requests: list[std_srvs.srv.Trigger.Request] = []
        self._success = success
        self._message = message
        self._exception = exception

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._service = cast(Any, object())
        return TransitionCallbackReturn.SUCCESS

    def on_service_request(
        self,
        request: std_srvs.srv.Trigger.Request,
        response: std_srvs.srv.Trigger.Response,
    ) -> std_srvs.srv.Trigger.Response:
        self.requests.append(request)
        if self._exception is not None:
            raise self._exception
        response.success = self._success
        response.message = self._message
        return response

    def _release_resources(self) -> None:
        self._service = None
        LifecycleComponent._release_resources(self)


class _FakeClient:
    def __init__(self, response_factory: Callable[[], std_srvs.srv.Trigger.Response], service_available: bool) -> None:
        self.requests: list[std_srvs.srv.Trigger.Request] = []
        self.wait_calls: list[float | None] = []
        self._response_factory = response_factory
        self._service_available = service_available

    def wait_for_service(self, timeout_sec: float | None = None) -> bool:
        self.wait_calls.append(timeout_sec)
        return self._service_available

    def call(
        self,
        request: std_srvs.srv.Trigger.Request,
        timeout_sec: float | None = None,
    ) -> std_srvs.srv.Trigger.Response:
        self.requests.append(request)
        return self._response_factory()

    def call_async(self, request: std_srvs.srv.Trigger.Request) -> Any:
        self.requests.append(request)
        return self._response_factory()


class FakeClientComponent(LifecycleServiceClientComponent[std_srvs.srv.Trigger]):
    """Trigger client fake that returns a fixed response through the normal client API."""

    def __init__(
        self,
        name: str = "fake_client",
        service_name: str = "/fake_service",
        *,
        success: bool = True,
        message: str = "ok",
        service_available: bool = True,
    ) -> None:
        super().__init__(name=name, service_name=service_name, srv_type=std_srvs.srv.Trigger)
        self._success = success
        self._message = message
        self._service_available = service_available

    @property
    def requests(self) -> list[std_srvs.srv.Trigger.Request]:
        if self._client is None:
            return []
        return list(cast(_FakeClient, self._client).requests)

    def _make_response(self) -> std_srvs.srv.Trigger.Response:
        response = std_srvs.srv.Trigger.Response()
        response.success = self._success
        response.message = self._message
        return response

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._client = cast(Any, _FakeClient(self._make_response, self._service_available))
        return TransitionCallbackReturn.SUCCESS

    def _release_resources(self) -> None:
        self._client = None
        LifecycleComponent._release_resources(self)
