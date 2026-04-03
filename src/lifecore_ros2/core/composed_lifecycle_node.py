from __future__ import annotations

from collections.abc import Iterable

from rclpy.lifecycle.node import LifecycleNode

from .lifecycle_component import LifecycleComponent


class ComposedLifecycleNode(LifecycleNode):
    """LifecycleNode composed of lifecycle-aware components.

    Key design choice:
    we register each component as a ManagedEntity, then rely on the native
    LifecycleNode behavior to propagate lifecycle transitions.
    """

    def __init__(self, node_name: str, *, namespace: str | None = None, **kwargs) -> None:
        super().__init__(node_name, namespace=namespace, **kwargs)
        self._components: dict[str, LifecycleComponent] = {}

    @property
    def components(self) -> tuple[LifecycleComponent, ...]:
        return tuple(self._components.values())

    def add_component(self, component: LifecycleComponent) -> None:
        if component.name in self._components:
            raise ValueError(f"Component name already registered: {component.name}")

        component.attach(self)
        self.add_managed_entity(component)
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
