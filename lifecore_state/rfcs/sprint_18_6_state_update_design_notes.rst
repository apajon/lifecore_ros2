Sprint 18.6 - StateUpdate.msg Design Notes
==========================================

**Status.** Completed.

**Track.** State Architecture / ROS ABI.

**Scope.** Message definition design and implementation for ``StateUpdate``.

Purpose
-------

This document records the design rationale, field decisions, and semantic
choices for ``StateUpdate.msg`` in the Sprint 18 messages-only ABI prototype.

Message Purpose
---------------

``StateUpdate`` represents a published batch of observed ``StateSample``
values. It reports observed truth. It does not express requested mutation,
and it is not a command or descriptor list.

Field Ordering Rationale
------------------------

Fields are organized in four logical groups for readability:

1. **Transport header.** ``std_msgs/Header`` carries the publish/batch
   timestamp.
2. **Source and schema identity group.** ``source_uuid`` and ``schema_uuid``
   identify the update stream and the schema used to interpret its samples.
3. **Ordering and versioning group.** ``sequence``, ``description_version``,
   and ``update_mode`` provide enough metadata for consumers to detect loss,
   duplication, schema mismatch, and snapshot-vs-delta semantics.
4. **Payload group.** ``samples`` carries the batch of ``StateSample`` entries.

Field Decisions
---------------

Header
~~~~~~

``header`` (std_msgs/Header)
    ``header.stamp`` is the publish/batch timestamp: the time when this update
    was assembled and sent on the transport. Each contained
    ``StateSample.header.stamp`` is the source observation timestamp. These
    timestamps may differ. See ``message_semantics.rst`` timestamp semantics
    section.

Source and Schema Identity Group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``source_uuid`` (unique_identifier_msgs/UUID)
    Stable identity of the source, owner, or publisher scope for this update.
    Used to correlate updates with a specific state producer or registry scope.
    Sequence numbers are per ``source_uuid`` stream.

``schema_uuid`` (unique_identifier_msgs/UUID)
    Identity of the schema or ``StateDescription`` used to interpret the
    samples. Must match ``StateDescription.schema_uuid`` for the declared
    ``description_version``.

Ordering and Versioning Group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``sequence`` (uint64)
    Monotonically increasing sequence number per ``source_uuid`` stream.
    Consumers use it to detect:

    - lost updates (gap in sequence);
    - duplicated updates (same sequence received twice);
    - out-of-order updates (sequence decreases);
    - stream discontinuity (large gap requiring resynchronization).

    Sequence is scoped to ``source_uuid``, not global. Two different sources
    may independently use overlapping sequence numbers.

``description_version`` (uint64)
    ``StateDescription`` version used to interpret descriptor ids, types, and
    semantics. Must match ``StateDescription.description_version`` for the
    declared ``schema_uuid``.

    Receivers must not blindly apply updates against a different
    ``description_version``. A version mismatch signals potential semantic
    incompatibility: descriptor ids may have changed, types may differ, or
    descriptors may have been added or removed.

    When a receiver detects a ``description_version`` mismatch, it should
    either request the latest ``StateDescription`` (via transient_local
    delivery) or quarantine the update until schema compatibility is verified.

``update_mode`` (uint8)
    Declares whether this update is a full snapshot or a partial delta.

    ``UPDATE_FULL`` (value 1):
        Contains a complete snapshot for the publisher's declared scope.
        Useful for startup, resynchronization after discontinuity, and
        debugging. A consumer can rebuild current state from a single
        ``UPDATE_FULL`` without relying on prior updates.

    ``UPDATE_DELTA`` (value 2):
        Contains only changed samples since the prior update. Assumes the
        receiver has compatible prior state (same ``source_uuid``, continuous
        ``sequence``, matching ``description_version``). Should not be applied
        after unknown history unless explicit checks allow it.

    ``UPDATE_UNKNOWN`` (value 0):
        Reserved sentinel. A valid update must declare an explicit mode.

Payload Group
~~~~~~~~~~~~~

``samples`` (StateSample[])
    Array of observed ``StateSample`` values. Each sample carries its own
    source timestamp in ``StateSample.header.stamp``.

    For ``UPDATE_FULL``, samples represent a complete snapshot for the
    publisher scope. Missing descriptors are implicitly absent or not
    available in the snapshot scope.

    For ``UPDATE_DELTA``, samples represent only changed values since the
    prior update. Unchanged descriptors are not included.

Update Mode Constants
~~~~~~~~~~~~~~~~~~~~~

Embedded in ``StateUpdate.msg`` for v0 ABI clarity (consistent with the
Sprint 18.8 constants decision to keep constants embedded until duplication
becomes problematic):

================= =====  =====================================================
Constant          Value  Meaning
================= =====  =====================================================
UPDATE_UNKNOWN    0      Reserved sentinel; a valid update must declare a mode.
UPDATE_FULL       1      Complete snapshot for the publisher's declared scope.
UPDATE_DELTA      2      Partial update containing only changed samples.
================= =====  =====================================================

Timestamp Semantics
-------------------

``StateUpdate.header.stamp`` is the publish/batch timestamp. It records when
this batch was assembled and sent. ``StateSample.header.stamp`` is the source
observation timestamp — when the value was observed at the source. These are
distinct facts, and they may differ. A consumer that needs to reason about
observation age must use the sample timestamp, not the update timestamp.

Sequence Semantics
------------------

``sequence`` is per ``source_uuid`` stream. It is monotonically increasing
but not required to be gap-free at the protocol level. A consumer should
treat a missing sequence number as a potential loss event and either:

- request resynchronization via the next ``UPDATE_FULL``;
- quarantine the stream until continuity is restored;
- apply the update anyway if its policy accepts gaps for non-critical state.

Sequence wraps at ``uint64`` maximum. Consumers should detect wrap using
standard unsigned delta comparison.

Description Version Semantics
-----------------------------

``description_version`` identifies the ``StateDescription`` version used to
interpret descriptor ids, types, and semantics. It is a critical safety
field: applying an update against an incompatible description can silently
misinterpret values, types, or descriptor identities.

A receiver must compare ``description_version`` with its cached
``StateDescription.description_version``. A mismatch means the receiver must
fetch the current description before interpreting samples.

Update Mode Semantics
---------------------

``UPDATE_FULL`` carries a complete snapshot. Useful for:

- initial synchronization after subscription;
- recovery after detected discontinuity (large sequence gap, wrap, restart);
- debugging and introspection.

``UPDATE_DELTA`` carries only changed samples. Useful for:

- efficient steady-state streaming;
- high-frequency updates where full snapshots are too large.

Lifecycle notes (documentation-only, no implementation in Sprint 18):

- Delta updates should not be applied while inactive (the receiver lacks
  the continuity context).
- Full snapshots may be cached while inactive, but only by explicit policy
  (e.g., a node that caches the latest snapshot during configure for fast
  activation readiness).

Relation to StateCommand
------------------------

``StateUpdate`` reports observed truth. ``StateCommand`` (Sprint 18.7)
expresses intent. They are distinct contracts:

- A ``StateUpdate`` may report the observed result of a ``StateCommand``,
  but the update carries the observed value, not the command identity.
- A ``StateCommand`` is not a ``StateUpdate`` with a target field; it has
  different identity (command_uuid, target_*), purpose (intent), and
  validation expectations.

Constraints
-----------

- No command fields (``command_uuid``, ``target_*``) added.
- No registry behavior added.
- No QoS implementation added.
- No lifecycle implementation added.
- Constants embedded (no separate ``StateUpdateMode.msg``); consistent with
  Sprint 18.5 ``StateSample.msg`` constants approach.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18
is accepted.
