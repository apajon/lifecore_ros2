Sprint 18.2 - Package Scaffold
==============================

**Status.** Planned.

**Track.** State Architecture / ROS ABI.

**Type.** ROS 2 interface package scaffolding.

**Parent sprint.** :doc:`../active/sprint_18_lifecore_state_msgs_abi`.

Objective
---------

Create the ROS 2 interface package ``lifecore_state/lifecore_state_msgs/``.
This is the first real ``lifecore_state`` package.

Architecture Decision
---------------------

The parent folder ``lifecore_state/`` is a repository-level logical folder only.
It must not contain ``package.xml``, ``CMakeLists.txt``, Python package
metadata, or installable code.

Create
------

- ``lifecore_state/lifecore_state_msgs/package.xml``
- ``lifecore_state/lifecore_state_msgs/CMakeLists.txt``
- ``lifecore_state/lifecore_state_msgs/msg/``

Expected package name: ``lifecore_state_msgs``.

Expected build type: standard ROS 2 interface package with
``rosidl_default_generators``.

Dependencies
------------

Choose only dependencies justified by the message fields. Candidates:

- ``std_msgs``
- ``unique_identifier_msgs``
- ``builtin_interfaces`` if needed
- ``rosidl_default_generators``
- ``rosidl_default_runtime``

Constraints
-----------

- Do not create ``lifecore_state_core``.
- Do not create ``lifecore_state_ros``.
- Do not modify ``lifecore_ros2`` runtime code.
- Do not add Python modules.
- Do not add publishers, subscribers, QoS code, registry logic, lifecycle logic,
  command handling, or synchronization behavior.

Validation
----------

Verify that the repository has:

- no ``package.xml`` directly under ``lifecore_state/``;
- one ``package.xml`` under ``lifecore_state/lifecore_state_msgs/``;
- no runtime Python code under ``lifecore_state/``.

Deliverable
-----------

Create or update ``lifecore_state/rfcs/sprint_18_package_scaffold.rst`` with:

- files created;
- dependencies chosen;
- why this remains messages-only;
- what remains deferred.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
