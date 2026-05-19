Sprint 18.6 - Define StateUpdate.msg
====================================

**Status.** Planned.

**Track.** State Architecture / ROS ABI.

**Type.** Message contract.

**Parent sprint.** :doc:`../active/sprint_18_lifecore_state_msgs_abi`.

Objective
---------

Create ``lifecore_state/lifecore_state_msgs/msg/StateUpdate.msg``.

Purpose
-------

``StateUpdate`` represents a published batch of observed ``StateSample`` values.
It reports observed truth. It does not express requested mutation, and it is not
a command or descriptor list.

Required Semantics
------------------

Include:

- header;
- source UUID;
- schema UUID;
- sequence;
- description version;
- update mode;
- array of ``StateSample`` entries.

Recommended fields
------------------

.. code-block:: text

    std_msgs/Header header

    unique_identifier_msgs/UUID source_uuid
    unique_identifier_msgs/UUID schema_uuid

    uint64 sequence
    uint64 description_version
    uint8 update_mode

    StateSample[] samples

    uint8 UPDATE_UNKNOWN=0
    uint8 UPDATE_FULL=1
    uint8 UPDATE_DELTA=2

Timestamp Semantics
-------------------

``StateUpdate.header.stamp`` is the publish/batch timestamp. Each
``StateSample.header.stamp`` is the source observation timestamp. These
timestamps may differ.

Sequence and Version Semantics
------------------------------

``sequence`` is per ``source_uuid`` stream and helps detect lost, duplicated,
out-of-order, or discontinuous updates.

``description_version`` identifies the ``StateDescription`` version used to
interpret descriptor ids, types, and semantics. Receivers must not blindly apply
updates against a different description version.

Update Mode Semantics
---------------------

``UPDATE_FULL`` contains a complete snapshot for the publisher scope.
``UPDATE_DELTA`` contains only changed samples and assumes compatible prior
state.

Constraints
-----------

- Do not add command fields.
- Do not add registry behavior.
- Do not add QoS or lifecycle implementation.
- Preserve that delta updates should not be applied while inactive, while full
  snapshots may be cached while inactive only by explicit policy.

Documentation
-------------

Update ``lifecore_state/message_semantics.rst`` and
``lifecore_state/rfcs/sprint_18_message_notes.rst`` as needed.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
