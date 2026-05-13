from __future__ import annotations

import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal

from rclpy.callback_groups import CallbackGroup
from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.parameter import Parameter

from lifecore_ros2.core.lifecycle_component import LifecycleComponent

_DEFAULT_READ_TIMEOUT_SEC: float = 1.0


class WatchState(StrEnum):
    """Availability state recorded for a watched remote parameter after an initial read.

    This state is testable via ``get_observed_parameter``. Logging may explain
    the condition, but the state itself is the contract — not warnings.
    """

    UNKNOWN_NODE = "unknown_node"
    """Remote node could not be identified as available within the read timeout."""

    UNKNOWN_PARAMETER = "unknown_parameter"
    """Remote node responded but the watched parameter was absent or not set."""

    UNAVAILABLE = "unavailable"
    """Initial read could not complete due to a timeout, transport error, or other transient reason."""

    VALUE_AVAILABLE = "value_available"
    """An initial value was read and stored successfully."""


@dataclass(frozen=True)
class ObservedParameterEvent:
    """A single observed change for a remote parameter.

    Passed to per-watch callbacks and the ``on_observed_parameter_event`` hook.
    Represents a fact already accepted by the remote node. The observer has no
    validation authority.
    """

    node_name: str
    """Full name of the remote node that owns the parameter."""

    parameter_name: str
    """Name of the changed parameter on the remote node."""

    value: object
    """New value as accepted by the remote node."""

    previous_value: object | None
    """Last value known to this observer before the change, or ``None`` if not previously observed."""

    source: Literal["initial_read", "parameter_event"]
    """Whether this event originated from an initial read during configure or a live parameter event."""


@dataclass(frozen=True)
class ObservedParameterSnapshot:
    """Current observation state for a single watched parameter.

    Query via ``get_observed_parameter``. Check ``state`` before using ``value``.
    """

    node_name: str
    """Full name of the remote node that owns the parameter."""

    parameter_name: str
    """Name of the watched parameter on the remote node."""

    state: WatchState
    """Availability state. Inspect this before relying on ``value``."""

    value: object | None
    """Latest value observed, or ``None`` when state is not ``VALUE_AVAILABLE``."""

    previous_value: object | None
    """Value observed before the most recent change, or ``None`` if not previously observed."""


@dataclass(frozen=True)
class ParameterWatchHandle:
    """Identifies a registered parameter watch.

    Returned by ``watch_parameter``. Carries the watch coordinates for reference.
    """

    node_name: str
    parameter_name: str


@dataclass
class _WatchEntry:
    node_name: str
    parameter_name: str
    read_initial: bool
    callback: Callable[[ObservedParameterEvent], None] | None
    snapshot: ObservedParameterSnapshot


def _value_from_ros_parameter_value(pv: Any) -> tuple[bool, object]:
    """Extract a Python value from ``rcl_interfaces.msg.ParameterValue``.

    Returns ``(True, value)`` when the type is set, or ``(False, None)`` for NOT_SET.
    """
    t = int(pv.type)
    if t == 0:
        return False, None
    if t == 1:
        return True, bool(pv.bool_value)
    if t == 2:
        return True, int(pv.integer_value)
    if t == 3:
        return True, float(pv.double_value)
    if t == 4:
        return True, str(pv.string_value)
    if t == 5:
        return True, bytes(pv.bytes_value)
    if t == 6:
        return True, list(pv.bool_array_value)
    if t == 7:
        return True, list(pv.integer_array_value)
    if t == 8:
        return True, list(pv.double_array_value)
    if t == 9:
        return True, list(pv.string_array_value)
    return False, None


