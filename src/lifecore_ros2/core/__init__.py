"""Core runtime primitives for lifecore_ros2."""

from .exceptions import (
    ComponentDependencyError,
    ComponentNotAttachedError,
    ComponentNotConfiguredError,
    ConcurrentTransitionError,
    CyclicDependencyError,
    DuplicateComponentError,
    InvalidLifecycleTransitionError,
    LifecoreError,
    LifecycleHookError,
    RegistrationClosedError,
    UnknownDependencyError,
)
from .health import HealthLevel, HealthStatus
from .lifecycle_component import LifecycleComponent, when_active
from .lifecycle_component_node import LifecycleComponentNode

__all__ = [
    "LifecycleComponentNode",
    "LifecycleComponent",
    "when_active",
    "HealthStatus",
    "HealthLevel",
    "LifecoreError",
    "LifecycleHookError",
    "RegistrationClosedError",
    "DuplicateComponentError",
    "ComponentNotAttachedError",
    "ComponentNotConfiguredError",
    "InvalidLifecycleTransitionError",
    "ConcurrentTransitionError",
    "ComponentDependencyError",
    "UnknownDependencyError",
    "CyclicDependencyError",
]
