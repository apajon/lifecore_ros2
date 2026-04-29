"""Regression tests for LifecycleServiceClientComponent lifecycle, activation gating, and call parameters.

Coverage map (this file):
    Transition  | Unit (component) | Failure path
    configure   |        ✓ D       |      –
    activate    |        ✓ D       |      –
    deactivate  |        ✓ E       |      –
    cleanup     |        ✓ D       |      –

Activation gating (Section E):
    Outbound (call, call_async, wait_for_service): RuntimeError while inactive ✓
    ComponentNotConfiguredError when _client is None ✓

Call parameters (Section E2):
    call timeout_service: wait guard, TimeoutError when unavailable ✓
    call timeout_call: forwarded as timeout_sec to rclpy ✓
    call_async timeout_service: wait guard, TimeoutError when unavailable ✓

See also:
    tests/components/test_service_server.py  — LifecycleServiceServerComponent lifecycle and gating
    tests/components/test_service_components.py — ServiceComponent inference, integration, and four-primitive consistency
"""

from __future__ import annotations

import pytest
import std_srvs.srv
from rclpy.lifecycle import TransitionCallbackReturn

from lifecore_ros2.core import LifecycleComponentNode
from lifecore_ros2.core.exceptions import ComponentNotConfiguredError
from tests.components._service_stubs import DUMMY_STATE, _TriggerClient

