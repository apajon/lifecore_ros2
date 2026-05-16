Anti-goals
==========

Purpose
-------

This document records what ``lifecore_state`` must not become. Its purpose is
to give reviewers a direct reference when a proposal expands the architecture
beyond typed, explicit, reviewable state semantics.

Use this document as a rejection aid during design review. A future proposal
that needs one of these rejected directions must either be redesigned smaller or
explicitly reopen the architecture decision before implementation begins.

Current scope
-------------

This document is architecture-only. It does not create enforcement code,
runtime checks, package hooks, public APIs, ROS interfaces, or Python runtime
modules.

Sprint 17.8 does not change lifecycle behavior for any existing
``lifecore_ros2`` node or component:

- **configure:** no runtime resource creation changes;
- **activate:** no activation gate changes;
- **deactivate:** no deactivation behavior changes;
- **cleanup:** no cleanup behavior changes;
- **shutdown:** no shutdown behavior changes;
- **error:** no error recovery changes.

Why anti-goals matter
---------------------

``State`` is a broad word. Without explicit limits, it can invite a global
runtime, a hidden blackboard, a workflow engine, an EventBus, an ECS platform,
or a code generation system. Those directions would blur the small set of
concerns Sprint 17 is trying to make reviewable: descriptors, descriptions,
samples, updates, commands, quality, snapshots, deltas, registries, and
projections.

Anti-goals anchor the architecture against worse alternatives. They make it
acceptable for reviewers to say no to proposals that are powerful but too broad,
too hidden, or too coupled to lifecycle behavior.

The shared principle is simple: no magic. State synchronization must remain
visible in topics, message semantics, explicit policies, version checks,
sequence checks, and small components with clear responsibilities.

Not a robotics operating system
-------------------------------

``lifecore_state`` must not become a robotics operating system. It must not own
global mission planning, global task execution, fleet coordination, launch
policy, deployment policy, hardware abstraction, or replacement middleware.

ROS 2 remains the middleware and lifecycle foundation. ``lifecore_state`` may
describe typed state and synchronization semantics, but it must not replace ROS
2 nodes, topics, services, actions, parameters, lifecycle nodes, launch files,
or system composition tools.

This rejection matters because state visibility is not system authority. Knowing
what a robot reports does not mean the state layer should plan missions, route
commands globally, or decide how every node in a system is started and stopped.

Not a global orchestration runtime
----------------------------------

``lifecore_state`` must not become a workflow engine, planning engine, behavior
tree system, global decision engine, or multi-node orchestration runtime.

Future integration must stay local, explicit, and scoped to the node or adapter
that owns it. It must not add automatic configure, activate, deactivate,
cleanup, shutdown, restart, recovery, or compensation behavior across nodes.

This protects the existing ``lifecore_ros2`` contract: lifecycle transitions are
visible, local readiness remains owned by lifecycle nodes and managed entities,
and diagnostics or observed state do not secretly drive lifecycle transitions.

Not a hidden synchronization framework
--------------------------------------

Synchronization must be explicit. A reviewer must be able to see:

- which ROS topics carry descriptions, updates, snapshots, deltas, commands, or
	diagnostics;
- which registry scope a descriptor, update, snapshot, or projection belongs
	to;
- which policy applies while inactive, stale, mismatched, or out of sequence;
- which ``description_version`` is required before interpreting an update;
- which ``sequence`` values prove continuity or expose loss, duplicates, and
	order violations.

Hidden synchronization is rejected because it makes state truth difficult to
debug. A future consumer must not depend on process-local subscription order,
implicit registries, object identity, silent best-effort merge behavior, or
magic background replication to know whether a delta is safe to apply.

Not a giant ECS platform
------------------------

ECS ideas may inspire some naming or separation patterns, especially the value
of small data contracts and explicit systems. ``lifecore_state`` must not become
a general ECS runtime.

Rejected directions include entity-wide queries, central system scheduling,
global entity storage, automatic system execution order, entity lifecycle rules,
and framework overhead that forces users to model ordinary ROS 2 nodes as ECS
worlds.

This rejection prevents terminology confusion. A ``LifecycleComponent`` is a
managed behavior unit in ``lifecore_ros2``; it must not be collapsed into the ECS
meaning of component as passive data attached to an entity.

Not an EventBus
---------------

Events may be useful later for diagnostics, observability, command feedback, or
tooling. ``lifecore_state`` must not become an EventBus where every mutation
automatically emits events to implicit listeners.

Rejected directions include publish-on-set, magic observable properties,
implicit listeners for state mutations, wildcard subscriptions to process-local
changes, and side effects triggered by field assignment.

This matters because ``StateUpdate`` is observed truth transported with explicit
identity, version, ordering, and quality. An implicit event fired from a local
setter does not provide those guarantees by itself.

Not a plugin framework
----------------------

``lifecore_state`` must not become a plugin framework. It must not load dynamic
behavior through shared library plugins, Python entry point plugins, registry
plugins, or convention-over-configuration discovery.

Future extension points, if any, must remain explicit and reviewed. A state
adapter should be visible in code and tests, not discovered because a name or
folder happens to match a convention.

This rejection keeps review focused. Dynamic behavior loading makes ownership,
dependency direction, security posture, and lifecycle effects harder to inspect.

Not a factory or spec system
----------------------------

``lifecore_state`` must not become the central factory that creates the
application. It must not introduce global specs that instantiate nodes,
components, registries, publishers, subscribers, commands, or lifecycle wiring
as the primary construction path.

Declarative specifications may be useful later for documentation, validation,
or generated artifacts, but imperative explicit code remains the primary way to
construct behavior during the architecture path described by Sprint 17.

