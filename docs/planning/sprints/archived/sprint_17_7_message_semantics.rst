Sprint 17.7 — Write Message Semantics
=====================================

**Status.** Archived after validation.

**Track.** Architecture / Research.

**Type.** Documentation.

**Objective.** Define future message semantics and data models for
``lifecore_state``, without creating compilable ``.msg`` files.

**Parent sprint.** :doc:`../active/sprint_17_lifecore_state_rfc`.

Feature goal
------------

Write ``lifecore_state/message_semantics.rst`` so Sprint 17 documents the
future message semantics for descriptors, descriptions, samples, updates, and
commands without creating ABI commitments too early.

Lifecycle behavior contract
---------------------------

Sprint 17.7 is documentation-only. It does not change configure, activate,
deactivate, cleanup, shutdown, or error behavior for any existing
``lifecore_ros2`` node or component.

Context
-------

Sprint 17.6 documented package boundaries. Sprint 17.7 documented message
semantics conceptually so later ABI work can start from stable meaning rather
than from ad hoc field choices.

The five core message concepts documented are:

- ``StateDescriptor``
- ``StateDescription``
- ``StateSample``
- ``StateUpdate``
- ``StateCommand``

All content is non-final sketch material. No compilable ``.msg`` files were
created.

Document location
-----------------

**File:** ``lifecore_state/message_semantics.rst``

Acceptance criteria
-------------------

- [x] All five message types documented
- [x] Semantics clear without ambiguity
- [x] No compilable ``.msg`` files created
- [x] No Python implementation code
- [x] Pseudo-sketches clearly marked non-final
- [x] QoS recommendations explicit
- [x] Timestamp semantics clarified
- [x] Quality enum values documented
- [x] Mandatory review phrase included

Content quality checklist
-------------------------

- [x] Each message has clear purpose
- [x] Field semantics explained
- [x] Type selection rule documented
- [x] Sketches show intended structure without committing
- [x] Delta vs snapshot clearly distinguished
- [x] Timestamp strategy justified
- [x] QoS rationale explained

Success criteria
----------------

A developer reading the document can understand:

- What messages ``lifecore_state`` may eventually send
- What fields are needed and why
- How snapshots differ from deltas
- How quality and sequence protect integrity
- What QoS is required for reliable state synchronization

Implementation notes
--------------------

Completed in ``lifecore_state/message_semantics.rst``. The document covers
all five message types with conceptual fields, non-final example sketches,
snapshot and delta semantics, timestamp semantics, quality values, version and
sequence semantics, QoS recommendations, and open questions. No ``.msg`` files
were created and no Python code was added.

Review requirement
------------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."
