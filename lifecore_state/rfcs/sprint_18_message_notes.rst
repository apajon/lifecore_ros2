Sprint 18.3 - StateDescriptor.msg Design Notes
===============================================

**Status.** Completed.

**Track.** State Architecture / ROS ABI.

**Scope.** Message definition design and implementation for ``StateDescriptor``.

Purpose
-------

This document records the design rationale, field decisions, and semantic
choices for the first concrete ROS 2 message definition in the Sprint 18
messages-only ABI prototype.

Message Purpose
---------------

``StateDescriptor`` defines one state field contract. It answers:

- What state exists (identity)
- How it is identified (id, uuid, key)
- How it is typed (type field)
- What direction it has (in, out, inout)
- Whether it can be commanded (writable flag)
- What metadata helps humans and tools interpret it (display_name, description, group, unit)
- What constraints apply to its value (numeric bounds only in v0)

It must not contain the current observed runtime value.

Field Ordering Rationale
------------------------

Fields are organized logically for readability rather than transport
optimization. ``StateDescriptor`` is schema metadata, not a high-frequency
transport structure. Logical grouping is more maintainable than attempting
byte-packing or alignment optimization at this stage.

Grouping:

1. **Transport header.** ``std_msgs/Header`` carries descriptor publication event metadata.

2. **Identity group.** ``id``, ``uuid``, ``key`` establish stable identifiers.
   - ``id`` is a compact numeric ID within the description/registry scope.
   - ``uuid`` is a stable persistent identifier across launches and bridges.
   - ``key`` is the human-reviewable canonical path (e.g., ``battery/pack/main/voltage``).

3. **Type system group.** ``type`` and ``direction`` express semantics.
   - ``type`` selects the active value representation in future ``StateSample`` and ``StateCommand``.
   - ``direction`` (OUT, IN, INOUT) expresses allowed information flow.

4. **Metadata group.** ``display_name``, ``description``, ``group``, ``unit`` support human and tool interpretation.
   - ``display_name``: for user interfaces and dashboards.
   - ``description``: for documenting purpose and semantics.
   - ``group``: for logical organization and categorization.
   - ``unit``: physical or semantic unit (empty string if unitless).

5. **Behavioral flags.** ``writable``, ``safety_related``, ``persistent`` describe usage and relevance.
   - ``writable``: whether future ``StateCommand`` may request mutations.
   - ``safety_related``: metadata flag for safety review and policy.
   - ``persistent``: metadata flag indicating durable or archived state (does not implement persistence).

6. **Constraints group.** Numeric bounds only in v0.
   - ``min_value``, ``max_value``: numeric range constraints.
   - ``has_min_value``, ``has_max_value``: presence flags (nullable pattern).

7. **Constants.** ``TYPE_*`` and ``DIR_*`` constants embedded in the message for v0.

Field Decisions
---------------

Identity Fields
~~~~~~~~~~~~~~~

``id`` (uint32)
	Compact numeric identifier within the declared description or registry scope.
	Useful for compact updates and lookups, but not globally meaningful by itself.
	Scope is defined by the parent ``StateDescription`` or registry context.

``uuid`` (unique_identifier_msgs/UUID)
	Stable persistent identifier for the descriptor. Suitable for cross-launch
	exports, bridges, and external tools. Derived from stable semantic paths
	rather than generated at runtime when possible.

``key`` (string)
	Canonical path or logical name, such as ``battery/pack/main/voltage``.
	Human-reviewable identity anchor. Must remain stable across versions and
	launches. Used for documentation, lookup, and matching.

Type System
~~~~~~~~~~~

``type`` (uint8)
	Declares the semantic value type. Selects exactly one active value field in
	future ``StateSample`` and ``StateCommand`` messages. Embedded constants
	(TYPE_UNKNOWN, TYPE_BOOL, TYPE_INT8, TYPE_FLOAT64, TYPE_STRING, etc.)
	are included in v0 for clarity. Future consistency reviews (Sprint 18.8)
	may create separate enum-like messages if duplication becomes problematic.

``direction`` (uint8)
	Expresses allowed information flow:
	- DIR_OUT: observed state only (read-only from a command perspective)
	- DIR_IN: commandable target only (write-only, future ``StateCommand``)
	- DIR_INOUT: bidirectional state with explicit authority or negotiation

Metadata Fields
~~~~~~~~~~~~~~~

