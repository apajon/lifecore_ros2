"""Shared test doubles and fixtures for service component tests.

Fixtures are loaded for tests/components via the local conftest module.

Import non-fixture helpers directly as needed::

    from tests.components._service_stubs import DUMMY_STATE, _TriggerServer, _TriggerClient
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import std_srvs.srv
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.components import (
    LifecyclePublisherComponent,
    LifecycleServiceClientComponent,
    LifecycleServiceServerComponent,
    LifecycleSubscriberComponent,
)
from lifecore_ros2.core import LifecycleComponentNode

# ---------------------------------------------------------------------------
# Shared constant
# ---------------------------------------------------------------------------

DUMMY_STATE = LifecycleState(state_id=0, label="test")

# ---------------------------------------------------------------------------
# Concrete test doubles
# ---------------------------------------------------------------------------


class _TriggerServer(LifecycleServiceServerComponent[std_srvs.srv.Trigger]):
    """Trigger service server that records handler invocations and returns success."""

    def __init__(
        self,
        name: str = "trigger_srv",
        service_name: str = "/test_trigger_svc",
        **kwargs: Any,
    ) -> None:
        super().__init__(name=name, service_name=service_name, **kwargs)
        self.handler_called: bool = False

    def on_service_request(
        self,
        request: std_srvs.srv.Trigger.Request,
        response: std_srvs.srv.Trigger.Response,
    ) -> std_srvs.srv.Trigger.Response:
        self.handler_called = True
        response.success = True
        response.message = "ok"
        return response


class _EmptyServer(LifecycleServiceServerComponent[std_srvs.srv.Empty]):
    """Empty service server (response has no diagnostic fields)."""

    def __init__(self, name: str = "empty_srv", service_name: str = "/test_empty_svc") -> None:
        super().__init__(name=name, service_name=service_name)
        self.handler_called: bool = False

    def on_service_request(
        self,
        request: std_srvs.srv.Empty.Request,
        response: std_srvs.srv.Empty.Response,
    ) -> std_srvs.srv.Empty.Response:
        self.handler_called = True
        return response


class _CrashingServer(LifecycleServiceServerComponent[std_srvs.srv.Trigger]):
    """Server whose handler always raises to test exception-guard behavior."""

    def __init__(self, name: str = "crashing_srv", service_name: str = "/test_crashing_svc") -> None:
        super().__init__(name=name, service_name=service_name)

    def on_service_request(self, request: Any, response: Any) -> Any:
        raise RuntimeError("handler exploded")


class _TriggerClient(LifecycleServiceClientComponent[std_srvs.srv.Trigger]):
    """Trigger service client with srv_type inferred from the generic parameter."""

    def __init__(
        self,
        name: str = "trigger_cli",
        service_name: str = "/test_trigger_svc",
        **kwargs: Any,
    ) -> None:
        super().__init__(name=name, service_name=service_name, **kwargs)


class _GatedPublisher(LifecyclePublisherComponent[Any]):
    """Publisher stub with injected mock publisher for activation-gating consistency tests."""

    def __init__(self) -> None:
        super().__init__(name="g_pub", topic_name="/g_topic", msg_type=MagicMock, qos_profile=10)

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._publisher = MagicMock()
        return TransitionCallbackReturn.SUCCESS

    def _release_resources(self) -> None:
        self._publisher = None
        super()._release_resources()


class _GatedSubscriber(LifecycleSubscriberComponent[Any]):
    """Subscriber stub with injected mock subscription for activation-gating consistency tests."""

    def __init__(self) -> None:
        super().__init__(name="g_sub", topic_name="/g_topic", msg_type=MagicMock, qos_profile=10)
        self.received: list[Any] = []

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._subscription = MagicMock()
        return TransitionCallbackReturn.SUCCESS

    def on_message(self, msg: Any) -> None:
        self.received.append(msg)

    def _release_resources(self) -> None:
        self._subscription = None
        super()._release_resources()


# ---------------------------------------------------------------------------
# Shared fixtures — loaded via tests/components/conftest.py
# ---------------------------------------------------------------------------


@pytest.fixture()
def node() -> Generator[LifecycleComponentNode, None, None]:
    n = LifecycleComponentNode("svc_test_node")
    yield n
    n.destroy_node()


@pytest.fixture()
def mock_svc_factories(node: LifecycleComponentNode) -> Generator[None, None, None]:
    """Patch node service/client factory methods so no real ROS endpoints are created."""
    with (
        patch.object(node, "create_service", return_value=MagicMock()),
        patch.object(node, "destroy_service"),
        patch.object(node, "create_client", return_value=MagicMock()),
        patch.object(node, "destroy_client"),
    ):
        yield
