"""Framework-raised exception types for lifecore_ros2.

All framework boundary violations raise a subclass of :class:`LifecoreError`,
which is itself a plain :class:`Exception`. Every concrete subclass also inherits
from the corresponding standard Python exception so that existing ``except RuntimeError``
and ``except ValueError`` handlers remain unbroken.

Hierarchy::

    LifecoreError (Exception)
    ├── RegistrationClosedError   (RuntimeError)
    ├── DuplicateComponentError   (ValueError)
    ├── ComponentNotAttachedError (RuntimeError)
    ├── ComponentNotConfiguredError (RuntimeError)
    └── ConcurrentTransitionError (RuntimeError)
"""

from __future__ import annotations


class LifecoreError(Exception):
    """Base class for all boundary-violation exceptions raised by lifecore_ros2.

    Catch ``LifecoreError`` to handle any framework misuse error in one place.
    Concrete subclasses also inherit from standard Python exceptions for
    backward-compatibility with ``except RuntimeError`` / ``except ValueError``.
    """


class RegistrationClosedError(LifecoreError, RuntimeError):
    """Raised when ``add_component`` is called after lifecycle transitions have started."""


class DuplicateComponentError(LifecoreError, ValueError):
    """Raised when a component with the same name is already registered on the node."""


class ComponentNotAttachedError(LifecoreError, RuntimeError):
    """Raised when ``.node`` is accessed on a component that is not attached to a node."""


class ComponentNotConfiguredError(LifecoreError, RuntimeError):
    """Raised when ``publish()`` is called on a publisher that has not been configured yet."""


class ConcurrentTransitionError(LifecoreError, RuntimeError):
    """Raised when a lifecycle transition is attempted concurrently with an in-progress transition."""