``display_name`` (string)
	User-friendly name for dashboards, telemetry displays, and documentation.
	May differ from ``key`` to support localization, marketing, or UI-specific
	naming conventions.

``description`` (string)
	Explains the purpose, semantics, and context of this descriptor. Supports
	human understanding and future introspection tools.

``group`` (string)
	Logical category or subsystem grouping for organizational purposes.
	Supports hierarchical presentation and filtering in tools and dashboards.

``unit`` (string)
	Physical or semantic unit for the value type.
	- Common SI symbols: ``V``, ``A``, ``degC``, ``m/s``, ``kg``, ``rad/s``.
	- Semantic units: ``Hz``, ``dB``, ``%``.
	- Empty string (``""``) indicates unitless or unspecified.
	Prefer standard SI or engineering notation when possible.

Behavioral Flags
~~~~~~~~~~~~~~~~

``writable`` (bool)
	True if a future ``StateCommand`` may request mutation for this descriptor.
	Does not guarantee that every command will be accepted; only that the
	descriptor is in principle commandable. Actual command acceptance depends
	on runtime state, ownership, safety rules, and permissions.

``safety_related`` (bool)
	Metadata flag indicating that misuse or unexpected values can affect safety
	policy, operator review, or command validation. Does not implement safety
	mechanisms; it signals that downstream tools, operators, or validation
	systems should apply extra scrutiny.

``persistent`` (bool)
	Metadata flag indicating that this descriptor represents state that is
	durable or archived (e.g., logged, stored in databases, or replayed across
	launches). Does not implement persistence semantics; it is purely
	descriptive metadata. Actual persistence is the responsibility of
	applications and future ``lifecore_state_core`` or ``lifecore_state_ros``
	runtime layers.

Constraints
~~~~~~~~~~~

In Sprint 18.3, only numeric constraints are included:

``min_value`` (float64)
	Minimum allowed value for numeric types. Only meaningful if ``has_min_value``
	is true.

``max_value`` (float64)
	Maximum allowed value for numeric types. Only meaningful if ``has_max_value``
	is true.

``has_min_value`` (bool)
	Presence flag. True if ``min_value`` is defined and should be considered by
	validators, command handlers, or consumers.

``has_max_value`` (bool)
	Presence flag. True if ``max_value`` is defined and should be considered by
	validators, command handlers, or consumers.

**Rationale for numeric-only constraints in v0:**

Non-numeric constraints (enum values, allowed string values, regex patterns,
step size, structured validation schemas) are deferred to later sprints. These
would require additional fields, polymorphism, or separate constraint messages.
Deferring them keeps StateDescriptor focused and reviewable at v0.

Type Constants
~~~~~~~~~~~~~~

Embedded in ``StateDescriptor.msg`` for v0 ABI clarity:

- ``TYPE_UNKNOWN=0``: type not specified or invalid
- ``TYPE_BOOL=1``: boolean value (true/false)
- ``TYPE_INT8`` through ``TYPE_INT64``: signed integers
- ``TYPE_UINT8`` through ``TYPE_UINT64``: unsigned integers
- ``TYPE_FLOAT32``, ``TYPE_FLOAT64``: floating-point
- ``TYPE_STRING=12``: UTF-8 text
- ``TYPE_BYTES=13``: opaque binary data

These constants remain embedded in the message for Sprint 18. Sprint 18.8
consistency review may split them into a separate enum-like message if
duplication across multiple message types becomes a maintenance burden.

Direction Constants
~~~~~~~~~~~~~~~~~~~

Embedded in ``StateDescriptor.msg`` for v0 ABI clarity:

- ``DIR_OUT=0``: observed state, read-only from command perspective
- ``DIR_IN=1``: commandable target, write-only
- ``DIR_INOUT=2``: bidirectional state with explicit authority or negotiation

Deferred Non-Goals
-------------------

The following concepts are explicitly deferred and not present in
``StateDescriptor.msg``:

- **Current runtime value.** ``StateDescriptor`` is schema metadata only.
  Current observed values are transported in ``StateSample`` and ``StateUpdate``.

- **Default value.** No ``default_value`` field. Defaults are policy concerns
  for applications and future ``lifecore_state_core`` logic.

- **Generic metadata.** No ``metadata_json``, no ``metadata_string``, no
  key/value maps. All metadata is expressed as explicit named fields.
  This keeps the schema reviewable and stable.

