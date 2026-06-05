Message Semantics
=================

Purpose
-------

This document defines conceptual message semantics for future
``lifecore_state`` work before any ROS 2 interface package, ABI commitment, or
runtime implementation exists. It explains what future descriptors,
descriptions, samples, updates, and commands mean so a later Sprint 18 message
prototype can start from stable semantics rather than ad hoc field choices.

The content here is architecture-only. It is not a ``.msg`` specification, does
not create ROS 2 interfaces, does not add Python code, and does not change any
current ``lifecore_ros2`` public API.

Lifecycle behavior contract
---------------------------

Sprint 17 message semantics documentation is documentation-only. It does not change lifecycle behavior for
any existing node, component, publisher, subscriber, timer, service, or
watchdog.

- **configure:** no runtime resource creation changes.
- **activate:** no activation gate changes.
- **deactivate:** no deactivation behavior changes.
- **cleanup:** no cleanup behavior changes.
- **shutdown:** no shutdown behavior changes.
- **error:** no error recovery changes.

Future lifecycle/state integration remains governed by the Sprint 17 separation
rules: ``StateDescription`` metadata may be cached while inactive,
``StateUpdate`` deltas are not applied while inactive, and ``StateCommand``
handling requires active lifecycle readiness.

Message design principles
-------------------------

Future message contracts should be ROS-native, explicit, and stable. Message
fields should describe state semantics directly instead of hiding meaning in
opaque payloads or runtime-specific policy.

ROS-native transport
	Use ROS concepts such as topics, headers, timestamps, and QoS profiles
	directly when they carry transport meaning. A future ABI should make topic
	roles and QoS expectations reviewable instead of burying them in helper code.

Explicit fields
	Use named fields for identity, type, timestamp, quality, source, and value.
	Do not use JSON-in-string payloads as the normal way to transport typed state.

Stable contracts
	Message contracts should remain small, deterministic, and compatible with
	long-lived consumers. Schema or description versions should make incompatible
	interpretation visible.

No hidden synchronization magic
	Snapshots, deltas, sequence numbers, and schema versions must be explicit.
	A consumer should be able to tell whether it has enough history and metadata
	to apply an update.

No dynamic magic
	The future ABI should not depend on Python object identity, process-local
	counters, subscription order, reflection-only payloads, or implicit runtime
	registries.

One active value field
	A sample's ``type`` field selects exactly one active value field. For example,
	a ``type`` of ``FLOAT`` makes ``float_value`` meaningful and leaves the other
	value fields inactive.

StateDescriptor
---------------

``StateDescriptor`` is the stable contract for one state field or stream inside
a registry scope. It answers what state exists, how it is identified, how it is
typed, and whether it can be commanded.

Conceptual fields:

``id``
	Compact numeric identifier inside the declared description or registry scope.
	This is useful for compact updates, but it is not globally meaningful by
	itself.

``uuid``
	Stable identifier for the descriptor when a persistent identity is needed
	across launches, exports, or bridges. When possible, identity should be
	derived from stable semantic paths rather than generated at runtime.

``key``
	Canonical path or stable logical name, such as
	``battery/pack/main/voltage``. This is the human-reviewable identity anchor.

``type``
	Declared value type. The accepted type names are non-final, but the field
	must select one active value representation in future samples and commands.

``direction``
	Direction of allowed flow for the descriptor, such as read-only observed
	state, commandable target, or bidirectional state with explicit authority.

``unit``
	Optional physical or semantic unit, such as ``V``, ``A``, ``degC``, ``m/s``,
	or an empty value when the descriptor is unitless.

``writable``
	Indicates whether a future ``StateCommand`` may request mutation for this
	descriptor. It does not mean that every command will be accepted.

``safety_related``
	Marks descriptors whose misuse can affect safety policy, operator review, or
	command validation. It is metadata, not a runtime safety implementation.

``metadata``
	Optional structured metadata for display names, constraints, owner hints, or
	documentation links. Metadata must not replace the explicit fields above.

Non-final example sketch::

		[NON-FINAL SKETCH]

		StateDescriptor
			id: 17
			uuid: 5a8e2c8e-3f25-5e48-8f31-8a8a4f1df9b2
			key: battery/pack/main/voltage
			type: FLOAT
			direction: OUT
			unit: V
			writable: false
			safety_related: true
			metadata: {display_name: Main battery voltage}

StateDescription
----------------

