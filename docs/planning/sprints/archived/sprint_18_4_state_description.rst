Sprint 18.4 - Define StateDescription.msg
=========================================

**Status.** Archived.

**Track.** State Architecture / ROS ABI.

**Type.** Message contract.

**Parent sprint.** :doc:`../active/sprint_18_lifecore_state_msgs_abi`.

**Completion date.** 2026-05-19.

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

Create ``lifecore_state/lifecore_state_msgs/msg/StateDescription.msg``.

Purpose
-------

``StateDescription`` is a versioned collection of ``StateDescriptor`` entries.
It represents a coherent schema/scope description. It is not one descriptor,
runtime state, a state value, or a command.

Required Semantics
------------------

Include:

- header;
- schema UUID;
- description version;
- list of ``StateDescriptor`` entries.

Recommended fields
------------------

.. code-block:: text

    std_msgs/Header header

    unique_identifier_msgs/UUID schema_uuid
    uint64 description_version

    StateDescriptor[] descriptors

Semantics
---------

- ``header.stamp`` is the time this description was published or generated.
- ``schema_uuid`` identifies the schema/scope.
- ``description_version`` increments when the descriptor set or descriptor
  meaning changes.
- ``descriptors`` contains the coherent collection of descriptor entries.

Notes
-----

Do not implement QoS in this package. Documentation should state that
``StateDescription`` is intended for reliable, ``transient_local``,
``keep_last(1)`` delivery.

``StateDescription`` may be received and cached while a lifecycle node or
component is inactive because transient-local delivery may occur as soon as a
subscription is created during configure.

Constraints
-----------

- Do not add runtime sample values.
- Do not add command values.
- Do not add registry logic, QoS code, or lifecycle implementation.
- Do not split into ``StateDescriptionArray`` without a strong reason.

Deliverables
-----------

✅ **Completed:**

- ``lifecore_state/lifecore_state_msgs/msg/StateDescription.msg`` — created
- ``lifecore_state/rfcs/sprint_18_4_state_description_design_notes.rst`` — created
- ``CMakeLists.txt`` updated to include StateDescription message generation

Documentation
-------------

Ensure docs consistently say:

``StateDescription = versioned collection of StateDescriptor entries.``

Update ``lifecore_state/message_semantics.rst``,
``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst``, and
``lifecore_state/rfcs/sprint_18_message_notes.rst`` as needed.

Review Status
-----------

✅ Reviewed and accepted.

ChatGPT or Codex reviewed and validated the deliverables before archiving.
