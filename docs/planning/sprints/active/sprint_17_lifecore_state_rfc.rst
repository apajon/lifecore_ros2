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

``lifecore_ros2`` remains independent from future ``lifecore_state`` work during
Sprint 17. The current lifecycle framework keeps its existing public API,
package dependencies, lifecycle transition behavior, and examples unchanged
while architecture decisions are documented separately.

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
  Holds this active Sprint 17 coordinator.

``docs/planning/sprints/archived/``
  Holds validated Sprint 17.1 through Sprint 17.9 planning cards after review.

``docs/planning/sprints/sprint_17_substeps/``
  Keeps the remaining execution cards for Sprint 17.12 through Sprint 17.13.

``docs/planning/sprints/sprint_17_repository_audit.rst``
  Expected output of Sprint 17.1 after audit execution.

``lifecore_state/``
  Future documentation-only logical folder for Sprint 17 architecture documents.
  It must not be a ROS 2 package and must not contain ``package.xml`` at the
  parent level.

``src/``, ``tests/``, and ``examples/`` remain out of scope. Sprint 17 must not
change code, runtime behavior, tests, or examples unless a later explicit
planning decision changes scope.

Active sub-sprint
-----------------

- Sprint 17.12 - Static Verification
  Status: Active. Location: :doc:`sprint_17_12_static_check`

Deliverables
------------

- **17.1 - Repository audit.** Status: Archived. Audit the repository
  structure, identify risks, and recommend safe placement for
  ``lifecore_state`` documentation.
- **17.2 - Documentation structure.** Status: Archived. Created the
  documentation-only ``lifecore_state/`` skeleton files after placement was
  confirmed.
- **17.3 - RFC 001.** Status: Archived. Principal architecture RFC written.
- **17.4 - Terminology glossary.** Status: Archived. Accessible French
  terminology is now documented in ``lifecore_state/terminology.rst``.
- **17.5 - Lifecycle/state separation.** Status: Archived. Semantic
  gating and inactive behavior are now documented in
  ``lifecore_state/lifecycle_state_separation.rst``.
- **17.6 - Package boundaries.** Status: Archived. Future package
  responsibilities and dependency rules are now documented in
  ``lifecore_state/package_boundaries.rst``.
- **17.7 - Message semantics.** Status: Archived. Message semantics
  are now documented in ``lifecore_state/message_semantics.rst``.
- **17.8 - Anti-goals.** Status: Archived. Unsafe architectural
  directions are explicitly rejected in ``lifecore_state/anti_goals.rst``.
- **17.9 - Main sprint coordination.** Status: Archived. Kept this file
  synchronized with sub-sprint status and made it the Sprint 17 coordination hub.
- **17.10 - Consistency review.** Status: Archived. Check terminology,
  architecture, lifecycle, and message alignment.
- **17.11 - Final checklist.** Status: Archived. Created the reviewer
  sign-off checklist.
- **17.12 - Static verification.** Status: Active. Verify file presence,
  forbidden files, key phrases, and documentation integrity.
- **17.13 - PR description draft.** Status: Pending. Prepare a ready-to-use PR
  summary.

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
- ``StateUpdate`` snapshot-like inactive refresh is narrower and optional, not
  assumed as a global rule.
- ``StateCommand`` handling requires active lifecycle state.
- A command is a requested mutation, not observed truth.
- Quality describes reliability of a value, not business state.
- Snapshot and delta semantics must remain distinct.
- Descriptor and description semantics must remain distinct.

Acceptance criteria
-------------------

- [x] Sprint 17.1 is archived after validation.
- [x] Sprint 17.2 is archived after validation.
- [x] Sprint 17.3 is archived after review.
- [x] Sprint 17.4 glossary exists and is accessible.
- [x] Sprint 17.5 lifecycle/state separation exists and is reviewable.
- [x] Sprint 17.6 package boundaries exist and are reviewable.
- [x] Sprint 17.7 is archived after validation.
- [x] Sprint 17.8 is archived after validation.
- [x] Sprint 17.9 is archived after validation.
- [x] Sprint 17.10 is archived after validation.
- [x] Sprint 17.11 is archived after validation.
- [x] Sprint 17.12 is active and linked from the planning index.
- [x] Sprint 17.13 remains listed as pending work.
- [x] Repository audit document exists and is validated.
- [x] ``lifecore_state/`` exists as a documentation-only logical group.
- [x] No ``package.xml`` exists in the ``lifecore_state/`` parent folder.
- [x] No runtime code is added.
- [x] ``lifecore_ros2`` remains behaviorally unchanged.
- [x] Package dependency rules are documented.
- [x] Lifecycle/state separation is documented.
- [x] ``StateDescription`` inactive caching is documented.
- [x] ``StateUpdate`` inactive delta rejection is documented.
- [x] ``StateCommand`` active-only handling is documented.
- [x] Sprint 18 entry criteria are documented.
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
- [x] RFC is complete and reviewable.
- [x] Glossary is accessible.
- [x] Package boundaries are clear.
- [x] Message semantics are consistent.
- [x] Lifecycle/state separation is sound.
- [x] Anti-patterns are rejected.
- [x] No implementation is present.
- [x] ``lifecore_ros2`` independence is maintained.
- [x] Future ``lifecore_state`` packages are not treated as existing runtime
  packages.
- [x] Mandatory review phrases are present where required.
- [x] Sprint 18 entry criteria are explicit.

Clarifications needed
---------------------

None for planning. Any architectural uncertainty discovered during Sprint 17.1
must be recorded in the repository audit instead of being resolved silently.

Review requirement
------------------

Mandatory phrase:

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
