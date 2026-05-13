from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from rclpy.lifecycle import TransitionCallbackReturn

from lifecore_ros2.components import LifecycleParameterObserverComponent
from lifecore_ros2.components.lifecycle_parameter_observer_component import (
    ObservedParameterEvent,
    ObservedParameterSnapshot,
    ParameterWatchHandle,
    WatchState,
)
from lifecore_ros2.core import LifecycleComponentNode
from lifecore_ros2.testing import DUMMY_STATE

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_parameter_event(
    node_name: str,
    changed: dict[str, Any] | None = None,
    new: dict[str, Any] | None = None,
    deleted: list[str] | None = None,
) -> Any:
    """Build a minimal fake ParameterEvent message for use in unit tests."""
    from rcl_interfaces.msg import Parameter as RclParam
    from rcl_interfaces.msg import ParameterEvent, ParameterValue
    from rclpy.parameter import Parameter

    def _make_param(name: str, value: Any) -> RclParam:
        pv = ParameterValue()
        t = Parameter.Type.from_parameter_value(value)
        pv.type = t.value
        if t == Parameter.Type.BOOL:
            pv.bool_value = value
        elif t == Parameter.Type.INTEGER:
            pv.integer_value = value
        elif t == Parameter.Type.DOUBLE:
            pv.double_value = value
        elif t == Parameter.Type.STRING:
            pv.string_value = value
        elif t == Parameter.Type.BYTE_ARRAY:
            pv.bytes_value = list(value)
        p = RclParam()
        p.name = name
        p.value = pv
        return p

    def _make_deleted(name: str) -> RclParam:
        p = RclParam()
        p.name = name
        p.value = ParameterValue()  # type NOT_SET = 0
        return p

    msg = ParameterEvent()
    msg.node = node_name
    msg.changed_parameters = [_make_param(k, v) for k, v in (changed or {}).items()]
    msg.new_parameters = [_make_param(k, v) for k, v in (new or {}).items()]
    msg.deleted_parameters = [_make_deleted(n) for n in (deleted or [])]
    return msg


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def node() -> Generator[LifecycleComponentNode, None, None]:
    n = LifecycleComponentNode("observer_test_node")
    yield n
    n.destroy_node()


@pytest.fixture()
def mock_sub(node: LifecycleComponentNode) -> Generator[MagicMock, None, None]:
    sub_mock = MagicMock()
    with (
        patch.object(node, "create_subscription", return_value=sub_mock),
        patch.object(node, "destroy_subscription"),
    ):
        yield sub_mock


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