class LifecycleParameterObserverComponent(LifecycleComponent):
    """Lifecycle-aware observer for parameters owned by remote ROS 2 nodes.

    Watches may be registered before configure. During configure, the component
    subscribes to ``/parameter_events`` for live change observation and optionally
    reads initial values from each remote node. Missing nodes or parameters do not
    fail configure; each watch records an explicit :class:`WatchState` that is
    testable via ``get_observed_parameter``.

    User callbacks and the ``on_observed_parameter_event`` hook run only while the
    component is active. Snapshot updates from live events happen regardless of
    activation state so that ``get_observed_parameter`` always reflects the latest
    observed value.

    The component never declares, validates, rejects, or owns remote parameters.
    It observes facts already accepted by the remote node.

    Note:
        ``_read_initial_parameter`` uses ``AsyncParameterClient`` and
        ``rclpy.spin_until_future_complete``. For production use, prefer a
        multi-threaded executor to avoid blocking the lifecycle transition thread.
        Override ``_read_initial_parameter`` in tests to inject a stub.
    """

    def __init__(
        self,
        name: str,
        *,
        read_timeout_sec: float = _DEFAULT_READ_TIMEOUT_SEC,
        callback_group: CallbackGroup | None = None,
        dependencies: Sequence[str] = (),
        priority: int = 0,
    ) -> None:
        """Initialize the parameter observer component.

        Args:
            name: Unique component name within the parent node.
            read_timeout_sec: Timeout in seconds for each initial remote parameter read.
            callback_group: Optional callback group forwarded to ``LifecycleComponent``.
            dependencies: Names of components that must transition before this one.
            priority: Tie-breaking ordering hint.
        """
        super().__init__(name=name, callback_group=callback_group, dependencies=dependencies, priority=priority)
        self._read_timeout_sec = read_timeout_sec
        self._watches: dict[tuple[str, str], _WatchEntry] = {}
        self._watches_lock: threading.Lock = threading.Lock()
        self._event_subscription: Any = None

    def watch_parameter(
        self,
        *,
        node_name: str,
        parameter_name: str,
        read_initial: bool = True,
        callback: Callable[[ObservedParameterEvent], None] | None = None,
    ) -> ParameterWatchHandle:
        """Register a parameter on a remote node for observation.

        Must be called before configure. The watch records an explicit
        :class:`WatchState` for the initial read outcome when the component is
        configured.

        Args:
            node_name: Full name of the remote node that owns the parameter (e.g. ``"/sensor_node"``).
            parameter_name: Name of the parameter on the remote node.
            read_initial: If ``True``, attempt to read the current value during configure.
            callback: Optional per-watch callable invoked for this specific
                node/parameter pair while the component is active. Use
                ``on_observed_parameter_event`` instead when one component-wide
                hook should handle all observed parameters.

        Returns:
            A :class:`ParameterWatchHandle` identifying the registered watch.

        Raises:
            ValueError: If a watch for this node/parameter pair is already registered.
            RuntimeError: If the component is already configured.
        """
        if self._is_configured:
            raise RuntimeError(
                f"Component '{self.name}' cannot register a watch while configured; "
                "register watches before configure"
            )
        key = (node_name, parameter_name)
        with self._watches_lock:
            if key in self._watches:
                raise ValueError(f"Already watching parameter '{parameter_name}' on node '{node_name}'")
            self._watches[key] = _WatchEntry(
                node_name=node_name,
                parameter_name=parameter_name,
                read_initial=read_initial,
                callback=callback,
                snapshot=ObservedParameterSnapshot(
                    node_name=node_name,
                    parameter_name=parameter_name,
                    state=WatchState.UNAVAILABLE,
                    value=None,
                    previous_value=None,
                ),
            )
        return ParameterWatchHandle(node_name=node_name, parameter_name=parameter_name)

    def get_observed_parameter(
        self,
        node_name: str,
        parameter_name: str,
    ) -> ObservedParameterSnapshot | None:
        """Return the current observation snapshot for a watched parameter.

        Returns ``None`` if no watch is registered for the given node/parameter pair.

        Args:
            node_name: Full name of the remote node.
            parameter_name: Name of the parameter on the remote node.
        """
        with self._watches_lock:
            entry = self._watches.get((node_name, parameter_name))
        return entry.snapshot if entry is not None else None

    def on_observed_parameter_event(
        self,
        node_name: str,
        parameter_name: str,
        event: ObservedParameterEvent,
    ) -> None:
        """React to an observed parameter change while active.

        Called for every watched parameter that changes while the component is
        active. This is the component-wide hook: unlike ``callback=...`` on
        ``watch_parameter``, it is not tied to one watch. Override it when the
        same reaction should apply across all observed parameters owned by this
        component instance.

        If a watch-specific callback was registered with ``watch_parameter``,
        that callback runs first for the matching watch and this hook runs
        afterward. The default implementation is a no-op.

        Args:
            node_name: Full name of the remote node that owns the parameter.
            parameter_name: Name of the changed parameter.
            event: The observed event carrying the new and previous values.
        """

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Subscribe to ``/parameter_events`` and optionally read initial values."""
        from rcl_interfaces.msg import ParameterEvent  # type: ignore[import-untyped]

        self._event_subscription = self.node.create_subscription(
            ParameterEvent,
            "/parameter_events",
            self._on_parameter_event_msg,
            10,
            callback_group=self._callback_group,
        )

        with self._watches_lock:
            entries = list(self._watches.values())

        for entry in entries:
            if not entry.read_initial:
                continue
            watch_state, value = self._read_initial_parameter(entry.node_name, entry.parameter_name)
            with self._watches_lock:
                self._update_snapshot(entry, watch_state, value)
            if watch_state == WatchState.VALUE_AVAILABLE:
                self.get_logger().debug(
                    f"[{self.name}] initial '{entry.node_name}/{entry.parameter_name}': {value!r}"
                )
            else:
                self.get_logger().info(
                    f"[{self.name}] initial '{entry.node_name}/{entry.parameter_name}': {watch_state}"
                )

        return TransitionCallbackReturn.SUCCESS

    def _read_initial_parameter(
        self,
        node_name: str,
        parameter_name: str,
    ) -> tuple[WatchState, object | None]:
        """Attempt to read a parameter from a remote node.

        Returns a ``(WatchState, value)`` pair. ``value`` is ``None`` when the
        state is not ``VALUE_AVAILABLE``.

        This method is the recommended override point for tests. Override it to
        inject a stub without needing a live ROS 2 graph.

        Note:
            The default implementation calls ``rclpy.spin_until_future_complete``
            which blocks the calling thread. Use a multi-threaded executor when
            this component is used in a production lifecycle node.
        """
        import rclpy
        from rclpy.parameter_client import AsyncParameterClient  # type: ignore[import-untyped]

        client = AsyncParameterClient(self.node, node_name)
        if not client.wait_for_service(timeout_sec=self._read_timeout_sec):
            return WatchState.UNKNOWN_NODE, None

        future = client.get_parameters([parameter_name])
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=self._read_timeout_sec)

        if not future.done():
            return WatchState.UNAVAILABLE, None

        response = future.result()
        if response is None:
            return WatchState.UNAVAILABLE, None

        values = response.values
        if not values:
            return WatchState.UNAVAILABLE, None

        has_value, extracted = _value_from_ros_parameter_value(values[0])
        if not has_value:
            return WatchState.UNKNOWN_PARAMETER, None

        return WatchState.VALUE_AVAILABLE, extracted

    def _update_snapshot(
        self,
        entry: _WatchEntry,
        state: WatchState,
        value: object | None,
    ) -> None:
        """Update the snapshot for an entry. Caller must hold ``_watches_lock``."""
        previous = entry.snapshot.value
        entry.snapshot = ObservedParameterSnapshot(
            node_name=entry.node_name,
            parameter_name=entry.parameter_name,
            state=state,
            value=value,
            previous_value=previous,
        )

    def _on_parameter_event_msg(self, msg: Any) -> None:
        """Handle incoming ``/parameter_events`` messages.

        Updates snapshots for all matching watches regardless of activation state.
        Calls watch-specific callbacks first and
        ``on_observed_parameter_event`` second, but only while active.
        """
        node_name: str = msg.node
        affected: dict[str, Any] = {p.name: p for p in [*msg.new_parameters, *msg.changed_parameters]}
        deleted: set[str] = {p.name for p in msg.deleted_parameters}

        if not affected and not deleted:
            return

        currently_active = self.is_active
        notifications: list[tuple[_WatchEntry, ObservedParameterEvent]] = []

        with self._watches_lock:
            for (n, p_name), entry in self._watches.items():
                if n != node_name:
                    continue
                if p_name in deleted:
                    self._update_snapshot(entry, WatchState.UNKNOWN_PARAMETER, None)
                    continue
                if p_name not in affected:
                    continue
                try:
                    param = Parameter.from_parameter_msg(affected[p_name])
                except Exception:
                    continue
                if param.type_ == Parameter.Type.NOT_SET:
                    self._update_snapshot(entry, WatchState.UNKNOWN_PARAMETER, None)
                    continue
                previous_value = entry.snapshot.value
                value: object = param.value
                self._update_snapshot(entry, WatchState.VALUE_AVAILABLE, value)
                if currently_active:
                    event = ObservedParameterEvent(
                        node_name=node_name,
                        parameter_name=p_name,
                        value=value,
                        previous_value=previous_value,
                        source="parameter_event",
                    )
                    notifications.append((entry, event))

        for entry, event in notifications:
            if entry.callback is not None:
                entry.callback(event)
            self.on_observed_parameter_event(event.node_name, event.parameter_name, event)

    def _release_resources(self) -> None:
        """Destroy the parameter event subscription and clear observer-owned tracking."""
        if self._event_subscription is not None:
            self.node.destroy_subscription(self._event_subscription)
            self._event_subscription = None
        super()._release_resources()
