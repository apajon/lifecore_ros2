"""Tests for LifecycleComponentNode.get_or_create_callback_group.

Covers:
  - Default type is MutuallyExclusiveCallbackGroup.
  - Idempotency: same name and compatible type returns the same instance.
  - Different names produce distinct instances.
  - Type conflict raises TypeError.
  - None (default) then explicit same type is idempotent.
  - None (default) then explicit different type raises TypeError.
  - Thread-safe: concurrent calls for different names do not corrupt the registry.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator

import pytest
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup

from lifecore_ros2.core import LifecycleComponentNode


@pytest.fixture()
def node() -> Iterator[LifecycleComponentNode]:
    n = LifecycleComponentNode("callback_group_test_node")
    yield n
    n.destroy_node()


class TestGetOrCreateCallbackGroup:
    """Callback group helper — idempotency, defaults, and error cases."""

    def test_default_type_is_mutually_exclusive(self, node: LifecycleComponentNode) -> None:
        group = node.get_or_create_callback_group("cam")
        assert isinstance(group, MutuallyExclusiveCallbackGroup)

    def test_idempotent_same_name_no_type(self, node: LifecycleComponentNode) -> None:
        group_a = node.get_or_create_callback_group("cam")
        group_b = node.get_or_create_callback_group("cam")
        assert group_a is group_b

    def test_idempotent_same_name_explicit_mutually_exclusive(self, node: LifecycleComponentNode) -> None:
        group_a = node.get_or_create_callback_group("lidar", MutuallyExclusiveCallbackGroup)
        group_b = node.get_or_create_callback_group("lidar", MutuallyExclusiveCallbackGroup)
        assert group_a is group_b

    def test_idempotent_same_name_explicit_reentrant(self, node: LifecycleComponentNode) -> None:
        group_a = node.get_or_create_callback_group("imu", ReentrantCallbackGroup)
        group_b = node.get_or_create_callback_group("imu", ReentrantCallbackGroup)
        assert group_a is group_b

    def test_different_names_distinct_groups(self, node: LifecycleComponentNode) -> None:
        group_a = node.get_or_create_callback_group("sensor_a")
        group_b = node.get_or_create_callback_group("sensor_b")
        assert group_a is not group_b

    def test_type_conflict_raises_type_error(self, node: LifecycleComponentNode) -> None:
        node.get_or_create_callback_group("cam", MutuallyExclusiveCallbackGroup)
        with pytest.raises(TypeError, match="cam"):
            node.get_or_create_callback_group("cam", ReentrantCallbackGroup)

    def test_default_then_explicit_same_type_is_idempotent(self, node: LifecycleComponentNode) -> None:
        # None defaults to MutuallyExclusiveCallbackGroup; requesting the same explicit type
        # must return the same instance.
        group_a = node.get_or_create_callback_group("cam")
        group_b = node.get_or_create_callback_group("cam", MutuallyExclusiveCallbackGroup)
        assert group_a is group_b

    def test_default_then_explicit_different_type_raises(self, node: LifecycleComponentNode) -> None:
        node.get_or_create_callback_group("cam")
        with pytest.raises(TypeError, match="cam"):
            node.get_or_create_callback_group("cam", ReentrantCallbackGroup)

    def test_thread_safe_concurrent_different_names(self, node: LifecycleComponentNode) -> None:
        # Regression: without _lock, concurrent inserts could corrupt the registry.
        # Expected: both groups are created exactly once, no errors.
        barrier = threading.Barrier(2, timeout=5.0)
        errors: list[Exception] = []
        results: list[object] = []

        def create(name: str) -> None:
            try:
                barrier.wait()
                results.append(node.get_or_create_callback_group(name))
            except Exception as exc:
                errors.append(exc)

        t1 = threading.Thread(target=create, args=("thread_a",))
        t2 = threading.Thread(target=create, args=("thread_b",))
        t1.start()
        t2.start()
        t1.join(timeout=5.0)
        t2.join(timeout=5.0)

        assert not errors, f"Unexpected errors: {errors}"
        assert len(results) == 2
        assert results[0] is not results[1]

    def test_thread_safe_concurrent_same_name(self, node: LifecycleComponentNode) -> None:
        # Concurrent idempotent calls on the same name must return the same instance.
        barrier = threading.Barrier(4, timeout=5.0)
        errors: list[Exception] = []
        results: list[object] = []

        def create() -> None:
            try:
                barrier.wait()
                results.append(node.get_or_create_callback_group("shared"))
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=create) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        assert not errors, f"Unexpected errors: {errors}"
        assert len(results) == 4
        first = results[0]
        assert all(r is first for r in results), "Concurrent calls returned different instances"
