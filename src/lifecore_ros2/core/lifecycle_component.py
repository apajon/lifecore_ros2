from __future__ import annotations

import traceback
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from logging import getLogger
from typing import TYPE_CHECKING, Any, Protocol, cast, overload

from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.managed_entity import ManagedEntity
from rclpy.lifecycle.node import LifecycleState

if TYPE_CHECKING:
    from .lifecycle_component_node import LifecycleComponentNode

_LifecycleHook = Callable[["LifecycleComponent", LifecycleState], TransitionCallbackReturn]


class _LoggerLike(Protocol):
    def debug(self, msg: str) -> None: ...

    def warning(self, msg: str) -> None: ...

    def error(self, msg: str) -> None: ...


def _lifecycle_guard_component(strict: bool = True) -> Callable[[_LifecycleHook], _LifecycleHook]:
    """Decorator to guard lifecycle component methods.

    Args:
        strict: If ``True``, invalid return values will result in ERROR.
    """

    def decorator(method: _LifecycleHook) -> _LifecycleHook:
        @wraps(method)
        def wrapper(self: LifecycleComponent, state: LifecycleState) -> TransitionCallbackReturn:
            log: _LoggerLike = getLogger(__name__)

            if hasattr(self, "get_logger") and callable(self.get_logger):
                log = cast(_LoggerLike, self.get_logger())
            else:
                node = getattr(self, "_node", None)
                if node is not None and hasattr(node, "get_logger") and callable(node.get_logger):
                    log = cast(_LoggerLike, node.get_logger())

            if not isinstance(self, LifecycleComponent):
                msg = (
                    f"{method.__qualname__} is decorated with _lifecycle_guard_component "
                    f"but self is {type(self).__name__}, expected LifecycleComponent"
                )

                log.error(msg)
                log.error("Decorator misuse detected, forcing lifecycle ERROR return")
                return TransitionCallbackReturn.ERROR

            method_name = method.__name__
            component_name = self.name

            try:
                log.debug(f"[{component_name}.{method_name}] start")

                result = method(self, state)

                valid_returns = (
                    TransitionCallbackReturn.SUCCESS,
                    TransitionCallbackReturn.FAILURE,
                    TransitionCallbackReturn.ERROR,
                )

                if result not in valid_returns:
                    msg = f"[{component_name}.{method_name}] invalid return value: {result!r}"
                    if strict:
                        log.error(msg)
                        return TransitionCallbackReturn.ERROR
                    log.warning(msg)
                    return TransitionCallbackReturn.FAILURE

                log.debug(f"[{component_name}.{method_name}] result={result}")
                return result

            except Exception as exc:
                log.error(f"[{component_name}.{method_name}] crashed with {type(exc).__name__}: {exc}")
                log.error(traceback.format_exc())
                return TransitionCallbackReturn.ERROR

        return wrapper

    return decorator


_SENTINEL = object()


@overload
def when_active[F: Callable[..., Any]](wrapped: F, /) -> F: ...


@overload
def when_active[F: Callable[..., Any]](*, when_not_active: Callable[[], Any] | None = ...) -> Callable[[F], F]: ...


def when_active[F: Callable[..., Any]](
    wrapped: F | None = None,
    /,
    *,
    when_not_active: Callable[[], Any] | object = _SENTINEL,
) -> F | Callable[[F], F]:
    """Gate a method so it only executes when the component is active.

    Default behavior raises ``RuntimeError``.  Pass a callable to
    ``when_not_active`` to customise, or ``None`` for a silent no-op.

    Usage::

        @when_active
        def publish(self, msg): ...

        @when_active(when_not_active=None)
        def _on_message_wrapper(self, msg): ...

        @when_active(when_not_active=lambda: logger.warning("dropped"))
        def do_something(self): ...
    """

    def _default_raise(self: LifecycleComponent) -> None:
        raise RuntimeError(f"Component '{self.name}' is not active")

    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(self: LifecycleComponent, *args: Any, **kwargs: Any) -> Any:
            if not self._is_active:
                if when_not_active is _SENTINEL:
                    _default_raise(self)
                elif when_not_active is not None:
                    cast(Callable[[], Any], when_not_active)()
                return None
            return fn(self, *args, **kwargs)

        return cast(F, wrapper)

    if wrapped is not None:
        return decorator(wrapped)
    return decorator


