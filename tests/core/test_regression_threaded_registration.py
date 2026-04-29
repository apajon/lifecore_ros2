"""Threaded registration tests for LifecycleComponentNode.

Validates that the component registry remains consistent under concurrent
access. Covers:
- concurrent registration of different components
- concurrent registration of same-name components (duplicate rejection)
- race between registration and lifecycle gate closure
"""

from __future__ import annotations

import threading

import pytest
from rclpy.lifecycle.node import LifecycleState

from lifecore_ros2.core import LifecycleComponent, LifecycleComponentNode

DUMMY_STATE = LifecycleState(state_id=0, label="test")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def node():
    n = LifecycleComponentNode("threaded_reg_node")
    yield n
    n.destroy_node()


# ---------------------------------------------------------------------------
# Concurrent registration of different components
# ---------------------------------------------------------------------------


class TestConcurrentRegistration:
    """Two threads register different components simultaneously."""

    def test_concurrent_add_different_components(self, node: LifecycleComponentNode) -> None:
        # Regression: without locking, concurrent add_component could corrupt
        # the registry or produce duplicate managed entities.
        # Expected: both components are registered exactly once.
        barrier = threading.Barrier(2, timeout=5.0)
        errors: list[Exception] = []

        def add_with_barrier(comp: LifecycleComponent) -> None:
            try:
                barrier.wait()
                node.add_component(comp)
            except Exception as exc:
                errors.append(exc)

        comp_a = _DummyComponent("thread_a")
        comp_b = _DummyComponent("thread_b")

        t1 = threading.Thread(target=add_with_barrier, args=(comp_a,))
        t2 = threading.Thread(target=add_with_barrier, args=(comp_b,))
        t1.start()
        t2.start()
        t1.join(timeout=5.0)
        t2.join(timeout=5.0)

        assert not errors, f"Unexpected errors: {errors}"
        names = [c.name for c in node.components]
        assert "thread_a" in names
        assert "thread_b" in names
        assert len(node.components) == 2

    def test_concurrent_add_many_components(self, node: LifecycleComponentNode) -> None:
        # Guard: stress test with more threads to validate lock correctness.
        count = 10
        barrier = threading.Barrier(count, timeout=5.0)
        errors: list[Exception] = []

        def add_with_barrier(comp: LifecycleComponent) -> None:
            try:
                barrier.wait()
                node.add_component(comp)
            except Exception as exc:
                errors.append(exc)

        comps = [_DummyComponent(f"stress_{i}") for i in range(count)]
        threads = [threading.Thread(target=add_with_barrier, args=(c,)) for c in comps]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        assert not errors, f"Unexpected errors: {errors}"
        assert len(node.components) == count
        registered_names = {c.name for c in node.components}
        expected_names = {f"stress_{i}" for i in range(count)}
        assert registered_names == expected_names


# ---------------------------------------------------------------------------
# Concurrent registration of duplicate names
# ---------------------------------------------------------------------------


class TestConcurrentDuplicateRejection:
    """Two threads try to register a component with the same name."""

    def test_concurrent_duplicate_name_one_wins(self, node: LifecycleComponentNode) -> None:
        # Regression: without locking, both threads could pass the duplicate check
        # before either inserts, leading to a corrupted registry.
        # Expected: exactly one succeeds, one raises ValueError.
        barrier = threading.Barrier(2, timeout=5.0)
        results: list[str] = []  # "ok" or "dup"
        errors: list[Exception] = []

        def try_add(comp: LifecycleComponent) -> None:
            try:
                barrier.wait()
                node.add_component(comp)
                results.append("ok")
            except ValueError:
                results.append("dup")
            except Exception as exc:
                errors.append(exc)

        comp1 = _DummyComponent("same_name")
        comp2 = _DummyComponent("same_name")

        t1 = threading.Thread(target=try_add, args=(comp1,))
        t2 = threading.Thread(target=try_add, args=(comp2,))
        t1.start()
        t2.start()
        t1.join(timeout=5.0)
        t2.join(timeout=5.0)

        assert not errors, f"Unexpected errors: {errors}"
        assert sorted(results) == ["dup", "ok"]
        assert len(node.components) == 1
        assert node.components[0].name == "same_name"

        # The winning component must be attached; the loser must not.
        winner = node.get_component("same_name")
        loser = comp1 if winner is comp2 else comp2
        assert winner._node is node
        assert loser._node is None


# ---------------------------------------------------------------------------
# Race between registration and gate closure
# ---------------------------------------------------------------------------


class TestConcurrentGateClosure:
    """One thread registers while another closes the registration gate."""

    def test_registration_race_with_configure(self, node: LifecycleComponentNode) -> None:
        # Regression: without locking, a thread could add a component after
        # the gate was logically closed but before the flag was set, leaving
        # a component that missed configure propagation.
        # Expected: the component is either registered (before gate close)
        # or rejected (after gate close). The registry is always consistent.
        barrier = threading.Barrier(2, timeout=5.0)
        registration_result: list[str] = []
        errors: list[Exception] = []

        def try_add() -> None:
            try:
                barrier.wait()
                node.add_component(_DummyComponent("late_component"))
                registration_result.append("registered")
            except RuntimeError:
                registration_result.append("rejected")
            except Exception as exc:
                errors.append(exc)

        def close_gate() -> None:
            try:
                barrier.wait()
                node.on_configure(DUMMY_STATE)
            except Exception as exc:
                errors.append(exc)

        t_add = threading.Thread(target=try_add)
        t_gate = threading.Thread(target=close_gate)
        t_add.start()
        t_gate.start()
        t_add.join(timeout=5.0)
        t_gate.join(timeout=5.0)

        assert not errors, f"Unexpected errors: {errors}"
        assert len(registration_result) == 1
        result = registration_result[0]

        if result == "registered":
            assert len(node.components) == 1
            assert node.components[0].name == "late_component"
        else:
            assert result == "rejected"
            assert len(node.components) == 0

        # In either case, gate must now be closed
        assert not node._registration_open

    def test_registration_after_gate_closure_rejected(self, node: LifecycleComponentNode) -> None:
        # Guard: sequential gate closure then registration must always reject.
        node.on_configure(DUMMY_STATE)

        with pytest.raises(RuntimeError, match="lifecycle transitions have already started"):
            node.add_component(_DummyComponent("too_late"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _DummyComponent(LifecycleComponent):
    pass
