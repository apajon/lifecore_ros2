from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.core import LifecycleComponent

HookName = Literal["configure", "activate", "deactivate", "cleanup", "shutdown", "error"]

TEST_STATE = LifecycleState(state_id=0, label="test")
_HOOK_NAMES: tuple[HookName, ...] = ("configure", "activate", "deactivate", "cleanup", "shutdown", "error")
_HOOK_ALIASES: dict[str, HookName] = {
    "configure": "configure",
    "_on_configure": "configure",
    "activate": "activate",
    "_on_activate": "activate",
    "deactivate": "deactivate",
    "_on_deactivate": "deactivate",
    "cleanup": "cleanup",
    "_on_cleanup": "cleanup",
    "shutdown": "shutdown",
    "_on_shutdown": "shutdown",
    "error": "error",
    "_on_error": "error",
}


def _normalize_hook_name(hook_name: str) -> HookName:
    try:
        return _HOOK_ALIASES[hook_name]
    except KeyError as exc:
        expected = ", ".join(_HOOK_NAMES)
        raise ValueError(f"Unknown lifecycle hook '{hook_name}', expected one of: {expected}") from exc


class FakeLifecycleComponent(LifecycleComponent):
    """Private lifecycle fake for component transition tests."""

    def __init__(
        self,
        name: str = "fake_lifecycle_component",
        *,
        fail_on: str | None = None,
        raise_on: str | None = None,
        exception: Exception | None = None,
        failure_return: TransitionCallbackReturn = TransitionCallbackReturn.FAILURE,
    ) -> None:
        super().__init__(name=name)
        self.hook_calls: list[HookName] = []
        self.states: dict[HookName, list[LifecycleState]] = {hook_name: [] for hook_name in _HOOK_NAMES}
        self._fail_on = _normalize_hook_name(fail_on) if fail_on is not None else None
        self._raise_on = _normalize_hook_name(raise_on) if raise_on is not None else None
        self._exception = exception if exception is not None else RuntimeError("configured lifecycle exception")
        self._failure_return = failure_return

    @property
    def hook_order(self) -> list[HookName]:
        return list(self.hook_calls)

    @property
    def contract_state(self) -> str:
        return self._contract_state()  # pyright: ignore[reportPrivateUsage]

    def _record(self, hook_name: HookName, state: LifecycleState) -> TransitionCallbackReturn:
        self.hook_calls.append(hook_name)
        self.states[hook_name].append(state)
        if self._raise_on == hook_name:
            raise self._exception
        if self._fail_on == hook_name:
            return self._failure_return
        return TransitionCallbackReturn.SUCCESS

    def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._record("configure", state)

    def _on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._record("activate", state)

    def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._record("deactivate", state)

    def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._record("cleanup", state)

    def _on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._record("shutdown", state)

    def _on_error(self, state: LifecycleState) -> TransitionCallbackReturn:
        return self._record("error", state)


def assert_transition_result(
    component: FakeLifecycleComponent,
    transition: str,
    actual: TransitionCallbackReturn,
    expected: TransitionCallbackReturn,
) -> None:
    hook_name = _normalize_hook_name(transition)
    if actual == expected:
        return
    raise AssertionError(
        f"Expected component '{component.name}' {hook_name} transition to return {expected.name}; "
        f"got {actual.name}. Hook order: {component.hook_order}. Contract state: {component.contract_state}."
    )


def assert_transition_success(
    component: FakeLifecycleComponent,
    transition: str,
    actual: TransitionCallbackReturn,
) -> None:
    assert_transition_result(component, transition, actual, TransitionCallbackReturn.SUCCESS)


def assert_hook_order(component: FakeLifecycleComponent, expected_order: Sequence[str]) -> None:
    expected_hooks = [_normalize_hook_name(hook_name) for hook_name in expected_order]
    actual_hooks = component.hook_order
    if actual_hooks == expected_hooks:
        return
    raise AssertionError(
        f"Expected component '{component.name}' hook order {expected_hooks}; "
        f"got {actual_hooks}. Contract state: {component.contract_state}."
    )


def assert_contract_state(component: FakeLifecycleComponent, expected_state: str) -> None:
    actual_state = component.contract_state
    if actual_state == expected_state:
        return
    raise AssertionError(
        f"Expected component '{component.name}' contract state '{expected_state}'; "
        f"got '{actual_state}'. Hook order: {component.hook_order}."
    )


def assert_component_active(component: FakeLifecycleComponent) -> None:
    assert_contract_state(component, "active")


def assert_component_inactive(component: FakeLifecycleComponent) -> None:
    assert_contract_state(component, "inactive")
