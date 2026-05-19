Sprint 18.5 - StateSample.msg Design Notes
==========================================

**Status.** Completed.

**Track.** State Architecture / ROS ABI.

**Scope.** Message definition design and implementation for ``StateSample``.

Purpose
-------

This document records the design rationale, field decisions, and semantic
choices for ``StateSample.msg`` in the Sprint 18 messages-only ABI prototype.

Message Purpose
---------------

``StateSample`` represents one observed state value for one descriptor at one
source timestamp. It is runtime truth as observed by a source. It is not
metadata, a schema descriptor, or a command.

Field Ordering Rationale
------------------------

Fields are organized in four logical groups for readability:

1. **Transport header.** ``std_msgs/Header`` carries the source observation
   timestamp.
2. **Descriptor identity group.** ``descriptor_id``, ``descriptor_uuid``, and
   ``key`` link the sample to its ``StateDescriptor`` without embedding the
   full descriptor object.
3. **Value type and context group.** ``type``, ``quality``, and ``source``
   express the active value semantics and observation context.
4. **Variant value group.** Five explicit value fields; exactly one is active
   at a time, selected by ``type``.

Field Decisions
---------------

Header
~~~~~~

``header`` (std_msgs/Header)
	The ``header.stamp`` field carries the source timestamp: the time when the
	value was observed at the source. This is not the publication time of the
	containing ``StateUpdate``. Source time and publish time are distinct facts;
	see ``message_semantics.rst`` timestamp semantics section.

Descriptor Identity Group
~~~~~~~~~~~~~~~~~~~~~~~~~

All three identity references are included so that consumers at different
integration depths can use the most appropriate link:

``descriptor_id`` (uint32)
	Compact numeric identifier within the containing ``StateDescription`` scope.
	Matches ``StateDescriptor.id``. Efficient for high-frequency updates where
	the consumer holds a cached description. Not globally meaningful by itself.

``descriptor_uuid`` (unique_identifier_msgs/UUID)
	Stable persistent identifier across launches, exports, and bridges.
	Matches ``StateDescriptor.uuid``. Useful for consumers that cannot assume a
	shared compact-ID scope.

``key`` (string)
	Canonical path or logical name, such as ``battery/pack/main/voltage``.
	Matches ``StateDescriptor.key``. Supports readability in logs, bridges, and
	diagnostic tools.

No obligation exists to populate all three fields simultaneously. The consumer
must document which reference it relies on. ``descriptor_id`` is preferred in
high-frequency streaming; ``descriptor_uuid`` or ``key`` are preferred in
bridge, logging, and diagnostic contexts.

Value Type and Context Group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``type`` (uint8)
	Declares the active value type for this sample. Selects exactly one value
	field in the variant group. Uses the same ``TYPE_*`` constants as
	``StateDescriptor.msg``. Sprint 18.8 may extract a shared ``StateType.msg``;
	until then, constants are duplicated with identical values.

``quality`` (uint8)
	Describes the reliability and validity state of the observed value.
	Quality describes the sample, not the lifecycle state of the publishing
	node. See ``QUALITY_*`` constants section below.

``source`` (uint8)
	Semantic identity of the observation origin. Describes the kind of source
	that produced the observed value. It is not the same as the ROS node name
	or topic that relayed the message. See ``SOURCE_*`` constants section below.

	``SOURCE_COMMANDED`` is deliberately excluded from ``StateSample``. A sample
	reports observed truth. A commanded value that has been applied and observed
	should be reported with the appropriate origin source (e.g., ``SOURCE_OPERATOR``
	or ``SOURCE_SOFTWARE``). ``StateCommand`` expresses intent and is the correct
	vehicle for the commanded value before observation.

Variant Value Group
~~~~~~~~~~~~~~~~~~~

``bool_value`` (bool)
	Active when ``type = TYPE_BOOL``.

``int_value`` (int64)
	Active when ``type`` selects any signed integer type (``TYPE_INT8``,
	``TYPE_INT16``, ``TYPE_INT32``, ``TYPE_INT64``). A single ``int64`` field
	covers the full signed integer range; the narrower ``TYPE_INT*`` constants
	express the semantic width at the descriptor level, not a separate field.

``uint_value`` (uint64)
	Active when ``type`` selects any unsigned integer type (``TYPE_UINT8``
	through ``TYPE_UINT64``). Same rationale as ``int_value``.

``float_value`` (float64)
	Active when ``type`` selects a floating-point type (``TYPE_FLOAT32`` or
	``TYPE_FLOAT64``). ``float64`` is the transport representation; the narrower
	``TYPE_FLOAT32`` expresses semantic precision at the descriptor level.

``string_value`` (string)
	Active when ``type = TYPE_STRING``.

``TYPE_BYTES`` (value 13) is present in the type constants for consistency with
``StateDescriptor.msg``, but no ``bytes_value`` field is included in Sprint 18.5.
Bytes variant support is deferred to a future sprint.

