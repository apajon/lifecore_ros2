RFC 001: lifecore_state architecture direction
==============================================

Status
------

Draft for Sprint 17.3.

This document is architecture-only. It records a proposed direction for future
``lifecore_state`` work and does not create an implementation commitment,
runtime package, ROS 2 interface package, public API, or lifecycle behavior
change.

During Sprint 17.3, ``lifecore_state/`` remains a documentation-only logical
folder at the repository root. Future package names in this RFC are planning
labels until a later sprint explicitly creates packages.

Context
-------

``lifecore_ros2`` is an explicit composition framework for ROS 2 lifecycle
nodes and managed entities. It keeps ROS 2 lifecycle semantics visible:
components configure resources, activate behavior, deactivate behavior, clean
up resources, shut down deterministically, and handle error transitions through
the existing lifecycle hooks.

The framework intentionally avoids hidden runtimes, hidden state machines,
giant managers, orchestration frameworks, plugin-heavy designs, and code
generation as a first design move.

``lifecore_state`` is a future architecture direction for typed distributed
state. It exists to make state contracts, identity, quality, registry scope,
and synchronization semantics reviewable before messages or runtime modules are
created.

Problem statement
-----------------

Robotics systems often need more than lifecycle activation and raw topic
traffic. They need typed state that can be discovered, described, projected,
checked for freshness, synchronized by registry scope, and transported through
ROS-native message contracts.

The future ``lifecore_state`` architecture must address these needs without
turning ``lifecore_ros2`` into a broad runtime platform or hiding state truth in
lifecycle transition machinery.

The core problems are:

- typed distributed state needs stable contracts before message ABI work;
- registry-scoped synchronization needs clear ownership and namespace rules;
- state projection needs deterministic identity so consumers know what they are
	observing;
- snapshot and delta synchronization need distinct semantics;
- quality-aware transport needs a way to describe validity, freshness, and
	confidence without confusing those concepts with business state;
- ROS-native message contracts need to remain ABI-oriented, not overloaded with
	runtime policy;
- lifecycle activation must remain separate from state validity.

Goals
-----

- Define architecture boundaries between ``lifecore_ros2`` and future
	``lifecore_state`` packages.
- Stabilize package separation before implementation begins.
- Document message semantics before compiled ROS 2 interfaces exist.
- Make lifecycle/state separation explicit and reviewable.
- Stabilize terminology for descriptors, descriptions, samples, updates,
	commands, registries, projections, snapshots, deltas, and quality.
- Reduce implementation risk before a future sprint considers message ABI work.

Non-goals
---------

``lifecore_state`` is not:

- a robotics operating system;
- a replacement for ROS 2 lifecycle nodes;
- a hidden lifecycle manager;
- an orchestration runtime;
- an EventBus framework;
- an ECS runtime;
- a global blackboard runtime;
- a plugin framework;
- a factory/spec system;
- a code generation-first design;
- a reason to add runtime state storage inside ``lifecore_ros2``;
- a reason to change lifecycle transition behavior during Sprint 17.3.

Naming decision
---------------

The recommended public architecture name is ``lifecore_state``.

The rejected alternative ``lifecore_io`` is too narrow. It suggests transport,
input/output channels, or device integration. The architecture under review is
broader: typed observed state, descriptions, commands, quality, projections,
registry-scoped synchronization, and lifecycle/state separation.

``lifecore_state`` names the source-of-truth concern directly without implying
that it owns lifecycle orchestration.

Repository organization decision
--------------------------------

During Sprint 17.3, ``lifecore_state/`` remains a root-level documentation group.
It is not importable runtime code and is not a ROS 2 package.

The Sprint 17 folder may contain only architecture documents, RFC material, and
review notes. It must not contain:

- ``package.xml``;
- ``CMakeLists.txt``;
- ``setup.py``;
- ``pyproject.toml``;
- Python runtime modules;
- compiled ``.msg`` files;
- compiled ``.srv`` files;
- compiled ``.action`` files.

If the architecture is accepted, later work may split the design into three
future packages:

- ``lifecore_state_msgs``;
- ``lifecore_state_core``;
- ``lifecore_state_ros``.

Those names remain planning labels in Sprint 17.

Future package boundaries
-------------------------

``lifecore_state_msgs``
	Future ROS 2 ABI contracts only. This package would own message definitions,
	service definitions if needed, semantic versioning of wire contracts, and ABI
	compatibility review.

``lifecore_state_core``
	Future pure Python state semantics. This package would own descriptors,
	descriptions, identity rules, validation helpers, policy objects, snapshot
	and delta semantics, projection semantics, and quality interpretation. It
	must not depend on ROS 2 or ``rclpy``.

