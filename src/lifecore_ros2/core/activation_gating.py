"""Shared activation-gating primitive for lifecore_ros2 components.

This module contains the single authoritative check for component activation
state. All framework gating paths delegate here — ``@when_active``,
``LifecycleComponent.require_active()``, and component-specific inactive
handlers — so the raise contract is defined in exactly one place.
"""

from __future__ import annotations


def require_active(is_active: bool, *, component_name: str) -> None:
    """Raise ``RuntimeError`` if the component is not active.

    This is the shared primitive used by all activation-gating paths in the
    framework. Most component code should prefer
    ``LifecycleComponent.require_active()``; the standalone function exists so
    ``@when_active`` and custom inactive handlers share the same raise contract.

    Args:
        is_active: Current activation state of the component.
        component_name: Name used in the error message for diagnosis.

    Raises:
        RuntimeError: If ``is_active`` is ``False``.
    """
    if not is_active:
        raise RuntimeError(f"Component '{component_name}' is not active")
