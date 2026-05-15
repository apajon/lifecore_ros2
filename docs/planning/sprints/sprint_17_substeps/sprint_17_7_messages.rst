Sprint 17.7 — Write Message Semantics
=====================================

**Track.** Architecture / Research.

**Type.** Documentation.

**Objective.** Define future message semantics and data models for
``lifecore_state``, without creating compilable ``.msg`` files.

Context
-------

Document the five core message types conceptually:

- StateDescriptor
- StateDescription
- StateSample
- StateUpdate
- StateCommand

All content is **non-final sketches** only. No actual ROS 2 message files.

Document Location
------------------

**File:** ``lifecore_state/message_semantics.rst``

Required Sections
------------------

1. **Purpose**
   Define message design principles and semantics

2. **Message design principles**
   - ROS-native (Topic, Header, QoS)
   - Explicit fields, no JSON-in-string
   - Stable contracts
   - No hidden synchronization
   - No dynamic magic
   - Type field selects exactly one active value field

3. **StateDescriptor**
   - Static field definition
   - Fields: id, uuid, key, type, direction, unit, writable, safety_related, optional metadata
   - Example sketches (marked non-final)

4. **StateDescription**
   - Versioned collection of descriptors
   - Fields: schema_uuid, description_version, array of descriptors
   - QoS: reliable + transient_local + keep_last(1)
   - Allowed to cache while lifecycle inactive
   - Example sketches (marked non-final)

5. **StateSample**
   - One observed value
   - Header with source timestamp
   - Type field
   - Quality field
   - Source field
   - Explicit value fields: bool_value, int_value, uint_value, float_value, string_value
   - Rule: type field selects exactly one active value
   - Example sketches (marked non-final)

6. **StateUpdate**
   - Batch of samples
   - Header with publish timestamp
   - source_uuid, schema_uuid
   - sequence field for order/loss detection
   - description_version for schema mismatch detection
   - update_mode: FULL or DELTA
   - Array of samples
   - Example sketches (marked non-final)

7. **StateCommand**
   - Request/intention (not observed truth)
   - Must be validated by receiver
   - Command acceptance shown later by StateUpdate or explicit feedback
   - Example sketches (marked non-final)

8. **Snapshot semantics**
   - Full state capture
   - update_mode = FULL
   - All known fields present

9. **Delta semantics**
   - Partial changes only
   - update_mode = DELTA
   - Requires sequence continuity
   - Requires known schema
   - Unsafe after unknown history unless schema rules allow recovery

10. **Timestamp semantics**
    - sample.source_timestamp: when value observed (hardware/sensor)
    - update.publish_timestamp: when message sent
    - Distinguish source_timestamp from publish_timestamp

11. **Quality semantics**
    - VALID – value trusted
    - STALE – value too old
    - INVALID – malformed or out-of-range
    - COMM_ERROR – communication failure
    - OUT_OF_RANGE – exceeds limits
    - FORCED – manually set
    - SIMULATED – not from hardware
    - DISABLED – functionality off
    - NOT_AVAILABLE – not yet known

12. **Version and sequence semantics**
    - sequence: detects loss, order violation, duplicates
    - description_version: detects schema mismatch
    - Mismatch policy: REJECT or QUARANTINE

13. **QoS recommendations**

    StateDescription:
    - Reliability: RELIABLE
    - History: TRANSIENT_LOCAL
    - Keep: KEEP_LAST(1)

    StateUpdate:
    - Reliability: BEST_EFFORT or RELIABLE (by criticality)
    - History: VOLATILE
    - Keep: KEEP_LAST(1)

    StateCommand:
    - Reliability: RELIABLE
    - History: VOLATILE

14. **Non-final message sketches**

    Include pseudo-msg blocks, clearly marked as non-final:

    .. code-block:: text

        [NON-FINAL SKETCH]

        StateDescriptor:
          id: uint32
          uuid: uint8[16]
          key: string
          type: string
          direction: string (in, out, inout)
          unit: string
          writable: bool
          safety_related: bool

15. **Open questions**

    Include:
    - Should UUID be in every sample or only descriptor?
    - Should compact sample type exist?
    - Should default_value be in descriptor?
    - Should command feedback be message, service, or action?

Acceptance Criteria
-------------------

- [ ] All five message types documented
- [ ] Semantics clear without ambiguity
- [ ] No compilable ``.msg`` files created
- [ ] No Python implementation code
- [ ] Pseudo-sketches clearly marked non-final
- [ ] QoS recommendations explicit
- [ ] Timestamp semantics clarified
- [ ] Quality enum values documented
- [ ] Mandatory review phrase included

Content Quality Checklist
-------------------------

- [ ] Each message has clear purpose
- [ ] Field semantics explained
- [ ] Type selection rule documented
- [ ] Sketches show intended structure without committing
- [ ] Delta vs snapshot clearly distinguished
- [ ] Timestamp strategy justified
- [ ] QoS rationale explained

Success Criteria
----------------

A developer can read this and understand:

- What messages ``lifecore_state`` will send
- What fields are needed and why
- How snapshots differ from deltas
- How quality and sequence protect integrity
- What QoS is required for reliable state sync
