from __future__ import annotations

import pytest
from rclpy.lifecycle import TransitionCallbackReturn

from tests.helpers.lifecycle import (
    TEST_STATE,
    FakeLifecycleComponent,
    assert_component_active,
    assert_component_inactive,
    assert_contract_state,
    assert_hook_order,
    assert_transition_result,
    assert_transition_success,
)


class TestFakeLifecycleComponent:
    def test_records_successful_hook_order(self) -> None:
        component = FakeLifecycleComponent("ordered")

        assert_transition_success(component, "configure", component.on_configure(TEST_STATE))
        assert_transition_success(component, "activate", component.on_activate(TEST_STATE))
        assert_transition_success(component, "deactivate", component.on_deactivate(TEST_STATE))
        assert_transition_success(component, "cleanup", component.on_cleanup(TEST_STATE))
        assert_transition_success(component, "shutdown", component.on_shutdown(TEST_STATE))
        assert_transition_success(component, "error", component.on_error(TEST_STATE))

        assert_hook_order(component, ["configure", "activate", "deactivate", "cleanup", "shutdown", "error"])
        assert component.states["configure"] == [TEST_STATE]

    def test_returns_configured_failure(self) -> None:
        component = FakeLifecycleComponent("fail_activate", fail_on="activate")

        assert_transition_success(component, "configure", component.on_configure(TEST_STATE))
        result = component.on_activate(TEST_STATE)

        assert_transition_result(component, "activate", result, TransitionCallbackReturn.FAILURE)
        assert_hook_order(component, ["configure", "activate"])
        assert_contract_state(component, "inactive")

    def test_returns_error_when_hook_raises(self) -> None:
        component = FakeLifecycleComponent("raise_configure", raise_on="configure", exception=RuntimeError("boom"))

        result = component.on_configure(TEST_STATE)

        assert_transition_result(component, "configure", result, TransitionCallbackReturn.ERROR)
        assert_hook_order(component, ["configure"])
        assert_contract_state(component, "partially_configured")

    def test_accepts_protected_hook_names_for_failure_injection(self) -> None:
        component = FakeLifecycleComponent("protected_name", fail_on="_on_configure")

        result = component.on_configure(TEST_STATE)

        assert_transition_result(component, "configure", result, TransitionCallbackReturn.FAILURE)


class TestLifecycleAssertionMessages:
    def test_transition_result_message_names_component_transition_and_state(self) -> None:
        component = FakeLifecycleComponent("diagnostic")
        component.on_configure(TEST_STATE)

        with pytest.raises(AssertionError) as error:
            assert_transition_success(component, "activate", TransitionCallbackReturn.FAILURE)

        message = str(error.value)
        assert "Expected component 'diagnostic' activate transition to return SUCCESS; got FAILURE." in message
        assert "Hook order: ['configure']" in message
        assert "Contract state: inactive" in message

    def test_hook_order_message_includes_expected_and_actual_order(self) -> None:
        component = FakeLifecycleComponent("diagnostic")
        component.on_configure(TEST_STATE)
        component.on_activate(TEST_STATE)

        with pytest.raises(AssertionError) as error:
            assert_hook_order(component, ["configure", "cleanup"])

        message = str(error.value)
        assert "Expected component 'diagnostic' hook order ['configure', 'cleanup']" in message
        assert "got ['configure', 'activate']" in message
        assert "Contract state: active" in message

    def test_contract_state_message_includes_hook_order(self) -> None:
        component = FakeLifecycleComponent("diagnostic")
        component.on_configure(TEST_STATE)

        with pytest.raises(AssertionError) as error:
            assert_component_active(component)

        message = str(error.value)
        assert "Expected component 'diagnostic' contract state 'active'; got 'inactive'." in message
        assert "Hook order: ['configure']" in message

    def test_activation_helpers_accept_expected_states(self) -> None:
        component = FakeLifecycleComponent("diagnostic")
        component.on_configure(TEST_STATE)
        assert_component_inactive(component)

        component.on_activate(TEST_STATE)
        assert_component_active(component)
