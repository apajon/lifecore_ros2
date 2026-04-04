Contributing
============

Scope
-----

This repository is in early development. Contributions should remain small, explicit, and easy to review.

Environment
-----------

The project uses uv for workspace dependency management.
ROS 2 Jazzy and rclpy are expected to come from the system installation.

Set up a local environment with development tooling:

.. code-block:: bash

   uv sync --extra dev

If you also want the documentation toolchain:

.. code-block:: bash

   uv sync --extra dev --group docs

Validation
----------

Run the standard checks before proposing changes:

.. code-block:: bash

   uv run --extra dev python -m ruff check .
   uv run --extra dev python -m ruff format --check .
   uv run --extra dev pyright
   uv run --extra dev pytest

If you touch documentation pages or docstrings, also build the docs:

.. code-block:: bash

   uv run --group docs python -m sphinx -b html docs docs/_build/html

Repository Rules
----------------

Keep these design constraints in mind when contributing:

- preserve native ROS 2 lifecycle semantics
- do not add a parallel hidden state machine
- create topic resources during configure
- gate runtime behavior with activation state
- release topic resources during cleanup
- preserve typing and keep public APIs stable unless a change is explicitly intended

Documentation
-------------

Use concise Google-style docstrings for Python APIs.
For broader documentation, prefer adding or updating Sphinx pages under docs/ instead of overloading the README.
