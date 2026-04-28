lifecore_ros2
=============

Explicit lifecycle composition for ROS 2 Jazzy
==============================================

.. Canonical positioning sentence — keep in sync with pyproject.toml project.description.
.. See CONTRIBUTING.md "Canonical positioning sentence".

.. container:: doc-hero

  .. container:: doc-hero__lead

    lifecore_ros2 is a minimal lifecycle composition library for ROS 2 Jazzy — no hidden state machine.

  It provides a small composition layer for building lifecycle-managed ROS 2 nodes from explicit, reusable
  components. Instead of concentrating lifecycle behavior in one large ``rclpy`` node class, it lets a lifecycle
  node own named components and drive their hooks through the native ROS 2 transition flow.

  .. container:: doc-hero__actions

    :doc:`Quickstart <quickstart>`
    :doc:`Mental Model <concepts/mental_model>`
    :doc:`API Reference <api>`

The library exists to make raw ``rclpy`` lifecycle code easier to structure and verify. Resource creation, activation,
deactivation, and cleanup stay explicit; component boundaries stay testable; and the framework does not add a second
state machine behind ROS 2 lifecycle semantics.

Why lifecore_ros2?
------------------

- Explicit lifecycle flow from configure to activate, deactivate, and cleanup.
- Component ownership is centered in ``LifecycleComponentNode``.
- Activation and deactivation behavior stays predictable and visible in code.
- No hidden state machine beyond native ROS 2 lifecycle semantics.
- Testable component boundaries with small lifecycle hooks.

When to use it
--------------

- Composed robotics nodes built from multiple lifecycle-aware parts.
- Lifecycle-managed publishers and subscribers.
- Reusable ROS 2 components with explicit ownership and cleanup.
- Projects that need strict startup, pause, resume, and shutdown behavior.

Start here
----------

Begin with the guides below.
They explain the framework's lifecycle model, ownership rules, and recommended usage before you jump into symbol-level API details.

.. list-table::
   :widths: 30 70
   :header-rows: 0

   * - :doc:`Quickstart <quickstart>`
     - Clone the repository, install the dev environment, and run the smallest composed lifecycle example.
   * - :doc:`Getting Started <getting_started>`
     - Review prerequisites, validation commands, and reference setup details after the quickstart.
   * - :doc:`Mental Model <concepts/mental_model>`
     - Build the right framework intuition before diving into lifecycle internals and extension points.
   * - :doc:`Architecture <architecture>`
     - Read the lifecycle ownership model, transition rules, and component contracts.
   * - :doc:`Recommended Patterns and Anti-Patterns <patterns>`
     - Learn the concrete practices that keep components explicit, testable, and lifecycle-aligned.
   * - :doc:`Examples <examples>`
     - Walk through runnable publisher, subscriber, and composed node examples.
   * - :doc:`Migration from Raw rclpy <migration_from_rclpy>`
     - Compare the framework approach with direct lifecycle code in ``rclpy``.

Documentation map
-----------------

The guides section is the recommended reading path for new users.
Use the API reference afterward as a lookup surface for classes, methods, and module details.

.. toctree::
   :maxdepth: 1
   :caption: Guides

   quickstart
   getting_started
   concepts/mental_model
   architecture
   patterns
   migration_from_rclpy
   examples
   faq

.. toctree::
   :maxdepth: 1
   :caption: API Reference

   api

.. toctree::
   :maxdepth: 1
   :caption: Planning

   planning/README
   planning/backlog
   planning/adoption_hardening
   planning/examples_repo
   planning/sprints/README

.. toctree::
   :maxdepth: 1
   :caption: Project

   changelog
   contributing
   mempalace_strategy

.. toctree::
   :maxdepth: 2
   :caption: Design notes

   design_notes/runtime_introspection
   design_notes/observability
   design_notes/dynamic_components
   design_notes/error_handling_contract
   design_notes/lifecycle_policies
   design_notes/callback_groups
