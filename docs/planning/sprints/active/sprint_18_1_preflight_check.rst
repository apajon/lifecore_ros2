Sprint 18.1 - Pre-flight Check
===============================

**Status.** Active.

**Track.** State Architecture / ROS ABI.

**Type.** Pre-flight check.

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

Sprint 18 pre-flight check only.

Do not redo a full pre-audit. Sprint 17 already produced the architecture,
package boundary, message semantics, and static check documents.

Verify that the repository state still matches the Sprint 17 closure
assumptions before creating ``lifecore_state_msgs``.

Checks
------

Perform and record the following eight checks:

1. ``lifecore_state/`` exists.
2. ``lifecore_state/`` has no ``package.xml``.
3. ``lifecore_state/`` has no ``CMakeLists.txt``.
4. ``lifecore_state/`` currently contains documentation only.
5. ``lifecore_state/lifecore_state_msgs`` does not already exist.
6. ``lifecore_state_core`` does not already exist.
7. ``lifecore_state_ros`` does not already exist.
8. Sprint 17 docs define:

   - ``lifecore_state_msgs`` as the future ROS 2 ABI package;
   - ``lifecore_state_core`` as deferred;
   - ``lifecore_state_ros`` as deferred;
   - ``StateDescription`` as a versioned collection of ``StateDescriptor``
     entries;
   - ``StateCommand`` v0 as single-target.

Constraints
-----------

- Do not create ROS packages.
- Do not create ``.msg`` files.
- Do not modify build files.
- Do not implement runtime code.

Deliverable
-----------

Create ``lifecore_state/rfcs/sprint_18_preflight_check.rst`` with:

- checks performed;
- pass/fail result for each check;
- any mismatch found;
- whether Sprint 18 package scaffolding can start.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