- **Command semantics.** ``StateDescriptor`` does not specify command feedback,
  command timeout, rollback behavior, or command validation policies. These
  are future concerns for ``StateCommand`` and command handling logic.

- **Lifecycle semantics.** No integration with ROS 2 lifecycle states. State
  descriptors are independent from lifecycle activation. Lifecycle/state
  separation remains enforced per Sprint 17 rules.

- **Registry behavior.** ``StateDescriptor`` does not specify ownership,
  namespace rules, synchronization scope, or registry lookup semantics.

Serialization and ROS 2 Message Compatibility
----------------------------------------------

``StateDescriptor.msg`` is compiled by ``rosidl_default_generators`` into
language-specific type definitions. The C++ and Python generated code will
include:

- Generated struct/class definitions
- Serialization and deserialization methods
- Python properties with introspection

No custom serialization logic is required.

Build Integration
-----------------

The ``CMakeLists.txt`` for ``lifecore_state_msgs`` includes the necessary
``rosidl_generate_interfaces()`` call:

.. code-block:: cmake

    rosidl_generate_interfaces(${PROJECT_NAME}
      msg/StateDescriptor.msg
      DEPENDENCIES std_msgs unique_identifier_msgs
    )

This wires the message generation for both C++ and Python during the
``colcon build`` step (Sprint 18.9).

Documentation Consistency
-------------------------

Reference documents have been reviewed for consistency with the message design:

- **message_semantics.rst:** Contains the conceptual sketch for ``StateDescriptor``.
  The actual message structure aligns with the sketch. The ``persistent`` flag
  is included as "if useful" recommendation; it is included in v0 as descriptive
  metadata.

- **package_boundaries.rst:** Confirms that ``lifecore_state_msgs`` is the ROS 2
  ABI package and that the parent ``lifecore_state/`` folder remains
  documentation-only. This structure is preserved.

- **lifecycle_state_separation.rst:** Confirms that ``StateDescriptor`` is
  independent from lifecycle activation. No lifecycle state integration is added.

Sprint 18.6 - StateUpdate.msg Design Notes
==========================================

**Status.** Completed.

**Track.** State Architecture / ROS ABI.

**Scope.** Message definition design and implementation for ``StateUpdate``.

See ``sprint_18_6_state_update_design_notes.rst`` for the full design rationale.

Summary
-------

``StateUpdate`` represents a published batch of observed ``StateSample`` values.
It reports observed truth.

Fields: ``header``, ``source_uuid``, ``schema_uuid``, ``sequence``,
``description_version``, ``update_mode``, ``samples`` (``StateSample[]``).

Constants: ``UPDATE_UNKNOWN=0``, ``UPDATE_FULL=1``, ``UPDATE_DELTA=2``.

Key semantics:

- ``header.stamp`` is the publish/batch timestamp.
- Each ``StateSample.header.stamp`` is the source observation timestamp.
- ``sequence`` is per ``source_uuid`` stream.
- ``description_version`` identifies the ``StateDescription`` version.
- ``UPDATE_FULL`` is a complete snapshot; ``UPDATE_DELTA`` is a partial change set.

Delta updates should not be applied while inactive. Full snapshots may be
cached while inactive only by explicit policy.

Sprint 18.7 - StateCommand.msg Design Notes
===========================================

**Status.** Completed.

**Track.** State Architecture / ROS ABI.

**Scope.** Message definition design and implementation for ``StateCommand``.

Purpose
-------

``StateCommand`` v0 represents a single-target requested mutation. It expresses
intent: "I request this target descriptor to change to this desired value." It
is not observed truth and does not claim that the requested value is already
true or has been accepted.

Batched command semantics are explicitly deferred.

Field Ordering Rationale
------------------------

Fields are organized logically for readability (command metadata, not
high-frequency transport).

Grouping:

1. **Transport header.** ``std_msgs/Header`` carries command request event
   metadata.

2. **Command identity and scoping group.** ``source_uuid``, ``target_uuid``,
   ``schema_uuid``.
   - ``source_uuid``: requester identity for authorization and audit.
   - ``target_uuid``: intended receiver (not broadcast by default in v0).
   - ``schema_uuid``: identifies the ``StateDescription`` used to interpret the
     target descriptor and value type.

