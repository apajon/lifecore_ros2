"""Regression tests for LifecycleServiceServerComponent lifecycle and activation gating.

Coverage map (this file):
    Transition  | Unit (component) | Failure path | Exception guard
    configure   |        ✓ B       |      ✓ B     |       –
    activate    |        ✓ B       |      –       |       –
    deactivate  |        ✓ C       |      –       |       –
    cleanup     |        ✓ B       |      –       |       –
    shutdown    |        ✓ B       |      –       |       –
    error       |        ✓ B       |      –       |       –

Activation gating (Section C):
    Inbound inactive-response policy: success=False + message for Trigger, unchanged for Empty ✓
    Exception in on_service_request: absorbed, component state unaffected ✓

See also:
    tests/components/test_service_client.py  — LifecycleServiceClientComponent lifecycle, gating, and call parameters
    tests/components/test_service_components.py — ServiceComponent inference, integration, and four-primitive consistency
"""

from __future__ import annotations

import pytest
import std_srvs.srv
from rclpy.lifecycle import TransitionCallbackReturn

from lifecore_ros2.core import LifecycleComponentNode
from lifecore_ros2.core.exceptions import InvalidLifecycleTransitionError
from tests.components._service_stubs import DUMMY_STATE, _CrashingServer, _EmptyServer, _TriggerServer

