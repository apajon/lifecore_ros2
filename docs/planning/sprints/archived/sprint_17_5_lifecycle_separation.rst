Sprint 17.5 — Write Lifecycle/State Separation
==============================================

**Status.** Archived.

**Track.** Architecture / Research.

**Type.** Documentation.

**Parent sprint.** :doc:`../active/sprint_17_lifecore_state_rfc`.

Feature goal
------------

Write ``lifecore_state/lifecycle_state_separation.rst`` so Sprint 17 clearly
separates ROS 2 lifecycle readiness from future ``lifecore_state`` truth,
caching, update, and command semantics before any implementation is proposed.

Lifecycle behavior contract
---------------------------

Sprint 17.5 is documentation-only. It must not change configure, activate,
deactivate, cleanup, shutdown, or error behavior for any existing
``lifecore_ros2`` node or component.

The document clarifies the expected semantic boundary:

- **configure:** subscribers and publishers may be created by future designs,
  but Sprint 17.5 changes no runtime creation path.
- **activate:** activation enables runtime behavior and command handling, but
  Sprint 17.5 changes no activation gate in code.
- **deactivate:** deactivation stops active behavior, but does not by itself
  prove that remote truth, cached description, or registry knowledge vanished.
- **cleanup:** cleanup releases local resources, but does not imply that a
  remote state source was cleared.
- **shutdown:** shutdown semantics remain unchanged.
- **error:** error transition and recovery remain unchanged.

Context
-------

Sprint 17.4 stabilized the glossary so this document could use terms such as
``StateDescription``, ``StateUpdate``, ``StateCommand``, snapshot, delta,
registry, projection, authority, and quality without redefining them.

The key design issue was preserved explicitly: a ``transient_local``
description message may arrive as soon as a subscriber exists, including while
the component is inactive. The archived document therefore explains why a
global "ignore everything while inactive" rule is too blunt.

Document location
-----------------

**File:** ``lifecore_state/lifecycle_state_separation.rst``

Acceptance criteria
-------------------

- [x] Lifecycle controls clearly separated from state controls
- [x] StateDescription caching rule explained
- [x] StateUpdate delta rule explained
- [x] StateCommand activation requirement explained
- [x] Pseudo-code sketches present and marked non-final
- [x] InactiveMessagePolicy enum documented
- [x] Defaults recommended for each message type
- [x] Mandatory review phrase included

Success criteria
----------------

Developers reading this document understand:

- Why global activation gates do not work for all callback categories
- When a callback may fire before active state
- What can remain cached across lifecycle changes
- Why transient_local delivery matters for future design

Implementation notes
--------------------

Completed in ``lifecore_state/lifecycle_state_separation.rst``.
The document remains architecture-only and does not create a runtime API, a
message ABI, or a new lifecycle policy surface in current code.

Review requirement
------------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."