from __future__ import annotations

from typing import Any

import pytest
from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.parameter import Parameter

from lifecore_ros2.components import LifecycleParameterComponent, ParameterMutability
from lifecore_ros2.core import ComponentNotConfiguredError, LifecycleComponentNode
from lifecore_ros2.testing import DUMMY_STATE


def _set_parameter(node: LifecycleComponentNode, name: str, value: Any) -> bool:
    result = node.set_parameters([Parameter(name, value=value)])
    assert len(result) == 1
    return result[0].successful


class TestLifecycleParameterComponent:
    def test_configure_declares_and_reads_registered_parameter(self, node: LifecycleComponentNode) -> None:
        component = LifecycleParameterComponent("params")
        component.declare_lifecycle_parameter("gain", 1, mutability=ParameterMutability.ACTIVE)
        node.add_component(component)

        with pytest.raises(ComponentNotConfiguredError):
            component.get_parameter_value("gain")

        result = component.on_configure(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        assert node.has_parameter("params.gain")
        assert component.has_parameter("gain")
        assert component.get_parameter_value("gain") == 1

    def test_register_duplicate_parameter_fails_clearly(self) -> None:
        component = LifecycleParameterComponent("params")
        component.declare_lifecycle_parameter("gain", 1)

        with pytest.raises(ValueError, match="already registered"):
            component.declare_lifecycle_parameter("gain", 2)

    def test_cleanup_preserves_definitions_and_clears_runtime_values(self, node: LifecycleComponentNode) -> None:
        component = LifecycleParameterComponent("params")
        component.declare_lifecycle_parameter("gain", 1)
        node.add_component(component)
        component.on_configure(DUMMY_STATE)

        component.on_cleanup(DUMMY_STATE)

        assert component.has_parameter("gain")
        with pytest.raises(ComponentNotConfiguredError):
            component.get_parameter_value("gain")

        result = component.on_configure(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        assert component.get_parameter_value("gain") == 1

    def test_configure_reads_existing_compatible_parameter(self, node: LifecycleComponentNode) -> None:
        node.declare_parameter("params.gain", 2)
        component = LifecycleParameterComponent("params")
        component.declare_lifecycle_parameter("gain", 1)
        node.add_component(component)

        result = component.on_configure(DUMMY_STATE)

        assert result == TransitionCallbackReturn.SUCCESS
        assert component.get_parameter_value("gain") == 2

    def test_configure_rejects_existing_incompatible_parameter(self, node: LifecycleComponentNode) -> None:
        node.declare_parameter("params.gain", "fast")
        component = LifecycleParameterComponent("params")
        component.declare_lifecycle_parameter("gain", 1)
        node.add_component(component)

        result = component.on_configure(DUMMY_STATE)

        assert result == TransitionCallbackReturn.ERROR

    def test_inactive_runtime_write_to_owned_parameter_is_rejected(self, node: LifecycleComponentNode) -> None:
        component = LifecycleParameterComponent("params")
        component.declare_lifecycle_parameter("gain", 1, mutability=ParameterMutability.ACTIVE)
        node.add_component(component)
        component.on_configure(DUMMY_STATE)

        assert not _set_parameter(node, "params.gain", 2)
        assert component.get_parameter_value("gain") == 1

    def test_active_runtime_write_updates_tracked_value(self, node: LifecycleComponentNode) -> None:
        component = LifecycleParameterComponent("params")
        component.declare_lifecycle_parameter("gain", 1, mutability=ParameterMutability.ACTIVE)
        node.add_component(component)
        component.on_configure(DUMMY_STATE)
        component.on_activate(DUMMY_STATE)

        assert _set_parameter(node, "params.gain", 2)
        assert component.get_parameter_value("gain") == 2

    def test_static_parameter_rejects_runtime_write_even_when_active(self, node: LifecycleComponentNode) -> None:
        component = LifecycleParameterComponent("params")
        component.declare_lifecycle_parameter("mode", "auto")
        node.add_component(component)
        component.on_configure(DUMMY_STATE)
        component.on_activate(DUMMY_STATE)

        assert not _set_parameter(node, "params.mode", "manual")
        assert component.get_parameter_value("mode") == "auto"

    def test_validation_hook_rejects_invalid_active_update(self, node: LifecycleComponentNode) -> None:
        class PositiveParameters(LifecycleParameterComponent):
            def validate_parameter_update(self, name: str, old_value: Any, new_value: Any) -> str | None:
                if name == "gain" and new_value <= 0:
                    return "gain must be positive"
                return None

        component = PositiveParameters("params")
        component.declare_lifecycle_parameter("gain", 1, mutability=ParameterMutability.ACTIVE)
        node.add_component(component)
        component.on_configure(DUMMY_STATE)
        component.on_activate(DUMMY_STATE)

        assert not _set_parameter(node, "params.gain", 0)
        assert component.get_parameter_value("gain") == 1

    def test_post_set_hook_runs_only_after_successful_active_update(self, node: LifecycleComponentNode) -> None:
        class RecordingParameters(LifecycleParameterComponent):
            def __init__(self) -> None:
                super().__init__("params")
                self.post_set_names: list[str] = []

            def validate_parameter_update(self, name: str, old_value: Any, new_value: Any) -> str | None:
                if new_value == 0:
                    return "zero rejected"
                return None

            def on_post_set_owned_parameters(self, parameters: list[Parameter]) -> None:
                self.post_set_names.extend(parameter.name for parameter in parameters)

        component = RecordingParameters()
        component.declare_lifecycle_parameter("gain", 1, mutability=ParameterMutability.ACTIVE)
        node.add_component(component)
        component.on_configure(DUMMY_STATE)
        component.on_activate(DUMMY_STATE)

        assert not _set_parameter(node, "params.gain", 0)
        assert component.post_set_names == []

        assert _set_parameter(node, "params.gain", 2)
        assert component.post_set_names == ["params.gain"]

    def test_unowned_parameter_update_is_ignored_while_component_inactive(self, node: LifecycleComponentNode) -> None:
        component = LifecycleParameterComponent("params")
        component.declare_lifecycle_parameter("gain", 1, mutability=ParameterMutability.ACTIVE)
        node.add_component(component)
        component.on_configure(DUMMY_STATE)
        node.declare_parameter("other.gain", 1)

        assert _set_parameter(node, "other.gain", 2)
        assert component.get_parameter_value("gain") == 1

    def test_inactive_component_does_not_block_another_component_parameter(self, node: LifecycleComponentNode) -> None:
        active_component = LifecycleParameterComponent("active_params")
        active_component.declare_lifecycle_parameter("gain", 1, mutability=ParameterMutability.ACTIVE)
        inactive_component = LifecycleParameterComponent("inactive_params")
        inactive_component.declare_lifecycle_parameter("gain", 10, mutability=ParameterMutability.ACTIVE)
        node.add_component(active_component)
        node.add_component(inactive_component)
        active_component.on_configure(DUMMY_STATE)
        inactive_component.on_configure(DUMMY_STATE)
        active_component.on_activate(DUMMY_STATE)

        assert _set_parameter(node, "active_params.gain", 2)
        assert active_component.get_parameter_value("gain") == 2
        assert inactive_component.get_parameter_value("gain") == 10