``StateDescription`` is a versioned collection of ``StateDescriptor`` entries
for a schema/scope. It is metadata, not observed truth. Consumers use it to
understand later samples, updates, projections, and commands.

Conceptual fields:

``header``
	Transport header for the description publication event, if a future ABI uses
	one.

``schema_uuid``
	Stable identity for the schema or registry description being declared.

``description_version``
	Monotonic or otherwise comparable version used to detect schema mismatches.

``descriptors``
	Array of ``StateDescriptor`` entries that define known fields for the schema.

QoS direction:

- reliability: ``RELIABLE``;
- durability: ``TRANSIENT_LOCAL``;
- history: ``KEEP_LAST(1)``.

This QoS direction supports late joiners. A future subscriber may receive and
cache the latest description while lifecycle inactive because the description is
metadata. Caching a description while inactive must not trigger active runtime
behavior and must not prove that any observed value is current or valid.

Non-final example sketch::

		[NON-FINAL SKETCH]

		StateDescription
			header: transport header for description publication
			schema_uuid: 8ed3b983-59e3-54b2-9a1d-77ff0c5964ea
			description_version: 12
			descriptors:
				- battery/pack/main/voltage
				- battery/pack/main/current
				- battery/pack/main/temperature

StateSample
-----------

``StateSample`` is one observed value for one descriptor at one source time,
with quality and source context. A sample is the semantic unit of observed
state; it is not by itself a synchronization batch.

Decided fields (Sprint 18.5):

``header``
	``header.stamp`` is the source timestamp: the time when the value was
	observed at the source. This is not the publication time of the containing
	``StateUpdate``. See the timestamp semantics section.

``descriptor_id``
	Compact numeric identifier within the ``StateDescription`` scope. Matches
	``StateDescriptor.id``. Efficient for high-frequency streaming.

``descriptor_uuid``
	Stable persistent identifier across launches and bridges. Matches
	``StateDescriptor.uuid``.

``key``
	Canonical path or logical name for readability and bridge behavior. Matches
	``StateDescriptor.key``.

``type``
	Declared active value type for this sample. Uses the same ``TYPE_*``
	constants as ``StateDescriptor.msg``.

``quality``
	Reliability and validity state of the observed value. Quality describes the
	sample, not lifecycle state. Constants: ``QUALITY_UNKNOWN=0``,
	``QUALITY_VALID=1``, ``QUALITY_STALE=2``, ``QUALITY_INVALID=3``,
	``QUALITY_COMM_ERROR=4``, ``QUALITY_OUT_OF_RANGE=5``, ``QUALITY_FORCED=6``,
	``QUALITY_SIMULATED=7``, ``QUALITY_DISABLED=8``, ``QUALITY_NOT_AVAILABLE=9``.

``source``
	Semantic identity of the observation origin. Not the same as the ROS node
	relaying the message. Constants: ``SOURCE_UNKNOWN=0``,
	``SOURCE_HARDWARE=1``, ``SOURCE_SOFTWARE=2``, ``SOURCE_SIMULATION=3``,
	``SOURCE_OPERATOR=4``, ``SOURCE_REPLAY=5``. ``SOURCE_COMMANDED`` is excluded
	because a sample reports observed truth; ``StateCommand`` expresses intent.

``bool_value``
	Active only when ``type = TYPE_BOOL``.

``int_value``
	Active only when ``type`` selects a signed integer type.

``uint_value``
	Active only when ``type`` selects an unsigned integer type.

``float_value``
	Active only when ``type`` selects a floating-point type.

``string_value``
	Active only when ``type = TYPE_STRING``.

The ``type`` field selects exactly one active value field. Consumers must treat
multiple populated value fields, or a populated field that does not match
``type``, as invalid or quarantined input according to the accepted mismatch
policy.

Example (Sprint 18.5)::

		StateSample
			header.stamp: 2026-05-16T10:30:00.125Z  # source observation time
			descriptor_id: 17
			descriptor_uuid: 5a8e2c8e-3f25-5e48-8f31-8a8a4f1df9b2
			key: "battery/pack/main/voltage"
			type: TYPE_FLOAT64
			quality: QUALITY_VALID
			source: SOURCE_HARDWARE
			bool_value: false
			int_value: 0
			uint_value: 0
			float_value: 24.7
			string_value: ""

StateUpdate
-----------

