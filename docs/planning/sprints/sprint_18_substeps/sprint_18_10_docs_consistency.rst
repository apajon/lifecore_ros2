Sprint 18.10 - Documentation Consistency Pass
=============================================

**Status.** Planned.

**Track.** State Architecture / ROS ABI.

**Type.** Documentation review.

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

Perform a documentation consistency pass after creating ``lifecore_state_msgs``.

Documents to Review
-------------------

- ``lifecore_state/README.rst``
- ``lifecore_state/message_semantics.rst``
- ``lifecore_state/package_boundaries.rst``
- ``lifecore_state/lifecycle_state_separation.rst``
- ``lifecore_state/anti_goals.rst``
- ``lifecore_state/terminology.rst``
- ``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst``
- ``docs/planning/sprints/active/sprint_18_lifecore_state_msgs_abi.rst``

Consistency Checks
------------------

Verify that:

- ``StateDescription`` is always a versioned collection of
  ``StateDescriptor`` entries;
- ``StateCommand`` v0 is always single-target;
- batched commands are always deferred;
- ``StateCommand`` is always intent, not truth;
- ``StateUpdate`` is observed truth;
- ``StateSample`` carries source timestamp semantics;
- ``StateUpdate`` carries publish/batch timestamp semantics;
- ``StateUpdate`` has sequence, ``description_version``, and ``update_mode``;
- ``StateDescription`` has ``schema_uuid`` and ``description_version``;
- ``StateDescriptor`` does not carry current runtime value;
- ``lifecore_state_msgs`` is described as a real package;
- ``lifecore_state_core`` and ``lifecore_state_ros`` remain deferred;
- ``lifecore_state/`` parent is still not a package;
- no docs imply runtime registry, publisher/subscriber, or lifecycle integration
  exists.

Deliverable
-----------

Create ``lifecore_state/rfcs/sprint_18_docs_consistency_review.rst`` with:

- inconsistencies found;
- corrections applied;
- unresolved questions;
- recommended review focus.

Constraints
-----------

- Do not expand the scope.
- Do not add new architecture beyond Sprint 18.
- Do not implement runtime behavior.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
