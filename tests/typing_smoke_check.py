"""Pyright-only smoke check for the MsgT generic contract.

This file is intentionally NOT a test module (no ``test_`` prefix, no test functions).
pytest will not collect it. Run manually with:

    uv run pyright tests/typing_smoke_check.py

Self-verifying design: the wrong-type call below carries ``# type: ignore[arg-type]``.
Under pyright strict ``reportUnnecessaryTypeIgnoreComment`` is enabled — if the generic
were broken and ``MsgT`` resolved to ``Any``, pyright would report the ignore as
unnecessary, surfacing the failure automatically.
"""

from __future__ import annotations

from typing import assert_type

from lifecore_ros2 import LifecycleComponentNode, LifecyclePublisherComponent, LifecycleSubscriberComponent

# ---------------------------------------------------------------------------
# Local stub message types — avoids any ROS runtime dependency in type checks
# ---------------------------------------------------------------------------


class _MsgA:
    data: str = ""


class _MsgB:
    value: int = 0


# ---------------------------------------------------------------------------
# Publisher generic contract
# ---------------------------------------------------------------------------


def _check_publisher_valid(pub: LifecyclePublisherComponent[_MsgA]) -> None:
    """Publishing the correct type is accepted by pyright."""
    pub.publish(_MsgA())  # OK


def _check_publisher_wrong_type(pub: LifecyclePublisherComponent[_MsgA]) -> None:
    """Publishing the wrong type must be rejected.

    If MsgT were ``Any`` (broken generic), this ``# type: ignore`` would be
    unnecessary and pyright strict would raise ``reportUnnecessaryTypeIgnoreComment``.
    """
    pub.publish(_MsgB())  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Subscriber generic contract
# ---------------------------------------------------------------------------


class _StubSubscriber(LifecycleSubscriberComponent[_MsgA]):
    """Correctly typed subscriber — on_message takes _MsgA."""

    def on_message(self, msg: _MsgA) -> None:
        _ = msg.data  # valid attribute access; pyright knows msg is _MsgA


class _BrokenSubscriber(LifecycleSubscriberComponent[_MsgA]):
    """Wrong parameter type in on_message must be caught by pyright."""

    def on_message(  # type: ignore[override]
        self,
        msg: _MsgB,  # type: ignore[override]
    ) -> None: ...


# ---------------------------------------------------------------------------
# msg_type property returns the correct type
# ---------------------------------------------------------------------------


def _check_msg_type_property(pub: LifecyclePublisherComponent[_MsgA]) -> None:
    assert_type(pub.msg_type, type[_MsgA])


# ---------------------------------------------------------------------------
# Node holds heterogeneous components — LifecycleComponentNode is NOT generic
# ---------------------------------------------------------------------------


def _check_node_not_generic() -> None:
    """LifecycleComponentNode is intentionally non-generic (heterogeneous registry)."""
    node = LifecycleComponentNode("smoke_node")
    pub: LifecyclePublisherComponent[_MsgA] = LifecyclePublisherComponent(name="p", topic_name="/t", msg_type=_MsgA)
    sub: LifecycleSubscriberComponent[_MsgA] = _StubSubscriber(name="s", topic_name="/t", msg_type=_MsgA)
    node.add_component(pub)
    node.add_component(sub)
