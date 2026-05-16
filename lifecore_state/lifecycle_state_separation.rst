Lifecycle and State Separation
==============================

Purpose
-------

This document will explain how ``lifecore_state`` stays separate from
``lifecore_ros2`` lifecycle orchestration. Sprint 17.5 will complete the
separation rules before any integration design is considered.

Separation principles
---------------------

- lifecycle activation is not proof that a state value is valid;
- a valid state value is not proof that a lifecycle component is active;
- lifecycle transitions remain owned by ``lifecore_ros2`` components and nodes;
- state truth must not be hidden inside lifecycle transition machinery;
- optional future integration must be explicit and reviewed.

Inactive message behavior direction
-----------------------------------

Future integration must keep lifecycle state separate from message semantics.
The current architectural direction is:

.. list-table::
	 :header-rows: 1

	 * - Message type
		 - Direction while inactive
	 * - ``StateDescription``
		 - May be received and cached because it is metadata rather than observed
			 truth.
	 * - ``StateSnapshot``
		 - May be received for resynchronization preparation, but must not by
			 itself imply active behavior or current valid live truth.
	 * - ``StateSample``
		 - Must not update live state interpretation while inactive unless a later
			 review explicitly accepts a narrower cached-observation policy.
	 * - ``StateUpdate`` or ``StateDelta``
		 - Must not be applied while inactive because continuity assumptions cannot
			 be trusted across inactive periods.
	 * - ``StateCommand``
		 - Requires active lifecycle state and must be rejected, ignored, or not
			 handled according to the accepted policy.

Additional separation rules
---------------------------

- cached descriptions or snapshots must not imply active behavior;
- activation does not by itself validate cached values;
- reactivation after inactive time may require a fresh snapshot before deltas
	can be trusted;
- no future package may introduce a parallel lifecycle state machine;
- ``lifecore_ros2`` remains responsible for lifecycle transitions, while future
	``lifecore_state`` work describes state truth and synchronization semantics.

Current scope
-------------

This document does not change configure, activate, deactivate, cleanup,
shutdown, or error behavior. It is a planning artifact for architecture review.

Review questions
----------------

- Which lifecycle concepts are safe to reference from state documentation?
- Which state concepts must never become implicit lifecycle behavior?
- What integration points, if any, should be deferred beyond Sprint 17?
- Should any inactive snapshot behavior be narrowed further before Sprint 18
	message ABI work?

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
