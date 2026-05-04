"""Regression tests for add_component registration guard and atomic rollback."""

from __future__ import annotations

import pytest

from lifecore_ros2.core import LifecycleComponentNode
from lifecore_ros2.testing import DUMMY_STATE, FakeComponent

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def node():
    n = LifecycleComponentNode("regression_add_node")
    yield n
    n.destroy_node()


# ---------------------------------------------------------------------------
# Fix 1 — Guard add_component after lifecycle transitions
# ---------------------------------------------------------------------------


class TestRegressionRegistrationGuard:
    """Registration must be rejected after the first lifecycle transition."""

    def test_configure_closes_registration(self, node: LifecycleComponentNode) -> None:
        # Regression: add_component was silently accepted after on_configure,
        # leading to components that never received configure propagation.
        # Expected: RuntimeError prevents late registration.

        # Negative case first: registration works before any transition
        comp_before = FakeComponent("before_configure")
        node.add_component(comp_before)
        assert comp_before.name in [c.name for c in node.components]

        # Trigger lifecycle transition
        node.on_configure(DUMMY_STATE)

        # Positive case: adding after configure must raise
        with pytest.raises(RuntimeError, match="lifecycle transitions have already started"):
            node.add_component(FakeComponent("after_configure"))

    def test_shutdown_closes_registration(self, node: LifecycleComponentNode) -> None:
        # Regression: add_component was accepted after on_shutdown,
        # leaving orphan components on a shutting-down node.
        # Expected: RuntimeError prevents registration after shutdown.

        # Negative case first: registration works before shutdown
        comp_before = FakeComponent("before_shutdown")
        node.add_component(comp_before)
        assert comp_before.name in [c.name for c in node.components]

        # Trigger shutdown
        node.on_shutdown(DUMMY_STATE)

        # Positive case: adding after shutdown must raise
        with pytest.raises(RuntimeError, match="lifecycle transitions have already started"):
            node.add_component(FakeComponent("after_shutdown"))

    def test_registration_open_flag_initially_true(self, node: LifecycleComponentNode) -> None:
        # Guard: the flag must default to True for fresh nodes.
        assert node._registration_open is True
