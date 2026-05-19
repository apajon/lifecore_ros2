Sprint 18.5 - Define StateSample.msg
====================================

**Status.** Planned.

**Track.** State Architecture / ROS ABI.

**Type.** Message contract.

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

Create ``lifecore_state/lifecore_state_msgs/msg/StateSample.msg``.

Purpose
-------

``StateSample`` represents one observed state value at a source timestamp. It is
runtime truth as observed by a source, but only for one field. It is not
metadata, a descriptor, or a command.

Required Semantics
------------------

Include:

- header;
- descriptor identity reference;
- type;
- quality;
- source;
- explicit variant value fields.

Recommended fields
------------------

.. code-block:: text

    std_msgs/Header header

    uint32 descriptor_id
    unique_identifier_msgs/UUID descriptor_uuid
    string key

    uint8 type
    uint8 quality
    uint8 source

    bool bool_value
    int64 int_value
    uint64 uint_value
    float64 float_value
    string string_value

Timestamp Semantics
-------------------

``StateSample.header.stamp`` is the source timestamp: the time when this value
was true or observed at the source. It is not necessarily the publication time
of the containing ``StateUpdate``.

Variant Semantics
-----------------

``type`` selects exactly one active value field. Never interpret multiple value
fields at the same time.

Constants
---------

Include quality and source constants unless Sprint 18.8 creates separate
enum-like messages. Repeat type constants consistently unless Sprint 18.8
extracts ``StateType.msg``.

Constraints
-----------

- Do not add metadata or descriptor fields such as ``unit`` or ``description``.
- Do not add command or lifecycle semantics.
- Do not add callback, registry, publisher, or subscriber behavior.

Documentation
-------------

Update ``lifecore_state/message_semantics.rst`` and
``lifecore_state/rfcs/sprint_18_message_notes.rst`` as needed.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
