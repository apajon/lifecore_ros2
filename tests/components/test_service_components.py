"""Regression tests for ServiceComponent base, integration, and four-primitive activation-gating consistency.

Coverage map (this file):
    Section A — srv_type inference (ServiceComponent base via server and client subclasses)
    Section F — Integration: server + client co-located on the same node
    Section G — Four-primitive activation-gating consistency regression

See also:
    tests/components/test_service_server.py  — LifecycleServiceServerComponent lifecycle and activation gating
    tests/components/test_service_client.py  — LifecycleServiceClientComponent lifecycle, gating, and call parameters
"""

from __future__ import annotations

import threading
import time
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
import std_srvs.srv
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from lifecore_ros2.components import LifecycleServiceServerComponent
from lifecore_ros2.core import LifecycleComponentNode
from lifecore_ros2.core.exceptions import _InterfaceTypeNotResolvedError
from tests.components._service_stubs import (
    DUMMY_STATE,
    _GatedPublisher,
    _GatedSubscriber,
    _TriggerClient,
    _TriggerServer,
)

# ---------------------------------------------------------------------------
# Local fixture — only needed in this file
# ---------------------------------------------------------------------------


@pytest.fixture()
def spinning_service_node() -> Generator[tuple[LifecycleComponentNode, MultiThreadedExecutor], None, None]:
    """LifecycleComponentNode with a background MultiThreadedExecutor for real service round-trips."""
    node = LifecycleComponentNode("svc_integ_node")
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()
    yield node, executor
    executor.shutdown()
    node.destroy_node()
    spin_thread.join(timeout=5.0)


# ---------------------------------------------------------------------------
# Section A — ServiceComponent srv_type inference
# ---------------------------------------------------------------------------


class TestServiceComponentTypeInference:
    """srv_type is resolved from the generic parameter or explicit argument at __init__ time."""

    def test_srv_type_inferred_from_generic_server(self, node: LifecycleComponentNode) -> None:
        # Regression: srv_type not inferred when generic parameter is supplied without explicit arg.
        # Expected: LifecycleServiceServerComponent[Trigger] resolves srv_type as Trigger.
        server = _TriggerServer()
        node.add_component(server)
        assert server.srv_type is std_srvs.srv.Trigger

    def test_srv_type_inferred_from_generic_client(self, node: LifecycleComponentNode) -> None:
        # Regression: srv_type not inferred on client side.
        # Expected: _TriggerClient (parameterized with Trigger) resolves srv_type correctly.
        client = _TriggerClient()
        node.add_component(client)
        assert client.srv_type is std_srvs.srv.Trigger

    def test_srv_type_explicit_honored(self, node: LifecycleComponentNode) -> None:
        # Regression: explicit srv_type argument ignored when generic is unparameterized.
        # Expected: explicitly supplied type is stored as srv_type.
        class _UnparamServer(LifecycleServiceServerComponent):  # type: ignore[type-arg]
            def on_service_request(self, request: Any, response: Any) -> Any:
                return response

        server = _UnparamServer(name="explicit_srv", service_name="/test", srv_type=std_srvs.srv.Trigger)
        node.add_component(server)
        assert server.srv_type is std_srvs.srv.Trigger

    def test_srv_type_not_resolved_raises(self) -> None:
        # Regression: unparameterized subclass with no explicit srv_type must fail immediately.
        # Expected: _InterfaceTypeNotResolvedError raised at __init__ time (is-a TypeError).
        class _UnparamServer(LifecycleServiceServerComponent):  # type: ignore[type-arg]
            def on_service_request(self, request: Any, response: Any) -> Any:
                return response

        with pytest.raises(_InterfaceTypeNotResolvedError):
            _UnparamServer(name="no_type_srv", service_name="/test")

    def test_srv_type_conflict_raises(self) -> None:
        # Regression: conflicting generic and explicit types must fail instead of silently using one.
        # Expected: _InterfaceTypeNotResolvedError raised when both sources disagree.
        with pytest.raises(_InterfaceTypeNotResolvedError):
            _TriggerServer(
                name="conflict_srv",
                service_name="/test",
                srv_type=std_srvs.srv.Empty,  # type: ignore[arg-type]
            )


# ---------------------------------------------------------------------------
# Section B — see tests/components/test_service_server.py
# Section C — see tests/components/test_service_server.py
# Section D — see tests/components/test_service_client.py
# Section E — see tests/components/test_service_client.py
# Section E2 — see tests/components/test_service_client.py
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Section F — Integration: server + client co-located on the same node
# ---------------------------------------------------------------------------