``StateUpdate`` is a synchronization event for a known source and schema. It
carries a batch of samples and enough ordering metadata for consumers to detect
loss, duplicates, schema mismatches, and snapshot or delta meaning.

Decided fields (Sprint 18.6):

``header`` (std_msgs/Header)
	``header.stamp`` is the publish/batch timestamp: the time when this update
	was assembled and sent on the transport. Each contained
	``StateSample.header.stamp`` is the source observation timestamp. These
	timestamps may differ. See the timestamp semantics section.

``source_uuid`` (unique_identifier_msgs/UUID)
	Stable identity of the source, owner, or publisher scope for this update.
	Sequence numbers are per ``source_uuid`` stream.

``schema_uuid`` (unique_identifier_msgs/UUID)
	Identity of the schema or ``StateDescription`` used to interpret the
	samples. Must match ``StateDescription.schema_uuid`` for the declared
	``description_version``.

``sequence`` (uint64)
	Monotonically increasing sequence number per ``source_uuid`` stream.
	Used to detect lost, duplicated, out-of-order, or discontinuous updates.

``description_version`` (uint64)
	``StateDescription`` version used to interpret descriptor ids, types, and
	semantics. Receivers must not blindly apply updates against a different
	version. A mismatch signals potential semantic incompatibility.

``update_mode`` (uint8)
	Declares whether this update is a full snapshot or a partial delta.
	Constants: ``UPDATE_UNKNOWN=0``, ``UPDATE_FULL=1``, ``UPDATE_DELTA=2``.

	``UPDATE_FULL``: complete snapshot for the publisher's declared scope.
	Useful for startup, resynchronization, and debugging.

	``UPDATE_DELTA``: only changed samples since the prior update. Assumes
	receiver has compatible prior state. Should not be applied after unknown
	history unless explicit checks allow it.

``samples`` (StateSample[])
	Array of observed ``StateSample`` values. For ``UPDATE_FULL``, this
	represents a complete snapshot. For ``UPDATE_DELTA``, only changed
	samples are included.

Example (Sprint 18.6)::

		StateUpdate
			header.stamp: 2026-05-16T10:30:00.140Z  # publish/batch time
			source_uuid: 1c5d7d6e-3a40-5fc8-bd7e-bd4c7c39f0db
			schema_uuid: 8ed3b983-59e3-54b2-9a1d-77ff0c5964ea
			sequence: 2042
			description_version: 12
			update_mode: UPDATE_DELTA
			samples:
				- header.stamp: 2026-05-16T10:30:00.125Z  # source observation time
				  descriptor_id: 17
				  type: TYPE_FLOAT64
				  quality: QUALITY_VALID
				  source: SOURCE_HARDWARE
				  float_value: 24.7

StateCommand
------------

``StateCommand`` v0 is a single-target requested mutation. It expresses intent:
"I request this target descriptor to change to this desired value." It is not
observed truth and must not be interpreted as proof that the requested state has
already happened or has been accepted.

Batched command semantics (multiple targets in one message) are explicitly
deferred until a concrete future need reopens the decision.

Decided fields (Sprint 18.7):

``header`` (std_msgs/Header)
	Transport header for the command request event metadata.

``source_uuid`` (unique_identifier_msgs/UUID)
	Stable identity of the requester issuing this command. Used to correlate
	commands with a specific source for authorization and audit.

``target_uuid`` (unique_identifier_msgs/UUID)
	Intended owner or receiver for this command. When the command is not
	broadcast to a scoped authority, ``target_uuid`` identifies the expected
	receiver.

``schema_uuid`` (unique_identifier_msgs/UUID)
	Schema used to interpret the target descriptor and value type. Must match
	``StateDescription.schema_uuid`` for the declared ``description_version``.

``sequence`` (uint64)
	Monotonically increasing sequence number per ``source_uuid`` stream. Used to
	detect lost, duplicated, or out-of-order commands.

``description_version`` (uint64)
	``StateDescription`` version used to interpret the target descriptor identity,
	type, and semantics. Receivers must not blindly apply commands against a
	different ``description_version``.

``target_descriptor_id`` (uint32)
	Compact numeric identifier of the target descriptor within the schema scope.
	Matches ``StateDescriptor.id``.

``target_descriptor_uuid`` (unique_identifier_msgs/UUID)
	Stable persistent identifier for the target descriptor. Matches
	``StateDescriptor.uuid``.

