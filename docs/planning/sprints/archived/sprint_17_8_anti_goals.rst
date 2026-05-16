Sprint 17.8 — Write Anti-Goals and Anti-Patterns
=================================================

**Status.** Archived after validation.

**Track.** Architecture / Research.

**Type.** Documentation.

**Objective.** Explicitly reject unsafe architectural directions for
``lifecore_state`` before any implementation sprint begins.

**Parent sprint.** :doc:`../active/sprint_17_lifecore_state_rfc`.

Feature goal
------------

Write ``lifecore_state/anti_goals.rst`` so Sprint 17 documents what
``lifecore_state`` must not become. The document acts as a defensive guard
against architectural scope creep and design mistakes, providing reviewers with
explicit justification to reject overreaching proposals.

Lifecycle behavior contract
---------------------------

Sprint 17.8 is documentation-only. It does not change configure, activate,
deactivate, cleanup, shutdown, or error behavior for any existing
``lifecore_ros2`` node or component.

Document location
-----------------

**File:** ``lifecore_state/anti_goals.rst``

Acceptance criteria
-------------------

- [x] All major anti-patterns explicitly rejected
- [x] Rationale for each rejection clear
- [x] ``No giant manager`` pattern documented
- [x] ``No magic`` principle stated
- [x] Lifecycle/core separation enforced
- [x] Safe future directions listed
- [x] Mandatory review phrase included

Content quality checklist
-------------------------

- [x] Anti-goals are specific, not vague
- [x] Each rejection has justification
- [x] Patterns are tied to real risks
- [x] Language is direct but not hostile
- [x] Document is usable as PR review reference

Success criteria
----------------

Reviewers can cite this document to:

- Reject architectural overreach
- Require simpler alternatives
- Enforce separation of concerns
- Prevent hidden complexity

Implementation notes
--------------------

Completed in ``lifecore_state/anti_goals.rst``. The document rejects the major
unsafe directions for ``lifecore_state``, keeps lifecycle non-impact rules
explicit, documents the no-magic principle, enforces pure-core separation, and
lists safe but deferred future directions. No runtime code, tests, examples,
ROS interfaces, or package metadata were added.

Review requirement
------------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."
