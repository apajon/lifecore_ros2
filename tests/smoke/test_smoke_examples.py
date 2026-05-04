"""Smoke-import tests for core examples: verify each file is import-safe without triggering main."""

from __future__ import annotations

import pathlib
import runpy

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples"


def _example_modules() -> list[pathlib.Path]:
    return sorted(path for path in EXAMPLES_DIR.glob("*.py") if path.name != "__init__.py")


@pytest.mark.parametrize(
    "module_path",
    _example_modules(),
    ids=lambda p: p.name,
)
def test_example_is_import_safe(module_path: pathlib.Path) -> None:
    """Example modules should be import-safe before their main routines run."""
    module_globals = runpy.run_path(
        str(module_path),
        run_name=f"lifecore_ros2_smoke.{module_path.stem}",
    )

    assert module_globals