3. **Ordering and versioning group.** ``sequence``, ``description_version``.
   - ``sequence``: per ``source_uuid`` stream, for loss/duplicate/order detection.
   - ``description_version``: ``StateDescription`` version for schema compatibility.

4. **Target descriptor identity group.** ``target_descriptor_id``,
   ``target_descriptor_uuid``, ``target_key``.
   - Triple identity pattern matching ``StateDescriptor`` and ``StateSample``.

5. **Requested value group.** ``type``, ``bool_value``, ``int_value``,
   ``uint_value``, ``float_value``, ``string_value``.
   - Same variant pattern as ``StateSample``. ``type`` selects exactly one active
     value field.

Field Decisions
---------------

Single-target v0
~~~~~~~~~~~~~~~~

``StateCommand`` v0 commands exactly one target descriptor per message. No
``StateSample[]`` array, no multi-target batch. This keeps the v0 contract
simple, reviewable, and aligned with the Sprint 17 RFC decision.

Batched commands are deferred until a concrete use case reopens the discussion.
The expected approach for multi-target commands would be separate
``StateCommand`` messages per target, not a batch list in a single message.

Command UUID Not Included
~~~~~~~~~~~~~~~~~~~~~~~~~

The Sprint 17 conceptual sketch included ``command_uuid``. Sprint 18.7 omits it
for v0. The triple ``(source_uuid, sequence, target_descriptor_uuid)`` is
sufficient to correlate commands with outcomes. A dedicated ``command_uuid``
can be added in a future ABI revision if feedback paths require explicit
correlation beyond what sequence-based tracking provides.

Source and Target as UUIDs
~~~~~~~~~~~~~~~~~~~~~~~~~~

The conceptual sketch used ``source`` and ``receiver`` as generic identities.
Sprint 18.7 uses ``source_uuid`` and ``target_uuid`` as
``unique_identifier_msgs/UUID`` for consistency with ``StateUpdate``
(``source_uuid``, ``schema_uuid``) and for deterministic identity across
launches and bridges.

Schema UUID
~~~~~~~~~~~

``schema_uuid`` is included for the same reason it appears in ``StateUpdate``:
a command receiver must know which ``StateDescription`` defines the target
descriptor. Without it, a receiver with multiple schemas cannot safely
interpret ``target_descriptor_id``.

Sequence per Source
~~~~~~~~~~~~~~~~~~~

``sequence`` is per ``source_uuid`` stream, matching ``StateUpdate`` semantics.
This allows receivers to detect gaps, duplicates, or out-of-order commands
from a known requester.

Description Version
~~~~~~~~~~~~~~~~~~~

``description_version`` carries the ``StateDescription`` version used by the
sender. If a receiver has a different version, it must not blindly apply the
command. The mismatch signals potential semantic incompatibility.

Type Constants
~~~~~~~~~~~~~~

``TYPE_*`` constants are duplicated from ``StateDescriptor.msg`` and
``StateSample.msg`` for v0 consistency. Sprint 18.8 will decide whether to
extract a shared ``StateType.msg``.

Command Acceptance Not Encoded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``StateCommand`` does not encode acceptance, rejection, or progress. Future
feedback paths (``StateUpdate``, service responses, action feedback, dedicated
command status) are deferred. The message contract only expresses the requested
mutation.

Constraints Not Encoded
~~~~~~~~~~~~~~~~~~~~~~~

Validation expectations (descriptor existence, type match, writable flag,
direction, description_version, target ownership, lifecycle active state) are
documented as future receiver responsibilities. None are implemented in the
message package.

Deferred Non-Goals
-------------------

- **Batched commands.** ``StateSample[]`` and multi-target lists are deferred.
- **Command feedback.** No ``command_status``, ``command_result``, or
  ``command_ack`` messages.
- **Command validation logic.** No Python code for validation, authorization,
  or lifecycle gating.
- **Lifecycle integration.** ``StateCommand`` handling rules are documented
  but not implemented.
- **Registry behavior.** No ``StateRegistry`` lookup or ownership resolution.

Documentation Consistency
-------------------------

- ``message_semantics.rst``: Updated to reflect actual message fields with a
  concrete example.
- ``rfc_001_lifecore_state_architecture.rst``: Already states "StateCommand v0
  is single-target" and "Batched commands are deferred."
- ``sprint_18_lifecore_state_msgs_abi.rst``: Acceptance criteria updated.
