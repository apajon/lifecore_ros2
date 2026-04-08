from __future__ import annotations

import traceback
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from logging import getLogger
from typing import TYPE_CHECKING, Any, Protocol, cast

from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.managed_entity import ManagedEntity
from rclpy.lifecycle.node import LifecycleState

if TYPE_CHECKING:
    from .composed_lifecycle_node import ComposedLifecycleNode

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


class LifecycleComponent(ManagedEntity, ABC):
    """Base class for lifecycle-aware components attached to a composed node.

    This class intentionally stays small:
    - it is a ManagedEntity, so ROS 2 lifecycle callbacks are native
    - it knows its parent node
    - it does not introduce any parallel state machine
    """

    def __init__(self, name: str) -> None:
        super().__init__()
        self._name: str = name
        self._node: ComposedLifecycleNode | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def node(self) -> ComposedLifecycleNode:
        if self._node is None:
            raise RuntimeError(f"Component '{self._name}' is not attached to a node")
        return self._node

    def get_logger(self) -> Any:
        return self.node.get_logger()

    def get_parent_name(self) -> str:
        return self.node.get_name()

    def get_parent_namespace(self) -> str:
        return self.node.get_namespace()

    def attach(self, node: ComposedLifecycleNode) -> None:
        """Attach the component to a node.

        Args:
            node (ComposedLifecycleNode): The node to attach the component to.

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
        self.get_logger().debug(f"[{self.name}] component configure")
        return TransitionCallbackReturn.SUCCESS

    @_lifecycle_guard_component()
    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._on_activate(state)

    @abstractmethod
    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.get_logger().debug(f"[{self.name}] component activate")
        return TransitionCallbackReturn.SUCCESS

    @_lifecycle_guard_component()
    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._on_deactivate(state)

    @abstractmethod
    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.get_logger().debug(f"[{self.name}] component deactivate")
        return TransitionCallbackReturn.SUCCESS

    @_lifecycle_guard_component()
    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._on_cleanup(state)

    @abstractmethod
    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.get_logger().debug(f"[{self.name}] component cleanup")
        return TransitionCallbackReturn.SUCCESS

    def _release_resources(self) -> None:
        """Release resources managed by this component.

        Called automatically during shutdown, error, and cleanup.
        Override in subclasses that allocate ROS resources.
        """

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
