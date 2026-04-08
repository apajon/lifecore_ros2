"""Smoke-import test: verify every symbol in lifecore_ros2.__all__ is importable."""

from __future__ import annotations

import lifecore_ros2


class TestSmokeImport:
    def test_all_exports_are_importable(self) -> None:
        for name in lifecore_ros2.__all__:
            obj = getattr(lifecore_ros2, name, None)
            assert obj is not None, f"{name} listed in __all__ but not importable"

    def test_all_exports_are_classes(self) -> None:
        for name in lifecore_ros2.__all__:
            obj = getattr(lifecore_ros2, name)
            assert isinstance(obj, type), f"{name} is not a class: {type(obj)}"
