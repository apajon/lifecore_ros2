Sprint 18.11 - Main Sprint Planning File
========================================

**Status.** Planned.

**Track.** State Architecture / ROS ABI.

**Type.** Planning synchronization.

**Parent sprint.** :doc:`../active/sprint_18_lifecore_state_msgs_abi`.

Objective
---------

Keep the active Sprint 18 planning file synchronized with the accepted Sprint
18 scope and with the real repository sprint organization.

Planning File
-------------

Use the existing active sprint file:

``docs/planning/sprints/active/sprint_18_lifecore_state_msgs_abi.rst``

The file should state that Sprint 18 is a ROS 2 message ABI prototype with no
runtime implementation.

Required Content
----------------

The main file must cover:

- Sprint 17 context;
- goals;
- non-goals;
- expected package path;
- expected messages;
- deliverables;
- acceptance criteria;
- open questions;
- final review expectations;
- link to the Sprint 18 sub-sprints overview.

Required Decisions
------------------

Preserve these decisions:

- create ``lifecore_state_msgs`` package;
- define prototype ``.msg`` contracts;
- validate ``colcon`` build;
- keep ``lifecore_state_core`` deferred;
- keep ``lifecore_state_ros`` deferred;
- preserve ``lifecore_ros2`` independence;
- keep parent ``lifecore_state/`` as logical grouping only.

Constraints
-----------

- Do not add runtime implementation to satisfy planning text.
- Do not describe future packages as existing.
- Do not let older names such as ``StateValue`` override the Sprint 17 accepted
  ``StateSample`` concept.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
