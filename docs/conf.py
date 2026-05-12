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
html_static_path = ["_static"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "bysource"
autodoc_mock_imports = ["rcl_interfaces", "rclpy"]
napoleon_google_docstring = True
napoleon_numpy_docstring = False
pygments_style = "default"
pygments_dark_style = "monokai"

html_title = "lifecore_ros2"
html_theme = "furo"
html_favicon = "_static/Logo_github_HD.png"
html_css_files = ["custom.css"]
html_theme_options = {
    "light_logo": "Logo_main_light_HD.png",
    "dark_logo": "Logo_main_dark_HD.png",
    "light_css_variables": {
        "color-brand-primary": "#2563EB",
        "color-brand-content": "#2563EB",
        "color-admonition-background": "#F8FAFC",
    },
    "dark_css_variables": {
        "color-brand-primary": "#60A5FA",
        "color-brand-content": "#60A5FA",
        "color-admonition-background": "#0F172A",
    },
    "source_repository": "https://github.com/apajon/lifecore_ros2",
    "source_branch": "main",
    "source_directory": "docs/",
}

rst_prolog = """
.. raw:: html

     <div class="page-lifecycle-banner">
         <div class="page-lifecycle-banner__icon" role="img" aria-label="lifecore_ros2 icon"></div>
         <div>
             <p class="page-lifecycle-banner__eyebrow">Lifecycle interface</p>
             <p class="page-lifecycle-banner__title">Core lifecycle for modular robotics systems</p>
             <p class="page-lifecycle-banner__trace">Configure <span>·</span> Activate <span>·</span> Run <span>·</span> Transition <span>·</span> Shutdown</p>
         </div>
     </div>
"""

# Extension points (protected hooks subclasses are meant to override) are
# documented by default because their leading underscore reflects the
# framework's naming convention, not "do not read this".
# Framework-internal helpers (_attach, _detach, _guarded_call, etc.) are
# excluded because they are implementation details with no user contract.
#
# NOTE: api.rst uses :undoc-members: so autodoc emits members that have no
# docstring. This skip filter is the companion gate: it re-hides private
# members that :undoc-members: would otherwise expose. Any new private helper
# added to the codebase is automatically excluded unless its name is added to
# _EXTENSION_POINTS below.
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
