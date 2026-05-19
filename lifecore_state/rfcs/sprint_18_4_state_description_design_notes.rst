Sprint 18.4 - StateDescription.msg Design Notes
===============================================

**Status.** Completed.

**Track.** State Architecture / ROS ABI.

**Scope.** Message definition design and implementation for ``StateDescription``.

Purpose
-------

This document records the design rationale, field decisions, and semantic
choices for the second concrete ROS 2 message definition in the Sprint 18
messages-only ABI prototype.

Message Purpose
---------------

``StateDescription`` is a versioned collection of ``StateDescriptor`` entries.
It represents a coherent schema/scope description and serves as metadata that
consumers use to understand the structure and constraints of related
``StateSample`` and ``StateCommand`` messages. It is not one descriptor, runtime
state, a state value, or a command.

Field Ordering Rationale
------------------------

Fields are organized logically for readability rather than transport
optimization. ``StateDescription`` is schema metadata, not a high-frequency
transport structure. Logical grouping is more maintainable than attempting
byte-packing or alignment optimization at this stage.

Grouping:

1. **Transport header.** ``std_msgs/Header`` carries the description publication
   event metadata.

2. **Schema and versioning group.** ``schema_uuid`` and ``description_version``
   establish stable identity and allow consumers to detect schema incompatibility.

3. **Descriptors group.** ``descriptors[]`` contains the coherent collection of
   ``StateDescriptor`` entries that define the state schema.

Field Decisions
---------------

Transport Header
~~~~~~~~~~~~~~~~

``header`` (std_msgs/Header)
	Carries the description publication event metadata.
	- ``header.stamp`` records the time this description was published or generated.
	- ``header.frame_id`` remains available for future use (transport-native).

Schema and Versioning
~~~~~~~~~~~~~~~~~~~~~

``schema_uuid`` (unique_identifier_msgs/UUID)
	Stable identifier for the schema or registry scope being declared by this
	description. This UUID identifies which state domain or state registry this
	description covers. Consumers use this to match descriptions with related
	samples, updates, and commands. The UUID should be derived from stable
	semantic paths or registry names rather than generated at runtime when
	possible, ensuring persistence across launches and bridges.

``description_version`` (uint64)
	Version number for this description. Increments when the descriptor set or
	descriptor meaning changes. Allows consumers to:
	- Detect schema incompatibility when comparing cached descriptions.
	- Determine whether new descriptors have been added or existing ones modified.
	- Stale cached metadata becomes detectable when a new version is received.

	Version numbering is left flexible (monotonic, semantic, or timestamp-based)
	at the application level. The message itself only requires that consumers can
	compare versions as comparable numbers.

Descriptors Collection
~~~~~~~~~~~~~~~~~~~~~~

``descriptors`` (StateDescriptor[])
	Coherent collection of ``StateDescriptor`` entries that define the state
	fields or streams within this schema. Each descriptor describes one state
	field contract.
	- The descriptors array is the primary payload.
	- The array must not be empty when a valid ``StateDescription`` is published.
	- Order within the array is meaningful for human readability and should be
	  stable across versions when possible (though not required by the ABI).
	- Consumers must not rely on array indices for semantic meaning; use descriptor
	  identity fields (``uuid``, ``key``, or ``id``) instead.

Semantics and Lifecycle Implications
------------------------------------

**No lifecycle behavior changes.** This is a message definition only. No ROS 2
lifecycle hooks, state machines, or behavioral side effects are introduced.

**Future lifecycle/state integration (deferred):**

- ``StateDescription`` metadata may be received and cached while a lifecycle
  node or component is inactive because ROS 2 transient-local QoS may deliver
  the message as soon as a subscription is created during the configure phase.
- Caching a description while inactive must not trigger active runtime behavior.
- The fact that a node is inactive does not prove that state samples or commands
  are stale or invalid.
- Command handling and sample validation logic depend on runtime state and are
  deferred to future ``lifecore_state_core`` or ``lifecore_state_ros`` packages.

