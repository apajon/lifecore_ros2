"""Regression tests for resource ownership and cleanup semantics across all component types.

Sprint 7: cleanup and ownership API.

Coverage map:
    TestPublisherOwnership       — publisher: owned resource lifecycle, callback_group borrow
    TestSubscriberOwnership      — subscriber: owned resource lifecycle, callback_group borrow
    TestTimerOwnership           — timer: owned resource lifecycle + start/stop/reset after cleanup
    TestServiceServerOwnership   — service server: owned resource lifecycle, callback_group borrow
    TestServiceClientOwnership   — service client: owned resource lifecycle, callback_group borrow

Contract tested:
    - configure creates the owned ROS resource
    - cleanup releases the owned ROS resource (_resource is None after on_cleanup)
    - _release_resources() is idempotent (double call raises no exception)
    - deactivate does NOT destroy the resource (resource is still valid after on_deactivate)
    - borrowed callback_group is preserved intact after cleanup
    - shutdown releases the owned ROS resource
    - error releases the owned ROS resource
    - Timer.start/stop/reset raise ComponentNotConfiguredError after cleanup
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from rclpy.callback_groups import CallbackGroup

from lifecore_ros2.components import (
    LifecyclePublisherComponent,
    LifecycleServiceClientComponent,
    LifecycleSubscriberComponent,
    LifecycleTimerComponent,
)
from lifecore_ros2.core import ComponentNotConfiguredError, LifecycleComponentNode
from tests.components._service_stubs import DUMMY_STATE, _TriggerClient, _TriggerServer
from tests.components._topic_stubs import StubSubscriber, StubTimer

# ---------------------------------------------------------------------------
# Publisher
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestPublisherOwnership:
    def test_cleanup_releases_publisher(self, node: LifecycleComponentNode) -> None:
        pub = LifecyclePublisherComponent("pub", "/t", MagicMock)
        node.add_component(pub)
        pub.on_configure(DUMMY_STATE)
        pub.on_cleanup(DUMMY_STATE)
        assert pub._publisher is None

    def test_cleanup_is_idempotent(self, node: LifecycleComponentNode) -> None:
        pub = LifecyclePublisherComponent("pub_idem", "/t", MagicMock)
        node.add_component(pub)
        pub.on_configure(DUMMY_STATE)
        pub.on_cleanup(DUMMY_STATE)
        assert pub._publisher is None
        pub._release_resources()  # second call must not raise

    def test_deactivate_does_not_destroy_publisher(self, node: LifecycleComponentNode) -> None:
        pub = LifecyclePublisherComponent("pub_deact", "/t", MagicMock)
        node.add_component(pub)
        pub.on_configure(DUMMY_STATE)
        pub.on_activate(DUMMY_STATE)
        pub.on_deactivate(DUMMY_STATE)
        assert pub._publisher is not None

    def test_cleanup_preserves_borrowed_callback_group(self, node: LifecycleComponentNode) -> None:
        cg = MagicMock(spec=CallbackGroup)
        pub = LifecyclePublisherComponent("pub_cg", "/t", MagicMock, callback_group=cg)
        node.add_component(pub)
        pub.on_configure(DUMMY_STATE)
        pub.on_cleanup(DUMMY_STATE)
        assert pub._callback_group is cg

    def test_shutdown_releases_publisher(self, node: LifecycleComponentNode) -> None:
        pub = LifecyclePublisherComponent("pub_sd", "/t", MagicMock)
        node.add_component(pub)
        pub.on_configure(DUMMY_STATE)
        pub.on_shutdown(DUMMY_STATE)
        assert pub._publisher is None

    def test_error_releases_publisher(self, node: LifecycleComponentNode) -> None:
        pub = LifecyclePublisherComponent("pub_err", "/t", MagicMock)
        node.add_component(pub)
        pub.on_configure(DUMMY_STATE)
        pub.on_error(DUMMY_STATE)
        assert pub._publisher is None


# ---------------------------------------------------------------------------
# Subscriber
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestSubscriberOwnership:
    def test_cleanup_releases_subscription(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber("sub")
        node.add_component(sub)
        sub.on_configure(DUMMY_STATE)
        sub.on_cleanup(DUMMY_STATE)
        assert sub._subscription is None

    def test_cleanup_is_idempotent(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber("sub_idem")
        node.add_component(sub)
        sub.on_configure(DUMMY_STATE)
        sub.on_cleanup(DUMMY_STATE)
        assert sub._subscription is None
        sub._release_resources()  # second call must not raise

    def test_deactivate_does_not_destroy_subscription(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber("sub_deact")
        node.add_component(sub)
        sub.on_configure(DUMMY_STATE)
        sub.on_activate(DUMMY_STATE)
        sub.on_deactivate(DUMMY_STATE)
        assert sub._subscription is not None

    def test_cleanup_preserves_borrowed_callback_group(self, node: LifecycleComponentNode) -> None:
        cg = MagicMock(spec=CallbackGroup)

        class _SubCg(LifecycleSubscriberComponent[Any]):
            def __init__(self) -> None:
                super().__init__(name="sub_cg", topic_name="/t", msg_type=MagicMock, callback_group=cg)

            def on_message(self, msg: Any) -> None: ...

        sub = _SubCg()
        node.add_component(sub)
        sub.on_configure(DUMMY_STATE)
        sub.on_cleanup(DUMMY_STATE)
        assert sub._callback_group is cg

    def test_shutdown_releases_subscription(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber("sub_sd")
        node.add_component(sub)
        sub.on_configure(DUMMY_STATE)
        sub.on_shutdown(DUMMY_STATE)
        assert sub._subscription is None

    def test_error_releases_subscription(self, node: LifecycleComponentNode) -> None:
        sub = StubSubscriber("sub_err")
        node.add_component(sub)
        sub.on_configure(DUMMY_STATE)
        sub.on_error(DUMMY_STATE)
        assert sub._subscription is None


# ---------------------------------------------------------------------------
# Timer
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_topic_factories")
class TestTimerOwnership:
    def test_cleanup_releases_timer(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer("timer")
        node.add_component(timer)
        timer.on_configure(DUMMY_STATE)
        timer.on_cleanup(DUMMY_STATE)
        assert timer._timer is None

    def test_cleanup_is_idempotent(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer("timer_idem")
        node.add_component(timer)
        timer.on_configure(DUMMY_STATE)
        timer.on_cleanup(DUMMY_STATE)
        assert timer._timer is None
        timer._release_resources()  # second call must not raise

    def test_deactivate_does_not_destroy_timer(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer("timer_deact")
        node.add_component(timer)
        timer.on_configure(DUMMY_STATE)
        timer.on_activate(DUMMY_STATE)
        timer.on_deactivate(DUMMY_STATE)
        assert timer._timer is not None

    def test_cleanup_preserves_borrowed_callback_group(self, node: LifecycleComponentNode) -> None:
        cg = MagicMock(spec=CallbackGroup)

        class _TimerCg(LifecycleTimerComponent):
            def on_tick(self) -> None: ...

        timer = _TimerCg(name="timer_cg", period=0.1, callback_group=cg)
        node.add_component(timer)
        timer.on_configure(DUMMY_STATE)
        timer.on_cleanup(DUMMY_STATE)
        assert timer._callback_group is cg

    def test_shutdown_releases_timer(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer("timer_sd")
        node.add_component(timer)
        timer.on_configure(DUMMY_STATE)
        timer.on_shutdown(DUMMY_STATE)
        assert timer._timer is None

    def test_error_releases_timer(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer("timer_err")
        node.add_component(timer)
        timer.on_configure(DUMMY_STATE)
        timer.on_error(DUMMY_STATE)
        assert timer._timer is None

    def test_start_after_cleanup_raises_component_not_configured(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer("timer_start_after_cleanup")
        node.add_component(timer)
        timer.on_configure(DUMMY_STATE)
        timer.on_cleanup(DUMMY_STATE)
        with pytest.raises(ComponentNotConfiguredError):
            timer.start()

    def test_stop_after_cleanup_raises_component_not_configured(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer("timer_stop_after_cleanup")
        node.add_component(timer)
        timer.on_configure(DUMMY_STATE)
        timer.on_cleanup(DUMMY_STATE)
        with pytest.raises(ComponentNotConfiguredError):
            timer.stop()

    def test_reset_after_cleanup_raises_component_not_configured(self, node: LifecycleComponentNode) -> None:
        timer = StubTimer("timer_reset_after_cleanup")
        node.add_component(timer)
        timer.on_configure(DUMMY_STATE)
        timer.on_cleanup(DUMMY_STATE)
        with pytest.raises(ComponentNotConfiguredError):
            timer.reset()


# ---------------------------------------------------------------------------
# Service server
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_svc_factories")
class TestServiceServerOwnership:
    def test_cleanup_releases_service(self, node: LifecycleComponentNode) -> None:
        srv = _TriggerServer("srv")
        node.add_component(srv)
        srv.on_configure(DUMMY_STATE)
        srv.on_cleanup(DUMMY_STATE)
        assert srv._service is None

    def test_cleanup_is_idempotent(self, node: LifecycleComponentNode) -> None:
        srv = _TriggerServer("srv_idem")
        node.add_component(srv)
        srv.on_configure(DUMMY_STATE)
        srv.on_cleanup(DUMMY_STATE)
        assert srv._service is None
        srv._release_resources()  # second call must not raise

    def test_deactivate_does_not_destroy_service(self, node: LifecycleComponentNode) -> None:
        srv = _TriggerServer("srv_deact")
        node.add_component(srv)
        srv.on_configure(DUMMY_STATE)
        srv.on_activate(DUMMY_STATE)
        srv.on_deactivate(DUMMY_STATE)
        assert srv._service is not None

    def test_cleanup_preserves_borrowed_callback_group(self, node: LifecycleComponentNode) -> None:
        import std_srvs.srv

        cg = MagicMock(spec=CallbackGroup)

        from lifecore_ros2.components import LifecycleServiceServerComponent

        class _SrvCg(LifecycleServiceServerComponent[std_srvs.srv.Trigger]):
            def __init__(self) -> None:
                super().__init__(
                    name="srv_cg",
                    service_name="/t",
                    srv_type=std_srvs.srv.Trigger,
                    callback_group=cg,
                )

            def on_service_request(self, request: Any, response: Any) -> Any:
                return response

        srv = _SrvCg()
        node.add_component(srv)
        srv.on_configure(DUMMY_STATE)
        srv.on_cleanup(DUMMY_STATE)
        assert srv._callback_group is cg

    def test_shutdown_releases_service(self, node: LifecycleComponentNode) -> None:
        srv = _TriggerServer("srv_sd")
        node.add_component(srv)
        srv.on_configure(DUMMY_STATE)
        srv.on_shutdown(DUMMY_STATE)
        assert srv._service is None

    def test_error_releases_service(self, node: LifecycleComponentNode) -> None:
        srv = _TriggerServer("srv_err")
        node.add_component(srv)
        srv.on_configure(DUMMY_STATE)
        srv.on_error(DUMMY_STATE)
        assert srv._service is None


# ---------------------------------------------------------------------------
# Service client
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_svc_factories")
class TestServiceClientOwnership:
    def test_cleanup_releases_client(self, node: LifecycleComponentNode) -> None:
        cli = _TriggerClient("cli")
        node.add_component(cli)
        cli.on_configure(DUMMY_STATE)
        cli.on_cleanup(DUMMY_STATE)
        assert cli._client is None

    def test_cleanup_is_idempotent(self, node: LifecycleComponentNode) -> None:
        cli = _TriggerClient("cli_idem")
        node.add_component(cli)
        cli.on_configure(DUMMY_STATE)
        cli.on_cleanup(DUMMY_STATE)
        assert cli._client is None
        cli._release_resources()  # second call must not raise

    def test_deactivate_does_not_destroy_client(self, node: LifecycleComponentNode) -> None:
        cli = _TriggerClient("cli_deact")
        node.add_component(cli)
        cli.on_configure(DUMMY_STATE)
        cli.on_activate(DUMMY_STATE)
        cli.on_deactivate(DUMMY_STATE)
        assert cli._client is not None

    def test_cleanup_preserves_borrowed_callback_group(self, node: LifecycleComponentNode) -> None:
        import std_srvs.srv

        cg = MagicMock(spec=CallbackGroup)
        cli = LifecycleServiceClientComponent(
            "cli_cg",
            "/t",
            std_srvs.srv.Trigger,
            callback_group=cg,
        )
        node.add_component(cli)
        cli.on_configure(DUMMY_STATE)
        cli.on_cleanup(DUMMY_STATE)
        assert cli._callback_group is cg

    def test_shutdown_releases_client(self, node: LifecycleComponentNode) -> None:
        cli = _TriggerClient("cli_sd")
        node.add_component(cli)
        cli.on_configure(DUMMY_STATE)
        cli.on_shutdown(DUMMY_STATE)
        assert cli._client is None

    def test_error_releases_client(self, node: LifecycleComponentNode) -> None:
        cli = _TriggerClient("cli_err")
        node.add_component(cli)
        cli.on_configure(DUMMY_STATE)
        cli.on_error(DUMMY_STATE)
        assert cli._client is None