``lifecore_state_ros``
	Future ROS 2 integration. This package may depend on ROS 2, ``rclpy``,
	``lifecore_state_msgs``, and ``lifecore_state_core``. It would adapt pure
	state semantics to ROS topics, services, QoS, nodes, and optional lifecycle
	integration points.

``lifecore_ros2``
	Existing lifecycle composition framework. It must remain independent from
	``lifecore_state`` unless a later sprint explicitly accepts an optional
	integration surface.

Dependency rules
----------------

- ``lifecore_ros2`` must not depend on future ``lifecore_state`` packages by
	default.
- ``lifecore_state_msgs`` must contain ABI contracts only and must not depend on
	``lifecore_ros2``.
- ``lifecore_state_core`` must remain pure Python and must not depend on ROS 2,
	``rclpy``, or ``lifecore_ros2``.
- ``lifecore_state_ros`` may depend on ROS 2, ``rclpy``,
	``lifecore_state_msgs``, and ``lifecore_state_core``.
- Optional future integration with ``lifecore_ros2`` must be explicit,
	reviewed, and additive.
- No package may introduce a parallel lifecycle state machine.

Conceptual model
----------------

This model is non-final. It names the concepts a future implementation sprint
may need to convert into message ABI, pure Python semantics, and ROS
integration responsibilities.

``StateDescriptor``
	Stable identity and type contract for a state field or state stream. A
	descriptor answers what state exists and how it is identified.

``StateDescription``
	Descriptive metadata for a descriptor. A description may include display
	names, units, constraints, owner metadata, and semantic hints. It helps
	consumers understand a descriptor without becoming the observed value.

``StateOwner``
	Entity considered authoritative for producing observed state, accepting
	commands, or rejecting mutations for a descriptor within a registry scope.
	Ownership is semantic and must not be inferred only from the ROS node
	currently publishing a message.

``StateSample``
	Observed semantic value at a point in time, including identity, value
	payload, timestamp information, and quality information.

``StateUpdate``
	Synchronization event that carries one or more observed changes for a known
	scope. An update may transport one or more samples, partial mutations,
	invalidation information, or a snapshot-equivalent payload depending on the
	accepted message semantics.

``StateCommand``
	Requested mutation or operation. A command is an intent sent toward an owner,
	not observed truth.

``StateRegistry``
	Scoped catalog of descriptors and descriptions for a known state space. A
	registry scope bounds identity and synchronization, but a registry must not
	be treated as a global mutable store by default.

``StateProjection``
	Consumer-oriented view over registry state. A projection may filter, rename,
	aggregate, or reshape state for a specific use without changing the source
	registry contract.

``StateSnapshot``
	Complete state image for a scope at a known synchronization point.

``StateDelta``
	Ordered change set that can be applied to a known prior state when continuity
	assumptions hold.

``StateQuality``
	Reliability metadata for a value or update, such as validity, freshness,
	confidence, source health, or staleness.

Descriptor vs description
-------------------------

A descriptor is the stable contract for identity and type. It should be small,
deterministic, and suitable for registry comparison.

A description is metadata about that contract. It helps humans, tools, and
consumers interpret the descriptor. A description may evolve more readily than
the descriptor, but it must not silently change identity.

Non-final sketch::

		StateDescriptor = identity + type + registry scope
		StateDescription = descriptor identity + metadata + constraints + hints

The sketch is not a message schema and must not be copied into a ``.msg`` file
without a later ABI review.

State vs command
----------------

State is observed truth reported by an owner or accepted source. It can be
sampled, snapshotted, projected, and checked for quality.

A command is a requested mutation. It may ask an owner to change state, trigger
an operation, or move toward a target. It is not proof that the requested state
exists.

Command outcomes must be represented separately from the command itself. A
future implementation may acknowledge, reject, or report the observed result of
a command, but the command message remains intent rather than truth.

Sample vs update
----------------

A sample is the semantic unit of observed value. It answers what value was
observed for a descriptor at a given time and with what quality.

An update is a synchronization event. It describes how observed changes are
transported or synchronized for a scope and may carry one sample, multiple
samples, partial mutations, invalidation markers, or another accepted update
form.

This distinction matters for future ABI review. A future message package must
not assume that ``StateSample`` and ``StateUpdate`` are interchangeable names
for the same transport contract.

Snapshot vs delta
-----------------

A snapshot is complete for its declared scope. A consumer can use it to rebuild
current state for that scope without relying on earlier deltas.

A delta is partial and depends on a known prior state. A consumer must know that
the delta belongs to the same registry scope, follows the expected ordering,
and applies to the expected base before applying it.

