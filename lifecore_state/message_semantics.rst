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

Sprint 17.7 is documentation-only. It does not change lifecycle behavior for
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

``StateDescription`` is a versioned collection of descriptors for a known
schema or registry scope. It is metadata, not observed truth. Consumers use it
to understand later samples, updates, projections, and commands.

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

Conceptual fields:

``header``
	Header whose timestamp represents the source timestamp when the value was
	observed. A future ABI may also name this field ``source_timestamp`` directly
	if that proves clearer than overloading a transport header.

``descriptor_id`` or ``descriptor_uuid``
	Link to the descriptor being sampled. Whether every sample carries a UUID or
	uses compact IDs remains open for ABI review.

``key``
	Optional canonical key when readability or bridge behavior requires it.

``type``
	Declared active value type for this sample.

``quality``
	Reliability state for the value, such as ``VALID``, ``STALE``, or
	``COMM_ERROR``. Quality describes value reliability, not lifecycle state.

``source``
	Source or owner identity responsible for the observation. This is semantic
	source context and must not be inferred only from the ROS node relaying the
	message.

``bool_value``
	Active only when ``type`` selects a boolean value.

``int_value``
	Active only when ``type`` selects a signed integer value.

``uint_value``
	Active only when ``type`` selects an unsigned integer value.

``float_value``
	Active only when ``type`` selects a floating-point value.

``string_value``
	Active only when ``type`` selects a string value.

The ``type`` field selects exactly one active value field. Consumers must treat
multiple populated value fields, or a populated field that does not match
``type``, as invalid or quarantined input according to the accepted mismatch
policy.

Non-final example sketch::

		[NON-FINAL SKETCH]

		StateSample
			header.stamp: 2026-05-16T10:30:00.125Z  # source observation time
			descriptor_id: 17
			type: FLOAT
			quality: VALID
			source: robot_1/battery_controller
			bool_value: inactive
			int_value: inactive
			uint_value: inactive
			float_value: 24.7
			string_value: inactive

StateUpdate
-----------

``StateUpdate`` is a synchronization event for a known source and schema. It
carries a batch of samples and enough ordering metadata for consumers to detect
loss, duplicates, schema mismatches, and snapshot or delta meaning.

Conceptual fields:

``header``
	Header whose timestamp represents the publish timestamp when the update was
	sent on the transport.

``source_uuid``
	Stable identity of the source, owner, registry, or publisher scope for this
	update.

``schema_uuid``
	Identity of the schema or description used to interpret the samples.

``sequence``
	Ordered sequence number used to detect loss, duplicates, and order
	violations within the source and schema scope.

``description_version``
	Version of the description expected by this update. Consumers compare it to
	their cached ``StateDescription`` before interpreting samples.

``update_mode``
	Either ``FULL`` or ``DELTA``. ``FULL`` means a snapshot for the declared
	scope. ``DELTA`` means partial changes that require known continuity.

``samples``
	Array of ``StateSample`` entries.

Non-final example sketch::

		[NON-FINAL SKETCH]

		StateUpdate
			header.stamp: 2026-05-16T10:30:00.140Z  # publish time
			source_uuid: 1c5d7d6e-3a40-5fc8-bd7e-bd4c7c39f0db
			schema_uuid: 8ed3b983-59e3-54b2-9a1d-77ff0c5964ea
			sequence: 2042
			description_version: 12
			update_mode: DELTA
			samples:
				- descriptor_id: 17
					type: FLOAT
					quality: VALID
					float_value: 24.7

StateCommand
------------

``StateCommand`` is requested intent. It asks an owner or receiver to mutate a
state target, perform an operation, or move toward a desired value. It is not
observed truth and must not be interpreted as proof that the requested state has
already happened.

Conceptual fields:

``header``
	Transport timestamp for the command request.

``command_uuid``
	Unique identity for the command request so receivers and feedback paths can
	correlate outcomes.

``target_descriptor_id`` or ``target_descriptor_uuid``
	Descriptor being commanded.

``target_key``
	Optional canonical key for readability or bridge behavior.

``type``
	Requested value type. It follows the same one-active-value-field rule as
	samples.

``source``
	Identity of the requester.

``receiver``
	Intended owner or receiver, when the command is not broadcast to a scoped
	authority.

``bool_value``, ``int_value``, ``uint_value``, ``float_value``, ``string_value``
	Explicit requested value fields. The ``type`` field selects exactly one active
	field.

The receiver must validate descriptor existence, authority, lifecycle readiness,
safety policy, type compatibility, and range constraints before acting.
Acceptance of a command is separate from command success. A later
``StateUpdate`` may show the observed result, or an explicit feedback path may
acknowledge, reject, or report progress for the request.

Non-final example sketch::

		[NON-FINAL SKETCH]

		StateCommand
			header.stamp: 2026-05-16T10:31:00.000Z
			command_uuid: b4ff54d7-2068-5e8d-9d6f-3cc912a0a95f
			target_descriptor_id: 42
			target_key: drive/linear_velocity/setpoint
			type: FLOAT
			source: operator_console
			receiver: robot_1/drive_controller
			float_value: 0.4

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

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
