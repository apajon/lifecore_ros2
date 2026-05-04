from __future__ import annotations

import traceback
from abc import ABC
from collections.abc import Callable, Sequence
from functools import wraps
from logging import getLogger
from typing import TYPE_CHECKING, Any, Protocol, cast, final, overload

from rclpy.callback_groups import CallbackGroup
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.managed_entity import ManagedEntity
from rclpy.lifecycle.node import LifecycleState

from .exceptions import ComponentNotAttachedError, InvalidLifecycleTransitionError, LifecycleHookError

if TYPE_CHECKING:
    from .lifecycle_component_node import LifecycleComponentNode

_VALID_RETURNS = frozenset(
    {
        TransitionCallbackReturn.SUCCESS,
        TransitionCallbackReturn.FAILURE,
        TransitionCallbackReturn.ERROR,
    }
)

# Ordering used by _worst_of: SUCCESS=0 < FAILURE=1 < ERROR=2
_SEVERITY: dict[TransitionCallbackReturn, int] = {
    TransitionCallbackReturn.SUCCESS: 0,
    TransitionCallbackReturn.FAILURE: 1,
    TransitionCallbackReturn.ERROR: 2,
}


def _worst_of(
    a: TransitionCallbackReturn,
    b: TransitionCallbackReturn,
) -> TransitionCallbackReturn:
    """Return the more severe of two TransitionCallbackReturn values.

    Ordering: SUCCESS < FAILURE < ERROR.
    Used to aggregate hook and resource-release results in cleanup/shutdown/error
    entry points so the worst outcome is always propagated upward.
    """
    return a if _SEVERITY.get(a, 2) >= _SEVERITY.get(b, 2) else b


class _LoggerLike(Protocol):
    def debug(self, msg: str) -> None: ...

    def info(self, msg: str) -> None: ...

    def warning(self, msg: str) -> None: ...

    def error(self, msg: str) -> None: ...

    def fatal(self, msg: str) -> None: ...


_SENTINEL = object()


# Any in this decorator is justified at three points:
#   1. TypeVar bound `F: Callable[..., Any]` — idiomatic way to express "any callable with any return";
#      `Callable[..., Any]` is the canonical PEP 484 spelling; tightening it is not possible without
#      introducing a second return TypeVar that would complicate every call site.
#   2. `Callable[[], Any]` for `when_not_active` — the return value of the user-supplied fallback
#      is intentionally discarded; `None` would be incorrect for callables that return a value.
#   3. `cast(Callable[[], Any], ...)` inside the body — narrows the union to call the fallback;
#      same justification as (2).
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
        # Any: standard callable-preserving decorator pattern; cast(F, wrapper) restores the wrapped signature for callers
        def wrapper(self: LifecycleComponent, *args: Any, **kwargs: Any) -> Any:
            if not self._is_active:  # pyright: ignore[reportPrivateUsage]
                if when_not_active is _SENTINEL:
                    _default_raise(self)
                elif when_not_active is not None:
                    cast(Callable[[], Any], when_not_active)()
                else:
                    # Silent no-op — trace at debug level for diagnosis.
                    self._resolve_logger().debug(f"[{self._name}] {fn.__name__} dropped: component not active")  # pyright: ignore[reportPrivateUsage]
                return None
            return fn(self, *args, **kwargs)

        return cast(F, wrapper)

    if wrapped is not None:
        return decorator(wrapped)
    return decorator


