"""Tests for ROS interface-type inference on topic components.

Covers the resolution rules established in ``docs/api_friction_audit.rst``
(ADR R-IfaceTypeInference): a component parameterized over a ROS interface
type may declare it via the generic parameter, an explicit constructor
argument, or both (when in agreement). Missing or conflicting sources raise
``_InterfaceTypeNotResolvedError`` at ``__init__``.
"""

from __future__ import annotations

from typing import Any

import pytest

from lifecore_ros2.components import LifecyclePublisherComponent, LifecycleSubscriberComponent
from lifecore_ros2.components.topic_component import TopicComponent
from lifecore_ros2.core._iface_type import _extract_generic_arg, _resolve_iface_type
from lifecore_ros2.core.exceptions import LifecoreError, _InterfaceTypeNotResolvedError


class _MsgA:
    pass


class _MsgB:
    pass


# ---------------------------------------------------------------------------
# Subscriber-side scenarios (also exercise TopicComponent.__init__).
# ---------------------------------------------------------------------------


class _GenericSub(LifecycleSubscriberComponent[_MsgA]):
    def on_message(self, msg: Any) -> None:
        pass


class _ExplicitSub(LifecycleSubscriberComponent[Any]):  # type: ignore[type-arg]
    def on_message(self, msg: Any) -> None:
        pass


class _AgreementSub(LifecycleSubscriberComponent[_MsgA]):
    def on_message(self, msg: Any) -> None:
        pass


class _ConflictSub(LifecycleSubscriberComponent[_MsgA]):
    def on_message(self, msg: Any) -> None:
        pass


class _IndirectSub(_GenericSub):
    pass


class _MidPub(LifecyclePublisherComponent[_MsgA]):
    pass


class _LeafPub(_MidPub):
    pass


class TestInferenceFromGeneric:
    def test_subscriber_infers_from_generic(self) -> None:
        sub = _GenericSub(name="s", topic_name="/t")
        assert sub.msg_type is _MsgA

    def test_publisher_infers_from_generic(self) -> None:
        pub = _LeafPub(name="p", topic_name="/t")
        assert pub.msg_type is _MsgA

    def test_indirect_subclass_inherits_generic(self) -> None:
        sub = _IndirectSub(name="s", topic_name="/t")
        assert sub.msg_type is _MsgA


class TestExplicitArgument:
    def test_explicit_only_still_works(self) -> None:
        # Backward compatibility: subclass not parameterized, msg_type passed.
        class _Sub(LifecycleSubscriberComponent):  # type: ignore[type-arg]
            def on_message(self, msg: Any) -> None:
                pass

        sub = _Sub(name="s", topic_name="/t", msg_type=_MsgA)
        assert sub.msg_type is _MsgA

    def test_explicit_and_generic_agree(self) -> None:
        sub = _AgreementSub(name="s", topic_name="/t", msg_type=_MsgA)
        assert sub.msg_type is _MsgA


class TestBoundaryFailures:
    def test_missing_both_raises(self) -> None:
        class _Sub(LifecycleSubscriberComponent):  # type: ignore[type-arg]
            def on_message(self, msg: Any) -> None:
                pass

        with pytest.raises(_InterfaceTypeNotResolvedError):
            _Sub(name="s", topic_name="/t")

    def test_conflict_raises(self) -> None:
        with pytest.raises(_InterfaceTypeNotResolvedError):
            _ConflictSub(name="s", topic_name="/t", msg_type=_MsgB)  # type: ignore[arg-type]

    def test_error_is_lifecore_and_typeerror(self) -> None:
        # Caught either way for caller-side ergonomics.
        assert issubclass(_InterfaceTypeNotResolvedError, LifecoreError)
        assert issubclass(_InterfaceTypeNotResolvedError, TypeError)

    def test_error_not_publicly_exported(self) -> None:
        import lifecore_ros2

        public = set(getattr(lifecore_ros2, "__all__", ()))
        assert "_InterfaceTypeNotResolvedError" not in public

    def test_typevar_forwarding_does_not_resolve(self) -> None:
        # A generic ancestor that forwards its own TypeVar must not be treated
        # as resolved. We exercise the resolver directly because shaping this
        # via TopicComponent subclassing requires reproducing the framework's
        # internal generics.
        from typing import TypeVar

        T = TypeVar("T")

        class _Forwarding(TopicComponent[T]):  # type: ignore[valid-type, misc]
            pass

        with pytest.raises(_InterfaceTypeNotResolvedError):
            _resolve_iface_type(_Forwarding, base=TopicComponent, explicit=None)


class TestExtractGenericArg:
    def test_returns_none_when_unparameterized(self) -> None:
        class _Sub(LifecycleSubscriberComponent):  # type: ignore[type-arg]
            def on_message(self, msg: Any) -> None:
                pass

        assert _extract_generic_arg(_Sub, base=TopicComponent) is None

    def test_returns_arg_for_parameterized_chain(self) -> None:
        assert _extract_generic_arg(_LeafPub, base=TopicComponent) is _MsgA
