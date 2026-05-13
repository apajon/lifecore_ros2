lifecore_ros2
=============

.. raw:: html

   <img src="_static/Logo_main_light_HD.png" class="index-logo index-logo--light" alt="lifecore_ros2">
   <img src="_static/Logo_main_dark_HD.png" class="index-logo index-logo--dark" alt="lifecore_ros2">

Explicit lifecycle composition for ROS 2 Jazzy
==============================================

.. Canonical positioning sentence — keep in sync with pyproject.toml project.description.
.. See CONTRIBUTING.md "Canonical positioning sentence".

.. container:: doc-hero

  .. container:: doc-hero__lead

    lifecore_ros2 is a minimal lifecycle composition library for ROS 2 Jazzy — no hidden state machine.

  ROS 2 lifecycle works well for nodes. lifecore_ros2 makes it practical for reusable components.

  It provides a small composition layer for building lifecycle-managed ROS 2 nodes from explicit, reusable
  components. Instead of concentrating lifecycle behavior in one large ``rclpy`` node class, it lets a lifecycle
  node own named components and drive their hooks through the native ROS 2 transition flow.

  .. container:: doc-hero__actions

    :doc:`Quickstart <quickstart>`
    :doc:`Mental Model <concepts/mental_model>`
    :doc:`API Reference <api>`

.. raw:: html

   <div class="lifecycle-map">
     <div class="lifecycle-step"><strong>⚙ Configure</strong><p>Start with environment setup, resource creation rules, and the ownership model that keeps ROS handles explicit.</p></div>
     <div class="lifecycle-step"><strong>▶ Activate</strong><p>Read how runtime behavior becomes live only through lifecycle transitions and explicit activation gates.</p></div>
     <div class="lifecycle-step"><strong>▶ Run</strong><p>Move into examples and API lookup once the lifecycle contract is clear.</p></div>
     <div class="lifecycle-step lifecycle-step--transition"><strong>🔁 Transition</strong><p>Use architecture and patterns to understand propagation, registration, and failure handling.</p></div>
     <div class="lifecycle-step"><strong>■ Shutdown</strong><p>Keep cleanup and release semantics in view so resources never outlive the lifecycle that created them.</p></div>
   </div>

.. code-block:: text

   Raw rclpy lifecycle:
   LifecycleNode
    ├── publishers
    ├── subscriptions
    ├── timers
    └── lifecycle logic mixed into one class

   lifecore_ros2:
   LifecycleComponentNode
    ├── LifecyclePublisherComponent
    ├── LifecycleSubscriberComponent
    ├── LifecycleTimerComponent
    ├── LifecycleParameterComponent
    └── LifecycleParameterObserverComponent

The library exists to make raw ``rclpy`` lifecycle code easier to structure and verify. Resource creation, activation,
deactivation, and cleanup stay explicit; component boundaries stay testable; and the library does not add a second
state machine behind ROS 2 lifecycle semantics.

What this is not
----------------

- A second lifecycle state machine.
- A plugin system or ROS 2 component container replacement.
- A behavior tree system, orchestration middleware, or launch replacement.
- A replacement for native ROS 2 lifecycle semantics.

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
They explain the library's lifecycle model, ownership rules, and recommended usage before you jump into symbol-level API details.

.. raw:: html

   <div class="state-box">
     <strong>Read the docs like a lifecycle.</strong>
     Quickstart gets a node running, Getting Started fixes the environment contract, Mental Model explains ownership, Architecture defines transition rules, and Examples shows the contract under load.
   </div>

.. list-table::
   :widths: 30 70
   :header-rows: 0

   * - :doc:`Quickstart <quickstart>`
     - Install from PyPI for an application project, or clone the repository to run the smallest composed lifecycle example.
   * - :doc:`Getting Started <getting_started>`
     - Review prerequisites, validation commands, and reference setup details after the quickstart.
   * - :doc:`Mental Model <concepts/mental_model>`
     - Build the right lifecycle composition intuition before diving into lifecycle internals and extension points.
   * - :doc:`Architecture <architecture>`
     - Read the lifecycle ownership model, transition rules, and component contracts.
   * - :doc:`Recommended Patterns and Anti-Patterns <patterns>`
     - Learn the concrete practices that keep components explicit, testable, and lifecycle-aligned.
   * - :doc:`Testing Utilities <testing>`
     - Reuse fakes, fixtures, assertions, and helpers for lifecycle-focused tests.
   * - :doc:`Examples <examples>`
     - Walk through runnable publisher, subscriber, parameter ownership, parameter observation, service, watchdog, and composed node examples.
   * - :doc:`Migration from Raw rclpy <migration_from_rclpy>`
     - Compare the library approach with direct lifecycle code in ``rclpy``.

.. raw:: html

   <div class="state-box transition">
     <strong>Need a side-by-side comparison?</strong>
     Use the <a href="https://github.com/apajon/lifecore_ros2_examples/blob/main/examples/lifecycle_comparison/README.md">sensor watchdog comparison</a>
     in the companion examples repository to compare the same node behavior across plain ROS 2,
     classic lifecycle, and lifecore_ros2.
   </div>

Documentation map
-----------------

The guides section is the recommended reading path for new users.
Use the API reference afterward as a lookup surface for classes, methods, and module details.

Lifecycle-oriented reading order:

#. Configure the environment and first node with :doc:`Quickstart <quickstart>` and :doc:`Getting Started <getting_started>`.
#. Activate the mental model with :doc:`Mental Model <concepts/mental_model>`.
#. Understand transition ownership with :doc:`Architecture <architecture>` and :doc:`Recommended Patterns and Anti-Patterns <patterns>`.
#. Test lifecycle boundaries with :doc:`Testing Utilities <testing>`.
#. Run concrete flows with :doc:`Examples <examples>`, then use the `companion sensor watchdog comparison <https://github.com/apajon/lifecore_ros2_examples/blob/main/examples/lifecycle_comparison/README.md>`_ for a side-by-side view against plain ROS 2 and classic lifecycle before comparing tradeoffs in :doc:`Migration from Raw rclpy <migration_from_rclpy>`.

.. toctree::
   :maxdepth: 1
   :caption: Guides

   quickstart
   getting_started
   concepts/mental_model
   architecture
   patterns
   testing
   migration_from_rclpy
   examples
   faq

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api

.. toctree::
   :maxdepth: 1
   :caption: Planning

   planning/README
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
