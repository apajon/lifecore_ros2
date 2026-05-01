from __future__ import annotations

import logging
import re
from collections.abc import Callable, Sequence

from rclpy.lifecycle import TransitionCallbackReturn

from lifecore_ros2.core import LifecycleComponent, LifecycleComponentNode

from .fakes import DUMMY_STATE


def activate_component(node: LifecycleComponentNode, name: str) -> LifecycleComponent:
    """Configure and activate one registered component, asserting both transitions succeed."""
    component = node.get_component(name)
    configure_result = component.on_configure(DUMMY_STATE)
    assert configure_result == TransitionCallbackReturn.SUCCESS
    activate_result = component.on_activate(DUMMY_STATE)
    assert activate_result == TransitionCallbackReturn.SUCCESS
    return component


def deactivate_component(node: LifecycleComponentNode, name: str) -> LifecycleComponent:
    """Deactivate and cleanup one registered component, asserting both transitions succeed."""
    component = node.get_component(name)
    deactivate_result = component.on_deactivate(DUMMY_STATE)
    assert deactivate_result == TransitionCallbackReturn.SUCCESS
    cleanup_result = component.on_cleanup(DUMMY_STATE)
    assert cleanup_result == TransitionCallbackReturn.SUCCESS
    return component


class _ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


def collect_logs(logger: logging.Logger, test_fn: Callable[[], None]) -> list[str]:
    """Run ``test_fn`` and return log messages emitted by a standard Python logger."""
    handler = _ListHandler()
    logger.addHandler(handler)
    try:
        test_fn()
    finally:
        logger.removeHandler(handler)
    return handler.messages


def expect_log(logs: Sequence[str], pattern: str) -> str:
    """Return the first log matching ``pattern`` or raise ``AssertionError``."""
    compiled_pattern = re.compile(pattern)
    for message in logs:
        if compiled_pattern.search(message):
            return message
    raise AssertionError(f"No log message matched pattern: {pattern}")
