"""Regression tests for Sprint 5.1: registration-site composition metadata.

Covers:
- dependencies declared at add_component site (no constructor pass-through)
- priority declared at add_component site
- ordering equivalence: registration-site vs constructor declaration
- TypeError on explicit conflict (both sites non-default)
"""

from __future__ import annotations

from typing import Any

import pytest
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.core import LifecycleComponent, LifecycleComponentNode
from lifecore_ros2.testing import DUMMY_STATE


class RecordingComponent(LifecycleComponent):
    """Appends ``(name, hook_name)`` tuples to a shared recorder on each transition."""

    def __init__(self, name: str, recorder: list[tuple[str, str]], **kwargs: Any) -> None:
        super().__init__(name, **kwargs)
        self._recorder = recorder

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._recorder.append((self.name, "configure"))
        return TransitionCallbackReturn.SUCCESS

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._recorder.append((self.name, "activate"))
        return TransitionCallbackReturn.SUCCESS

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._recorder.append((self.name, "deactivate"))
        return TransitionCallbackReturn.SUCCESS

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._recorder.append((self.name, "cleanup"))
        return TransitionCallbackReturn.SUCCESS


@pytest.fixture()
def node() -> LifecycleComponentNode:
    n = LifecycleComponentNode("test_regsite_node")
    yield n  # type: ignore[misc]
    n.destroy_node()


class TestRegistrationSiteMetadata:
    # -- dependencies declared at registration site ----------------------

    def test_dependencies_at_registration_site_configure_order(self, node: LifecycleComponentNode) -> None:
        recorder: list[tuple[str, str]] = []
        a = RecordingComponent("a", recorder)
        b = RecordingComponent("b", recorder)
        node.add_component(a)
        node.add_component(b, dependencies=("a",))
        node.on_configure(DUMMY_STATE)
        configure_order = [name for name, hook in recorder if hook == "configure"]
        assert configure_order == ["a", "b"]

    def test_dependencies_at_registration_site_activate_order(self, node: LifecycleComponentNode) -> None:
        recorder: list[tuple[str, str]] = []
        a = RecordingComponent("a", recorder)
        b = RecordingComponent("b", recorder)
        node.add_component(a)
        node.add_component(b, dependencies=("a",))
        node.on_configure(DUMMY_STATE)
        recorder.clear()
        node.on_activate(DUMMY_STATE)
        activate_order = [name for name, hook in recorder if hook == "activate"]
        assert activate_order == ["a", "b"]

    def test_dependencies_at_registration_site_reverse_on_deactivate(self, node: LifecycleComponentNode) -> None:
        recorder: list[tuple[str, str]] = []
        a = RecordingComponent("a", recorder)
        b = RecordingComponent("b", recorder)
        node.add_component(a)
        node.add_component(b, dependencies=("a",))
        node.on_configure(DUMMY_STATE)
        node.on_activate(DUMMY_STATE)
        recorder.clear()
        node.on_deactivate(DUMMY_STATE)
        deactivate_order = [name for name, hook in recorder if hook == "deactivate"]
        assert deactivate_order == ["b", "a"]

    # -- priority declared at registration site --------------------------

    def test_priority_at_registration_site_breaks_ties(self, node: LifecycleComponentNode) -> None:
        recorder: list[tuple[str, str]] = []
        low = RecordingComponent("low", recorder)
        high = RecordingComponent("high", recorder)
        node.add_component(low, priority=1)
        node.add_component(high, priority=5)
        node.on_configure(DUMMY_STATE)
        configure_order = [name for name, hook in recorder if hook == "configure"]
        assert configure_order == ["high", "low"]

    # -- ordering equivalence: registration-site == constructor ----------

    def test_ordering_equivalent_to_constructor_declaration(self, node: LifecycleComponentNode) -> None:
        """Registration-site dependencies produce the same resolved order as constructor."""
        recorder_reg: list[tuple[str, str]] = []
        a_reg = RecordingComponent("a", recorder_reg)
        b_reg = RecordingComponent("b", recorder_reg)
        node.add_component(a_reg)
        node.add_component(b_reg, dependencies=("a",))
        node.on_configure(DUMMY_STATE)
        reg_order = [name for name, hook in recorder_reg if hook == "configure"]

        node2 = LifecycleComponentNode("test_regsite_equiv_node")
        recorder_ctor: list[tuple[str, str]] = []
        a_ctor = RecordingComponent("a", recorder_ctor)
        b_ctor = RecordingComponent("b", recorder_ctor, dependencies=("a",))
        node2.add_component(a_ctor)
        node2.add_component(b_ctor)
        node2.on_configure(DUMMY_STATE)
        ctor_order = [name for name, hook in recorder_ctor if hook == "configure"]
        node2.destroy_node()

        assert reg_order == ctor_order

    # -- TypeError on explicit conflict ----------------------------------

    def test_conflict_dependencies_raises_type_error(self, node: LifecycleComponentNode) -> None:
        comp = RecordingComponent("c", [], dependencies=("x",))
        with pytest.raises(TypeError, match="provide the value in one place only"):
            node.add_component(comp, dependencies=("y",))

    def test_conflict_priority_raises_type_error(self, node: LifecycleComponentNode) -> None:
        comp = RecordingComponent("c", [], priority=3)
        with pytest.raises(TypeError, match="provide the value in one place only"):
            node.add_component(comp, priority=7)

    # -- no conflict when constructor uses defaults ----------------------

    def test_no_conflict_when_constructor_default_dependencies(self, node: LifecycleComponentNode) -> None:
        """Registration-site metadata applies cleanly when constructor uses default."""
        dep = RecordingComponent("dep", [])
        comp = RecordingComponent("c", [])
        node.add_component(dep)
        node.add_component(comp, dependencies=("dep",))  # no TypeError expected

    def test_no_conflict_when_constructor_default_priority(self, node: LifecycleComponentNode) -> None:
        """Registration-site priority applies cleanly when constructor uses default."""
        comp = RecordingComponent("c", [])
        node.add_component(comp, priority=10)  # no TypeError expected
