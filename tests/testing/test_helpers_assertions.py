from __future__ import annotations

import logging

import pytest

from lifecore_ros2.testing import (
    DUMMY_STATE,
    FakeComponent,
    FakePublisherComponent,
    activate_component,
    assert_activation_gated,
    assert_component_state,
    assert_transition_order,
    collect_logs,
    deactivate_component,
    expect_log,
)


def test_activate_component_configures_and_activates(lifecycle_node_fixture) -> None:
    component = FakeComponent("component_a")
    lifecycle_node_fixture.add_component(component)

    returned = activate_component(lifecycle_node_fixture, "component_a")

    assert returned is component
    assert component.calls == ["configure", "activate"]
    assert_component_state(lifecycle_node_fixture, "component_a", "active")


def test_deactivate_component_deactivates_and_cleans_up(lifecycle_node_fixture) -> None:
    component = FakeComponent("component_a")
    lifecycle_node_fixture.add_component(component)
    activate_component(lifecycle_node_fixture, "component_a")

    returned = deactivate_component(lifecycle_node_fixture, "component_a")

    assert returned is component
    assert component.calls == ["configure", "activate", "deactivate", "cleanup"]
    assert_component_state(lifecycle_node_fixture, "component_a", "unconfigured")


def test_assert_transition_order_accepts_component() -> None:
    component = FakeComponent()

    component.on_configure(DUMMY_STATE)

    assert_transition_order(component, ["configure"])


def test_assert_transition_order_raises_on_mismatch() -> None:
    component = FakeComponent()

    component.on_configure(DUMMY_STATE)

    with pytest.raises(AssertionError, match="Expected transition order"):
        assert_transition_order(component, ["activate"])


def test_assert_activation_gated_accepts_fake_publisher() -> None:
    assert_activation_gated(FakePublisherComponent())


def test_collect_logs_and_expect_log() -> None:
    logger = logging.getLogger("lifecore_ros2.testing.tests")

    logs = collect_logs(logger, lambda: logger.warning("component failed during configure"))

    assert expect_log(logs, "failed during configure") == "component failed during configure"


def test_expect_log_raises_when_pattern_is_missing() -> None:
    with pytest.raises(AssertionError, match="No log message matched"):
        expect_log(["configure ok"], "activate failed")
