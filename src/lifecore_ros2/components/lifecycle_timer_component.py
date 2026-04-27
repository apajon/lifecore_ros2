from __future__ import annotations

from abc import abstractmethod
from typing import final

from rclpy.callback_groups import CallbackGroup
from rclpy.duration import Duration
from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.timer import Timer

from lifecore_ros2.core.exceptions import ComponentNotConfiguredError
from lifecore_ros2.core.lifecycle_component import LifecycleComponent, when_active


class LifecycleTimerComponent(LifecycleComponent):
    """Timer component that creates a periodic ROS timer and gates ticks through the lifecycle.

    The timer is created on configure and destroyed automatically on cleanup.
    Ticks are silently dropped while the component is inactive,
    and routed to ``on_tick`` when active.

    Owns:
        - The ROS ``Timer`` instance (created on configure, released automatically on cleanup).
        - ``_on_timer_wrapper``: the ``@when_active``-gated internal callback.
        - The autostart flag and the explicit ``start`` / ``stop`` / ``reset`` controls.

    Does not own:
        - The clock — uses the node default clock.
        - The callback group — it is borrowed from the application; lifetime is owned by the caller.
        - The node or lifecycle state transitions.
        - Activation state management (handled by the framework).

    Override points:
        - ``on_tick``: implement to handle each timer tick. Called only while active.
        - Override ``_on_configure`` only for additional setup; call ``super()._on_configure(state)`` first.
        - Do not override ``_on_timer_wrapper``.
    """

    def __init__(
        self,
        name: str,
        period: float | Duration,
        *,
        autostart: bool = True,
        callback_group: CallbackGroup | None = None,
    ) -> None:
        """Initialize the lifecycle timer component.

        Args:
            name: Unique name for this component within the node.
            period: Timer period. Either a duration in seconds (``float``) or a
                ``rclpy.duration.Duration``.
            autostart: If True (default), the underlying ROS timer starts firing as soon as
                it is created in ``_on_configure`` (ticks are still gated by activation).
                If False, the timer is created in a canceled state and only starts firing
                when ``start()`` is called.
            callback_group: Optional CallbackGroup borrowed from the application and
                forwarded to ``create_timer`` on configure. Lifetime is owned by the
                caller; the component never destroys it. ``None`` selects the node
                default group.

        Raises:
            ValueError: If ``period`` is not strictly positive.
        """
        super().__init__(name=name, callback_group=callback_group)
        period_sec = period.nanoseconds / 1e9 if isinstance(period, Duration) else float(period)
        if period_sec <= 0.0:
            raise ValueError(f"Timer '{name}' period must be > 0 seconds, got {period_sec}")
        self._period_sec: float = period_sec
        self._autostart: bool = autostart
        self._timer: Timer | None = None

    @property
    def period_sec(self) -> float:
        """The timer period in seconds."""
        return self._period_sec

    @property
    def autostart(self) -> bool:
        """Whether the timer starts firing automatically when created on configure."""
        return self._autostart

    @property
    def is_running(self) -> bool:
        """True iff the underlying timer exists and is currently firing (not canceled)."""
        return self._timer is not None and not self._timer.is_canceled()

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Extension point. Creates the ROS timer.

        Override in subclasses for additional setup. Call ``super()._on_configure(state)`` first.
        """
        self._timer = self.node.create_timer(
            self._period_sec,
            self._on_timer_wrapper,
            callback_group=self._callback_group,
            autostart=self._autostart,
        )
        self.node.get_logger().info(
            f"[{self.name}] timer created with period {self._period_sec}s (autostart={self._autostart})"
        )
        return TransitionCallbackReturn.SUCCESS

    @final
    @when_active(when_not_active=None)
    def _on_timer_wrapper(self) -> None:
        """Framework-internal. Do not call from user code."""
        try:
            self.on_tick()
        except Exception as exc:
            # Rule C (inbound): never propagate user exceptions into the rclpy executor.
            # Log the error and drop the tick silently.
            self._resolve_logger().error(f"[{self._name}.on_tick] {type(exc).__name__}: {exc}")

    @abstractmethod
    def on_tick(self) -> None:
        """Extension point. Implement to handle each timer tick while active.

        This is the timer callback contract. Unlike the ``_on_*`` lifecycle hooks,
        ``on_tick`` is intentionally public because it defines application behavior,
        not framework behavior. It is only called while the component is active.
        """
        raise NotImplementedError("on_tick must be implemented by LifecycleTimerComponent subclasses")

    # -- explicit timer controls ------------------------------------------
    #
    # start/stop/reset operate on the underlying ROS timer's running state. They are
    # independent of activation: stopping a timer prevents it from firing at all,
    # while activation gating only controls whether ticks reach ``on_tick``. All three
    # require the component to be configured (timer must exist).

    def start(self) -> None:
        """Resume firing the underlying timer. No-op if already running.

        Raises:
            ComponentNotConfiguredError: If called before ``configure`` or after ``cleanup``.
        """
        if self._timer is None:
            raise ComponentNotConfiguredError(f"Timer '{self.name}' is not configured")
        if self._timer.is_canceled():
            self._timer.reset()

    def stop(self) -> None:
        """Stop the underlying timer. No-op if already stopped.

        Raises:
            ComponentNotConfiguredError: If called before ``configure`` or after ``cleanup``.
        """
        if self._timer is None:
            raise ComponentNotConfiguredError(f"Timer '{self.name}' is not configured")
        self._timer.cancel()

    def reset(self) -> None:
        """Restart the timer period from now. Resumes firing if currently stopped.

        Raises:
            ComponentNotConfiguredError: If called before ``configure`` or after ``cleanup``.
        """
        if self._timer is None:
            raise ComponentNotConfiguredError(f"Timer '{self.name}' is not configured")
        self._timer.reset()

    def _release_resources(self) -> None:
        """Extension point. Override to release additional resources; call ``super()._release_resources()`` last."""
        if self._timer is not None:
            self._timer.cancel()
            self.node.destroy_timer(self._timer)
            self._timer = None
        super()._release_resources()
