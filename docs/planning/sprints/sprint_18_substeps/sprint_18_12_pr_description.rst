Sprint 18.12 - Pull Request Description
=======================================

**Status.** Planned.

**Track.** State Architecture / ROS ABI.

**Type.** Review preparation.

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

Prepare a pull request description for Sprint 18.

Deliverable
-----------

Create ``lifecore_state/rfcs/sprint_18_pr_description.md``.

Title
-----

``Sprint 18: lifecore_state_msgs ABI prototype``

Required Sections
-----------------

The PR description must include:

- Context;
- What changed;
- Message contracts added;
- Key decisions;
- What did not change;
- Validation;
- Review focus;
- Checklist.

Required Content
----------------

Mention that Sprint 17 closed the architecture/RFC phase,
``lifecore_state_msgs`` is the first real package under ``lifecore_state/``, and
the parent ``lifecore_state/`` folder remains logical only.

List package metadata, message files, docs updates, and build validation docs.

Highlight these decisions:

- ``StateDescription`` is a versioned collection of ``StateDescriptor`` entries.
- ``StateCommand`` v0 is single-target.
- Batched commands are deferred.
- ``StateCommand`` is intent.
- ``StateUpdate`` is observed truth.
- ``StateSample`` timestamp is source timestamp.
- ``StateUpdate`` timestamp is publish/batch timestamp.

Scope Guard
-----------

The PR description must explicitly say there is no ``lifecore_state_core``, no
``lifecore_state_ros``, no registry, no projection, no publisher/subscriber, no
lifecycle integration, no runtime Python code, and no behavior change in
``lifecore_ros2``.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
