Getting Started
===============

Need the shortest runnable path first? Start with :doc:`Quickstart <quickstart>`.
This page remains the reference for prerequisites, validation commands, and documentation tooling.

Audience
--------

This page is for developers who want to understand or try the repository with ROS 2 Jazzy.

Prerequisites
-------------

- Python 3.12 or newer
- ROS 2 Jazzy installed on the system
- uv available in the workspace

Environment Notes
-----------------

The project expects rclpy to come from the system ROS installation.
It should not be added as a normal PyPI dependency of the package.

Install Development Dependencies
--------------------------------

Use uv to sync the default project environment with development tools:

.. code-block:: bash

   uv sync --extra dev

If you want the documentation toolchain as well:

.. code-block:: bash

   uv sync --extra dev --group docs

Common Validation Commands
--------------------------

The repository currently uses these commands:

.. code-block:: bash

   uv run ruff check .
   uv run ruff format --check .
   uv run pyright
   uv run pytest

Build the Documentation
-----------------------

The Sphinx documentation can be built with:

.. code-block:: bash

   uv run --group docs python -m sphinx -b html docs docs/_build/html

The generated HTML output is written to docs/_build/html.

Repository Concepts
-------------------

For the intended conceptual model before reading API details, start with
:doc:`Mental Model <concepts/mental_model>`.

The architecture is organized around:

- LifecycleComponentNode as the lifecycle-aware orchestrator
- LifecycleComponent as the base managed entity for reusable logic
- topic-oriented components for publishers and subscribers

Lifecycle rules used by the repository:

- create ROS resources during configure
- enable or gate runtime behavior during activate and deactivate
- release ROS resources during cleanup

These rules keep component behavior explicit and aligned with native ROS 2 lifecycle semantics.
