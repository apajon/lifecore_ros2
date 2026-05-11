from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from rclpy.callback_groups import CallbackGroup
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState
from rclpy.time import Time

from lifecore_ros2.core.health import HealthLevel, HealthStatus

from .lifecycle_timer_component import LifecycleTimerComponent


class _WatchableHealth(Protocol):
    """Structural protocol: any object exposing a ``HealthStatus`` snapshot."""

    @property
    def health(self) -> HealthStatus: ...


@dataclass
class _WatchState:
    """Per-target tracking state owned by the watchdog.

    ``last_change_time`` holds the node-clock timestamp of the last level change.
    It is always initialised from ``node.get_clock().now()`` so the clock type
    matches every subsequent ``now - last_change_time`` subtraction.
    """

    last_level: HealthLevel
    last_change_time: Time


def _target_name(target: object) -> str:
    """Return a human-readable identifier for a watchable target."""
    name = getattr(target, "name", None)
    if isinstance(name, str):
        return name
    get_name = getattr(target, "get_name", None)
    if callable(get_name):
        return str(get_name())
    return repr(target)


class LifecycleWatchdogComponent(LifecycleTimerComponent):
    """Watchdog component that polls component or node health and logs actionable diagnostics.

    Observes one or more targets that expose a ``.health`` property (such as
    :class:`~lifecore_ros2.core.LifecycleComponent` or
    :class:`~lifecore_ros2.core.LifecycleComponentNode`) on a fixed polling interval.
    For each target the watchdog:

    - logs a WARN when health level is ``DEGRADED``,
    - logs an ERROR when health level is ``ERROR`` (includes ``last_error`` if set),
    - logs an additional WARN labelled ``STALE`` when the level has been non-OK
      for longer than ``stale_threshold`` seconds.

    The watchdog is purely read-only: it never triggers lifecycle transitions.
    Polling runs only while the component is active (between ``_on_activate`` and
    ``_on_deactivate``). ``OK`` and ``UNKNOWN`` levels are silent.

    Staleness is tracked from the first time the current level was observed. The
    clock resets each time the level changes.

    Args:
        name: Unique component name within the node.
        targets: Objects to watch. Each must expose a ``.health`` property returning a
            :class:`~lifecore_ros2.core.HealthStatus`. Accepts
            :class:`~lifecore_ros2.core.LifecycleComponent` or
            :class:`~lifecore_ros2.core.LifecycleComponentNode` instances.
        poll_period: Polling interval in seconds. Must be > 0.
        stale_threshold: Seconds after which a persistently non-OK level is labelled
            STALE in the log. Must be > 0.
        callback_group: Optional callback group forwarded to the underlying ROS timer.
            ``None`` selects the node default group.
        dependencies: Names of other components that must be transitioned before this one.
        priority: Tie-breaking ordering hint within the resolved transition order.

    Raises:
        ValueError: If ``poll_period`` or ``stale_threshold`` is not strictly positive.
    """

    def __init__(
        self,
        name: str,
        targets: Sequence[_WatchableHealth],
        poll_period: float,
        stale_threshold: float,
        *,
        callback_group: CallbackGroup | None = None,
        dependencies: Sequence[str] = (),
        priority: int = 0,
    ) -> None:
        if stale_threshold <= 0.0:
            raise ValueError(f"Watchdog '{name}' stale_threshold must be > 0 seconds, got {stale_threshold}")
        super().__init__(
            name=name,
            period=poll_period,
            autostart=True,
            callback_group=callback_group,
            dependencies=dependencies,
            priority=priority,
        )
        self._targets: tuple[_WatchableHealth, ...] = tuple(targets)
        self._stale_threshold: float = stale_threshold
        self._watch_states: dict[int, _WatchState] = {}

    @property
    def stale_threshold(self) -> float:
        """Staleness threshold in seconds."""
        return self._stale_threshold

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Create the poll timer and initialize per-target tracking state.

        Calls ``super()._on_configure(state)`` first to create the underlying ROS timer.
        """
        result = super()._on_configure(state)
        if result != TransitionCallbackReturn.SUCCESS:
            return result
        now = self.node.get_clock().now()
        self._watch_states = {
            id(t): _WatchState(last_level=t.health.level, last_change_time=now) for t in self._targets
        }
        self.node.get_logger().info(
            f"[{self.name}] watching {len(self._targets)} target(s), "
            f"poll={self._period_sec}s, stale_threshold={self._stale_threshold}s"
        )
        return TransitionCallbackReturn.SUCCESS

    def _release_resources(self) -> None:
        """Clear tracking state and release the underlying timer."""
        self._watch_states.clear()
        super()._release_resources()

    def on_tick(self) -> None:
        """Poll each watched target and log actionable diagnostics.

        Called on every timer tick while the component is active. Behaviour per target:

        - ``DEGRADED`` → WARN log with reason.
        - ``ERROR`` → ERROR log with reason and ``last_error`` if set.
        - Non-OK for longer than ``stale_threshold`` → additional WARN labelled ``STALE``.
        - ``OK`` and ``UNKNOWN`` → no log.
        """
        now = self.node.get_clock().now()
        log = self.node.get_logger()
        for target in self._targets:
            status = target.health
            level = status.level
            target_id = id(target)

            state = self._watch_states.get(target_id)
            if state is None:
                # Defensive: initialize if entry is missing (e.g. first tick after configure).
                self._watch_states[target_id] = _WatchState(last_level=level, last_change_time=now)
                state = self._watch_states[target_id]
            elif level != state.last_level:
                state.last_level = level
                state.last_change_time = now

            tname = _target_name(target)

            if level == HealthLevel.DEGRADED:
                log.warn(f"[{self.name}] {tname} DEGRADED: {status.reason}")
            elif level == HealthLevel.ERROR:
                detail = f" (last_error={status.last_error})" if status.last_error else ""
                log.error(f"[{self.name}] {tname} ERROR: {status.reason}{detail}")

            if level in (HealthLevel.DEGRADED, HealthLevel.ERROR):
                elapsed_sec = (now - state.last_change_time).nanoseconds / 1e9
                if elapsed_sec >= self._stale_threshold:
                    log.warn(
                        f"[{self.name}] {tname} STALE: level={level.value} "
                        f"for {elapsed_sec:.1f}s (threshold={self._stale_threshold}s)"
                    )