Snapshot and delta semantics must remain distinct because they have different
failure modes:

- snapshots are larger but recover from missed history;
- deltas are efficient but require continuity;
- missed deltas require resynchronization from a snapshot or another complete
	source.

Identity model
--------------

State identity must be deterministic inside a registry scope. A future identity
model should make it possible to compare descriptors, route updates, apply
deltas, and build projections without relying on transient process details.

Identity should include:

- registry scope;
- owner identity or source identity;
- descriptor key;
- type or schema identity;
- version or compatibility marker when needed.

When descriptors originate from structured registries or external
specifications, identity should preferably be derived from stable semantic
paths rather than generated UUIDs. Generated UUIDs are acceptable only when the
source identity is explicitly persistent and controlled.

Identity must not depend on object memory addresses, temporary Python object
names, process-local counters, or subscription order.

Quality model
-------------

Quality describes reliability of state, not the business meaning of the state.

A future ``StateQuality`` model may describe:

- valid or invalid value status;
- freshness or staleness;
- confidence;
- source availability;
- timestamp age;
- known degradation;
- unknown or unassessed quality.

Quality must not be used as a substitute for lifecycle state. An active
component may publish poor-quality state. An inactive component may have cached
state whose quality is stale or unknown. A valid value does not prove that its
owner is active.

Registry-scoped synchronization
-------------------------------

A registry scope bounds the meaning of descriptors, snapshots, deltas, and
projections. Synchronization must happen within a known scope so identity,
ordering, and recovery rules are unambiguous.

Registry-scoped synchronization should support:

- descriptor discovery;
- description metadata discovery;
- snapshot publication or retrieval;
- ordered delta application;
- resynchronization after missed deltas;
- projection construction from a known source registry.

Cross-registry projection may be useful later, but Sprint 17 does not define
cross-registry merge semantics.

Registry, store, and mirror terminology
---------------------------------------

A ``StateRegistry`` is primarily a scoped catalog of known contracts. It
defines which descriptors exist, how they are identified, and how descriptions
can be discovered inside a registry scope.

A registry must not be treated as a global mutable blackboard by default.
Future implementations may maintain local stores, caches, or mirrors of
observed values, but those responsibilities must remain explicit and must not
silently change the meaning of the registry itself.

Possible future terms:

``StateStore``
	Local storage for current known samples or values.

``StateMirror``
	Local synchronized view of a remote registry scope.

These names are not accepted implementation concepts during Sprint 17.3, but
the distinction prevents ``StateRegistry`` from becoming an overloaded runtime
object.

Lifecycle/state separation
--------------------------

Lifecycle state and observed state are separate concerns.

``lifecore_ros2`` lifecycle activation controls when managed entities process
or publish runtime behavior. ``lifecore_state`` state validity describes the
reliability of observed values. Neither implies the other.

Rules for future integration:

- lifecycle activation is not proof that a state value is valid;
- a valid state value is not proof that a lifecycle component is active;
- lifecycle transitions remain owned by ROS 2 lifecycle nodes and
	``lifecore_ros2`` components;
- state truth must not be hidden inside lifecycle transition callbacks;
- inactive lifecycle state must gate state updates and commands according to
	message type;
- no future package may add a parallel lifecycle state machine.

Inactive lifecycle behavior by message type
-------------------------------------------

Future ROS integration may subscribe to ``StateDescription`` messages while a
component is inactive because descriptions are metadata, not observed state
values. This supports discovery and UI/tool preparation without implying that
the owner is active or that current values are valid.

The intended inactive behavior is:

.. list-table::
	:header-rows: 1

	* - Message type
	  - Inactive behavior direction
	* - ``StateDescription``
	  - May be received and cached while inactive because it is metadata rather
		than observed truth.
	* - ``StateSnapshot``
	  - May be received for resynchronization preparation, but must not by itself
		imply active behavior or current valid live truth.
	* - ``StateSample``
	  - Must not update live state interpretation while inactive unless a later
		review explicitly accepts a narrower policy for cached observation.
	* - ``StateUpdate`` or ``StateDelta``
	  - Must not be applied while inactive because continuity assumptions cannot
		be trusted across inactive periods.
	* - ``StateCommand``
	  - Requires active lifecycle state and must be rejected, ignored, or not
		handled according to the accepted policy.

Additional rules:

- cached descriptions or snapshots must not imply active behavior;
- activation does not by itself validate cached values;
- reactivation after inactive time may require a fresh snapshot before deltas
	can be trusted.

This section describes future integration direction only. It does not change
existing ``lifecore_ros2`` publisher, subscriber, timer, service, watchdog, or
component behavior.