class LifecycleComponent(ManagedEntity, ABC):
    """Base class for lifecycle-aware components attached to a composed node.

    This class intentionally stays small:

    - it is a ``ManagedEntity``, so ROS 2 lifecycle callbacks are driven natively by the parent node.
    - it knows its parent node via ``node``.
    - it exposes explicit lifecycle hooks (``_on_configure``, ``_on_activate``, etc.).
    - it does **not** introduce any parallel hidden state machine.

    Lifecycle invariants:

    - **configure**: allocate ROS resources (publishers, subscriptions). Do not enable runtime behavior.
    - **activate**: enable runtime behavior. Must call ``super()._on_activate(state)`` to set ``_is_active``.
    - **deactivate**: disable runtime behavior. Must call ``super()._on_deactivate(state)`` to clear ``_is_active``. Does not release resources.
    - **cleanup**: release all ROS resources. Must call ``_release_resources()``. Does not affect activation state directly.
    - **shutdown / error**: automatic call to ``_release_resources()``. No override needed for most subclasses.

    Note:
        ``_is_active`` is managed exclusively in the abstract bodies of ``_on_activate`` and
        ``_on_deactivate``. Subclasses must call ``super()`` in both hooks for gating to work
        correctly. Methods decorated with ``@when_active`` rely on this flag.
    """

    def __init__(self, name: str) -> None:
        super().__init__()
        self._name: str = name
        self._node: LifecycleComponentNode | None = None
        self._is_active: bool = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_active(self) -> bool:
        """Whether the component is in the active state."""
        return self._is_active

    @property
    def node(self) -> LifecycleComponentNode:
        if self._node is None:
            raise RuntimeError(f"Component '{self._name}' is not attached to a node")
        return self._node

    def get_logger(self) -> Any:
        return self.node.get_logger()

    def get_parent_name(self) -> str:
        return self.node.get_name()

    def get_parent_namespace(self) -> str:
        return self.node.get_namespace()

    def attach(self, node: LifecycleComponentNode) -> None:
        """Attach the component to a node.

        Args:
            node (LifecycleComponentNode): The node to attach the component to.

        Raises:
            RuntimeError: If the component is already attached to a node.
        """
        if self._node is not None:
            raise RuntimeError(
                f"Component '{self._name}' is already attached to Node '{self.node.get_namespace() + self.get_parent_name()}'"
            )
        self._node = node

    def _detach(self) -> None:
        """Reset the node reference (internal rollback for failed registration)."""
        self._node = None

    @_lifecycle_guard_component()
    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._on_configure(state)

    @abstractmethod
    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Configure the component.

        Allowed: allocate ROS resources (create publishers, subscriptions, timers).
        Not allowed: enable runtime behavior or set ``_is_active``.

        Subclasses must call ``super()._on_configure(state)`` first.

        Returns:
            TransitionCallbackReturn: SUCCESS, FAILURE, or ERROR.
        """
        self.get_logger().debug(f"[{self.name}] component configure")
        return TransitionCallbackReturn.SUCCESS

    @_lifecycle_guard_component()
    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._on_activate(state)

    @abstractmethod
    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Activate the component.

        Allowed: enable runtime behavior (start publishing, accept messages).
        Not allowed: allocate new ROS resources.

        Subclasses must call ``super()._on_activate(state)`` to set ``_is_active = True``.
        Methods decorated with ``@when_active`` will not execute until this flag is set.

        Returns:
            TransitionCallbackReturn: SUCCESS, FAILURE, or ERROR.
        """
        self._is_active = True
        self.get_logger().debug(f"[{self.name}] component activate")
        return TransitionCallbackReturn.SUCCESS

    @_lifecycle_guard_component()
    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._on_deactivate(state)

    @abstractmethod
    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Deactivate the component.

        Required: disable runtime behavior.
        Not allowed: release ROS resources (that is cleanup's responsibility).

        Subclasses must call ``super()._on_deactivate(state)`` to clear ``_is_active = False``.
        After this call, all ``@when_active``-gated methods stop executing.

        Returns:
            TransitionCallbackReturn: SUCCESS, FAILURE, or ERROR.
        """
        self._is_active = False
        self.get_logger().debug(f"[{self.name}] component deactivate")
        return TransitionCallbackReturn.SUCCESS

    @_lifecycle_guard_component()
    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._on_cleanup(state)

    @abstractmethod
    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Clean up the component.

        Required: release all ROS resources allocated during configure.
        Subclasses must call ``_release_resources()`` explicitly — the base body does not do it.

        Subclasses should call ``super()._on_cleanup(state)`` first, then ``_release_resources()``.

        Returns:
            TransitionCallbackReturn: SUCCESS, FAILURE, or ERROR.
        """
        self.get_logger().debug(f"[{self.name}] component cleanup")
        return TransitionCallbackReturn.SUCCESS

    @abstractmethod
    def _release_resources(self) -> None:
        """Release all ROS resources allocated by this component.

        Called automatically by ``_on_shutdown`` and ``_on_error``.
        Must be called explicitly by subclasses inside ``_on_cleanup``.

        Subclasses must call ``super()._release_resources()`` last to ensure
        ``_is_active`` is cleared.
        """
        self._is_active = False

    @_lifecycle_guard_component()
    def on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._on_shutdown(state)

    def _on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._release_resources()
        self.get_logger().debug(f"[{self.name}] component shutdown")
        return TransitionCallbackReturn.SUCCESS

    @_lifecycle_guard_component()
    def on_error(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._on_error(state)

    def _on_error(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._release_resources()
        self.get_logger().error(f"[{self.name}] component error")
        return TransitionCallbackReturn.SUCCESS
