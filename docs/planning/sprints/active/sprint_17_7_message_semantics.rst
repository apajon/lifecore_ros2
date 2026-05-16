Sprint 17.7 — Write Message Semantics
=====================================

**Status.** Archived. See :doc:`../archived/sprint_17_7_message_semantics`.

**Track.** Architecture / Research.

**Type.** Documentation.

**Objective.** Define future message semantics and data models for
``lifecore_state``, without creating compilable ``.msg`` files.

**Parent sprint.** :doc:`sprint_17_lifecore_state_rfc`.

Feature goal
------------

Write ``lifecore_state/message_semantics.rst`` so Sprint 17 documents the
future message semantics for descriptors, descriptions, samples, updates, and
commands without creating ABI commitments too early.

Lifecycle behavior contract
---------------------------

Sprint 17.7 is documentation-only. It must not change configure, activate,
deactivate, cleanup, shutdown, or error behavior for any existing
``lifecore_ros2`` node or component.

The document must keep these non-impact rules explicit:

- **configure:** no runtime resource creation changes.
- **activate:** no activation gate changes.
- **deactivate:** no deactivation behavior changes.
- **cleanup:** no cleanup behavior changes.
- **shutdown:** no shutdown behavior changes.
- **error:** no error recovery changes.

Context
-------

Sprint 17.6 documented package boundaries. Sprint 17.7 now documents message
semantics conceptually so later ABI work can start from stable meaning rather
than from ad hoc field choices.

The five core message concepts under review are:

- ``StateDescriptor``
- ``StateDescription``
- ``StateSample``
- ``StateUpdate``
- ``StateCommand``

All content remains non-final sketch material only. Sprint 17.7 must not
create compilable ``.msg`` files.

The intent is to document the message model conceptually, not to lock an ABI
too early.

Impacted modules
----------------

``lifecore_state/message_semantics.rst``
  Primary deliverable for Sprint 17.7.

``docs/planning/sprints/active/``
  Hosts this active planning card and the main Sprint 17 coordinator.

``src/``, ``tests/``, and ``examples/``
  Not impacted. Sprint 17.7 must not change runtime behavior, tests, or public
  APIs.

Document location
-----------------

**File:** ``lifecore_state/message_semantics.rst``

Required sections
-----------------

1. **Purpose**
   Define message design principles and semantics.
2. **Message design principles**
   Cover ROS-native transport, explicit fields, stable contracts, no hidden
   synchronization, and no dynamic magic. The section should explicitly cover:

   - ROS-native concepts such as topic, header, and QoS;
   - explicit fields rather than JSON-in-string payloads;
   - stable contracts;
   - no hidden synchronization magic;
   - no dynamic magic;
   - a type field that selects exactly one active value field.
3. **StateDescriptor**
   Document conceptual fields and example sketches.
   The section should cover a static field definition with conceptual fields
   such as ``id``, ``uuid``, ``key``, ``type``, ``direction``, ``unit``,
   ``writable``, ``safety_related``, and optional metadata.
4. **StateDescription**
   Document versioned descriptor collections, QoS direction, and inactive
   caching semantics. The section should state conceptually:

   - versioned collection of descriptors;
   - fields such as ``schema_uuid``, ``description_version``, and an array of
     descriptors;
   - QoS direction: reliable + transient_local + keep_last(1);
   - allowed to cache while lifecycle inactive;
   - example sketches marked non-final.
5. **StateSample**
   Document single observed values, timestamp, quality, source, and the
   explicit active-value-field rule. The section should include:

   - one observed value;
   - a header with source timestamp;
   - a type field;
   - a quality field;
   - a source field;
   - explicit value fields such as ``bool_value``, ``int_value``,
     ``uint_value``, ``float_value``, and ``string_value``;
   - the rule that the type field selects exactly one active value field.
6. **StateUpdate**
   Document batches, schema linkage, sequence, update mode, and example
   sketches. The section should include:

   - batch of samples;
   - a header with publish timestamp;
   - ``source_uuid`` and ``schema_uuid``;
   - ``sequence`` for order and loss detection;
   - ``description_version`` for schema mismatch detection;
   - ``update_mode`` with ``FULL`` or ``DELTA``;
   - an array of samples;
   - example sketches marked non-final.
7. **StateCommand**
   Document request semantics and how command outcomes remain separate. The
   section should state that commands are requested intent rather than observed
   truth, must be validated by the receiver, and that command acceptance is
   shown later by ``StateUpdate`` or explicit feedback.
8. **Snapshot semantics**
   Clarify full-state meaning, including that ``update_mode = FULL`` and that
   all known fields for the declared scope are present.
9. **Delta semantics**
   Clarify partial-state meaning and continuity constraints, including:

   - partial changes only;
   - ``update_mode = DELTA``;
   - requires sequence continuity;
   - requires known schema;
   - unsafe after unknown history unless schema rules allow recovery.
10. **Timestamp semantics**
    Distinguish source timestamp from publish timestamp. The section should make
    explicit that ``sample.source_timestamp`` is when the value was observed,
    while ``update.publish_timestamp`` is when the message was sent.
11. **Quality semantics**
    Document the meaning of quality values. At minimum cover:

    - ``VALID``;
    - ``STALE``;
    - ``INVALID``;
    - ``COMM_ERROR``;
    - ``OUT_OF_RANGE``;
    - ``FORCED``;
    - ``SIMULATED``;
    - ``DISABLED``;
    - ``NOT_AVAILABLE``.
12. **Version and sequence semantics**
    Document mismatch and ordering semantics, including:

    - ``sequence`` for loss, order violation, and duplicate detection;
    - ``description_version`` for schema mismatch detection;
    - mismatch policy such as ``REJECT`` or ``QUARANTINE``.
13. **QoS recommendations**
    Document recommendations for description, update, and command flows.
    The section should include:

    ``StateDescription``
      ``RELIABLE`` + ``TRANSIENT_LOCAL`` + ``KEEP_LAST(1)``.

    ``StateUpdate``
      ``BEST_EFFORT`` or ``RELIABLE`` by criticality, with ``VOLATILE`` and
      ``KEEP_LAST(1)``.

    ``StateCommand``
      ``RELIABLE`` with ``VOLATILE`` history.
14. **Non-final message sketches**
    Include clearly marked pseudo-message examples. The section should contain
    pseudo-message blocks marked as non-final, for example a text sketch of
    ``StateDescriptor`` fields.
15. **Open questions**
    Record remaining design questions instead of hiding them. At minimum keep:

    - whether UUID should be in every sample or only in descriptors;
    - whether a compact sample type is needed;
    - whether ``default_value`` belongs in the descriptor;
    - whether command feedback should be a message, service, or action.

Acceptance criteria
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

Content quality checklist
-------------------------

- [ ] Each message has clear purpose
- [ ] Field semantics explained
- [ ] Type selection rule documented
- [ ] Sketches show intended structure without committing
- [ ] Delta vs snapshot clearly distinguished
- [ ] Timestamp strategy justified
- [ ] QoS rationale explained

Success criteria
----------------

A developer reading this document can understand:

- What messages ``lifecore_state`` may eventually send
- What fields are needed and why
- How snapshots differ from deltas
- How quality and sequence protect integrity
- What QoS is required for reliable state synchronization

Review requirement
------------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."