``target_key`` (string)
	Canonical path or logical name for readability and bridge behavior. Matches
	``StateDescriptor.key``.

``type`` (uint8)
	Declared value type for the requested mutation. Selects exactly one active
	value field below. Uses the same ``TYPE_*`` constants as
	``StateDescriptor.msg`` and ``StateSample.msg``.

``bool_value``, ``int_value``, ``uint_value``, ``float_value``, ``string_value``
	Desired value as explicit variant fields. Exactly one field is active,
	selected by ``type``.

Acceptance or rejection is not encoded by ``StateCommand`` itself. Future
feedback may be represented through ``StateUpdate`` reflecting an observed
change, service responses, action feedback, or a dedicated command status
message. None of these feedback paths are implemented in Sprint 18.

The receiver must validate descriptor existence, authority, lifecycle readiness,
safety policy, type compatibility, and range constraints before acting.
Acceptance of a command is separate from command success.

Example (Sprint 18.7)::

		StateCommand
			header.stamp: 2026-05-16T10:31:00.000Z
			source_uuid: a1b2c3d4-e5f6-7890-abcd-ef1234567890
			target_uuid: f0e1d2c3-b4a5-9687-8fed-cba987654321
			schema_uuid: 8ed3b983-59e3-54b2-9a1d-77ff0c5964ea
			sequence: 157
			description_version: 12
			target_descriptor_id: 42
			target_descriptor_uuid: 7f8e9d0c-1b2a-3456-7890-abcdef123456
			target_key: "drive/linear_velocity/setpoint"
			type: TYPE_FLOAT64
			bool_value: false
			int_value: 0
			uint_value: 0
			float_value: 0.4
			string_value: ""

Snapshot semantics
------------------

A snapshot is a full-state synchronization event for the declared source,
schema, and scope. In ``StateUpdate`` terms, a snapshot uses
``update_mode = FULL``.

A full update means all known fields for the declared scope are present or are
explicitly represented according to the accepted schema rules. A consumer can
use a valid snapshot to rebuild current state for that scope without relying on
older deltas.

Snapshots are useful after startup, late join, schema changes, sequence gaps,
or inactive periods. Receiving a snapshot while inactive may be useful for
future resynchronization, but it must not trigger active behavior by itself.

Delta semantics
---------------

A delta is a partial-state synchronization event. In ``StateUpdate`` terms, a
delta uses ``update_mode = DELTA``.

A delta contains only changes since a known prior state. Applying a delta
requires:

- sequence continuity within the source and schema scope;
- a known ``schema_uuid`` and compatible ``description_version``;
- confidence that no required history was missed;
- a lifecycle policy that allows active runtime interpretation.

Deltas are unsafe after unknown history unless schema rules or a later snapshot
allow recovery. A consumer that sees a sequence gap, duplicate, order violation,
unknown schema, or incompatible description version should reject or quarantine
the delta rather than silently applying it.

Timestamp semantics
-------------------

Source time and publish time are different facts and should remain distinct.

``sample.source_timestamp``
	Time when the value was observed at the source, such as the hardware sensor
	reading time or the semantic observation time. If a future ABI uses a
	``Header`` inside ``StateSample``, that header timestamp carries this meaning.

``update.publish_timestamp``
	Time when the update message was sent on the transport. If a future ABI uses
	a ``Header`` inside ``StateUpdate``, that header timestamp carries this
	meaning.

A value can be old but published recently, or observed recently but delayed in
transport. Consumers need both meanings to judge freshness and synchronization
health.

Quality semantics
-----------------

Quality describes reliability of a value. It is not business state and is not
lifecycle state.

``VALID``
	The value is trusted by the source under current rules.

``STALE``
	The value is too old for the declared freshness policy, even if the last
	payload was well-formed.

``INVALID``
	The value is malformed, semantically invalid, or cannot be interpreted safely.

``COMM_ERROR``
	The source reports a communication failure affecting the value.

``OUT_OF_RANGE``
	The value is outside declared physical, semantic, or safety limits.

``FORCED``
	The value was manually forced, overridden, or injected by an operator or tool.

``SIMULATED``
	The value is produced by simulation rather than the real source of record.

``DISABLED``
	The underlying source or function is disabled.

``NOT_AVAILABLE``
	No value is currently available or known.

Future ABI work may decide whether quality is a fixed enum, flags, or a
structured field. The semantic distinction above must remain visible either
way.

Version and sequence semantics
------------------------------