class TestWatchParameterRegistration:
    def test_returns_handle_with_correct_coordinates(self) -> None:
        component = LifecycleParameterObserverComponent("obs")
        handle = component.watch_parameter(node_name="/sensor", parameter_name="rate")

        assert isinstance(handle, ParameterWatchHandle)
        assert handle.node_name == "/sensor"
        assert handle.parameter_name == "rate"

    def test_duplicate_watch_raises_value_error(self) -> None:
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate")

        with pytest.raises(ValueError, match="Already watching"):
            component.watch_parameter(node_name="/sensor", parameter_name="rate")

    def test_watch_after_configure_raises_runtime_error(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        component = LifecycleParameterObserverComponent("obs")
        node.add_component(component)

        with patch.object(component, "_read_initial_parameter", return_value=(WatchState.UNAVAILABLE, None)):
            component.on_configure(DUMMY_STATE)

        with pytest.raises(RuntimeError, match="cannot register a watch while configured"):
            component.watch_parameter(node_name="/sensor", parameter_name="rate")

    def test_different_parameters_can_be_registered(self) -> None:
        component = LifecycleParameterObserverComponent("obs")
        h1 = component.watch_parameter(node_name="/a", parameter_name="x")
        h2 = component.watch_parameter(node_name="/a", parameter_name="y")
        h3 = component.watch_parameter(node_name="/b", parameter_name="x")

        assert h1.parameter_name == "x"
        assert h2.parameter_name == "y"
        assert h3.node_name == "/b"


# ---------------------------------------------------------------------------
# Configure: initial read outcomes
# ---------------------------------------------------------------------------


class TestConfigureInitialRead:
    def _configure(
        self,
        component: LifecycleParameterObserverComponent,
        node: LifecycleComponentNode,
        mock_sub: MagicMock,
        read_result: tuple[WatchState, object | None],
    ) -> TransitionCallbackReturn:
        node.add_component(component)
        with patch.object(component, "_read_initial_parameter", return_value=read_result):
            return component.on_configure(DUMMY_STATE)

    def test_configure_returns_success(self, node: LifecycleComponentNode, mock_sub: MagicMock) -> None:
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate")

        result = self._configure(component, node, mock_sub, (WatchState.VALUE_AVAILABLE, 10))

        assert result == TransitionCallbackReturn.SUCCESS

    def test_configure_records_value_available(self, node: LifecycleComponentNode, mock_sub: MagicMock) -> None:
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate")

        self._configure(component, node, mock_sub, (WatchState.VALUE_AVAILABLE, 10))

        snapshot = component.get_observed_parameter("/sensor", "rate")
        assert snapshot is not None
        assert snapshot.state == WatchState.VALUE_AVAILABLE
        assert snapshot.value == 10

    def test_configure_records_unknown_node(self, node: LifecycleComponentNode, mock_sub: MagicMock) -> None:
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/missing_node", parameter_name="rate")

        self._configure(component, node, mock_sub, (WatchState.UNKNOWN_NODE, None))

        snapshot = component.get_observed_parameter("/missing_node", "rate")
        assert snapshot is not None
        assert snapshot.state == WatchState.UNKNOWN_NODE
        assert snapshot.value is None

    def test_configure_records_unknown_parameter(self, node: LifecycleComponentNode, mock_sub: MagicMock) -> None:
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="absent")

        self._configure(component, node, mock_sub, (WatchState.UNKNOWN_PARAMETER, None))

        snapshot = component.get_observed_parameter("/sensor", "absent")
        assert snapshot is not None
        assert snapshot.state == WatchState.UNKNOWN_PARAMETER

    def test_configure_records_unavailable(self, node: LifecycleComponentNode, mock_sub: MagicMock) -> None:
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate")

        self._configure(component, node, mock_sub, (WatchState.UNAVAILABLE, None))

        snapshot = component.get_observed_parameter("/sensor", "rate")
        assert snapshot is not None
        assert snapshot.state == WatchState.UNAVAILABLE

    def test_configure_does_not_fail_on_absent_node(self, node: LifecycleComponentNode, mock_sub: MagicMock) -> None:
        """configure() must not fail by default when the remote node or parameter is absent."""
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/gone", parameter_name="x")

        result = self._configure(component, node, mock_sub, (WatchState.UNKNOWN_NODE, None))

        assert result == TransitionCallbackReturn.SUCCESS

    def test_read_initial_false_skips_read(self, node: LifecycleComponentNode, mock_sub: MagicMock) -> None:
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate", read_initial=False)
        node.add_component(component)

        with patch.object(component, "_read_initial_parameter") as mock_read:
            component.on_configure(DUMMY_STATE)

        mock_read.assert_not_called()

    def test_configure_creates_subscription(self, node: LifecycleComponentNode, mock_sub: MagicMock) -> None:
        component = LifecycleParameterObserverComponent("obs")
        node.add_component(component)

        component.on_configure(DUMMY_STATE)

        node.create_subscription.assert_called_once()  # type: ignore[attr-defined]
        call_kwargs = node.create_subscription.call_args  # type: ignore[attr-defined]
        assert call_kwargs.args[1] == "/parameter_events"


# ---------------------------------------------------------------------------
# get_observed_parameter
# ---------------------------------------------------------------------------