QoS direction
-------------

QoS choices should follow message semantics rather than use one default for
all state traffic.

Likely direction for later review:

- descriptors and descriptions favor discoverability and late-joiner behavior;
- snapshots favor reliable delivery within a bounded scope;
- deltas favor ordered delivery and explicit recovery when continuity is lost;
- commands favor explicit acknowledgement or rejection paths;
- high-rate samples may use different QoS than low-rate registry metadata.

This RFC does not finalize QoS profiles. A future implementation sprint should
treat QoS as part of message ABI and ROS integration review, not as an
incidental implementation detail.

Policies
--------

Policies are pure rules that affect interpretation or synchronization. They
should live in pure semantics when they do not require ROS 2, and in ROS
integration only when they depend on ROS transport behavior.

Candidate policy areas:

- stale value handling;
- missing descriptor handling;
- delta continuity recovery;
- snapshot refresh triggers;
- command acceptance and rejection;
- projection filtering;
- quality downgrade rules.

Policies must be explicit. Hidden defaults that change state truth, lifecycle
behavior, or command handling are out of scope for Sprint 17.3.

Anti-patterns
-------------

Future work must reject these patterns:

- adding a hidden state store inside ``lifecore_ros2``;
- making ``LifecycleComponentNode`` own a global state registry by default;
- treating commands as observed state;
- treating lifecycle activation as proof of state validity;
- treating valid state as proof of lifecycle activation;
- applying deltas after inactive periods without continuity checks;
- generating message schemas before semantics are accepted;
- making ``lifecore_state_core`` depend on ROS 2 or ``rclpy``;
- adding package metadata under ``lifecore_state/`` during Sprint 17.3;
- exporting speculative ``lifecore_state`` names from ``lifecore_ros2``.

Future implementation phases
----------------------------

The architecture should progress in small phases after Sprint 17 review:

1. Finalize terminology and message semantics.
2. Define message ABI candidates for ``lifecore_state_msgs``.
3. Prototype pure Python semantics in ``lifecore_state_core``.
4. Prototype ROS transport adaptation in ``lifecore_state_ros``.
5. Review optional integration points with ``lifecore_ros2``.
6. Add examples only after package boundaries and semantics are accepted.

Each phase should remain reviewable on its own. A later phase must not be used
to smuggle earlier unresolved decisions into implementation.

Next sprint entry criteria
--------------------------

The next implementation-oriented sprint may consider message ABI work only
after Sprint 17.3 confirms:

- this RFC is reviewed;
- terminology is stable enough for message naming;
- descriptor and description semantics are distinct;
- state and command semantics are distinct;
- snapshot and delta semantics are distinct;
- lifecycle/state separation is accepted;
- inactive behavior for descriptions, updates, and commands is accepted;
- package boundaries and dependency rules are accepted;
- anti-patterns are documented;
- no Sprint 17 implementation files were created.

Open questions
--------------

- What is the minimal descriptor identity that remains stable across launches?
- Which fields belong in ABI messages versus pure Python validation helpers?
- Does ``StateQuality`` need a fixed enum, extensible flags, or both?
- How should delta continuity be represented in ROS messages?
- Which command acknowledgement pattern best fits ROS-native behavior?
- Should projections be declared by descriptors, policy objects, or separate
	projection documents?
- What compatibility rules should govern future descriptor versioning?
- Does Sprint 18 need explicit terminology for ``StateStore`` or
	``StateMirror``, or is the registry distinction sufficient?

Decision summary
----------------

- Use ``lifecore_state`` as the architecture name.
- Keep ``lifecore_state/`` documentation-only during Sprint 17.3.
- Do not create packages, build metadata, runtime modules, or ROS interfaces in
	Sprint 17.3.
- Split future implementation responsibilities across
	``lifecore_state_msgs``, ``lifecore_state_core``, and
	``lifecore_state_ros`` if the architecture is accepted.
- Keep ``lifecore_ros2`` independent from future ``lifecore_state`` packages by
	default.
- Preserve native ROS 2 lifecycle semantics and avoid parallel state machines.
- Treat ``StateRegistry`` as a scoped contract catalog, not a default global
	mutable store.
- Prefer stable semantic paths over generated UUIDs when deriving descriptor
	identity.
- Keep lifecycle activation separate from state validity.
- Allow ``StateDescription`` metadata caching while inactive.
- Reject live ``StateSample`` interpretation changes while inactive by default.
- Reject ``StateUpdate`` delta application while inactive.
- Require active lifecycle state for ``StateCommand`` handling.
- Treat future message ABI work as conditional on Sprint 17.3 review.

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.3.
