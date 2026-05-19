Sprint 18.8 - Constants Decision
================================

**Status.** Planned.

**Track.** State Architecture / ROS ABI.

**Type.** ABI decision.

**Parent sprint.** :doc:`../active/sprint_18_lifecore_state_msgs_abi`.

Objective
---------

Review constants used by ``lifecore_state_msgs`` and decide whether to keep
them embedded in primary messages or extract enum-like messages.

Constants in Scope
------------------

- type constants;
- quality constants;
- direction constants;
- source constants;
- update mode constants.

Options
-------

Option A keeps constants embedded in primary messages:

- ``TYPE_*`` in ``StateDescriptor``, ``StateSample``, and ``StateCommand``;
- ``QUALITY_*`` in ``StateSample``;
- ``DIR_*`` in ``StateDescriptor``;
- ``SOURCE_*`` in ``StateSample``;
- ``UPDATE_*`` in ``StateUpdate``.

Option B creates enum-like messages:

- ``StateType.msg``
- ``StateQuality.msg``
- ``StateDirection.msg``
- ``StateSource.msg``
- ``StateUpdateMode.msg``

Sprint 18 Recommendation
------------------------

Prefer Option A for v0 unless duplication becomes clearly harmful. Do not
over-engineer enum-like messages prematurely.

Deliverable
-----------

Create or update ``lifecore_state/rfcs/sprint_18_constants_decision.rst`` with:

- chosen option;
- rationale;
- alternatives considered;
- impact on message files;
- deferred decisions.

If message files change because of this decision, update them consistently.

Constraints
-----------

- Do not add runtime code.
- Do not add ``lifecore_state_core`` or ``lifecore_state_ros``.
- Do not introduce code generation.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
