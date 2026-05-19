Sprint 18.2 - Package Scaffold Report
=====================================

**Status.** Completed.

**Track.** State Architecture / ROS ABI.

**Scope.** ROS 2 interface package scaffold only. This step creates the first
real ``lifecore_state`` package folder and its build metadata, but does not add
message definitions, runtime Python code, lifecycle behavior, or ROS transport
logic.

Purpose
-------

This report records the Sprint 18.2 package scaffold for
``lifecore_state/lifecore_state_msgs/``.

The scaffold keeps the parent ``lifecore_state/`` folder as a repository-level
logical grouping while introducing the first real ROS 2 package exactly where
Sprint 17 and Sprint 18 require it.

Files created
-------------

- ``lifecore_state/lifecore_state_msgs/package.xml``
- ``lifecore_state/lifecore_state_msgs/CMakeLists.txt``
- ``lifecore_state/lifecore_state_msgs/msg/``
- ``lifecore_state/lifecore_state_msgs/msg/.gitkeep``

Dependencies chosen
-------------------

The package scaffold declares only the dependencies justified by the documented
Sprint 17 message semantics sketches:

- ``rosidl_default_generators`` as the standard ROS 2 interface generation
  build dependency for the future ``.msg`` files.
- ``rosidl_default_runtime`` as the runtime dependency expected by generated
  interfaces.
- ``std_msgs`` because the Sprint 17 message semantics repeatedly use
  ``Header`` for description, sample, update, and command transport timestamps.
- ``unique_identifier_msgs`` because the Sprint 17 message semantics use UUID
  fields such as ``schema_uuid``, ``descriptor_uuid``, ``source_uuid``, and
  ``command_uuid``.

``builtin_interfaces`` was not added at this stage. The current documented
message direction uses ``std_msgs/Header`` rather than direct ``Time`` fields,
so adding ``builtin_interfaces`` now would be broader than the present
justification.

Why this remains messages-only
------------------------------

The scaffold stays within the Sprint 18 messages-only boundary:

- the parent ``lifecore_state/`` folder remains non-package documentation and
  review material;
- ``lifecore_state_msgs`` contains only ROS 2 package metadata and an empty
  tracked ``msg/`` directory reserved for later message definitions;
- no Python modules were added;
- no publishers, subscribers, QoS helpers, registry logic, lifecycle logic,
  synchronization behavior, or command handling code was added;
- ``lifecore_ros2`` runtime code remains untouched.

The ``CMakeLists.txt`` intentionally stops at package scaffolding. Message
generation is deferred until the later Sprint 18 sub-steps add concrete
``.msg`` files.

Deferred work
-------------

The following items remain explicitly deferred after Sprint 18.2:

- all concrete ``.msg`` definitions for ``StateDescriptor``,
  ``StateDescription``, ``StateSample``, ``StateUpdate``, and
  ``StateCommand``;
- any optional enum-like message split decision;
- ``rosidl_generate_interfaces(...)`` wiring once message files exist;
- build validation with ``colcon`` after the message set is present;
- any ``lifecore_state_core`` package;
- any ``lifecore_state_ros`` package;
- any runtime Python code, registry behavior, projections, publishers,
  subscribers, lifecycle integration, or command execution logic.

Validation summary
------------------

Sprint 18.2 preserves the required scaffold constraints:

- there is still no ``package.xml`` directly under ``lifecore_state/``;
- there is one real package scaffold under
  ``lifecore_state/lifecore_state_msgs/``;
- no runtime Python code was added under ``lifecore_state/``.

Review requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is
accepted.