class TestServiceIntegration:
    """Service is created on configure and released on cleanup / shutdown / error."""

    """Server and client on the same node communicate end-to-end through the lifecycle."""

    def test_server_client_full_roundtrip(
        self,
        spinning_service_node: tuple[LifecycleComponentNode, MultiThreadedExecutor],
    ) -> None:
        # Guard: both ACTIVE server and client on the same node complete a round-trip.
        # Expected: response is returned with success=True and message="ok".
        node, _executor = spinning_service_node
        cb_group = ReentrantCallbackGroup()

        server = _TriggerServer("integ_srv", "/svc_roundtrip", callback_group=cb_group)
        client = _TriggerClient("integ_cli", "/svc_roundtrip", callback_group=cb_group)
        node.add_component(server)
        node.add_component(client)

        node.trigger_configure()
        node.trigger_activate()

        future = client.call_async(std_srvs.srv.Trigger.Request())

        deadline = time.time() + 5.0
        while not future.done() and time.time() < deadline:
            time.sleep(0.01)

        assert future.done(), "service round-trip did not complete within 5 s"
        response = future.result()
        assert response is not None
        assert response.success is True
        assert response.message == "ok"

    def test_server_inactive_returns_default_response_directly(
        self,
        node: LifecycleComponentNode,
        mock_svc_factories: None,
    ) -> None:
        # Regression: inactive server silently dropped the request or raised.
        # Expected: _on_request_wrapper returns a default response; handler is NOT called.
        # Direct wrapper invocation avoids the need for a running executor.
        server = _TriggerServer("inact_srv", "/test_inact")
        node.add_component(server)
        server.on_configure(DUMMY_STATE)
        # NOT activated — server is inactive.

        request = std_srvs.srv.Trigger.Request()
        response = std_srvs.srv.Trigger.Response()
        result = server._on_request_wrapper(request, response)

        assert result.success is False
        assert result.message == "component inactive"
        assert not server.handler_called

    def test_client_deactivated_raises_on_call(
        self,
        node: LifecycleComponentNode,
        mock_svc_factories: None,
    ) -> None:
        # Regression: deactivated client did not raise on subsequent call().
        # Expected: RuntimeError raised after deactivate; client is not broken.
        client = _TriggerClient("deact_cli", "/test_deact")
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)
        client.on_deactivate(DUMMY_STATE)

        with pytest.raises(RuntimeError, match="not active"):
            client.call(std_srvs.srv.Trigger.Request())


# ---------------------------------------------------------------------------
# Section G — Four-primitive activation-gating consistency regression
# ---------------------------------------------------------------------------

_GATING_PARAMS: list[tuple[str, bool]] = [
    ("publisher_publish", True),
    ("client_call", True),
    ("client_call_async", True),
    ("client_wait_for_service", True),
    ("subscriber_on_message_wrapper", False),
    ("server_on_request_wrapper", False),
]


class TestFourPrimitiveActivationGatingConsistency:
    """Outbound primitives raise; inbound primitives absorb silently — all while inactive.

    This parametrized test guards the consistency contract across all four
    topic/service lifecycle primitives so a future change to one does not
    silently break the others.
    """

    @pytest.mark.parametrize("primitive_id,expect_raise", _GATING_PARAMS)
    def test_outbound_raises_inbound_silent_when_inactive(
        self,
        node: LifecycleComponentNode,
        mock_svc_factories: None,
        primitive_id: str,
        expect_raise: bool,
    ) -> None:
        # Regression: inconsistency between primitive families — one raised, another silently passed.
        # Expected:
        #   - Outbound (publish, call, call_async, wait_for_service): raise RuntimeError("not active").
        #   - Inbound  (subscriber wrapper, server wrapper): return without raising; user code NOT called.
        pub = _GatedPublisher()
        sub = _GatedSubscriber()
        server = _TriggerServer("g_srv", "/g_svc")
        client = _TriggerClient("g_cli", "/g_svc")

        for comp in (pub, sub, server, client):
            node.add_component(comp)
            comp.on_configure(DUMMY_STATE)
        # All four are configured but NOT activated.

        def _invoke_publisher() -> None:
            pub.publish(MagicMock())

        def _invoke_client_call() -> None:
            client.call(std_srvs.srv.Trigger.Request())

        def _invoke_client_call_async() -> None:
            client.call_async(std_srvs.srv.Trigger.Request())

        def _invoke_client_wait() -> None:
            client.wait_for_service(timeout=0.0)

        def _invoke_subscriber_wrapper() -> None:
            sub._on_message_wrapper("msg")

        def _invoke_server_wrapper() -> None:
            server._on_request_wrapper(std_srvs.srv.Trigger.Request(), std_srvs.srv.Trigger.Response())

        dispatch = {
            "publisher_publish": _invoke_publisher,
            "client_call": _invoke_client_call,
            "client_call_async": _invoke_client_call_async,
            "client_wait_for_service": _invoke_client_wait,
            "subscriber_on_message_wrapper": _invoke_subscriber_wrapper,
            "server_on_request_wrapper": _invoke_server_wrapper,
        }
        invoke = dispatch[primitive_id]

        if expect_raise:
            with pytest.raises(RuntimeError, match="not active"):
                invoke()
        else:
            invoke()  # must not raise
            # Inbound wrappers must not invoke user code while inactive.
            if primitive_id == "subscriber_on_message_wrapper":
                assert sub.received == [], "on_message must not be called while inactive"
            else:
                assert not server.handler_called, "on_service_request must not be called while inactive"