class LifecycleComponent(ManagedEntity, ABC):
    """Base managed entity for composable lifecycle behavior inside a ``LifecycleComponentNode``.

    Each subclass encapsulates a single concern (e.g. a publisher, subscriber, or timer)
    and integrates natively into the ROS 2 lifecycle via the ``ManagedEntity`` protocol.

    Framework guarantees:
        - ``_is_active`` is set to ``True`` after a successful ``_on_activate`` hook
          and cleared to ``False`` after a successful ``_on_deactivate`` hook.
          For ``_on_cleanup``, ``_on_shutdown``, and ``_on_error``, ``_is_active`` is
          cleared unconditionally before the hook runs. Subclasses never manage this flag.
        - ``_release_resources()`` is called automatically after ``_on_cleanup``,
          ``_on_shutdown``, and ``_on_error``. Subclasses do not need to call it.
        - Exceptions in hooks are caught and converted to ``TransitionCallbackReturn.ERROR``.
        - Invalid return values from hooks are caught and converted to ERROR.

    Subclass extension points (override these):
        - ``_on_configure``: allocate ROS resources. Default returns SUCCESS.
        - ``_on_activate``: enable runtime behavior. Default returns SUCCESS.
        - ``_on_deactivate``: disable runtime behavior. Default returns SUCCESS.
        - ``_on_cleanup``: custom cleanup before automatic resource release. Default returns SUCCESS.
        - ``_on_shutdown``: custom shutdown logic. Default returns SUCCESS.
        - ``_on_error``: custom error handling. Default returns SUCCESS.
        - ``_release_resources``: destroy ROS objects (publishers, subscriptions, timers).
          Must be idempotent. Call ``super()._release_resources()`` last when overriding.

    Do not override:
        - ``on_configure``, ``on_activate``, ``on_deactivate``, ``on_cleanup``,
          ``on_shutdown``, ``on_error`` — framework-controlled entry points that
          manage lifecycle invariants and delegate to the ``_on_*`` hooks.
    """

    def __init__(
        self,
        name: str,
        *,
        callback_group: CallbackGroup | None = None,
        dependencies: Sequence[str] = (),
        priority: int = 0,
    ) -> None:
        """Initialize the lifecycle component.

        Args:
            name: Unique name for this component within the node.
            callback_group: Optional CallbackGroup borrowed from the application; lifetime owned
                by the caller. None selects the node default group.
            dependencies: Names of other components that must be transitioned before this one.
                Used by ``LifecycleComponentNode`` to resolve the transition order.
            priority: Tie-breaking value for ordering when dependencies do not impose a strict
                ordering; higher values are resolved earlier.
        """
        super().__init__()
        self._name: str = name
        self._callback_group: CallbackGroup | None = callback_group
        self._dependencies: tuple[str, ...] = tuple(dependencies)
        self._priority: int = priority
        self._node: LifecycleComponentNode | None = None
        self._is_configured: bool = False
        self._needs_cleanup: bool = False
        self._is_active: bool = False
        self._withdrawn: bool = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_active(self) -> bool:
        """Whether the component is in the active state."""
        return self._is_active

    @property
    def callback_group(self) -> CallbackGroup | None:
        """The callback group borrowed from the application, or None for the node default."""
        return self._callback_group

    @property
    def node(self) -> LifecycleComponentNode:
        if self._node is None:
            raise ComponentNotAttachedError(f"Component '{self._name}' is not attached to a node")
        return self._node

    def get_logger(self) -> _LoggerLike:
        return self.node.get_logger()  # type: ignore[return-value]  # rclpy RcutilsLogger is not typed against _LoggerLike but is structurally compatible

    def get_parent_name(self) -> str:
        return self.node.get_name()

    def get_parent_namespace(self) -> str:
        return self.node.get_namespace()

    # -- framework-internal attachment ------------------------------------

    def _attach(self, node: LifecycleComponentNode) -> None:
        """Framework-internal. Do not call from user code.

        Raises:
            RuntimeError: If the component is already attached.
        """
        if self._node is not None:
            raise RuntimeError(
                f"Component '{self._name}' is already attached to "
                f"Node '{self._node.get_namespace()}{self._node.get_name()}'"
            )
        self._node = node

    def _detach(self) -> None:
        """Framework-internal. Do not call from user code."""
        self._node = None

    # -- logger resolution ------------------------------------------------

    def _resolve_logger(self) -> _LoggerLike:
        """Framework-internal. Do not call from user code."""
        if self._node is not None:
            return cast(_LoggerLike, self._node.get_logger())
        return cast(_LoggerLike, getLogger(__name__))

    # -- guarded hook dispatch --------------------------------------------

    def _guarded_call(
        self,
        hook_name: str,
        hook: Callable[[LifecycleState], TransitionCallbackReturn],
        state: LifecycleState,
    ) -> TransitionCallbackReturn:
        """Framework-internal. Do not call from user code."""
        log = self._resolve_logger()
        try:
            result = hook(state)
            if result not in _VALID_RETURNS:
                log.error(
                    f"[{self._name}.{hook_name}] expected TransitionCallbackReturn, "
                    f"got {type(result).__name__} {result!r}"
                )
                return TransitionCallbackReturn.ERROR
            return result
        except Exception as exc:
            hook_error = LifecycleHookError(f"[{self._name}.{hook_name}] raised {type(exc).__name__}: {exc}")
            hook_error.__cause__ = exc
            log.error(str(hook_error))
            log.error(traceback.format_exc())
            return TransitionCallbackReturn.ERROR

    def _safe_release_resources(self) -> TransitionCallbackReturn:
        """Framework-internal. Do not call from user code."""
        try:
            self._release_resources()
            return TransitionCallbackReturn.SUCCESS
        except Exception as exc:
            log = self._resolve_logger()
            log.error(f"[{self._name}._release_resources] {type(exc).__name__}: {exc}")
            log.error(traceback.format_exc())
            return TransitionCallbackReturn.ERROR

    def _contract_state(self) -> str:
        """Framework-internal. Do not call from user code."""
        if self._is_active:
            return "active"
        if self._is_configured:
            return "inactive"
        if self._needs_cleanup:
            return "partially_configured"
        return "unconfigured"

    def _is_node_managed_transition(self, attempted_transition: str) -> bool:
        """Framework-internal. Do not call from user code."""
        if self._node is None:
            return False
        return self._node._managed_transition_name == attempted_transition  # pyright: ignore[reportPrivateUsage]

    def _raise_invalid_transition(self, attempted_transition: str, reason: str) -> None:
        """Framework-internal. Do not call from user code."""
        current_state = self._contract_state()
        self._resolve_logger().error(
            f"[{self._name}] rejected lifecycle transition "
            f"attempted='{attempted_transition}' current_state='{current_state}' reason='{reason}'"
        )
        raise InvalidLifecycleTransitionError(
            f"Component '{self._name}' cannot '{attempted_transition}' from '{current_state}': {reason}"
        )

    def _assert_transition_allowed(self, attempted_transition: str) -> None:
        """Framework-internal. Do not call from user code."""
        if self._is_node_managed_transition(attempted_transition):
            return

        if attempted_transition == "configure":
            if self._needs_cleanup:
                self._raise_invalid_transition(attempted_transition, "component requires cleanup before reconfigure")
            return

        if attempted_transition == "activate":
            if not self._is_configured:
                self._raise_invalid_transition(attempted_transition, "component is not configured")
            if self._is_active:
                self._raise_invalid_transition(attempted_transition, "component is already active")
            return

        if attempted_transition == "deactivate":
            if not self._is_configured:
                self._raise_invalid_transition(attempted_transition, "component is not configured")
            if not self._is_active:
                self._raise_invalid_transition(attempted_transition, "component is not active")
            return

        if attempted_transition == "cleanup":
            if not self._needs_cleanup:
                self._raise_invalid_transition(attempted_transition, "component is not configured")
            if self._is_active:
                self._raise_invalid_transition(attempted_transition, "component is still active")

    def _rollback_failed_configure(self) -> TransitionCallbackReturn:
        """Framework-internal. Do not call from user code."""
        self._is_configured = False
        self._is_active = False
        release_result = self._safe_release_resources()
        if release_result == TransitionCallbackReturn.SUCCESS:
            self._needs_cleanup = False
        return release_result

    # -- framework-controlled entry points (do not override) ----------------
    # These implement the rclpy ManagedEntity protocol. Sealed with @final so
    # pyright catches accidental overrides in application code. Extend behavior
    # via the _on_* extension points below.

    @final
    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        if self._withdrawn:
            return TransitionCallbackReturn.SUCCESS
        self._assert_transition_allowed("configure")
        result = self._guarded_call("on_configure", self._on_configure, state)
        if result == TransitionCallbackReturn.SUCCESS:
            self._is_configured = True
            self._needs_cleanup = True
        elif result in {TransitionCallbackReturn.FAILURE, TransitionCallbackReturn.ERROR}:
            self._is_configured = False
            self._needs_cleanup = True
        return result

    @final
    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        if self._withdrawn:
            return TransitionCallbackReturn.SUCCESS
        self._assert_transition_allowed("activate")
        result = self._guarded_call("on_activate", self._on_activate, state)
        if result == TransitionCallbackReturn.SUCCESS:
            self._is_active = True
        return result

    @final
    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        if self._withdrawn:
            return TransitionCallbackReturn.SUCCESS
        self._assert_transition_allowed("deactivate")
        result = self._guarded_call("on_deactivate", self._on_deactivate, state)
        if result == TransitionCallbackReturn.SUCCESS:
            self._is_active = False
        return result

    @final
    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        if self._withdrawn:
            return TransitionCallbackReturn.SUCCESS
        self._assert_transition_allowed("cleanup")
        self._is_active = False
        self._is_configured = False
        result = self._guarded_call("on_cleanup", self._on_cleanup, state)
        release_result = self._safe_release_resources()
        if release_result == TransitionCallbackReturn.SUCCESS:
            self._is_configured = False
            self._needs_cleanup = False
        return _worst_of(result, release_result)

    @final
    def on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        if self._withdrawn:
            return TransitionCallbackReturn.SUCCESS
        self._is_active = False
        self._is_configured = False
        result = self._guarded_call("on_shutdown", self._on_shutdown, state)
        release_result = self._safe_release_resources()
        if release_result == TransitionCallbackReturn.SUCCESS:
            self._is_configured = False
            self._needs_cleanup = False
        return _worst_of(result, release_result)

    @final
    def on_error(self, state: LifecycleState) -> TransitionCallbackReturn:
        if self._withdrawn:
            return TransitionCallbackReturn.SUCCESS
        self._is_active = False
        self._is_configured = False
        result = self._guarded_call("on_error", self._on_error, state)
        release_result = self._safe_release_resources()
        if release_result == TransitionCallbackReturn.SUCCESS:
            self._is_configured = False
            self._needs_cleanup = False
        return _worst_of(result, release_result)

    # -- protected extension points (override these in subclasses) -----------

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Extension point. Override to allocate ROS resources.

        Called during the configure transition. Do not enable runtime behavior here.

        Returns:
            TransitionCallbackReturn: SUCCESS, FAILURE, or ERROR.
        """
        return TransitionCallbackReturn.SUCCESS

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Extension point. Override to enable runtime behavior.

        The framework sets ``_is_active = True`` after this hook returns SUCCESS.
        Do not set ``_is_active`` manually.

        Returns:
            TransitionCallbackReturn: SUCCESS, FAILURE, or ERROR.
        """
        return TransitionCallbackReturn.SUCCESS

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Extension point. Override to disable runtime behavior.

        The framework clears ``_is_active`` only after this hook returns SUCCESS.
        All ``@when_active``-gated methods stop executing after SUCCESS is returned.

        Returns:
            TransitionCallbackReturn: SUCCESS, FAILURE, or ERROR.
        """
        return TransitionCallbackReturn.SUCCESS

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Extension point. Override for custom cleanup before resource release.

        The framework calls ``_release_resources()`` automatically after this hook.

        Returns:
            TransitionCallbackReturn: SUCCESS, FAILURE, or ERROR.
        """
        return TransitionCallbackReturn.SUCCESS

    def _on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Extension point. Override for custom shutdown logic.

        The framework calls ``_release_resources()`` automatically after this hook.

        Returns:
            TransitionCallbackReturn: SUCCESS, FAILURE, or ERROR.
        """
        return TransitionCallbackReturn.SUCCESS

    def _on_error(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Extension point. Override for custom error handling.

        The framework calls ``_release_resources()`` automatically after this hook.

        Returns:
            TransitionCallbackReturn: SUCCESS, FAILURE, or ERROR.
        """
        return TransitionCallbackReturn.SUCCESS

    def _release_resources(self) -> None:
        """Extension point. Override to release ROS resources owned by this component.

        Called automatically by the framework during cleanup, shutdown, and error
        transitions. Destroy publishers, subscriptions, timers, etc. here.

        Implementations must be idempotent. Call ``super()._release_resources()`` last
        when overriding in a subclass chain.
        """
        self._is_configured = False
        self._needs_cleanup = False
        self._is_active = False
