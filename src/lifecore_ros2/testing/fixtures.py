from __future__ import annotations

from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Any, cast

try:
    import pytest
except ModuleNotFoundError:
    pytest = None  # type: ignore[assignment]

from lifecore_ros2.core import LifecycleComponentNode

from .fakes import (
    FakeClientComponent,
    FakeComponent,
    FakePublisherComponent,
    FakeServiceComponent,
    FakeSubscriberComponent,
    FakeTimerComponent,
)


def _pytest_fixture[FixtureT: Callable[..., Any]](function: FixtureT) -> FixtureT:
    if pytest is None:
        return function
    return cast(FixtureT, pytest.fixture()(function))


@dataclass(slots=True)
class NodeWithComponents:
    """Fixture value containing a node preloaded with standard fake components."""

    node: LifecycleComponentNode
    component: FakeComponent
    publisher: FakePublisherComponent
    subscriber: FakeSubscriberComponent
    timer: FakeTimerComponent
    service: FakeServiceComponent
    client: FakeClientComponent


@_pytest_fixture
def lifecycle_node_fixture() -> Generator[LifecycleComponentNode, None, None]:
    """Create a ``LifecycleComponentNode`` and destroy it after the test."""
    node = LifecycleComponentNode("lifecore_test_node")
    yield node
    node.destroy_node()


@_pytest_fixture
def node_with_components(lifecycle_node_fixture: LifecycleComponentNode) -> NodeWithComponents:
    """Create a node with one standard fake component of each supported kind."""
    components = NodeWithComponents(
        node=lifecycle_node_fixture,
        component=FakeComponent(),
        publisher=FakePublisherComponent(),
        subscriber=FakeSubscriberComponent(),
        timer=FakeTimerComponent(),
        service=FakeServiceComponent(),
        client=FakeClientComponent(),
    )
    lifecycle_node_fixture.add_components(
        (
            components.component,
            components.publisher,
            components.subscriber,
            components.timer,
            components.service,
            components.client,
        )
    )
    return components