# ---------------------------------------------------------------------------
# Section D — LifecycleServiceClientComponent lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_svc_factories")
class TestLifecycleServiceClientLifecycle:
    """Client is created on configure and released on cleanup."""

    def test_configure_creates_client(self, node: LifecycleComponentNode) -> None:
        # Regression: _on_configure did not create the ROS client.
        # Expected: node.create_client called once; _client is set.
        client = _TriggerClient()
        node.add_component(client)

        result = client.on_configure(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        node.create_client.assert_called_once()  # type: ignore[attr-defined]
        assert client._client is not None

    def test_cleanup_destroys_client(self, node: LifecycleComponentNode) -> None:
        # Regression: _on_cleanup did not release the ROS client.
        # Expected: node.destroy_client called; _client is None after cleanup.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)
        client.on_deactivate(DUMMY_STATE)

        result = client.on_cleanup(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        node.destroy_client.assert_called_once()  # type: ignore[attr-defined]
        assert client._client is None

    def test_reconfigure_cycle_client(self, node: LifecycleComponentNode) -> None:
        # Regression: second configure after cleanup failed because _client was not cleared.
        # Expected: configure → cleanup → configure works without error.
        client = _TriggerClient()
        node.add_component(client)

        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)
        client.on_deactivate(DUMMY_STATE)
        client.on_cleanup(DUMMY_STATE)
        result = client.on_configure(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        assert client._client is not None


# ---------------------------------------------------------------------------
# Section E — LifecycleServiceClientComponent activation gating
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_svc_factories")
class TestLifecycleServiceClientActivationGating:
    """Outbound client primitives raise RuntimeError while the component is not active."""

    def test_call_raises_when_not_active(self, node: LifecycleComponentNode) -> None:
        # Regression: client.call() did not raise when component was inactive.
        # Expected: RuntimeError from @when_active before any transport is touched.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        # Configured but NOT activated.

        with pytest.raises(RuntimeError, match="not active"):
            client.call(std_srvs.srv.Trigger.Request())

    def test_call_async_raises_when_not_active(self, node: LifecycleComponentNode) -> None:
        # Regression: client.call_async() did not raise when component was inactive.
        # Expected: RuntimeError from @when_active.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)

        with pytest.raises(RuntimeError, match="not active"):
            client.call_async(std_srvs.srv.Trigger.Request())

    def test_wait_for_service_raises_when_not_active(self, node: LifecycleComponentNode) -> None:
        # Regression: wait_for_service() did not raise when component was inactive.
        # Expected: RuntimeError from @when_active.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)

        with pytest.raises(RuntimeError, match="not active"):
            client.wait_for_service(timeout=0.0)

    def test_call_raises_component_not_configured_when_client_none(self, node: LifecycleComponentNode) -> None:
        # Regression: defensive guard inside call() could be bypassed if _client was somehow None
        # while _is_active was True (e.g. manual state corruption or future refactor).
        # Expected: ComponentNotConfiguredError from the _client is None guard.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)
        # Simulate _client being cleared while the component remains active.
        client._client = None  # type: ignore[assignment]

        with pytest.raises(ComponentNotConfiguredError):
            client.call(std_srvs.srv.Trigger.Request())


# ---------------------------------------------------------------------------
# Section E2 — call / call_async timeout parameters
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_svc_factories")
class TestLifecycleServiceClientCallParameters:
    """timeout_service and timeout_call parameters on call() and call_async()."""

    # -- call() timeout_service --------------------------------------------------

    def test_call_no_timeout_service_skips_wait(self, node: LifecycleComponentNode) -> None:
        # Guard: when timeout_service is None (default), wait_for_service is NOT called.
        # Expected: _client.wait_for_service is never invoked; call proceeds directly.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)
        client._client.call.return_value = std_srvs.srv.Trigger.Response()  # type: ignore[union-attr]

        client.call(std_srvs.srv.Trigger.Request())

        client._client.wait_for_service.assert_not_called()  # type: ignore[union-attr]

    def test_call_timeout_service_available_proceeds(self, node: LifecycleComponentNode) -> None:
        # Guard: when timeout_service is set and service is available, call proceeds normally.
        # Expected: wait_for_service called with timeout_sec=1.0; call() executed.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)
        client._client.wait_for_service.return_value = True  # type: ignore[union-attr]
        client._client.call.return_value = std_srvs.srv.Trigger.Response()  # type: ignore[union-attr]

        client.call(std_srvs.srv.Trigger.Request(), timeout_service=1.0)

        client._client.wait_for_service.assert_called_once_with(timeout_sec=1.0)  # type: ignore[union-attr]
        client._client.call.assert_called_once()  # type: ignore[union-attr]

    def test_call_timeout_service_unavailable_raises(self, node: LifecycleComponentNode) -> None:
        # Guard: when service is not available within timeout_service, TimeoutError is raised.
        # Expected: TimeoutError; _client.call is NOT invoked.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)
        client._client.wait_for_service.return_value = False  # type: ignore[union-attr]

        with pytest.raises(TimeoutError, match="not available after 0.5s"):
            client.call(std_srvs.srv.Trigger.Request(), timeout_service=0.5)

        client._client.call.assert_not_called()  # type: ignore[union-attr]

    # -- call() timeout_call -----------------------------------------------------

    def test_call_timeout_call_forwarded(self, node: LifecycleComponentNode) -> None:
        # Guard: timeout_call is passed as timeout_sec to the underlying rclpy client.call().
        # Expected: _client.call(request, timeout_sec=2.0) is called exactly once.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)
        client._client.call.return_value = std_srvs.srv.Trigger.Response()  # type: ignore[union-attr]

        client.call(std_srvs.srv.Trigger.Request(), timeout_call=2.0)

        client._client.call.assert_called_once()  # type: ignore[union-attr]
        _, kwargs = client._client.call.call_args  # type: ignore[union-attr]
        assert kwargs.get("timeout_sec") == 2.0

    def test_call_no_timeout_call_passes_none(self, node: LifecycleComponentNode) -> None:
        # Guard: when timeout_call is not supplied, timeout_sec=None is forwarded.
        # Expected: _client.call receives timeout_sec=None.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)
        client._client.call.return_value = std_srvs.srv.Trigger.Response()  # type: ignore[union-attr]

        client.call(std_srvs.srv.Trigger.Request())

        _, kwargs = client._client.call.call_args  # type: ignore[union-attr]
        assert kwargs.get("timeout_sec") is None

    def test_call_both_timeouts_combined(self, node: LifecycleComponentNode) -> None:
        # Guard: timeout_service and timeout_call can be used together.
        # Expected: wait_for_service called first; call forwarded with timeout_sec=3.0.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)
        client._client.wait_for_service.return_value = True  # type: ignore[union-attr]
        client._client.call.return_value = std_srvs.srv.Trigger.Response()  # type: ignore[union-attr]

        client.call(std_srvs.srv.Trigger.Request(), timeout_service=1.0, timeout_call=3.0)

        client._client.wait_for_service.assert_called_once_with(timeout_sec=1.0)  # type: ignore[union-attr]
        _, kwargs = client._client.call.call_args  # type: ignore[union-attr]
        assert kwargs.get("timeout_sec") == 3.0

    # -- call_async() timeout_service --------------------------------------------

    def test_call_async_no_timeout_service_skips_wait(self, node: LifecycleComponentNode) -> None:
        # Guard: when timeout_service is None (default), wait_for_service is NOT called.
        # Expected: _client.wait_for_service never invoked; call_async proceeds.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)

        client.call_async(std_srvs.srv.Trigger.Request())

        client._client.wait_for_service.assert_not_called()  # type: ignore[union-attr]

    def test_call_async_timeout_service_available_proceeds(self, node: LifecycleComponentNode) -> None:
        # Guard: when timeout_service is set and service is available, call_async proceeds.
        # Expected: wait_for_service called with timeout_sec=1.0; call_async() executed.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)
        client._client.wait_for_service.return_value = True  # type: ignore[union-attr]

        client.call_async(std_srvs.srv.Trigger.Request(), timeout_service=1.0)

        client._client.wait_for_service.assert_called_once_with(timeout_sec=1.0)  # type: ignore[union-attr]
        client._client.call_async.assert_called_once()  # type: ignore[union-attr]

    def test_call_async_timeout_service_unavailable_raises(self, node: LifecycleComponentNode) -> None:
        # Guard: when service is not available within timeout_service, TimeoutError is raised.
        # Expected: TimeoutError; _client.call_async is NOT invoked.
        client = _TriggerClient()
        node.add_component(client)
        client.on_configure(DUMMY_STATE)
        client.on_activate(DUMMY_STATE)
        client._client.wait_for_service.return_value = False  # type: ignore[union-attr]

        with pytest.raises(TimeoutError, match="not available after 0.5s"):
            client.call_async(std_srvs.srv.Trigger.Request(), timeout_service=0.5)

        client._client.call_async.assert_not_called()  # type: ignore[union-attr]
