from __future__ import annotations

import threading
from collections.abc import Callable, Iterable
from typing import Any

from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleNode, LifecycleState

from .exceptions import ConcurrentTransitionError, DuplicateComponentError, RegistrationClosedError
from .lifecycle_component import LifecycleComponent, _worst_of


class LifecycleComponentNode(LifecycleNode):
    """Base node for composing ``LifecycleComponent`` instances as managed entities.

    Owns:
        - The registry of attached ``LifecycleComponent`` instances.
        - Component registration gate: open before first transition, closed after.
        - Thread-safe access to the component registry and registration gate.
        - Propagation of ROS 2 lifecycle transitions to registered components via the
          native ``ManagedEntity`` mechanism.

    Does not own:
        - Component-level resource allocation or release.
        - Component activation state.
        - Application-level business logic.

    Override points:
        - Override ``on_configure``, ``on_activate``, ``on_deactivate``, ``on_cleanup``,
          or ``on_shutdown`` to add node-level behavior. Always call ``super()`` to
          preserve component propagation and the registration gate.
        - Do not override ``add_component``, ``add_components``, or ``_close_registration``.

    Note:
        Each component is registered as a ``ManagedEntity`` so the native ``LifecycleNode``
        propagates transitions automatically. ``add_component`` raises ``RuntimeError``
        once the first lifecycle transition has started.
    """

    # Any: passthrough to rclpy LifecycleNode.__init__; rclpy does not expose a typed kwargs signature
    def __init__(self, node_name: str, *, namespace: str | None = None, **kwargs: Any) -> None:
        super().__init__(node_name, namespace=namespace, **kwargs)
        self._components: dict[str, LifecycleComponent] = {}
        self._registration_open: bool = True
        self._in_transition: bool = False
        self._managed_transition_name: str | None = None
        self._lock: threading.RLock = threading.RLock()

    @property
    def components(self) -> tuple[LifecycleComponent, ...]:
        with self._lock:
            return tuple(self._components.values())

    def add_component(self, component: LifecycleComponent) -> None:
        """Register a component as a managed entity.

        Raises:
            RegistrationClosedError: If lifecycle transitions have already started.
            DuplicateComponentError: If a component with the same name is already registered.
        """
        with self._lock:
            if not self._registration_open:
                raise RegistrationClosedError(
                    f"Cannot add component '{component.name}': lifecycle transitions have already started"
                )

            if component.name in self._components:
                raise DuplicateComponentError(f"Component name already registered: {component.name}")

            component._attach(self)  # pyright: ignore[reportPrivateUsage]
            try:
                self.add_managed_entity(component)
            except Exception:
                component._detach()  # pyright: ignore[reportPrivateUsage]
                raise
            self._components[component.name] = component

        self.get_logger().info(f"Registered component '{component.name}'")

    def add_components(self, components: Iterable[LifecycleComponent]) -> None:
        for component in components:
            self.add_component(component)

    def get_component(self, name: str) -> LifecycleComponent:
        with self._lock:
            try:
                return self._components[name]
            except KeyError as exc:
                raise KeyError(f"Unknown component: {name}") from exc

    # -- registration gate -------------------------------------------------------

    def _close_registration(self) -> None:
        """Framework-internal. Do not call from user code."""
        with self._lock:
            self._registration_open = False

    def _begin_transition(self, name: str) -> None:
        """Framework-internal. Do not call from user code.

        Raises:
            ConcurrentTransitionError: If a lifecycle transition is already in progress.
        """
        with self._lock:
            if self._in_transition:
                raise ConcurrentTransitionError(
                    f"Cannot start '{name}': a lifecycle transition is already in progress"
                )
            self._in_transition = True

    def _end_transition(self) -> None:
        """Framework-internal. Do not call from user code."""
        with self._lock:
            self._in_transition = False

    def _begin_managed_transition(self, name: str) -> None:
        """Framework-internal. Do not call from user code."""
        with self._lock:
            self._managed_transition_name = name

    def _end_managed_transition(self) -> None:
        """Framework-internal. Do not call from user code."""
        with self._lock:
            self._managed_transition_name = None

    def _current_state_label(self) -> str:
        """Framework-internal. Do not call from user code."""
        _, current_state = self._state_machine.current_state  # pyright: ignore[reportPrivateUsage]
        return str(current_state)

    def _log_transition_rejection(self, attempted_transition: str, exc: Exception) -> None:
        """Framework-internal. Do not call from user code."""
        component_names = ", ".join(component.name for component in self.components) or "<none>"
        self.get_logger().error(
            f"Rejected lifecycle transition attempted='{attempted_transition}' "
            f"current_state='{self._current_state_label()}' components='{component_names}' "
            f"reason='{type(exc).__name__}: {exc}'"
        )

    def _run_trigger(
        self,
        attempted_transition: str,
        trigger: Callable[[], TransitionCallbackReturn],
    ) -> TransitionCallbackReturn:
        """Framework-internal. Do not call from user code."""
        try:
            return trigger()
        except Exception as exc:
            self._log_transition_rejection(attempted_transition, exc)
            raise

    def _rollback_failed_configure(self) -> TransitionCallbackReturn:
        """Framework-internal. Do not call from user code."""
        self.get_logger().warning(
            "Configure transition failed; releasing component resources to restore an unconfigured state"
        )

        rollback_result = TransitionCallbackReturn.SUCCESS
        for component in self.components:
            component_result = component._rollback_failed_configure()  # pyright: ignore[reportPrivateUsage]
            rollback_result = _worst_of(rollback_result, component_result)
        return rollback_result

    # -- override-with-super hooks -----------------------------------------------
    # Application nodes may override these. Always call super() to preserve
    # component propagation and the registration gate.

    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Close the registration gate and propagate configure to all components.

        Override in application nodes to add node-level configure behavior.
        Always call ``super().on_configure(state)`` first.

        Raises:
            ConcurrentTransitionError: If called concurrently with an in-progress transition.
        """
        self._begin_transition("configure")
        try:
            self._close_registration()
            self._begin_managed_transition("configure")
            try:
                result = super().on_configure(state)
            finally:
                self._end_managed_transition()
            if result != TransitionCallbackReturn.SUCCESS:
                rollback_result = self._rollback_failed_configure()
                return _worst_of(result, rollback_result)
            return result
        finally:
            self._end_transition()

    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Propagate activate to all components.

        Override in application nodes to add node-level activate behavior.
        Always call ``super().on_activate(state)``.

        Raises:
            ConcurrentTransitionError: If called concurrently with an in-progress transition.
        """
        self._begin_transition("activate")
        try:
            self._begin_managed_transition("activate")
            try:
                return super().on_activate(state)
            finally:
                self._end_managed_transition()
        finally:
            self._end_transition()

    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Propagate deactivate to all components.

        Override in application nodes to add node-level deactivate behavior.
        Always call ``super().on_deactivate(state)``.

        Raises:
            ConcurrentTransitionError: If called concurrently with an in-progress transition.
        """
        self._begin_transition("deactivate")
        try:
            self._begin_managed_transition("deactivate")
            try:
                return super().on_deactivate(state)
            finally:
                self._end_managed_transition()
        finally:
            self._end_transition()

    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Propagate cleanup to all components.

        Override in application nodes to add node-level cleanup behavior.
        Always call ``super().on_cleanup(state)``.

        Raises:
            ConcurrentTransitionError: If called concurrently with an in-progress transition.
        """
        self._begin_transition("cleanup")
        try:
            self._begin_managed_transition("cleanup")
            try:
                return super().on_cleanup(state)
            finally:
                self._end_managed_transition()
        finally:
            self._end_transition()

    def on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Close the registration gate and propagate shutdown to all components.

        Override in application nodes to add node-level shutdown behavior.
        Always call ``super().on_shutdown(state)``.

        Raises:
            ConcurrentTransitionError: If called concurrently with an in-progress transition.
        """
        self._begin_transition("shutdown")
        try:
            self._close_registration()
            self._begin_managed_transition("shutdown")
            try:
                return super().on_shutdown(state)
            finally:
                self._end_managed_transition()
        finally:
            self._end_transition()

    def trigger_configure(self) -> TransitionCallbackReturn:
        return self._run_trigger("configure", super().trigger_configure)

    def trigger_activate(self) -> TransitionCallbackReturn:
        return self._run_trigger("activate", super().trigger_activate)

    def trigger_deactivate(self) -> TransitionCallbackReturn:
        return self._run_trigger("deactivate", super().trigger_deactivate)

    def trigger_cleanup(self) -> TransitionCallbackReturn:
        return self._run_trigger("cleanup", super().trigger_cleanup)

    def trigger_shutdown(self) -> TransitionCallbackReturn:
        return self._run_trigger("shutdown", super().trigger_shutdown)
