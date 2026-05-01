"""Reusable test utilities for lifecycle-driven applications."""

from .assertions import assert_activation_gated, assert_component_state, assert_transition_order
from .concurrency import TransitionThreadResult, assert_no_race, barrier_hook, spawn_transition_thread
from .fakes import (
    DUMMY_STATE,
    FailingComponent,
    FakeClientComponent,
    FakeComponent,
    FakePublisherComponent,
    FakeServiceComponent,
    FakeSubscriberComponent,
    FakeTimerComponent,
)
from .fixtures import NodeWithComponents, lifecycle_node_fixture, node_with_components
from .helpers import activate_component, collect_logs, deactivate_component, expect_log

__all__ = [
    "DUMMY_STATE",
    "FakeComponent",
    "FailingComponent",
    "FakePublisherComponent",
    "FakeSubscriberComponent",
    "FakeTimerComponent",
    "FakeServiceComponent",
    "FakeClientComponent",
    "NodeWithComponents",
    "TransitionThreadResult",
    "lifecycle_node_fixture",
    "node_with_components",
    "assert_component_state",
    "assert_transition_order",
    "assert_activation_gated",
    "activate_component",
    "deactivate_component",
    "collect_logs",
    "expect_log",
    "spawn_transition_thread",
    "assert_no_race",
    "barrier_hook",
]
