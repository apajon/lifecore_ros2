"""Tests for Sprint 5 internal cascade: dependency-based transition ordering."""

from __future__ import annotations

from typing import Any

import pytest
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.core import (
    CyclicDependencyError,
    LifecycleComponent,
    LifecycleComponentNode,
    UnknownDependencyError,
)
from lifecore_ros2.testing import DUMMY_STATE


class RecordingComponent(LifecycleComponent):
    """Minimal component that appends ``(name, hook_name)`` tuples to a shared recorder list."""

    def __init__(self, name: str, recorder: list[tuple[str, str]], **kwargs: Any) -> None:
        super().__init__(name, **kwargs)
        self._recorder = recorder

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._recorder.append((self.name, "on_configure"))
        return TransitionCallbackReturn.SUCCESS

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._recorder.append((self.name, "on_activate"))
        return TransitionCallbackReturn.SUCCESS

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._recorder.append((self.name, "on_deactivate"))
        return TransitionCallbackReturn.SUCCESS

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._recorder.append((self.name, "on_cleanup"))
        return TransitionCallbackReturn.SUCCESS

    def _on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._recorder.append((self.name, "on_shutdown"))
        return TransitionCallbackReturn.SUCCESS


@pytest.fixture()
def node():
    n = LifecycleComponentNode("test_cascade_node")
    yield n
    n.destroy_node()


class TestCascadeOrder:
    # -- 1. configure order respects dependency --

    def test_configure_order_dep_a_before_b(self, node: LifecycleComponentNode) -> None:
        recorder: list[tuple[str, str]] = []
        node.add_component(RecordingComponent("a", recorder))
        node.add_component(RecordingComponent("b", recorder, dependencies=("a",)))
        node.on_configure(DUMMY_STATE)
        configure_order = [name for name, hook in recorder if hook == "on_configure"]
        assert configure_order == ["a", "b"]

    # -- 2. activate order respects dependency --

    def test_activate_order_dep_a_before_b(self, node: LifecycleComponentNode) -> None:
        recorder: list[tuple[str, str]] = []
        node.add_component(RecordingComponent("a", recorder))
        node.add_component(RecordingComponent("b", recorder, dependencies=("a",)))
        node.on_configure(DUMMY_STATE)
        recorder.clear()
        node.on_activate(DUMMY_STATE)
        activate_order = [name for name, hook in recorder if hook == "on_activate"]
        assert activate_order == ["a", "b"]

    # -- 3. priority breaks ties --

    def test_priority_higher_value_first(self, node: LifecycleComponentNode) -> None:
        recorder: list[tuple[str, str]] = []
        node.add_component(RecordingComponent("low", recorder, priority=0))
        node.add_component(RecordingComponent("high", recorder, priority=10))
        node.on_configure(DUMMY_STATE)
        configure_order = [name for name, hook in recorder if hook == "on_configure"]
        assert configure_order == ["high", "low"]

    # -- 4. registration order is stable fallback when no deps and equal priority --

    def test_registration_order_stable_fallback(self, node: LifecycleComponentNode) -> None:
        recorder: list[tuple[str, str]] = []
        for name in ["first", "second", "third"]:
            node.add_component(RecordingComponent(name, recorder))
        node.on_configure(DUMMY_STATE)
        configure_order = [name for name, hook in recorder if hook == "on_configure"]
        assert configure_order == ["first", "second", "third"]

    # -- 5. deactivate is reverse of configure order --

    def test_deactivate_reverse_of_configure_order(self, node: LifecycleComponentNode) -> None:
        recorder: list[tuple[str, str]] = []
        node.add_component(RecordingComponent("a", recorder))
        node.add_component(RecordingComponent("b", recorder, dependencies=("a",)))
        node.on_configure(DUMMY_STATE)
        node.on_activate(DUMMY_STATE)
        recorder.clear()
        node.on_deactivate(DUMMY_STATE)
        deactivate_order = [name for name, hook in recorder if hook == "on_deactivate"]
        assert deactivate_order == ["b", "a"]

    # -- 6. cleanup is reverse of configure order --

    def test_cleanup_reverse_of_configure_order(self, node: LifecycleComponentNode) -> None:
        recorder: list[tuple[str, str]] = []
        node.add_component(RecordingComponent("a", recorder))
        node.add_component(RecordingComponent("b", recorder, dependencies=("a",)))
        node.on_configure(DUMMY_STATE)
        recorder.clear()
        node.on_cleanup(DUMMY_STATE)
        cleanup_order = [name for name, hook in recorder if hook == "on_cleanup"]
        assert cleanup_order == ["b", "a"]

    # -- 7. unknown dependency raises UnknownDependencyError from on_configure --

    def test_unknown_dependency_raises(self, node: LifecycleComponentNode) -> None:
        node.add_component(RecordingComponent("a", [], dependencies=("ghost",)))
        with pytest.raises(UnknownDependencyError, match="ghost"):
            node.on_configure(DUMMY_STATE)

    # -- 8. cyclic dependency raises CyclicDependencyError from on_configure --

    def test_cyclic_dependency_raises(self, node: LifecycleComponentNode) -> None:
        recorder: list[tuple[str, str]] = []
        node.add_component(RecordingComponent("a", recorder, dependencies=("b",)))
        node.add_component(RecordingComponent("b", recorder, dependencies=("a",)))
        with pytest.raises(CyclicDependencyError):
            node.on_configure(DUMMY_STATE)

    # -- 9. no-deps backward compat: registration order preserved --

    def test_no_deps_backward_compat_registration_order(self, node: LifecycleComponentNode) -> None:
        recorder: list[tuple[str, str]] = []
        for name in ["x", "y", "z"]:
            node.add_component(RecordingComponent(name, recorder))
        node.on_configure(DUMMY_STATE)
        configure_order = [name for name, hook in recorder if hook == "on_configure"]
        assert configure_order == ["x", "y", "z"]
