Sprint 18.4 - Define StateDescription.msg
=========================================

**Status.** Planned.

**Track.** State Architecture / ROS ABI.

**Type.** Message contract.

**Parent sprint.** :doc:`../active/sprint_18_lifecore_state_msgs_abi`.

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

Documentation
-------------

Ensure docs consistently say:

``StateDescription = versioned collection of StateDescriptor entries.``

Update ``lifecore_state/message_semantics.rst``,
``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst``, and
``lifecore_state/rfcs/sprint_18_message_notes.rst`` as needed.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
