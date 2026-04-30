"""Core runtime primitives for lifecore_ros2."""

from .exceptions import (
    ComponentNotAttachedError,
    ComponentNotConfiguredError,
    ConcurrentTransitionError,
    DuplicateComponentError,
    InvalidLifecycleTransitionError,
    LifecoreError,
    LifecycleHookError,
    RegistrationClosedError,
)
from .lifecycle_component import LifecycleComponent, when_active
from .lifecycle_component_node import LifecycleComponentNode

__all__ = [
    "LifecycleComponentNode",
    "LifecycleComponent",
    "when_active",
    "LifecoreError",
    "LifecycleHookError",
    "RegistrationClosedError",
    "DuplicateComponentError",
    "ComponentNotAttachedError",
    "ComponentNotConfiguredError",
    "InvalidLifecycleTransitionError",
    "ConcurrentTransitionError",
]
