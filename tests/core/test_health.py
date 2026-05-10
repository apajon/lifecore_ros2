"""Regression tests for Sprint 10 Health Status API.

Coverage:
    - _worst_health unit tests
    - LifecycleComponent.health initial state (AC1, AC4, AC8)
    - Health updates for all six lifecycle transitions (unit, failure, exception)
    - LifecycleComponentNode.health aggregation (AC6-node)
    - Public import accessibility (AC7-import)
"""

from __future__ import annotations

from collections.abc import Generator

import pytest

import lifecore_ros2
from lifecore_ros2 import LifecycleComponentNode
from lifecore_ros2.core import HealthLevel, HealthStatus
from lifecore_ros2.core.health import HEALTH_UNKNOWN, _worst_health
from lifecore_ros2.testing import DUMMY_STATE, FailingComponent, FakeComponent


@pytest.fixture()
def node() -> Generator[LifecycleComponentNode, None, None]:
    n = LifecycleComponentNode("health_test_node")
    yield n
    n.destroy_node()


# ---------------------------------------------------------------------------
# _worst_health unit tests
# ---------------------------------------------------------------------------


class TestWorstHealth:
    """Unit tests for the _worst_health severity aggregation function."""

    def test_unknown_and_ok_returns_ok(self) -> None:
        a = HealthStatus(level=HealthLevel.UNKNOWN, reason="")
        b = HealthStatus(level=HealthLevel.OK, reason="")
        assert _worst_health(a, b) == b

    def test_degraded_and_error_returns_error(self) -> None:
        a = HealthStatus(level=HealthLevel.DEGRADED, reason="")
        b = HealthStatus(level=HealthLevel.ERROR, reason="")
        assert _worst_health(a, b) == b

    def test_error_and_ok_returns_error(self) -> None:
        a = HealthStatus(level=HealthLevel.ERROR, reason="")
        b = HealthStatus(level=HealthLevel.OK, reason="")
        assert _worst_health(a, b) == a


# ---------------------------------------------------------------------------
# AC1, AC4, AC8 — default health, no-node accessibility, no side effects
# ---------------------------------------------------------------------------


class TestFreshComponentHealth:
    """AC1, AC4, AC8: health is always accessible and carries correct defaults."""

    def test_fresh_component_health_level_is_unknown(self) -> None:
        # AC4 — initial level
        comp = FakeComponent("fresh")
        assert comp.health.level == HealthLevel.UNKNOWN

    def test_fresh_component_health_reason_is_empty(self) -> None:
        # AC4 — initial reason
        comp = FakeComponent("fresh")
        assert comp.health.reason == ""

    def test_health_accessible_without_node(self) -> None:
        # AC1 — must not raise when no node is attached
        comp = FakeComponent("standalone")
        _ = comp.health

    def test_health_access_triggers_no_callbacks(self) -> None:
        # AC8 — no transitions, no hook calls
        comp = FakeComponent("watch")
        _ = comp.health
        _ = comp.health
        assert comp.calls == []


# ---------------------------------------------------------------------------
# configure
# ---------------------------------------------------------------------------


