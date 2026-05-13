Sprint 18 - lifecore_state_msgs ABI prototype
=============================================

**Track.** State Architecture / ROS ABI.

**Branch.** ``sprint/18-lifecore-state-msgs-abi``.

**Priority.** P2 conditional.

**Condition.** Start only if Sprint 17 explicitly validates a go decision.

**Objective.** Prototype minimal ROS 2 Jazzy messages for the future typed state
model while avoiding complex Python core code.

Possible messages
-----------------

- ``StateDescriptor.msg``
- ``StateDescription.msg`` or ``StateDescriptionArray.msg``
- ``StateValue.msg``
- ``StateUpdate.msg`` or ``StateSnapshot.msg``
- ``StateCommand.msg`` only if the need is real
- optional ``StateType.msg`` / ``StateQuality.msg`` constants if the ABI needs
  them

Fields to consider
------------------

``StateDescriptor`` candidates: ``id``, ``uuid``, ``key``, ``display_name``,
``description``, ``group``, ``type``, ``direction``, ``unit``, ``min_value``,
``max_value``, ``writable``, ``safety_related``, and ``persistent``.

``StateValue`` candidates: ``header``, ``id``, optional ``uuid``, ``type``,
``quality``, ``source``, ``bool_value``, ``int_value``, ``uint_value``,
``float_value``, and ``string_value``.

``StateUpdate`` candidates: ``header``, ``source_uuid``, ``sequence``,
``description_version``, ``update_mode``, and ``values``.

Minimal qualities: ``UNKNOWN``, ``VALID``, ``STALE``, ``INVALID``,
``COMM_ERROR``, ``OUT_OF_RANGE``, ``FORCED``, ``SIMULATED``, ``DISABLED``, and
``NOT_AVAILABLE``.

Update modes: ``FULL_SNAPSHOT`` and ``DELTA_UPDATE``.

Non-goals
---------

- No complex Python runtime.
- No lifecycle-core coupling.
- No generated code before conventions stabilize.

Acceptance criteria
-------------------

- [ ] Messages compile in ROS 2 Jazzy.
- [ ] Names match the Sprint 17 RFC.
- [ ] ABI stability is prioritized over convenience.
- [ ] Messages are documented.
- [ ] Discussable choices are marked TODO or RFC-decision.
