Sprint 18.12 - Pull Request Description
=======================================

**Status.** Planned.

**Track.** State Architecture / ROS ABI.

**Type.** Review preparation.

**Parent sprint.** :doc:`../active/sprint_18_lifecore_state_msgs_abi`.

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