class TestHealthOnConfigure:
    """Health updates during the configure transition."""

    def test_configure_success_sets_ok(self, node: LifecycleComponentNode) -> None:
        # AC5
        comp = FakeComponent("cfg_ok")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        assert comp.health.level == HealthLevel.OK

    def test_configure_failure_sets_degraded(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("cfg_fail", fail_at_hook="configure")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        assert comp.health.level == HealthLevel.DEGRADED

    def test_configure_exception_sets_error(self, node: LifecycleComponentNode) -> None:
        # AC2 — exception path sets ERROR
        comp = FailingComponent("cfg_exc", exception=RuntimeError("disk full"))
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        assert comp.health.level == HealthLevel.ERROR

    def test_configure_exception_last_error_contains_hook_name(self, node: LifecycleComponentNode) -> None:
        # AC2 — last_error must name the failing hook
        comp = FailingComponent("cfg_exc2", exception=RuntimeError("disk full"))
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        assert comp.health.last_error is not None
        assert "on_configure" in comp.health.last_error

    def test_configure_exception_last_error_contains_exception_message(self, node: LifecycleComponentNode) -> None:
        # AC2 — last_error must include the original exception message
        comp = FailingComponent("cfg_exc3", exception=RuntimeError("disk full"))
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        assert comp.health.last_error is not None
        assert "disk full" in comp.health.last_error


# ---------------------------------------------------------------------------
# activate
# ---------------------------------------------------------------------------


class TestHealthOnActivate:
    """Health updates during the activate transition."""

    def test_activate_success_sets_ok(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("act_ok")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.health.level == HealthLevel.OK

    def test_activate_success_after_degraded_health_sets_ok(self, node: LifecycleComponentNode) -> None:
        # activate SUCCESS heals a previously DEGRADED health
        comp = FakeComponent("act_heal")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        comp._health = HealthStatus(level=HealthLevel.DEGRADED, reason="simulated prior failure")
        comp.on_activate(DUMMY_STATE)
        assert comp.health.level == HealthLevel.OK

    def test_activate_failure_sets_degraded(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("act_fail", fail_at_hook="activate")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        assert comp.health.level == HealthLevel.DEGRADED


# ---------------------------------------------------------------------------
# deactivate
# ---------------------------------------------------------------------------


class TestHealthOnDeactivate:
    """Health updates during the deactivate transition."""

    def test_deactivate_success_health_unchanged(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("deact_ok")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        health_before = comp.health
        comp.on_deactivate(DUMMY_STATE)
        assert comp.health == health_before

    def test_deactivate_failure_sets_degraded(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("deact_fail", fail_at_hook="deactivate")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        comp.on_activate(DUMMY_STATE)
        comp.on_deactivate(DUMMY_STATE)
        assert comp.health.level == HealthLevel.DEGRADED


# ---------------------------------------------------------------------------
# cleanup
# ---------------------------------------------------------------------------


class TestHealthOnCleanup:
    """Health updates during the cleanup transition."""

    def test_cleanup_success_resets_level_to_unknown(self, node: LifecycleComponentNode) -> None:
        # AC3 — cleanup SUCCESS resets health to UNKNOWN
        comp = FakeComponent("cln_ok")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        comp.on_cleanup(DUMMY_STATE)
        assert comp.health.level == HealthLevel.UNKNOWN

    def test_cleanup_success_clears_last_error(self, node: LifecycleComponentNode) -> None:
        # AC3 — cleanup SUCCESS must clear last_error even after a prior exception
        comp = FailingComponent("cln_exc", exception=RuntimeError("oops"))
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)  # → ERROR, last_error set
        comp.on_cleanup(DUMMY_STATE)  # → HEALTH_UNKNOWN reset
        assert comp.health.last_error is None

    def test_cleanup_failure_sets_degraded(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("cln_fail", fail_at_hook="cleanup")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        comp.on_cleanup(DUMMY_STATE)
        assert comp.health.level == HealthLevel.DEGRADED


# ---------------------------------------------------------------------------
# shutdown
# ---------------------------------------------------------------------------


class TestHealthOnShutdown:
    """Health updates during the shutdown transition."""

    def test_shutdown_success_preserves_last_error(self, node: LifecycleComponentNode) -> None:
        # last_error captured at configure exception must survive a subsequent shutdown
        comp = FailingComponent("shut_exc", exception=RuntimeError("sensor timeout"))
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)  # → ERROR, last_error set
        last_error_before = comp.health.last_error
        comp.on_shutdown(DUMMY_STATE)
        assert comp.health.last_error == last_error_before

    def test_shutdown_success_sets_level_unknown(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("shut_ok")
        node.add_component(comp)
        comp.on_configure(DUMMY_STATE)
        comp.on_shutdown(DUMMY_STATE)
        assert comp.health.level == HealthLevel.UNKNOWN

    def test_shutdown_failure_sets_degraded(self, node: LifecycleComponentNode) -> None:
        comp = FakeComponent("shut_fail", fail_at_hook="shutdown")
        node.add_component(comp)
        comp.on_shutdown(DUMMY_STATE)
        assert comp.health.level == HealthLevel.DEGRADED


# ---------------------------------------------------------------------------
# error
# ---------------------------------------------------------------------------


class TestHealthOnError:
    """Health updates during the error transition."""

    def test_error_hook_failure_sets_degraded_when_not_error(self, node: LifecycleComponentNode) -> None:
        # health is UNKNOWN (not ERROR) → FAILURE should set DEGRADED
        comp = FakeComponent("err_fail", fail_at_hook="error")
        node.add_component(comp)
        comp.on_error(DUMMY_STATE)
        assert comp.health.level == HealthLevel.DEGRADED

    def test_error_hook_failure_preserves_error_level(self, node: LifecycleComponentNode) -> None:
        # When health is already ERROR, a FAILURE from the error hook must not downgrade it
        comp = FakeComponent("err_fail_w_error", fail_at_hook="error")
        node.add_component(comp)
        comp._health = HealthStatus(level=HealthLevel.ERROR, reason="prior exception", last_error="prior error")
        comp.on_error(DUMMY_STATE)
        assert comp.health.level == HealthLevel.ERROR

    def test_error_hook_exception_sets_error(self, node: LifecycleComponentNode) -> None:
        # Exception inside the error hook sets ERROR via _guarded_call
        comp = FailingComponent("err_exc", fail_at_hook="error", exception=RuntimeError("error handler crash"))
        node.add_component(comp)
        comp.on_error(DUMMY_STATE)
        assert comp.health.level == HealthLevel.ERROR


# ---------------------------------------------------------------------------
# AC6-node — LifecycleComponentNode.health aggregation
# ---------------------------------------------------------------------------


class TestNodeHealth:
    """AC6-node: LifecycleComponentNode.health returns worst severity across components."""

    def test_node_no_components_returns_health_unknown(self, node: LifecycleComponentNode) -> None:
        assert node.health == HEALTH_UNKNOWN

    def test_node_mixed_health_returns_worst(self, node: LifecycleComponentNode) -> None:
        # One component succeeds configure (OK), one raises an exception (ERROR)
        # → node health must be ERROR
        comp_ok = FakeComponent("ok_comp")
        comp_err = FailingComponent("err_comp", exception=RuntimeError("sensor fail"))
        node.add_component(comp_ok)
        node.add_component(comp_err)
        node._close_registration()  # populate _resolved_order without triggering propagation
        comp_ok.on_configure(DUMMY_STATE)  # → health = OK
        comp_err.on_configure(DUMMY_STATE)  # → health = ERROR (exception)
        assert node.health.level == HealthLevel.ERROR


# ---------------------------------------------------------------------------
# AC7-import — public package accessibility
# ---------------------------------------------------------------------------


class TestImport:
    """AC7-import: HealthStatus and HealthLevel are importable from the top-level package."""

    def test_health_status_importable_from_package(self) -> None:
        assert lifecore_ros2.HealthStatus is HealthStatus

    def test_health_level_importable_from_package(self) -> None:
        assert lifecore_ros2.HealthLevel is HealthLevel
