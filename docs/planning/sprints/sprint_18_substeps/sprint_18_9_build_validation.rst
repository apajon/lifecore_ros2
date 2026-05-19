Sprint 18.9 - Build Validation
==============================

**Status.** Planned.

**Track.** State Architecture / ROS ABI.

**Type.** Validation.

**Parent sprint.** :doc:`../active/sprint_18_lifecore_state_msgs_abi`.

Reference documents
-------------------

Before editing, read:

- ``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst``
- ``lifecore_state/message_semantics.rst``
- ``lifecore_state/package_boundaries.rst``
- ``lifecore_state/lifecycle_state_separation.rst``
- ``lifecore_state/terminology.rst``
- ``lifecore_state/anti_goals.rst``

Treat them as the Sprint 18 source of truth.

Locked decisions
----------------

- ``lifecore_state/`` is a repository-level logical folder, not a ROS 2 package.
- ``lifecore_state_msgs`` is the first real package to create.
- ``lifecore_state_core`` is deferred.
- ``lifecore_state_ros`` is deferred.
- ``lifecore_ros2`` must remain independent from ``lifecore_state``.
- ``StateDescription`` is a versioned collection of ``StateDescriptor`` entries.
- ``StateCommand`` v0 is single-target.
- Batched commands are deferred.
- ``StateCommand`` expresses intent, not observed truth.
- ``StateUpdate`` reports observed truth.

Conflict rule
-------------

If the task prompt conflicts with the Sprint 17 documents, stop and report the
conflict instead of inventing a third interpretation.

Objective
---------

Build and validate the Sprint 18 ``lifecore_state_msgs`` package.

Validation Goals
----------------

Verify that:

- ``lifecore_state/lifecore_state_msgs`` is discovered as a ROS 2 package;
- ``lifecore_state/`` parent is not discovered as a package;
- messages generate successfully;
- ``colcon build`` succeeds;
- no runtime Python package was accidentally added;
- no ``lifecore_state_core`` or ``lifecore_state_ros`` package exists;
- existing ``lifecore_ros2`` package behavior was not modified;
- ``package.xml`` dependencies are minimal and correct;
- ``CMakeLists.txt`` uses standard ``rosidl`` generation patterns;
- generated interfaces are visible through normal ROS 2 tooling when the
  environment allows it.

Commands to Consider
--------------------

Use commands appropriate to the repository environment, for example:

.. code-block:: bash

    colcon list
    colcon build --packages-select lifecore_state_msgs
    colcon test --packages-select lifecore_state_msgs
    colcon test-result --verbose

If the environment does not support a full ROS 2 build, document exactly what
could not be run and why.

Deliverable
-----------

Create ``lifecore_state/rfcs/sprint_18_build_validation.rst`` with:

- commands run;
- results;
- failures if any;
- warnings;
- generated package discovery results;
- confirmation of no parent package;
- confirmation of no runtime implementation.

Constraints
-----------

- Do not implement missing runtime code to satisfy build.
- Do not create unrelated packages.
- Do not change ``lifecore_ros2`` behavior.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
