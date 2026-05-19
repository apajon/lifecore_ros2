Sprint 18.3 - Define StateDescriptor.msg
========================================

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

Create ``lifecore_state/lifecore_state_msgs/msg/StateDescriptor.msg``.

Purpose
-------

``StateDescriptor`` defines one state field contract. It describes what a field
is, how it is identified, what type it carries, what direction it has, whether
it is writable, and what metadata helps humans and tools interpret it.

It must not contain the current observed runtime value.

Required Semantics
------------------

Include:

- compact numeric id;
- stable UUID;
- canonical key;
- type;
- direction;
- human-readable metadata;
- optional constraints;
- writable flag;
- safety-related flag;
- persistent flag if useful.

Recommended fields
------------------

Use a ROS 2 ``.msg``-compatible structure similar to:

.. code-block:: text

    std_msgs/Header header

    uint32 id
    unique_identifier_msgs/UUID uuid
    string key

    uint8 type
    uint8 direction

    string display_name
    string description
    string group
    string unit

    bool writable
    bool safety_related
    bool persistent

    float64 min_value
    float64 max_value
    bool has_min_value
    bool has_max_value

Include ``TYPE_*`` and ``DIR_*`` constants unless Sprint 18.8 creates separate
enum-like messages.

Constraints
-----------

- Do not include current value fields.
- Do not include ``default_value`` unless explicitly justified and documented as
  an ABI decision.
- Do not use JSON strings or arbitrary metadata maps.
- Do not add command or lifecycle semantics.

Documentation
-------------

Update ``lifecore_state/message_semantics.rst`` if the actual message differs
from the Sprint 17 sketch. Update
``lifecore_state/rfcs/sprint_18_message_notes.rst`` with rationale.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
