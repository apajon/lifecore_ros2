"""Transverse resolver for ROS interface types declared on generic components.

A component parameterized over a ROS interface type (today ``msg_type`` on
:class:`~lifecore_ros2.components.topic_component.TopicComponent`, tomorrow
``srv_type`` and ``action_type`` on future ``ServiceComponent`` /
``ActionComponent``) can declare that type either via its generic parameter
(``Component[InterfaceT]``) or via an explicit constructor argument. This
module reconciles both sources at ``__init__`` time.

See ``docs/api_friction_audit.rst`` (ADR R-IfaceTypeInference) for the
decision record and the POC scenarios that validated the approach.

Internal module — not part of the public API.
"""

from __future__ import annotations

import typing
from typing import Any, TypeVar

from lifecore_ros2.core.exceptions import _InterfaceTypeNotResolvedError


def _extract_generic_arg(cls: type, *, base: type) -> Any | None:
    """Return the first concrete type argument bound to ``base`` in ``cls.__mro__``.

    Walks the MRO of ``cls`` looking for a parameterized generic whose origin
    is ``base`` or a subclass of ``base``. Returns the first concrete type
    argument found; returns ``None`` if every candidate forwards an unresolved
    :class:`~typing.TypeVar` or is :data:`typing.Any` (treated as "unspecified",
    not "resolved").
    """
    for ancestor in cls.__mro__:
        for orig in getattr(ancestor, "__orig_bases__", ()):
            origin = typing.get_origin(orig)
            if not isinstance(origin, type) or not issubclass(origin, base):
                continue
            args = typing.get_args(orig)
            if not args:
                continue
            arg = args[0]
            if isinstance(arg, TypeVar) or arg is Any:
                continue
            if isinstance(arg, type):
                return arg
    return None


def _resolve_iface_type(
    cls: type,
    *,
    base: type,
    explicit: type | None,
    interface_kind: str = "interface type",
) -> type:
    """Resolve the interface type for ``cls`` from its generic parameter or explicit argument.

    Args:
        cls: Concrete class being instantiated (typically ``type(self)``).
        base: Generic base whose first type parameter is the interface type
            (e.g. ``TopicComponent``). Subclasses of ``base`` are also accepted
            so user classes can subclass intermediate generics like
            ``LifecyclePublisherComponent[Msg]``.
        explicit: Interface type passed to ``__init__``, or ``None``.
        interface_kind: Human-readable label used in error messages
            (e.g. ``"msg_type"``). Defaults to ``"interface type"``.

    Returns:
        The resolved interface type.

    Raises:
        _InterfaceTypeNotResolvedError: if neither generic parameter nor
            explicit argument is available, or if both are present and
            disagree.
    """
    inferred = _extract_generic_arg(cls, base=base)

    if explicit is None and inferred is None:
        raise _InterfaceTypeNotResolvedError(
            f"{cls.__name__}: cannot resolve {interface_kind}. "
            f"Either parameterize the generic base ({base.__name__}[YourType]) "
            f"or pass {interface_kind} explicitly to __init__."
        )

    if explicit is not None and inferred is not None and explicit is not inferred:
        raise _InterfaceTypeNotResolvedError(
            f"{cls.__name__}: explicit {interface_kind} {explicit!r} conflicts with generic parameter {inferred!r}."
        )

    return explicit if explicit is not None else inferred  # type: ignore[return-value]