# ---------------------------------------------------------------------------
# Section B — LifecycleServiceServerComponent lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_svc_factories")
class TestLifecycleServiceServerLifecycle:
    """Service is created on configure and released on cleanup / shutdown / error."""

    def test_configure_creates_service(self, node: LifecycleComponentNode) -> None:
        # Regression: _on_configure did not create the ROS service.
        # Expected: node.create_service called once; _service is set.
        server = _TriggerServer()
        node.add_component(server)

        result = server.on_configure(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        node.create_service.assert_called_once()  # type: ignore[attr-defined]
        assert server._service is not None

    def test_cleanup_destroys_service(self, node: LifecycleComponentNode) -> None:
        # Regression: _on_cleanup did not release the ROS service.
        # Expected: node.destroy_service called; _service is None after cleanup.
        server = _TriggerServer()
        node.add_component(server)
        server.on_configure(DUMMY_STATE)
        server.on_activate(DUMMY_STATE)
        server.on_deactivate(DUMMY_STATE)

        result = server.on_cleanup(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        node.destroy_service.assert_called_once()  # type: ignore[attr-defined]
        assert server._service is None

    def test_reconfigure_cycle(self, node: LifecycleComponentNode) -> None:
        # Regression: second configure after cleanup failed because _service was not cleared.
        # Expected: configure → cleanup → configure works without error.
        server = _TriggerServer()
        node.add_component(server)

        server.on_configure(DUMMY_STATE)
        server.on_activate(DUMMY_STATE)
        server.on_deactivate(DUMMY_STATE)
        server.on_cleanup(DUMMY_STATE)
        result = server.on_configure(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        assert server._service is not None

    def test_double_activate_raises_invalid_transition(self, node: LifecycleComponentNode) -> None:
        # Guard: double activate is intentionally rejected to prevent hidden lifecycle bugs.
        # Expected: InvalidLifecycleTransitionError raised; component stays active after rejection.
        server = _TriggerServer()
        node.add_component(server)
        server.on_configure(DUMMY_STATE)
        server.on_activate(DUMMY_STATE)

        with pytest.raises(InvalidLifecycleTransitionError):
            server.on_activate(DUMMY_STATE)

        assert server.is_active  # activation state is preserved after the rejected transition

    def test_shutdown_releases_resources(self, node: LifecycleComponentNode) -> None:
        # Regression: shutdown path did not call _release_resources on the server.
        # Expected: _service is None and is_active is False after shutdown.
        server = _TriggerServer()
        node.add_component(server)
        server.on_configure(DUMMY_STATE)
        server.on_activate(DUMMY_STATE)

        result = server.on_shutdown(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        assert server._service is None
        assert not server.is_active

    def test_error_releases_resources(self, node: LifecycleComponentNode) -> None:
        # Regression: error transition did not release server resources.
        # Expected: _service is None and is_active is False after error.
        server = _TriggerServer()
        node.add_component(server)
        server.on_configure(DUMMY_STATE)
        server.on_activate(DUMMY_STATE)

        result = server.on_error(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        assert server._service is None
        assert not server.is_active


# ---------------------------------------------------------------------------
# Section C — LifecycleServiceServerComponent activation gating
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_svc_factories")
class TestLifecycleServiceServerActivationGating:
    """_on_request_wrapper gates requests and annotates responses while inactive."""

    def test_inactive_request_annotates_success_and_message_fields(self, node: LifecycleComponentNode) -> None:
        # Regression: inactive server returned an un-annotated default response.
        # Expected: success=False and message="component inactive" when fields exist (Trigger).
        server = _TriggerServer()
        node.add_component(server)
        server.on_configure(DUMMY_STATE)
        # Not activated — component is inactive.

        request = std_srvs.srv.Trigger.Request()
        response = std_srvs.srv.Trigger.Response()
        result = server._on_request_wrapper(request, response)

        assert result.success is False
        assert result.message == "component inactive"

    def test_inactive_request_leaves_fieldless_response_unmodified(self, node: LifecycleComponentNode) -> None:
        # Regression: framework tried to set .success on an Empty response and raised AttributeError.
        # Expected: Empty response (no diagnostic fields) is returned unchanged.
        server = _EmptyServer()
        node.add_component(server)
        server.on_configure(DUMMY_STATE)

        request = std_srvs.srv.Empty.Request()
        response = std_srvs.srv.Empty.Response()
        result = server._on_request_wrapper(request, response)

        assert result is response  # same object, unmodified

    def test_inactive_request_does_not_invoke_user_handler(self, node: LifecycleComponentNode) -> None:
        # Regression: user's on_service_request was called while the component was inactive.
        # Expected: handler_called stays False when component is inactive.
        server = _TriggerServer()
        node.add_component(server)
        server.on_configure(DUMMY_STATE)

        server._on_request_wrapper(std_srvs.srv.Trigger.Request(), std_srvs.srv.Trigger.Response())

        assert not server.handler_called

    def test_active_request_invokes_user_handler(self, node: LifecycleComponentNode) -> None:
        # Guard: on_service_request must be called when component is active.
        # Expected: handler_called is True; response reflects handler output.
        server = _TriggerServer()
        node.add_component(server)
        server.on_configure(DUMMY_STATE)
        server.on_activate(DUMMY_STATE)

        result = server._on_request_wrapper(std_srvs.srv.Trigger.Request(), std_srvs.srv.Trigger.Response())

        assert server.handler_called
        assert result.success is True
        assert result.message == "ok"

    def test_exception_in_handler_returns_default_response(self, node: LifecycleComponentNode) -> None:
        # Regression: unhandled exception in on_service_request propagated into the rclpy executor.
        # Expected: exception is caught; default-constructed response is returned.
        server = _CrashingServer()
        node.add_component(server)
        server.on_configure(DUMMY_STATE)
        server.on_activate(DUMMY_STATE)

        response = std_srvs.srv.Trigger.Response()
        result = server._on_request_wrapper(std_srvs.srv.Trigger.Request(), response)

        # The default (unmodified) response is returned — not an exception.
        assert result is response

    def test_exception_in_handler_does_not_affect_lifecycle_state(self, node: LifecycleComponentNode) -> None:
        # Regression: exception in handler silently corrupted _is_active.
        # Expected: component remains active after the exception is absorbed.
        server = _CrashingServer()
        node.add_component(server)
        server.on_configure(DUMMY_STATE)
        server.on_activate(DUMMY_STATE)

        server._on_request_wrapper(std_srvs.srv.Trigger.Request(), std_srvs.srv.Trigger.Response())

        assert server.is_active
