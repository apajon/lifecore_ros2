from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

sys.path.insert(0, os.fspath(SRC))

project = "lifecore_ros2"
author = "Adrien Pajon"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "bysource"
autodoc_mock_imports = ["rclpy"]
napoleon_google_docstring = True
napoleon_numpy_docstring = False

html_theme = "alabaster"

# Extension points (protected hooks subclasses are meant to override) are
# documented by default because their leading underscore reflects the
# framework's naming convention, not "do not read this".
# Framework-internal helpers (_attach, _detach, _guarded_call, etc.) are
# excluded because they are implementation details with no user contract.
_EXTENSION_POINTS = frozenset(
    {
        "_on_configure",
        "_on_activate",
        "_on_deactivate",
        "_on_cleanup",
        "_on_shutdown",
        "_on_error",
        "_release_resources",
    }
)


def autodoc_skip_member(app, what, name, obj, skip, options):  # type: ignore[no-untyped-def]
    """Include protected extension points; exclude all other underscore members."""
    if name.startswith("__"):
        # Let autodoc's default behavior handle dunder members.
        return skip
    if name.startswith("_"):
        return name not in _EXTENSION_POINTS
    return skip


def setup(app):  # type: ignore[no-untyped-def]
    app.connect("autodoc-skip-member", autodoc_skip_member)
