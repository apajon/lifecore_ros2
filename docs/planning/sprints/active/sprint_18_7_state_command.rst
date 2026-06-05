Sprint 18.7 - Define StateCommand.msg
=====================================

**Status.** In Progress.

**Track.** State Architecture / ROS ABI.

**Type.** Message contract.

**Parent sprint.** :doc:`sprint_18_lifecore_state_msgs_abi`.

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

Create ``lifecore_state/lifecore_state_msgs/msg/StateCommand.msg``.

Purpose
-------

``StateCommand`` v0 represents a single-target requested mutation. It expresses
intent. It is not observed truth. Batched command semantics are explicitly
deferred until a future need reopens the decision.

Required Semantics
------------------

Include:

- header;
- source UUID;
- target UUID;
- schema UUID;
- sequence;
- description version;
- target descriptor identity;
- type;
- desired value as explicit variant fields.

Recommended fields
------------------

.. code-block:: text

    std_msgs/Header header

    unique_identifier_msgs/UUID source_uuid
    unique_identifier_msgs/UUID target_uuid
    unique_identifier_msgs/UUID schema_uuid

    uint64 sequence
    uint64 description_version

    uint32 target_descriptor_id
    unique_identifier_msgs/UUID target_descriptor_uuid
    string target_key

    uint8 type

    bool bool_value
    int64 int_value
    uint64 uint_value
    float64 float_value
    string string_value

Semantics
---------

``StateCommand`` means: I request this target field to change to this desired
value.

It does not mean: this value is already true.

Acceptance or rejection is not encoded by ``StateCommand`` itself. Future
feedback may be represented through ``StateUpdate`` reflecting an observed
change, service responses, action feedback, or a dedicated command status
message.

Constraints
-----------

- Do not make ``StateCommand`` a batch.
- Do not include ``StateSample[]`` in v0.
- Do not describe command as truth.
- Do not implement command handling, lifecycle behavior, registry behavior, or
  validation logic.

Documentation
-------------

Update ``lifecore_state/message_semantics.rst``,
``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst``, and
``lifecore_state/rfcs/sprint_18_message_notes.rst`` as needed.

Ensure docs say:

- ``StateCommand`` v0 is single-target.
- Batched commands are deferred.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
