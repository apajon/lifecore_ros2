Quickstart
==========

Audience
--------

This page is the fastest path from a fresh clone to a running example.
It uses the smallest composed lifecycle example already in the repository:
``examples/minimal_node.py``.

Before You Start
----------------

- ROS 2 Jazzy must already be installed on the system.
- ``uv`` must already be available in your shell.
- ``rclpy`` comes from the system ROS installation, not from PyPI.

1. Clone the Repository
-----------------------

.. code-block:: bash

   git clone https://github.com/apajon/lifecore_ros2.git
   cd lifecore_ros2

2. Install Development Dependencies
-----------------------------------

Sync the local project environment with the repository's development tools:

.. code-block:: bash

   uv sync --extra dev

3. Build the ROS 2 Workspace
----------------------------

This repository does not currently ship a ``colcon`` package or generate a local
``install/setup.bash`` overlay. The build command supported by the project today is the
package build below:

.. code-block:: bash

   uv run python -m build

4. Source the Workspace
-----------------------

Because this repository does not generate a local overlay setup script today, source the
system ROS 2 environment so ``rclpy`` and the ROS CLI are available:

.. code-block:: bash

   source /opt/ros/jazzy/setup.bash

5. Run the Minimal Composed Lifecycle Example
---------------------------------------------

Start the node in one terminal:

.. code-block:: bash

   uv run python examples/minimal_node.py

In a second terminal, from the same repository, source ROS 2 Jazzy again and drive
the lifecycle transitions:

.. code-block:: bash

   source /opt/ros/jazzy/setup.bash
   ros2 lifecycle set /minimal_lifecore_node configure
   ros2 lifecycle set /minimal_lifecore_node activate

You can then stop the node cleanly with:

.. code-block:: bash

   ros2 lifecycle set /minimal_lifecore_node deactivate
   ros2 lifecycle set /minimal_lifecore_node cleanup
   ros2 lifecycle set /minimal_lifecore_node shutdown

Expected Behavior
-----------------

At a high level, you should observe the following:

- the node starts and waits for lifecycle commands
- ``configure`` triggers the component's ``_on_configure`` hook and logs
  ``[logger_component] on_configure called``
- ``activate`` succeeds without extra component output because the base activation hook is silent by design
- there are no publishers or subscribers in this example; it exists to show the smallest explicit composition pattern

Next Step
---------

After this minimal composed example works, continue with :doc:`Examples <examples>`
to run the subscriber, publisher, telemetry, and composed pipeline walkthroughs.