**QoS direction (no implementation, advisory only):**

Future ROS integration should use:
	- reliability: ``RELIABLE`` (descriptions are small metadata).
	- durability: ``TRANSIENT_LOCAL`` (late joiners need the latest description).
	- history: ``KEEP_LAST(1)`` (only the latest description is relevant).

This QoS profile supports late-joining subscribers to receive and cache
descriptions without requiring the publisher to remain running.

Non-Final Example Instance
--------------------------

.. code-block:: text

	[NON-FINAL EXAMPLE]

	StateDescription
		header.stamp: 2026-05-16T10:30:00.125Z
		schema_uuid: 8ed3b983-59e3-54b2-9a1d-77ff0c5964ea
		description_version: 12

		descriptors:
			- StateDescriptor(id=17, key=battery/pack/main/voltage, type=FLOAT, ...)
			- StateDescriptor(id=18, key=battery/pack/main/current, type=FLOAT, ...)
			- StateDescriptor(id=19, key=battery/pack/main/temperature, type=FLOAT, ...)

Deferred Non-Goals
-------------------

The following concepts are explicitly deferred and not present in
``StateDescription.msg``:

- **Current runtime values.** ``StateDescription`` is schema metadata only. No
  sample values or observed state are included.

- **Default values.** No ``default_value`` or ``default_descriptor`` field.
  Defaults are policy concerns and belong to application or registry logic,
  not the ABI.

- **Command semantics.** ``StateDescription`` does not specify command feedback,
  acknowledgment, or validation rules. Command handling is deferred to
  ``lifecore_state_core`` or ``lifecore_state_ros``.

- **Lifecycle semantics.** No integration with ROS 2 lifecycle states or
  transition logic. State metadata caching during inactive phases is allowed
  but does not change lifecycle behavior.

- **Registry behavior.** ``StateDescription`` does not specify ownership,
  permissions, or registry lookup logic. Registry scope is named by
  ``schema_uuid`` only.

- **Persistence or archival flags.** Unlike ``StateDescriptor``, the collection
  itself does not carry metadata flags for safety, persistence, or special
  handling. Those concerns live at the descriptor level.

Serialization and ROS 2 Message Compatibility
----------------------------------------------

``StateDescription.msg`` is compiled by ``rosidl_default_generators`` into
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
	  msg/StateDescription.msg
	  DEPENDENCIES std_msgs unique_identifier_msgs
	)

This wires the message generation for both C++ and Python during the
``colcon build`` step (Sprint 18.9).

Documentation Consistency
-------------------------

Reference documents are consistent with the message design:

- **message_semantics.rst:** Contains the conceptual sketch for ``StateDescription``.
  Confirms that ``StateDescription`` is a versioned collection of
  ``StateDescriptor`` entries.

- **package_boundaries.rst:** Confirms that ``lifecore_state_msgs`` is the ROS 2
  interface package for state messages.

- **lifecycle_state_separation.rst:** Confirms that ``StateDescription`` metadata
  can be cached while inactive without triggering active runtime behavior.

- **rfc_001_lifecore_state_architecture.rst:** Locked decision recorded as
  ``StateDescription = versioned collection of StateDescriptor entries for a
  schema/scope``.

Comparison with StateDescriptor
-------------------------------

- **StateDescriptor** describes one state field contract (schema for one field).
- **StateDescription** describes a collection of descriptors (schema for a scope).

- **StateDescriptor** fields: identity, type, direction, metadata, flags, constraints.
- **StateDescription** fields: transport metadata, schema identity, version, descriptors array.

- **StateDescriptor** is reusable across multiple descriptions if registry lookup
  or projection is implemented in future.
- **StateDescription** is a snapshot collection—consumers work with the specific
  version they receive.

Verification
------------

``StateDescription.msg`` is a message definition file. Verification will occur
in Sprint 18.9 (Build Validation) with ``colcon build``.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is
accepted.
