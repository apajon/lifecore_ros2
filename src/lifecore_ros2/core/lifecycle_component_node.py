from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleNode, LifecycleState

from .lifecycle_component import LifecycleComponent


class LifecycleComponentNode(LifecycleNode):
    """Base node for composing ``LifecycleComponent`` instances as managed entities.

    Owns:
        - The registry of attached ``LifecycleComponent`` instances.
        - Component registration gate: open before first transition, closed after.
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

    def __init__(self, node_name: str, *, namespace: str | None = None, **kwargs: Any) -> None:
        super().__init__(node_name, namespace=namespace, **kwargs)
        self._components: dict[str, LifecycleComponent] = {}
        self._registration_open: bool = True

    @property
    def components(self) -> tuple[LifecycleComponent, ...]:
        return tuple(self._components.values())

    def add_component(self, component: LifecycleComponent) -> None:
        """Register a component as a managed entity.

        Raises:
            RuntimeError: If lifecycle transitions have already started.
            ValueError: If a component with the same name is already registered.
        """
        if not self._registration_open:
            raise RuntimeError(f"Cannot add component '{component.name}': lifecycle transitions have already started")

        if component.name in self._components:
            raise ValueError(f"Component name already registered: {component.name}")

        component.attach(self)
        try:
            self.add_managed_entity(component)
        except Exception:
            component._detach()
            raise
        self._components[component.name] = component

        self.get_logger().info(f"Registered component '{component.name}'")

    def add_components(self, components: Iterable[LifecycleComponent]) -> None:
        for component in components:
            self.add_component(component)

    def get_component(self, name: str) -> LifecycleComponent:
        try:
            return self._components[name]
        except KeyError as exc:
            raise KeyError(f"Unknown component: {name}") from exc

    # -- lifecycle gate -------------------------------------------------------

    def _close_registration(self) -> None:
        self._registration_open = False

    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._close_registration()
        return super().on_configure(state)

    def on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._close_registration()
        return super().on_shutdown(state)
