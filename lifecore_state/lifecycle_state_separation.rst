Lifecycle and State Separation
==============================

Purpose
-------

This document explains why future ``lifecore_state`` semantics must stay
separate from ``lifecore_ros2`` lifecycle orchestration. The goal is to make
future state caching, update application, and command handling reviewable
without inventing a hidden runtime, a parallel lifecycle, or a new orchestration
layer.

Current scope
-------------

This document is architecture-only. It does not change configure, activate,
deactivate, cleanup, shutdown, or error behavior in current ``lifecore_ros2``
nodes or components. It describes future boundary rules that later sprints may
turn into pure semantics, message contracts, or explicit ROS integration.

Definitions
-----------

``Lifecycle state``
	Lifecycle state describes local readiness of a node or component to own
	resources and run behavior. It answers questions such as whether a subscriber
	exists, whether a timer is active, or whether command handling is currently
	allowed.

``Runtime state``
	Runtime state describes known values, metadata, and synchronization context
	for a state scope. It answers questions such as what value is known, how old
	it is, what quality it has, and whether a consumer has enough continuity to
	apply a delta.

``StateDescription``
	A description is metadata about descriptors and schema-like structure. It is
	not observed truth. A future component may need the latest description before
	activation to interpret later updates safely.

``StateUpdate``
	An update is a synchronization event for a known scope. It carries observed
	changes, not lifecycle commands. Its meaning depends on continuity, ordering,
	and whether it is a delta or a snapshot-like payload.

``StateCommand``
	A command is requested intent. It is allowed or rejected by policy and active
	lifecycle readiness, but it is not evidence that the requested state already
	exists.

What lifecycle controls
-----------------------

Lifecycle remains responsible for local resource and behavior readiness.
Future state work must not move these responsibilities into a hidden state
store, registry runtime, or orchestration layer.

Lifecycle controls at least the following concerns:

- whether publishers, subscribers, timers, and service clients or servers exist;
- whether callback-driven runtime behavior is active or inactive;
- whether command handling is currently allowed;
- whether runtime updates may be applied to active behavior;
- when local resources are cleaned up;
- when lifecycle error handling and recovery paths run.

Lifecycle does not decide by itself whether a state value is semantically valid,
fresh enough, complete enough, or authoritative enough to trust.

What lifecore_state controls
----------------------------

Future ``lifecore_state`` work is responsible for state truth and synchronization
semantics, not lifecycle ownership.

State concerns include at least:

- which fields and descriptors are known in a registry scope;
- which description version applies to those descriptors;
- what the latest samples or updates say;
- what quality, freshness, or staleness those values have;
- whether a consumer is looking at a full snapshot or only a delta;
- which owner or authority is responsible for a descriptor;
- which projection or filtered view a consumer is using;
- whether identity and ordering information are sufficient to apply a change.

These concerns may be cached, compared, projected, or invalidated without
becoming lifecycle transitions.

Important separation rules
--------------------------

The following non-equivalences are the core of the boundary:

- active lifecycle state is not proof that a state value is valid;
- valid or recent state is not proof that a lifecycle component is active;
- ``cleanup`` is not proof that remote truth was cleared;
- ``deactivate`` is not proof that registry knowledge or descriptions vanished;
- receiving metadata while inactive is not the same as running active behavior;
- command acceptance policy is not the same thing as command success;
- no future package may introduce a parallel lifecycle state machine;
- optional integration with ``lifecore_ros2`` must remain explicit and
	reviewable.

Practical examples:

- A component may be active while still waiting for a fresh snapshot after a
	transport interruption.
- A component may be inactive while already holding the latest
	``StateDescription`` needed to prepare activation.
- A cleanup step may free a local subscriber without implying that another node
	forgot the last published battery description.

Callback categories
-------------------

Not every callback has the same meaning. A single global "ignore everything
while inactive" rule is too blunt because callback categories serve different
purposes.

``Configuration callbacks``
	These callbacks prepare local resources or accept metadata needed to interpret
	future runtime behavior. A future ``StateDescription`` callback fits here when
	it only caches schema-like information and does not trigger active behavior.

``Runtime callbacks``
	These callbacks update live interpreted state, apply deltas, refresh active
	projections, or trigger behavior based on new observations. These callbacks
	generally require active lifecycle state.

``Command callbacks``
	These callbacks accept, reject, or log requested mutations. They require an
	explicit policy and normally require active lifecycle state because they imply
	readiness to act.

``Diagnostics callbacks``
	These callbacks record observability information, liveness signals, or stale
	conditions. They may remain more permissive than runtime callbacks, but they
	must not silently become a backdoor for active state mutation.

StateDescription lifecycle behavior
-----------------------------------

``StateDescription`` is special because it behaves more like metadata than live
observed truth.

The architectural direction for Sprint 17 is:

- a future subscriber may be created during ``configure``;
- a ``transient_local`` description message may arrive immediately after that
	subscriber exists;
- caching or replacing the latest description while inactive is allowed;
- this cached description must not by itself trigger active runtime behavior;
- activation may depend on having a valid cached description available.

This rule exists because description metadata can be needed to interpret later
updates correctly. Dropping every description received while inactive would make
future activation more fragile and would waste ROS 2 ``transient_local``
delivery.

StateUpdate lifecycle behavior
------------------------------

``StateUpdate`` is not treated the same way as ``StateDescription`` because it
represents observed change rather than interpretation metadata.

The architectural direction for Sprint 17 is:

- deltas are not applied while inactive;
- a full snapshot may optionally be cached while inactive if a later reviewed
	policy accepts that narrower behavior;
- receiving a snapshot while inactive must not imply active behavior or current
	validated live truth;
- updates are applied to active interpreted state only while active;
- after time spent inactive, a future implementation may require a fresh
	snapshot before trusting later deltas again.

This distinction protects continuity assumptions. A delta only makes sense when
the consumer knows which prior state it extends. An inactive period breaks that
confidence unless a reviewed policy restores it explicitly.

StateCommand lifecycle behavior
-------------------------------

``StateCommand`` handling requires active lifecycle readiness.

The architectural direction for Sprint 17 is:

- commands require active lifecycle state to be handled;
- inactive commands are rejected or ignored according to the accepted policy;
- command rejection while inactive is a lifecycle readiness decision, not proof
	that the command was semantically wrong;
- command acceptance is not proof that the requested state has been reached.

This rule keeps command intent separate from observed truth and avoids implying
that a future state layer owns hidden recovery or orchestration behavior.

InactiveMessagePolicy
---------------------

The policy names below are architectural vocabulary for review, not a public API
commitment in Sprint 17.

``IGNORE``
	Discard the message while inactive.

``CACHE_LATEST``
	Keep the most recent message while inactive, replacing older cached data.

``BUFFER_UNTIL_ACTIVE``
	Queue messages while inactive and defer handling until activation. This is the
	riskiest policy because it can silently accumulate assumptions about ordering,
	memory use, and delayed side effects.

``REJECT``
	Refuse handling explicitly because inactive state is not allowed for that
	message category.

Recommended direction by message type:

.. list-table::
	 :header-rows: 1

	 * - Message type
		 - Preferred inactive policy
		 - Reason
	 * - ``StateDescription``
		 - ``CACHE_LATEST``
		 - Metadata may be needed before activation and does not by itself imply
			 active behavior.
	 * - ``StateUpdate`` delta
		 - ``IGNORE``
		 - Delta continuity cannot be trusted across inactive periods.
	 * - ``StateUpdate`` snapshot-like payload
		 - ``CACHE_LATEST`` optionally
		 - A complete refresh may help later resynchronization, but must remain
			 non-active and explicitly reviewed.
	 * - ``StateCommand``
		 - ``REJECT`` or ``IGNORE``
		 - Inactive state is not ready to act on requested mutation.

``BUFFER_UNTIL_ACTIVE`` is intentionally not recommended by default for Sprint
17 because it hides too much runtime policy and invites queue semantics that
have not been reviewed.

Recommended pseudo-code
-----------------------

The following sketches are non-executable examples. They illustrate semantic
gating only and must not be copied as final implementation code.

.. code-block:: python

		# Non-final pseudo-code for architecture discussion only.
		def on_description_msg(self, msg):
				# Description metadata may be cached while inactive.
				self._cached_description = msg.description
				if self.is_active:
						self._refresh_description_view(msg.description)

		def on_state_update_msg(self, msg):
				# Deltas require active continuity assumptions.
				if msg.kind == "delta" and not self.is_active:
						return

				# Snapshot-like payloads may be cached if a reviewed policy allows it.
				if msg.kind == "snapshot" and not self.is_active:
						self._cached_snapshot = msg
						return

				if self.is_active:
						self._apply_update(msg)

		def on_command_msg(self, msg):
				if not self.is_active:
						self._reject_inactive_command(msg)
						return

				self._handle_command(msg)

Design decision summary
-----------------------

Sprint 17.5 documents the following boundary:

- ``lifecore_ros2`` owns lifecycle transitions and local readiness;
- future ``lifecore_state`` work owns state truth and synchronization semantics;
- ``StateDescription`` may be cached while inactive;
- ``StateUpdate`` deltas are not applied while inactive;
- snapshot-like refresh while inactive is narrower and optional, not assumed by
	default everywhere;
- ``StateCommand`` handling requires active lifecycle state;
- active state and valid state remain distinct concepts;
- no hidden orchestration runtime, giant manager, or parallel lifecycle is
	introduced by this document.

Review note
-----------

This document clarifies architectural direction only. It does not create a
runtime API, a message ABI, or a new lifecycle policy surface in current code.

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