This rejection protects local readability. Reviewers should be able to follow
which object owns which resource, which topic is used, and which lifecycle hook
creates or releases that resource.

Not codegen-first
-----------------

Code generation may become useful after concepts, terminology, message
semantics, and review expectations stabilize. It is rejected as a first design
move.

Sprint 17 must not generate ROS interfaces, Python modules, registries,
components, adapters, or documentation from a hidden schema. Sprint 18 may
consider message ABI prototypes only after Sprint 17 review is complete.

This rejection keeps the human review cycle ahead of automation. Generators
amplify design mistakes when names, semantics, and package boundaries are still
under discussion.

No giant StateManager class
---------------------------

A single ``StateManager`` class must not combine registry management,
publishers, subscribers, lifecycle integration, callback dispatch, stale
monitoring, command handling, validation, logging, diagnostics, and
orchestration.

That shape is rejected even if it looks convenient at first. It would turn a
state architecture into a broad runtime object with unclear ownership and too
many reasons to change.

Future implementation work must prefer separate classes with clear, single
responsibilities. For example, registry catalog semantics, ROS transport
adapters, command validation, stale monitoring, and lifecycle-aware integration
belong behind explicit boundaries rather than in one object that owns the whole
system.

No magical StateField
---------------------

``StateField`` must not become a magical descriptor object that hides
publication, subscription, lifecycle state, registry knowledge, descriptor
metadata, or global state access inside property access.

Rejected behavior includes:

- automatic publish-on-set;
- complex callbacks hidden in field accessors;
- lifecycle awareness in pure core field objects;
- registry awareness in pure core field objects;
- descriptor discovery hidden behind attribute access;
- global registry lookup from a field instance.

A field abstraction may be useful later if it stays small and explicit, but it
must not become a hidden runtime surface.

No automatic publish-on-set in core
-----------------------------------

The pure core must not publish because a value was assigned. Publication is a
transport concern and belongs outside ``lifecore_state_core``.

Future pure semantics may use explicit patterns such as ``set()``, mark-dirty,
and flush-delta, but those names are review vocabulary, not a Sprint 17 API
commitment. The key rule is that mutation and publication remain separate:
changing a local value does not silently create ROS traffic.

This separation keeps state interpretation testable without ROS 2 and prevents
ordinary Python assignment from becoming a hidden side-effect boundary.

No auto-register unknown fields by default
------------------------------------------

Unknown fields must not be auto-registered by default. A descriptor registry is
a contract, not a typo-tolerant dictionary.

Automatic registration is rejected because it:

- breaks API and ABI expectations;
- turns spelling mistakes into accepted state fields;
- defeats static schemas and description versions;
- creates implicit coupling between producers and consumers;
- makes debugging harder because the system appears to accept fields nobody
	reviewed.

Future tools may provide explicit migration, diagnostics, or authoring aids for
new fields, but runtime synchronization must not silently expand the contract.

No command-as-truth
-------------------

``StateCommand`` is intent, not reality. It asks an owner or receiver to mutate
state or perform an operation; it does not prove the requested state exists.

``StateUpdate`` carries observed truth. Commands require feedback, rejection, or
later observation. An accepted command must become visible in later state, and
the observed result must remain distinct from the original request.

This rejection prevents command messages from becoming durable state facts. A
late joiner must not see an old command and treat it as current truth, and a
consumer must not assume command acceptance equals command success.

No lifecycle contamination in core
----------------------------------

``lifecore_state_core`` must remain pure Python if it is created in a later
sprint. It must not import ``rclpy``, ROS 2 messages, lifecycle node classes,
``lifecore_ros2`` lifecycle components, or lifecycle transition helpers.

The core may define state semantics such as descriptors, descriptions, samples,
updates, snapshots, deltas, commands, quality, projection, identity, and
validation policies. It must not know whether a ROS 2 component is configured,
active, inactive, cleaning up, shutting down, or in error.

Lifecycle-aware behavior belongs in explicit ROS integration or optional
``lifecore_ros2`` adapters. This keeps pure semantics testable without ROS and
prevents a parallel lifecycle state machine from appearing in the core.

Safe future directions
----------------------

The following directions are not anti-goals, but they are deferred until the
architecture is stable enough to review them safely:

- diagnostics events for observability, as long as they do not become an
	implicit EventBus for state mutation;
- CLI and visualization tools for inspecting descriptions, registries,
	snapshots, deltas, versions, and sequence health;
- code generation after terminology, message semantics, package boundaries, and
	review expectations stabilize;
- compact message optimization after the readable ABI shape is understood;
- command-line inspection of registry scopes and transport health;
- optional ``lifecore_ros2`` integration that stays thin, explicit, additive,
	and non-invasive.

These directions stay safe only while they preserve explicit contracts and do
not move orchestration, lifecycle transitions, or hidden synchronization into
the state layer.

Decision summary
----------------

Sprint 17.8 rejects the following architectural directions:

- a robotics operating system;
- a global orchestration runtime;
- hidden synchronization;
- a giant ECS platform;
- an EventBus;
- a plugin framework;
- a factory or spec system as the primary construction path;
- codegen-first design;
- a giant ``StateManager``;
- magical ``StateField`` behavior;
- automatic publish-on-set in core;
- auto-registering unknown fields by default;
- command-as-truth semantics;
- lifecycle or ROS 2 contamination in ``lifecore_state_core``.

These rejections share one architectural principle: ``lifecore_state`` should
make typed distributed state explicit and reviewable without becoming a hidden
runtime, a lifecycle controller, or a global framework inside
``lifecore_ros2``.

Review note
-----------

Reviewers may cite this document to reject architectural overreach, require
simpler alternatives, enforce separation of concerns, and prevent hidden
complexity before implementation starts.

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
