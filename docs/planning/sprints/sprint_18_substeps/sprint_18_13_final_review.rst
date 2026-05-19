Sprint 18.13 - Final Review
===========================

**Status.** Planned.

**Track.** State Architecture / ROS ABI.

**Type.** Final review.

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

Perform the final Sprint 18 review.

Deliverable
-----------

Create ``lifecore_state/rfcs/sprint_18_final_review.rst``.

Review Areas
------------

Repository structure:

- ``lifecore_state/`` parent has no ``package.xml``;
- ``lifecore_state/lifecore_state_msgs`` has ``package.xml``;
- ``lifecore_state/lifecore_state_msgs`` has ``CMakeLists.txt``;
- ``lifecore_state/lifecore_state_msgs/msg`` contains expected messages;
- no ``lifecore_state_core`` or ``lifecore_state_ros`` package exists.

Build:

- ``colcon list`` sees ``lifecore_state_msgs``;
- ``colcon build --packages-select lifecore_state_msgs`` succeeds;
- ``colcon test`` succeeds or limitations are documented.

Message semantics:

- ``StateDescriptor`` equals one field contract;
- ``StateDescription`` equals versioned descriptor collection;
- ``StateSample`` equals one observed value;
- ``StateUpdate`` equals batch of observed truth;
- ``StateCommand`` equals single-target intent;
- batched commands remain deferred.

Field-level review:

- identity fields are coherent;
- type, quality, source, and direction fields are coherent;
- timestamps are coherent;
- sequence is present;
- ``description_version`` is present;
- ``schema_uuid`` is present where needed;
- ``update_mode`` is present in ``StateUpdate``.

Scope control:

- no registry behavior;
- no projection behavior;
- no publisher/subscriber behavior;
- no command handling;
- no lifecycle integration;
- no QoS implementation;
- no code generation.

Risks and Follow-ups
--------------------

List ABI concerns, field naming concerns, future compact message concerns,
future command feedback concerns, and future core implementation concerns.

Sprint 19 Recommendation
------------------------

If Sprint 18 passes, the likely next sprint is:

``Sprint 19 - lifecore_state_core pure Python model``

Sprint 19 must not start until message ABI review is accepted.

Final Decision
--------------

Write one of:

- Sprint 18 accepted.
- Sprint 18 accepted with minor follow-ups.
- Sprint 18 not accepted.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
