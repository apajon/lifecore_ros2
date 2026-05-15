Sprint 17 - lifecore_state Architecture and RFC
===============================================

**Status.** Active.

**Track.** Architecture / RFC / no implementation.

**Branch.** ``sprint/17-lifecore-state-rfc``.

**Priority.** P2 - separate future architecture.

**Type.** Documentation and architecture only.

Feature goal
------------

Plan and review the future ``lifecore_state`` architecture before any runtime,
message, or package implementation begins. Sprint 17 must remove ambiguity
around naming, package boundaries, message semantics, lifecycle/state
separation, and anti-patterns while keeping ``lifecore_ros2`` behaviorally
unchanged.

Lifecycle behavior contract
---------------------------

Sprint 17 is documentation-only. It must not change lifecycle behavior for any
existing node, component, publisher, subscriber, timer, service, or watchdog.

- **configure:** no runtime resource creation changes.
- **activate:** no activation gate changes.
- **deactivate:** no deactivation gate changes.
- **cleanup:** no resource cleanup changes.
- **shutdown:** no shutdown path changes.
- **error:** no error transition or recovery behavior changes.

The Sprint 17 architectural documents must clarify future lifecycle/state
semantics without implementing them. In particular, they must explain that
``StateDescription`` may be cached while inactive, ``StateUpdate`` deltas are
not applied while inactive, and ``StateCommand`` handling requires an active
component.

Context
-------

``lifecore_ros2`` is currently an explicit lifecycle-native framework for ROS 2
Jazzy components. It deliberately avoids hidden state machines, orchestration
runtimes, plugin frameworks, ECS runtimes, giant managers, and code generation.

``lifecore_state`` is a future architecture direction, not a feature to
implement during this sprint. The future model should be treated as a
distributed typed state space or semantic synchronized state model, not as a
generic industrial I/O bus hidden inside ``lifecore_ros2``.

Goals
-----

- Make architecture boundaries between ``lifecore_ros2`` and
  ``lifecore_state`` explicit.
- Stabilize terminology for descriptors, descriptions, samples, updates,
  commands, quality, snapshots, deltas, registries, and projections.
- Define the future package separation between ``lifecore_state_msgs``,
  ``lifecore_state_core``, and ``lifecore_state_ros``.
- Document message semantics and QoS direction before defining ROS messages.
- Clarify lifecycle/state separation and semantic gating by message type.
- Reject architectural anti-patterns before they leak into implementation.
- Define Sprint 18 entry criteria for a possible message ABI prototype.

Non-goals
---------

- No implementation.
- No ROS 2 package creation.
- No Python runtime package creation.
- No compiled ``.msg`` files.
- No EventBus.
- No ECS runtime.
- No code generation.
- No orchestration framework.
- No giant manager.
- No hidden state store inside ``lifecore_ros2``.
- No public API changes in ``lifecore_ros2``.

Impacted modules
----------------

``docs/planning/sprints/active/``
  Holds this active Sprint 17 coordinator and the active Sprint 17.3 planning
  card.

``docs/planning/sprints/sprint_17_substeps/``
  Keeps the remaining execution cards for Sprint 17 sub-sprints that are not
  yet active.

``docs/planning/sprints/sprint_17_repository_audit.rst``
  Expected output of Sprint 17.1 after audit execution.

``lifecore_state/``
  Future documentation-only logical folder for Sprint 17 architecture documents.
  It must not be a ROS 2 package and must not contain ``package.xml`` at the
  parent level.

``src/``, ``tests/``, and ``examples/``
  Not impacted. Sprint 17 must not change code, runtime behavior, tests, or
  examples unless a later explicit planning decision changes scope.

Active sub-sprint
-----------------

- Sprint 17.3 - Write Principal Architecture RFC
  Location: :doc:`sprint_17_3_rfc`

Deliverables
------------

- **17.1 - Repository audit.** Validated and archived. Audit the repository
  structure, identify risks, and recommend safe placement for
  ``lifecore_state`` documentation.
- **17.2 - Documentation structure.** Archived after validation. Created the
  documentation-only ``lifecore_state/`` skeleton files after placement was
  confirmed.
