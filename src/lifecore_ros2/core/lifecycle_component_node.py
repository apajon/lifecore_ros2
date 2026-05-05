from __future__ import annotations

import threading
from collections.abc import Callable, Iterable, Sequence
from typing import Any

from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleNode, LifecycleState

from .exceptions import (
    ConcurrentTransitionError,
    CyclicDependencyError,
    DuplicateComponentError,
    RegistrationClosedError,
    UnknownDependencyError,
)
from .lifecycle_component import LifecycleComponent, _worst_of


class LifecycleComponentNode(LifecycleNode):
    """Base node for composing ``LifecycleComponent`` instances as managed entities.

    Owns:
        - The registry of attached ``LifecycleComponent`` instances.
        - Component registration gate: open before first transition, closed after.
        - Thread-safe access to the component registry and registration gate.
        - Propagation of ROS 2 lifecycle transitions to registered components in
          dependency-resolved order via ``_resolved_order``.

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
        Transition order is resolved at the first lifecycle transition via ``_resolved_order``,
        applying Kahn's topological sort on declared ``dependencies`` with ``priority`` as the
        primary tiebreaker and registration order as the stable fallback. Metadata may be
        declared on the component constructor or at ``add_component(...)``.
        ``add_component`` raises ``RegistrationClosedError`` once the first lifecycle
        transition has started.
    """

    # Any: passthrough to rclpy LifecycleNode.__init__; rclpy does not expose a typed kwargs signature
    def __init__(self, node_name: str, *, namespace: str | None = None, **kwargs: Any) -> None:
        super().__init__(node_name, namespace=namespace, **kwargs)
        self._components: dict[str, LifecycleComponent] = {}
        self._registration_open: bool = True
        self._in_transition: bool = False
        self._managed_transition_name: str | None = None
        self._lock: threading.RLock = threading.RLock()
        self._resolved_order: tuple[LifecycleComponent, ...] = ()

    @property
    def components(self) -> tuple[LifecycleComponent, ...]:
        with self._lock:
            return tuple(self._components.values())

    def add_component(
        self,
        component: LifecycleComponent,
        *,
        dependencies: Sequence[str] | None = None,
        priority: int | None = None,
    ) -> None:
        """Register a component as a managed entity.

        Ordering metadata (``dependencies``, ``priority``) may be declared here instead of in
        the component's constructor.  Declaring the same field in both places raises ``TypeError``.

        Args:
            component: The component to register.
            dependencies: Names of other components that must be transitioned before this one.
                ``None`` leaves the component's constructor value unchanged.
            priority: Tie-breaking value for ordering when dependencies do not impose a strict
                order; higher values are resolved earlier.  ``None`` leaves the component's
                constructor value unchanged.

        Raises:
            RegistrationClosedError: If lifecycle transitions have already started.
            DuplicateComponentError: If a component with the same name is already registered.
            TypeError: If both the component and the registration site declare a non-default
                value for the same metadata field.
        """
        component._apply_registration_metadata(dependencies, priority)  # pyright: ignore[reportPrivateUsage]
        with self._lock:
            if not self._registration_open:
                raise RegistrationClosedError(
                    f"Cannot add component '{component.name}': lifecycle transitions have already started"
                )

            if component.name in self._components:
                raise DuplicateComponentError(f"Component name already registered: {component.name}")

            component._attach(self)  # pyright: ignore[reportPrivateUsage]
            self._components[component.name] = component

        self.get_logger().info(f"Registered component '{component.name}'")

    def add_components(self, components: Iterable[LifecycleComponent]) -> None:
        """Register a batch of components.

        This convenience method accepts bare components only. When different components need
        registration-site ordering metadata, call ``add_component(...)`` for each item so the
        metadata stays explicit at the assembly site.
        """
        for component in components:
            self.add_component(component)

    def get_component(self, name: str) -> LifecycleComponent:
        with self._lock:
            try:
                return self._components[name]
            except KeyError as exc:
                raise KeyError(f"Unknown component: {name}") from exc

    def remove_component(self, name: str) -> None:
        """Unregister a component before lifecycle transitions begin.

        Marks the component as withdrawn and detaches it from this node.
        The component remains in rclpy's managed entity list as a silent no-op:
        all subsequent transition callbacks return ``SUCCESS`` immediately without
        executing hooks, allocating resources, or modifying component state.

        Allowed states:
            Only callable before the first lifecycle transition (while registration
            is still open). Raises ``RegistrationClosedError`` after transitions
            have started, because components may have already allocated resources
            and must be cleaned up via the normal lifecycle path.

        Args:
            name: The name of the component to remove.

        Raises:
            RegistrationClosedError: If lifecycle transitions have already started.
            KeyError: If no component with the given name is registered.
        """
        with self._lock:
            if not self._registration_open:
                raise RegistrationClosedError(
                    f"Cannot remove component '{name}': lifecycle transitions have already started"
                )
            try:
                component = self._components.pop(name)
            except KeyError as exc:
                raise KeyError(f"Unknown component: {name}") from exc
            component._withdrawn = True  # pyright: ignore[reportPrivateUsage]
            component._detach()  # pyright: ignore[reportPrivateUsage]

        self.get_logger().info(f"Unregistered component '{name}'")

    # -- registration gate -------------------------------------------------------

    def _close_registration(self) -> None:
        """Framework-internal. Do not call from user code."""
        with self._lock:
            if not self._registration_open:
                return
            self._registration_open = False
        self._resolved_order = self._resolve_order()

    def _resolve_order(self) -> tuple[LifecycleComponent, ...]:
        """Framework-internal. Do not call from user code."""
        for comp_name, component in self._components.items():
            for dep in component._dependencies:  # pyright: ignore[reportPrivateUsage]
                if dep not in self._components:
                    raise UnknownDependencyError(f"Component '{comp_name}' declares unknown dependency '{dep}'")

        insertion_index = {name: i for i, name in enumerate(self._components)}
        successors: dict[str, list[str]] = {name: [] for name in self._components}
        in_degree: dict[str, int] = {name: 0 for name in self._components}

        for comp_name, component in self._components.items():
            for dep in set(component._dependencies):  # pyright: ignore[reportPrivateUsage]
                successors[dep].append(comp_name)
                in_degree[comp_name] += 1

        def sort_key(name: str) -> tuple[int, int]:
            return (-self._components[name]._priority, insertion_index[name])  # pyright: ignore[reportPrivateUsage]

        ready: list[str] = sorted(
            (n for n, deg in in_degree.items() if deg == 0),
            key=sort_key,
        )
        resolved: list[LifecycleComponent] = []

        while ready:
            name = ready.pop(0)
            resolved.append(self._components[name])
            new_ready: list[str] = []
            for succ in successors[name]:
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    new_ready.append(succ)
            if new_ready:
                ready = sorted(ready + new_ready, key=sort_key)

        if len(resolved) != len(self._components):
            raise CyclicDependencyError("Cyclic dependency detected among registered components")

        return tuple(resolved)

    def _propagate_forward(self, callback_name: str, state: LifecycleState) -> TransitionCallbackReturn:
        """Framework-internal. Do not call from user code."""
        for component in self._resolved_order:
            result: TransitionCallbackReturn = getattr(component, callback_name)(state)
            if result != TransitionCallbackReturn.SUCCESS:
                return result
        return TransitionCallbackReturn.SUCCESS

    def _propagate_reverse(self, callback_name: str, state: LifecycleState) -> TransitionCallbackReturn:
        """Framework-internal. Do not call from user code."""
        for component in reversed(self._resolved_order):
            result: TransitionCallbackReturn = getattr(component, callback_name)(state)
            if result != TransitionCallbackReturn.SUCCESS:
                return result
        return TransitionCallbackReturn.SUCCESS

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
                result = self._propagate_forward("on_configure", state)
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
                return self._propagate_forward("on_activate", state)
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
                return self._propagate_reverse("on_deactivate", state)
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
                return self._propagate_reverse("on_cleanup", state)
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
                return self._propagate_reverse("on_shutdown", state)
            finally:
                self._end_managed_transition()
        finally:
            self._end_transition()

    def on_error(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Propagate error to all components in reverse order.

        Not guarded by ``_begin_transition`` — error recovery must remain
        reachable during active transitions.
        """
        return self._propagate_reverse("on_error", state)

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