Variant Semantics
~~~~~~~~~~~~~~~~~

``type`` selects exactly one active value field. A consumer must never interpret
multiple value fields simultaneously. When ``type`` changes, the active value
field changes.

Consumers must treat a populated field that does not match ``type`` as invalid
or quarantined input.

Type Constants
~~~~~~~~~~~~~~

Duplicated from ``StateDescriptor.msg`` for v0 ABI consistency. Sprint 18.8
constants decision review may extract a shared ``StateType.msg``; until that
decision is taken, the constants are identical across both messages.

================= =====
Constant          Value
================= =====
TYPE_UNKNOWN      0
TYPE_BOOL         1
TYPE_INT8         2
TYPE_INT16        3
TYPE_INT32        4
TYPE_INT64        5
TYPE_UINT8        6
TYPE_UINT16       7
TYPE_UINT32       8
TYPE_UINT64       9
TYPE_FLOAT32      10
TYPE_FLOAT64      11
TYPE_STRING       12
TYPE_BYTES        13
================= =====

Quality Constants
~~~~~~~~~~~~~~~~~

``QUALITY_*`` constants describe the reliability and validity state of the
observed value. Multiple distinct failure modes are named explicitly so that
consumers can apply appropriate remediation or filtering without resorting to
opaque numeric comparisons.

====================== =====  ===============================================================
Constant               Value  Meaning
====================== =====  ===============================================================
QUALITY_UNKNOWN        0      Quality not specified or not yet assessed.
QUALITY_VALID          1      Value is reliable and within expected operational bounds.
QUALITY_STALE          2      Value was valid at a prior time but has not been refreshed.
QUALITY_INVALID        3      Value is known to be incorrect or could not be validated.
QUALITY_COMM_ERROR     4      Communication failure; value is absent or unreachable.
QUALITY_OUT_OF_RANGE   5      Value was observed but falls outside expected operational bounds.
QUALITY_FORCED         6      Value was explicitly overridden by an operator or test procedure.
QUALITY_SIMULATED      7      Value originates from a simulation model, not hardware.
QUALITY_DISABLED       8      Source or sensor is intentionally disabled; no value available.
QUALITY_NOT_AVAILABLE  9      Value does not exist for this descriptor in the current context.
====================== =====  ===============================================================

Source Constants
~~~~~~~~~~~~~~~~

``SOURCE_*`` constants identify the semantic origin of the observation. The
source field describes what kind of entity produced the value, not which ROS
node published the message.

``SOURCE_COMMANDED`` is excluded. A sample reports observed truth; when a
commanded value has been observed, the actual origin (hardware, software, or
operator) is the correct source. ``StateCommand`` is the vehicle for expressing
intent before observation.

================= =====  ===============================================================
Constant          Value  Meaning
================= =====  ===============================================================
SOURCE_UNKNOWN    0      Source not specified.
SOURCE_HARDWARE   1      Physical sensor or actuator feedback.
SOURCE_SOFTWARE   2      Computed, estimated, or software-derived value.
SOURCE_SIMULATION 3      Simulated or emulated value from a simulation model.
SOURCE_OPERATOR   4      Manually set or confirmed by a human operator.
SOURCE_REPLAY     5      Reproduced from recorded data (test, analysis, or replay).
================= =====  ===============================================================

Deferred Non-Goals
------------------

The following are explicitly excluded from Sprint 18.5:

- ``bytes_value`` field (``TYPE_BYTES=13`` constant is present for consistency,
  but no bytes transport field is included in this sprint).
- Separate ``StateType.msg``, ``StateQuality.msg``, ``StateSource.msg`` enum
  messages (deferred to Sprint 18.8 constants decision).
- Any Python runtime code, lifecycle integration, or ROS node behavior.
- Registry, subscriber, publisher, factory, or projection logic.
- Command semantics (``SOURCE_COMMANDED`` excluded by design).
- Lifecycle integration with ``lifecore_ros2`` (remains independent).

Build Integration
-----------------

``CMakeLists.txt`` has been updated to include ``msg/StateSample.msg`` in the
existing ``rosidl_generate_interfaces()`` call:

.. code-block:: cmake

    rosidl_generate_interfaces(${PROJECT_NAME}
      msg/StateDescriptor.msg
      msg/StateDescription.msg
      msg/StateSample.msg
      DEPENDENCIES std_msgs unique_identifier_msgs
    )

No new dependencies are required. ``StateSample.msg`` uses only
``std_msgs/Header`` and ``unique_identifier_msgs/UUID``, which are already
declared in ``package.xml``.

Full build validation with ``colcon`` is deferred to Sprint 18.9.

Documentation Consistency
-------------------------

- ``message_semantics.rst`` StateSample section updated to reflect decided
  fields, constants, and timestamp semantics.
- ``StateDescriptor.msg`` ``TYPE_*`` constants verified to match: the range
  ``TYPE_UNKNOWN=0`` through ``TYPE_BYTES=13`` is identical in both files.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is
accepted.