class TestGetObservedParameter:
    def test_returns_none_for_unregistered_watch(self) -> None:
        component = LifecycleParameterObserverComponent("obs")

        assert component.get_observed_parameter("/sensor", "rate") is None

    def test_returns_snapshot_for_registered_watch(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate")
        node.add_component(component)

        with patch.object(component, "_read_initial_parameter", return_value=(WatchState.VALUE_AVAILABLE, 5.0)):
            component.on_configure(DUMMY_STATE)

        snapshot = component.get_observed_parameter("/sensor", "rate")

        assert isinstance(snapshot, ObservedParameterSnapshot)
        assert snapshot.node_name == "/sensor"
        assert snapshot.parameter_name == "rate"
        assert snapshot.state == WatchState.VALUE_AVAILABLE
        assert snapshot.value == 5.0


# ---------------------------------------------------------------------------
# Parameter event handling
# ---------------------------------------------------------------------------


class TestParameterEventHandling:
    def _setup_active(
        self,
        component: LifecycleParameterObserverComponent,
        node: LifecycleComponentNode,
        mock_sub: MagicMock,
    ) -> None:
        node.add_component(component)
        with patch.object(component, "_read_initial_parameter", return_value=(WatchState.UNAVAILABLE, None)):
            component.on_configure(DUMMY_STATE)
        component.on_activate(DUMMY_STATE)

    def test_event_updates_snapshot_when_active(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate")
        self._setup_active(component, node, mock_sub)

        msg = _make_parameter_event("/sensor", changed={"rate": 42})
        component._on_parameter_event_msg(msg)

        snapshot = component.get_observed_parameter("/sensor", "rate")
        assert snapshot is not None
        assert snapshot.state == WatchState.VALUE_AVAILABLE
        assert snapshot.value == 42

    def test_event_updates_snapshot_when_inactive(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        """Snapshot updates happen regardless of activation state."""
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate")
        node.add_component(component)
        with patch.object(component, "_read_initial_parameter", return_value=(WatchState.UNAVAILABLE, None)):
            component.on_configure(DUMMY_STATE)
        # deliberately NOT activating

        msg = _make_parameter_event("/sensor", changed={"rate": 7})
        component._on_parameter_event_msg(msg)

        snapshot = component.get_observed_parameter("/sensor", "rate")
        assert snapshot is not None
        assert snapshot.value == 7

    def test_callback_called_only_when_active(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        received: list[ObservedParameterEvent] = []
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate", callback=received.append)
        node.add_component(component)
        with patch.object(component, "_read_initial_parameter", return_value=(WatchState.UNAVAILABLE, None)):
            component.on_configure(DUMMY_STATE)

        # Not active — callback must not fire
        msg = _make_parameter_event("/sensor", changed={"rate": 1})
        component._on_parameter_event_msg(msg)
        assert received == []

        component.on_activate(DUMMY_STATE)

        # Active — callback must fire
        msg = _make_parameter_event("/sensor", changed={"rate": 2})
        component._on_parameter_event_msg(msg)
        assert len(received) == 1
        assert received[0].value == 2
        assert received[0].source == "parameter_event"

    def test_on_observed_parameter_event_called_only_when_active(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        hook_calls: list[tuple[str, str, ObservedParameterEvent]] = []

        class _TestObserver(LifecycleParameterObserverComponent):
            def on_observed_parameter_event(
                self, node_name: str, parameter_name: str, event: ObservedParameterEvent
            ) -> None:
                hook_calls.append((node_name, parameter_name, event))

        component = _TestObserver("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="gain")
        node.add_component(component)
        with patch.object(component, "_read_initial_parameter", return_value=(WatchState.UNAVAILABLE, None)):
            component.on_configure(DUMMY_STATE)

        component._on_parameter_event_msg(_make_parameter_event("/sensor", changed={"gain": 0.5}))
        assert hook_calls == []

        component.on_activate(DUMMY_STATE)
        component._on_parameter_event_msg(_make_parameter_event("/sensor", changed={"gain": 1.0}))
        assert len(hook_calls) == 1
        assert hook_calls[0][2].value == 1.0

    def test_event_carries_previous_value(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        received: list[ObservedParameterEvent] = []
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate", callback=received.append)
        self._setup_active(component, node, mock_sub)

        component._on_parameter_event_msg(_make_parameter_event("/sensor", changed={"rate": 10}))
        component._on_parameter_event_msg(_make_parameter_event("/sensor", changed={"rate": 20}))

        assert received[0].previous_value is None
        assert received[1].previous_value == 10
        assert received[1].value == 20

    def test_deleted_parameter_records_unknown_parameter(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate")
        self._setup_active(component, node, mock_sub)

        component._on_parameter_event_msg(_make_parameter_event("/sensor", changed={"rate": 5}))
        component._on_parameter_event_msg(_make_parameter_event("/sensor", deleted=["rate"]))

        snapshot = component.get_observed_parameter("/sensor", "rate")
        assert snapshot is not None
        assert snapshot.state == WatchState.UNKNOWN_PARAMETER

    def test_event_for_different_node_is_ignored(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        received: list[ObservedParameterEvent] = []
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate", callback=received.append)
        self._setup_active(component, node, mock_sub)

        component._on_parameter_event_msg(_make_parameter_event("/other_node", changed={"rate": 99}))

        assert received == []
        snapshot = component.get_observed_parameter("/sensor", "rate")
        assert snapshot is not None
        assert snapshot.state == WatchState.UNAVAILABLE  # unchanged from configure


# ---------------------------------------------------------------------------
# Cleanup and resource release
# ---------------------------------------------------------------------------


class TestCleanupAndRelease:
    def test_cleanup_destroys_subscription(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        component = LifecycleParameterObserverComponent("obs")
        node.add_component(component)
        with patch.object(component, "_read_initial_parameter", return_value=(WatchState.UNAVAILABLE, None)):
            component.on_configure(DUMMY_STATE)

        component.on_cleanup(DUMMY_STATE)

        node.destroy_subscription.assert_called_once_with(mock_sub)  # type: ignore[attr-defined]
        assert component._event_subscription is None

    def test_cleanup_allows_reconfigure(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/sensor", parameter_name="rate")
        node.add_component(component)

        with patch.object(component, "_read_initial_parameter", return_value=(WatchState.VALUE_AVAILABLE, 1)):
            component.on_configure(DUMMY_STATE)
        component.on_cleanup(DUMMY_STATE)

        with patch.object(component, "_read_initial_parameter", return_value=(WatchState.VALUE_AVAILABLE, 2)):
            result = component.on_configure(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        snapshot = component.get_observed_parameter("/sensor", "rate")
        assert snapshot is not None
        assert snapshot.value == 2

    def test_shutdown_destroys_subscription(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        component = LifecycleParameterObserverComponent("obs")
        node.add_component(component)
        with patch.object(component, "_read_initial_parameter", return_value=(WatchState.UNAVAILABLE, None)):
            component.on_configure(DUMMY_STATE)

        component.on_shutdown(DUMMY_STATE)

        node.destroy_subscription.assert_called_once_with(mock_sub)  # type: ignore[attr-defined]
        assert component._event_subscription is None

    def test_error_destroys_subscription(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        component = LifecycleParameterObserverComponent("obs")
        node.add_component(component)
        with patch.object(component, "_read_initial_parameter", return_value=(WatchState.UNAVAILABLE, None)):
            component.on_configure(DUMMY_STATE)

        component.on_error(DUMMY_STATE)

        node.destroy_subscription.assert_called_once_with(mock_sub)  # type: ignore[attr-defined]
        assert component._event_subscription is None


# ---------------------------------------------------------------------------
# Authority boundary — observer never declares remote parameters
# ---------------------------------------------------------------------------


class TestAuthorityBoundary:
    def test_observer_never_declares_parameters_on_node(
        self, node: LifecycleComponentNode, mock_sub: MagicMock
    ) -> None:
        component = LifecycleParameterObserverComponent("obs")
        component.watch_parameter(node_name="/remote", parameter_name="gain")
        node.add_component(component)

        with (
            patch.object(node, "declare_parameter", wraps=node.declare_parameter) as mock_declare,
            patch.object(component, "_read_initial_parameter", return_value=(WatchState.VALUE_AVAILABLE, 1.0)),
        ):
            component.on_configure(DUMMY_STATE)

        mock_declare.assert_not_called()
