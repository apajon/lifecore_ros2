Sprint 17.6 — Write Package Boundaries
======================================

**Status.** Archived.

**Track.** Architecture / Research.

**Type.** Documentation.

**Objective.** Define future package separation for ``lifecore_state`` clearly,
with precise dependency rules and responsibility boundaries.

**Parent sprint.** :doc:`../active/sprint_17_lifecore_state_rfc`.

Feature goal
------------

Write ``lifecore_state/package_boundaries.rst`` so Sprint 17 documents the
future package split for ``lifecore_state`` with clear responsibilities,
dependency directions, and extraction constraints before any package is created.

Lifecycle behavior contract
---------------------------

Sprint 17.6 is documentation-only. It does not change configure, activate,
deactivate, cleanup, shutdown, or error behavior for any existing
``lifecore_ros2`` node or component.

Context
-------

Sprint 17 established that ``lifecore_state/`` is a logical documentation-only
folder, not a ROS 2 package and not a Python runtime package. Sprint 17.6 then
documented the future split between ``lifecore_state_msgs``,
``lifecore_state_core``, and ``lifecore_state_ros`` with explicit dependency
rules and extraction constraints.

Document location
-----------------

**File:** ``lifecore_state/package_boundaries.rst``

Acceptance criteria
-------------------

- [x] Future package roles clearly documented
- [x] Dependency rules explicit and mandatory
- [x] No circular dependencies possible
- [x] ``lifecore_state/`` confirmed as logical grouping
- [x] ``lifecore_ros2`` independence documented
- [x] ``lifecore_state_core`` Python-only documented
- [x] Extraction path viable
- [x] Mandatory review phrase included

Content validation checklist
----------------------------

- [x] Each package has clear, non-overlapping responsibility
- [x] Dependency direction is acyclic
- [x] ``lifecore_ros2`` needs not change
- [x] Future packages can be developed independently
- [x] ABI boundaries are explicit
- [x] Python boundaries are explicit

Success criteria
----------------

A future developer reading this document can:

- Explain why three packages exist
- Implement each without depending on each other except as documented
- Avoid architectural mistakes such as circular dependencies or responsibility
  leakage
- Extract the future packages to separate repos if needed

Implementation notes
--------------------

Completed in ``lifecore_state/package_boundaries.rst``. The document remains
architecture-only and does not create any package metadata, runtime API, or
ROS interface package.

Review requirement
------------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."