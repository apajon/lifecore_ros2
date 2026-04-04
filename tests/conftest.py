from __future__ import annotations

import pytest
import rclpy


@pytest.fixture(scope="session", autouse=True)
def rclpy_context():
    """Initialize and shutdown rclpy once for the entire test session."""
    rclpy.init()
    yield
    rclpy.shutdown()
