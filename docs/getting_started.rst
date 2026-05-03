Getting Started
===============

.. raw:: html

    <div class="lifecycle-signature">
       <svg class="lifecycle-signature__mark" viewBox="0 0 96 96" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <circle cx="48" cy="48" r="30" stroke="currentColor" stroke-width="12" stroke-linecap="round" stroke-dasharray="96 20"/>
          <path d="M48 12a36 36 0 0 1 25.46 10.54" stroke="#7C3AED" stroke-width="12" stroke-linecap="round"/>
          <path d="M79.82 64.5A36 36 0 0 1 48 84" stroke="#7C3AED" stroke-width="12" stroke-linecap="round" stroke-dasharray="22 16"/>
       </svg>
       <div>
          <p class="lifecycle-signature__eyebrow">Lifecycle interface</p>
          <p class="lifecycle-signature__title">Core lifecycle for modular robotics systems</p>
          <p class="lifecycle-signature__text">Start from the shortest runnable path, then follow the same lifecycle vocabulary used by the framework.</p>
       </div>
    </div>

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

Install Paths
-------------

For an application project that consumes the library from PyPI:

.. code-block:: bash

   source /opt/ros/jazzy/setup.bash
   uv add lifecore-ros2

For a development checkout of this repository, use the local dependency setup
below instead.

Lifecycle Landmarks
-------------------

.. raw:: html

    <div class="lifecycle-map">
       <div class="lifecycle-step"><strong>⚙ Configure</strong><p>Install ROS 2 Jazzy, keep <span class="lifecycle-accent">rclpy</span> system-provided, and sync the workspace with uv.</p></div>
       <div class="lifecycle-step"><strong>▶ Activate</strong><p>Enable the developer toolchain with lint, format, type-check, and test commands that match the repository defaults.</p></div>
       <div class="lifecycle-step"><strong>▶ Run</strong><p>Build the docs and exercise examples before diving into API details.</p></div>
       <div class="lifecycle-step lifecycle-step--transition"><strong>🔁 Transition</strong><p>Move from quick validation into the conceptual model and architecture pages.</p></div>
       <div class="lifecycle-step"><strong>■ Shutdown</strong><p>Keep cleanup semantics in mind: configured resources are meant to be released explicitly during lifecycle cleanup.</p></div>
    </div>

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

.. raw:: html

    <div class="state-box transition">
       <strong>Lifecycle reading path.</strong>
       The onboarding flow mirrors the framework vocabulary: configure the environment, activate tooling, run validation, then transition into the mental model before you rely on API details.
    </div>

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
