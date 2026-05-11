from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult
from rclpy.callback_groups import CallbackGroup
from rclpy.lifecycle.node import LifecycleState, TransitionCallbackReturn
from rclpy.parameter import Parameter

from lifecore_ros2.core.exceptions import ComponentNotConfiguredError
from lifecore_ros2.core.lifecycle_component import LifecycleComponent


class ParameterMutability(Enum):
    """Runtime mutability model for component-owned parameters."""

    STATIC = "static"
    ACTIVE = "active"


@dataclass(frozen=True)
class LifecycleParameter:
    """Definition of a parameter owned by a lifecycle component.

    Definitions are structural component metadata. They can be registered before
    configure and are preserved across cleanup. The actual ROS 2 parameter
    declaration happens during configure.
    """

    name: str
    default_value: Any
    mutability: ParameterMutability = ParameterMutability.STATIC
    description: str | None = None


_PreSetCallback = Callable[[list[Parameter]], list[Parameter]]
_OnSetCallback = Callable[[list[Parameter]], SetParametersResult]
_PostSetCallback = Callable[[list[Parameter]], None]


class LifecycleParameterComponent(LifecycleComponent):
    """Lifecycle-aware owner for local ROS 2 parameters on the parent node.

    The component owns only parameters registered through
    ``declare_lifecycle_parameter``. Parameter definitions are preserved across
    cleanup, while runtime values, configured ownership tracking, and callback
    registration are lifecycle state.

    Runtime writes are accepted only while the component is active. Static
    parameters reject all runtime writes. Parameters not owned by this component
    are ignored so multiple parameter components can attach callbacks to the
    same node safely.
    """

    def __init__(
        self,
        name: str,
        *,
        callback_group: CallbackGroup | None = None,
        dependencies: Sequence[str] = (),
        priority: int = 0,
    ) -> None:
        """Initialize the parameter component.

        Args:
            name: Unique component name within the parent node. Owned ROS 2
                parameter names are scoped as ``<name>.<parameter_name>``.
            callback_group: Optional callback group forwarded to
                ``LifecycleComponent`` for consistency with other components.
            dependencies: Names of components that must transition before this one.
            priority: Tie-breaking ordering hint.
        """
        super().__init__(name=name, callback_group=callback_group, dependencies=dependencies, priority=priority)
        self._parameter_definitions: dict[str, LifecycleParameter] = {}
        self._parameter_values: dict[str, Any] = {}
        self._configured_parameters: dict[str, LifecycleParameter] = {}
        self._pre_set_callback: _PreSetCallback | None = None
        self._on_set_callback: _OnSetCallback | None = None
        self._post_set_callback: _PostSetCallback | None = None

    def declare_lifecycle_parameter(
        self,
        name: str,
        default_value: Any,
        *,
        mutability: ParameterMutability = ParameterMutability.STATIC,
        description: str | None = None,
    ) -> None:
        """Register a component-owned parameter definition.

        Calling this before configure records local component metadata. The ROS 2
        parameter is declared on the parent node during configure.

        Args:
            name: Local parameter name, without the component prefix.
            default_value: Default value used when the ROS 2 parameter is absent.
            mutability: Runtime mutability policy.
            description: Optional ROS 2 parameter description.

        Raises:
            ValueError: If ``name`` is empty or already registered.
            RuntimeError: If called while the component has configured runtime state.
        """
        if not name:
            raise ValueError("Parameter name must not be empty")
        if name in self._parameter_definitions:
            raise ValueError(f"Parameter '{name}' is already registered by component '{self.name}'")
        if self._configured_parameters:
            raise RuntimeError(
                f"Component '{self.name}' cannot register parameter '{name}' while configured; "
                "register definitions before configure"
            )
        self._parameter_definitions[name] = LifecycleParameter(
            name=name,
            default_value=default_value,
            mutability=mutability,
            description=description,
        )

    def has_parameter(self, name: str) -> bool:
        """Return whether this component has a registered definition for ``name``."""
        return name in self._parameter_definitions

    def get_parameter_value(self, name: str) -> Any:
        """Return the tracked value for a configured owned parameter.

        Raises:
            KeyError: If ``name`` is not registered by this component.
            ComponentNotConfiguredError: If the component has no configured value
                for the registered parameter.
        """
        if name not in self._parameter_definitions:
            raise KeyError(f"Unknown parameter '{name}' for component '{self.name}'")
        if name not in self._parameter_values:
            raise ComponentNotConfiguredError(f"Parameter '{name}' for component '{self.name}' is not configured")
        return self._parameter_values[name]

    def on_pre_set_owned_parameters(self, parameters: list[Parameter]) -> list[Parameter]:
        """Hook for transforming active owned parameter updates before validation."""
        return parameters

    def on_validate_owned_parameters(self, parameters: list[Parameter]) -> SetParametersResult:
        """Validate active owned parameter updates.

        This batch hook is authoritative. The default implementation delegates
        each owned parameter to ``validate_parameter_update``.
        """
        for parameter in parameters:
            local_name = self._local_parameter_name(parameter.name)
            old_value = self._parameter_values[local_name]
            reason = self.validate_parameter_update(local_name, old_value, parameter.value)
            if reason is not None:
                return SetParametersResult(successful=False, reason=reason)
        return SetParametersResult(successful=True, reason="")

    def validate_parameter_update(self, name: str, old_value: Any, new_value: Any) -> str | None:
        """Validate one active parameter update.

        Returns ``None`` to accept the update. Return a string to reject it with
        that reason. Override this for simple per-parameter validation; override
        ``on_validate_owned_parameters`` for advanced batch validation.
        """
        return None

    def on_post_set_owned_parameters(self, parameters: list[Parameter]) -> None:
        """Hook called after successful active owned parameter updates."""

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Declare and read owned ROS 2 parameters on the parent node."""
        self._configured_parameters.clear()
        self._parameter_values.clear()
        for definition in self._parameter_definitions.values():
            scoped_name = self._scoped_parameter_name(definition.name)
            value = self._declare_or_read_parameter(definition, scoped_name)
            self._assert_compatible_value(definition, value)
            self._configured_parameters[scoped_name] = definition
            self._parameter_values[definition.name] = value
        self._register_parameter_callbacks()
        return TransitionCallbackReturn.SUCCESS

    def _release_resources(self) -> None:
        """Clear runtime parameter tracking and remove callbacks when possible."""
        self._remove_parameter_callbacks()
        self._parameter_values.clear()
        self._configured_parameters.clear()
        super()._release_resources()

    def _declare_or_read_parameter(self, definition: LifecycleParameter, scoped_name: str) -> Any:
        if self.node.has_parameter(scoped_name):
            parameter = self.node.get_parameter(scoped_name)
            self.node.get_logger().info(
                f"[{self.name}] using existing parameter '{scoped_name}' owned by this component"
            )
            return parameter.value

        descriptor = ParameterDescriptor(description=definition.description or "")
        parameter = self.node.declare_parameter(scoped_name, definition.default_value, descriptor)
        return parameter.value

    def _assert_compatible_value(self, definition: LifecycleParameter, value: Any) -> None:
        expected_type = Parameter.Type.from_parameter_value(definition.default_value)
        actual_type = Parameter.Type.from_parameter_value(value)
        if actual_type != expected_type:
            raise TypeError(
                f"Parameter '{self._scoped_parameter_name(definition.name)}' for component '{self.name}' "
                f"has incompatible type {actual_type.name}; expected {expected_type.name}"
            )

    def _register_parameter_callbacks(self) -> None:
        self._pre_set_callback = self._on_ros_pre_set_parameters
        self._on_set_callback = self._on_ros_validate_parameters
        self._post_set_callback = self._on_ros_post_set_parameters
        self.node.add_pre_set_parameters_callback(self._pre_set_callback)
        self.node.add_on_set_parameters_callback(self._on_set_callback)
        self.node.add_post_set_parameters_callback(self._post_set_callback)

    def _remove_parameter_callbacks(self) -> None:
        if self._pre_set_callback is not None:
            self.node.remove_pre_set_parameters_callback(self._pre_set_callback)
            self._pre_set_callback = None
        if self._on_set_callback is not None:
            self.node.remove_on_set_parameters_callback(self._on_set_callback)
            self._on_set_callback = None
        if self._post_set_callback is not None:
            self.node.remove_post_set_parameters_callback(self._post_set_callback)
            self._post_set_callback = None

    def _on_ros_pre_set_parameters(self, parameters: list[Parameter]) -> list[Parameter]:
        owned_parameters = self._owned_parameters(parameters)
        if not owned_parameters or not self.is_active:
            return parameters
        transformed_owned = self.on_pre_set_owned_parameters(owned_parameters)
        unowned_parameters = [parameter for parameter in parameters if not self._owns_scoped_parameter(parameter.name)]
        return [*unowned_parameters, *transformed_owned]

    def _on_ros_validate_parameters(self, parameters: list[Parameter]) -> SetParametersResult:
        owned_parameters = self._owned_parameters(parameters)
        if not owned_parameters:
            return SetParametersResult(successful=True, reason="")
        if not self.is_active:
            return SetParametersResult(
                successful=False,
                reason=f"Component '{self.name}' is not active; owned parameters are read-only while inactive",
            )
        for parameter in owned_parameters:
            definition = self._configured_parameters[parameter.name]
            expected_type = Parameter.Type.from_parameter_value(definition.default_value)
            actual_type = Parameter.Type.from_parameter_value(parameter.value)
            if actual_type != expected_type:
                return SetParametersResult(
                    successful=False,
                    reason=(
                        f"Parameter '{parameter.name}' has incompatible type {actual_type.name}; "
                        f"expected {expected_type.name}"
                    ),
                )
            if definition.mutability == ParameterMutability.STATIC:
                return SetParametersResult(
                    successful=False,
                    reason=f"Parameter '{parameter.name}' is static and cannot be changed at runtime",
                )
        return self.on_validate_owned_parameters(owned_parameters)

    def _on_ros_post_set_parameters(self, parameters: list[Parameter]) -> None:
        owned_parameters = self._owned_parameters(parameters)
        if not owned_parameters or not self.is_active:
            return
        for parameter in owned_parameters:
            self._parameter_values[self._local_parameter_name(parameter.name)] = parameter.value
        self.on_post_set_owned_parameters(owned_parameters)

    def _owned_parameters(self, parameters: list[Parameter]) -> list[Parameter]:
        return [parameter for parameter in parameters if self._owns_scoped_parameter(parameter.name)]

    def _owns_scoped_parameter(self, scoped_name: str) -> bool:
        return scoped_name in self._configured_parameters

    def _scoped_parameter_name(self, name: str) -> str:
        return f"{self.name}.{name}"

    def _local_parameter_name(self, scoped_name: str) -> str:
        prefix = f"{self.name}."
        if not scoped_name.startswith(prefix):
            raise KeyError(f"Parameter '{scoped_name}' is not owned by component '{self.name}'")
        return scoped_name.removeprefix(prefix)