``sequence`` detects order and continuity problems inside a source and schema
scope. Consumers use it to detect:

- lost updates when a number is skipped;
- duplicate updates when a number repeats;
- order violations when an older number arrives after a newer one.

``description_version`` detects schema mismatch. Consumers compare an update's
version with the cached ``StateDescription`` for the same ``schema_uuid`` before
interpreting descriptor IDs, keys, types, or values.

Mismatch policy should be explicit. Initial policy vocabulary:

``REJECT``
	Refuse to apply the update or command because required continuity or schema
	knowledge is missing.

``QUARANTINE``
	Preserve the message for diagnostics or later review while keeping it out of
	trusted live state.

Silent best-effort interpretation is not an accepted default for mismatched
schema or broken sequence continuity.

QoS recommendations
-------------------

QoS should follow message semantics instead of using one default for every
state flow.

``StateDescription``
	``RELIABLE`` + ``TRANSIENT_LOCAL`` + ``KEEP_LAST(1)``. Description metadata
	should be discoverable by late joiners and cacheable while inactive.

``StateUpdate``
	``BEST_EFFORT`` or ``RELIABLE`` by criticality, with ``VOLATILE`` and
	``KEEP_LAST(1)``. High-rate non-critical telemetry may accept loss when
	sequence checks and snapshots provide recovery. Critical state may require
	reliable delivery.

``StateCommand``
	``RELIABLE`` with ``VOLATILE`` history. Commands are requests, not durable
	state facts; late joiners should not receive stale command intent as if it
	were current truth.

Non-final message sketches
--------------------------

The following pseudo-message blocks are non-final sketches for discussion only.
They are intentionally not valid ROS 2 ``.msg`` files and must not be copied as
ABI definitions without a later review.

.. code-block:: text

		[NON-FINAL SKETCH]

		StateDescriptor
			uint32 id
			uuid uuid
			string key
			ValueType type
			Direction direction
			string unit
			bool writable
			bool safety_related
			Metadata metadata

.. code-block:: text

		[NON-FINAL SKETCH]

		StateDescription
			Header header
			uuid schema_uuid
			uint64 description_version
			StateDescriptor[] descriptors

.. code-block:: text

		[NON-FINAL SKETCH]

		StateSample
			Header source_header
			uint32 descriptor_id
			uuid descriptor_uuid
			string key
			ValueType type
			Quality quality
			string source
			bool bool_value
			int64 int_value
			uint64 uint_value
			float64 float_value
			string string_value

.. code-block:: text

		[NON-FINAL SKETCH]

		StateUpdate
			Header publish_header
			uuid source_uuid
			uuid schema_uuid
			uint64 sequence
			uint64 description_version
			UpdateMode update_mode  # FULL or DELTA
			StateSample[] samples

.. code-block:: text

		[NON-FINAL SKETCH]

		StateCommand
			Header request_header
			uuid command_uuid
			uint32 target_descriptor_id
			uuid target_descriptor_uuid
			string target_key
			ValueType type
			string source
			string receiver
			bool bool_value
			int64 int_value
			uint64 uint_value
			float64 float_value
			string string_value

Decided ABI scope
-----------------

Initial ``StateCommand`` semantics are single-target: one ``StateCommand``
targets one descriptor. Batched commands are deferred until a concrete need is
established. Sprint 18 must not assume batched command semantics without
explicitly reopening this decision.

Open questions
--------------

- What is the minimal descriptor identity that remains stable across launches,
	and should samples carry UUIDs directly or normally reference compact
	descriptor IDs after a description is known?
- Which fields belong in ABI messages versus pure Python validation helpers,
	including whether ``default_value`` belongs in ``StateDescriptor`` or in a
	separate semantic policy layer?
- Is a compact sample type needed for high-rate state streams?
- Should command feedback be represented as a message, service, or action?
- Should quality be represented as a fixed enum, extensible flags, or a
	structured status field?
- How should delta continuity, sequence recovery, and resynchronization be
	represented in ROS messages?
- Which compatibility rules should govern ``description_version`` and future
	descriptor versioning changes?
- Should future ABI work name source and publish timestamps directly, or use
	distinct headers with documented timestamp meaning?
- Should projections be declared by descriptors, policy objects, or separate
	projection documents?
- Does Sprint 18 need explicit terminology for ``StateStore`` or
	``StateMirror``, or is the registry distinction sufficient?