- **17.3 - RFC 001.** Active. Write the principal architecture RFC.
- **17.4 - Terminology glossary.** Define accessible French terminology.
- **17.5 - Lifecycle/state separation.** Clarify semantic gating and inactive
  behavior.
- **17.6 - Package boundaries.** Define future package responsibilities and
  dependency rules.
- **17.7 - Message semantics.** Document descriptor, description, sample,
  update, and command semantics.
- **17.8 - Anti-goals.** Reject unsafe architectural directions.
- **17.9 - Main sprint coordination.** Maintain this file as the coordination
  hub.
- **17.10 - Consistency review.** Check terminology, architecture, lifecycle,
  and message alignment.
- **17.11 - Final checklist.** Provide reviewer sign-off checklist.
- **17.12 - Static verification.** Verify file presence, forbidden files, key
  phrases, and documentation integrity.
- **17.13 - PR description draft.** Prepare a ready-to-use PR summary.

Explicit decisions to capture
-----------------------------

- ``lifecore_state`` is the preferred public name; ``lifecore_io`` is too
  narrow.
- ``lifecore_state/`` is a logical documentation group during Sprint 17, not a
  package.
- Future packages are ``lifecore_state_msgs``, ``lifecore_state_core``, and
  ``lifecore_state_ros``.
- ``lifecore_ros2`` must remain independent from ``lifecore_state``.
- ``lifecore_state_core`` must remain pure Python and independent from ROS 2.
- ``StateDescription`` can be cached while inactive.
- ``StateUpdate`` deltas are not applied while inactive.
- ``StateCommand`` handling requires active lifecycle state.
- A command is a requested mutation, not observed truth.
- Quality describes reliability of a value, not business state.
- Snapshot and delta semantics must remain distinct.
- Descriptor and description semantics must remain distinct.

Acceptance criteria
-------------------

- [x] Sprint 17.1 is archived after validation.
- [x] Sprint 17.2 is archived after validation.
- [x] Sprint 17.3 is active and linked from the planning index.
- [x] Repository audit document exists and is validated.
- [x] ``lifecore_state/`` exists as a documentation-only logical group.
- [x] No ``package.xml`` exists in the ``lifecore_state/`` parent folder.
- [x] No runtime code is added.
- [x] ``lifecore_ros2`` remains behaviorally unchanged.
- [ ] Package dependency rules are documented.
- [ ] Lifecycle/state separation is documented.
- [ ] ``StateDescription`` inactive caching is documented.
- [ ] ``StateUpdate`` inactive delta rejection is documented.
- [ ] ``StateCommand`` active-only handling is documented.
- [ ] Sprint 18 entry criteria are documented.
- [ ] All sub-sprint deliverables exist.
- [ ] Mandatory review phrase appears in required review deliverables.

Validation plan
---------------

Use documentation-scoped validation while Sprint 17 remains documentation-only:

- inspect changed RST files for coherent headings, links, and checklist syntax;
- run Sphinx documentation build after linking new documentation into the docs
  tree;
- verify no forbidden files were added under ``lifecore_state/``;
- verify ``src/``, ``tests/``, and ``examples/`` remain unchanged.

Run full Python validation only if later work touches Python code or project
configuration:

- ``uv run ruff check .``
- ``uv run pyright``
- ``uv run pytest``

Sprint 18 candidate scope
-------------------------

Sprint 18 may consider a message ABI prototype only after Sprint 17 review is
complete. Pure Python core sketches, ROS integration, tools, lifecycle
integration, and generated workflows remain later phases unless explicitly
approved by a follow-up plan.

Review checklist
----------------

- [x] Repository audit exists and is accurate.
- [ ] RFC is complete and reviewable.
- [ ] Glossary is accessible.
- [ ] Package boundaries are clear.
- [ ] Message semantics are consistent.
- [ ] Lifecycle/state separation is sound.
- [ ] Anti-patterns are rejected.
- [ ] No implementation is present.
- [ ] ``lifecore_ros2`` independence is maintained.
- [ ] Mandatory review phrases are present where required.
- [ ] Sprint 18 entry criteria are explicit.

Clarifications needed
---------------------

None for planning. Any architectural uncertainty discovered during Sprint 17.1
must be recorded in the repository audit instead of being resolved silently.

Review requirement
------------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."
