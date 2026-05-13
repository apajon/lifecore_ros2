Planning backlog
================

Sprint 14 is complete. The project is past the old Sprint 8 / 0.4.0 planning
state; the core is mature enough to shift focus toward adoption, documentation,
testing, diagnostics, and future architecture without automatically adding new
core abstractions.

What remains is split into strategic near-term work, future feature candidates,
and deliberately deferred ideas.

See `ROADMAP.md <https://github.com/apajon/lifecore_ros2/blob/main/ROADMAP.md>`_ for the public-facing scope and `CHANGELOG.md <https://github.com/apajon/lifecore_ros2/blob/main/CHANGELOG.md>`_ for shipped changes.

See :doc:`strategy` for the product cap that explains why the backlog is ordered this way.

---

Backlog governance
------------------

A sprint may target core, companion, docs, architecture, tooling, DX, external
modules, or research. Priority is based on risk reduction, adoption leverage,
architectural clarification, and strategic sequencing, not package location.

Sprint tracks
^^^^^^^^^^^^^

Track A — Core lifecore_ros2
  Maintain, harden, document, correct, and improve ergonomics without expanding
  scope abruptly. The core must stay small, testable, explicit, stable, and
  ROS-native.

Track B — Companion / Adoption
  Comparative examples, tutorials, concrete demonstrations, onboarding, and
  user-facing documentation. A good adoption example can be more valuable than
  a new internal feature.

Track C — State Architecture
  Prepare future ``lifecore_state`` concepts such as ``StateField``,
  ``StateRegistry``, ``StateDescriptor``, ``StateSnapshot``, ``StateDelta``,
  ``StateProjection``, and ``StateMirror`` separately from the lifecycle core.

Track D — DX / Testing / Diagnostics
  Test fixtures, fake components, activation helpers, ergonomic diagnostics,
  and lightweight developer tooling that improve reliability without adding a
  heavy concept layer.

Track E — Tooling / Codegen
  Scripts, templates, generation, scaffolding, and CLI commands. Defer until
  conventions are stable; codegen follows architecture, it does not discover it.

Track F — Research / RFC
  Decision documents, disposable prototypes, explorations, architecture
  framing, and risk analysis. An RFC sprint is valid when it avoids coding the
  wrong abstraction.

Priority model
^^^^^^^^^^^^^^

P0 — Project coherence and roadmap debt
  Synchronize roadmap, backlog, docs, and planning truth.

P1 — Usage proof and adoption
  Make the value of ``lifecore_ros2`` obvious through examples and onboarding.

P2 — Separate future architecture
  Clarify ``lifecore_state`` and related package boundaries before runtime work.

P3 — API hardening, tests, and diagnostics
  Improve reliability, debuggability, and test ergonomics.

P4 — New core abstractions
  Add only after concrete repeated pain proves the need.

P5 — Advanced tooling, generation, and automation
  Automate stabilized conventions only.

Recommended upcoming sprints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Sprint 16 — :doc:`sprints/planned/sprint_16_test_ergonomics_diagnostics` (Track A + D, P1/P3)
* Sprint 17 — :doc:`sprints/planned/sprint_17_lifecore_state_rfc` (Track C + F, P2)
* Sprint 18 — :doc:`sprints/planned/sprint_18_lifecore_state_msgs_abi` (Track C, P2 conditional)
* Sprint 19 — :doc:`sprints/deferred/former_sprint_14_factory_registry` (Track A extension, P4 conditional; historical Sprint 14)
* Sprint 20+ — :doc:`sprints/deferred/former_sprint_15_tooling_codegen` (Track E, P5 conditional; historical Sprint 15)

Deferred sprints
^^^^^^^^^^^^^^^^

Minimal factory and registry
  Historical Sprint 14 is now deferred/conditional and should be treated as
  Sprint 19 or later. Launch only if at least two real use cases prove that
  manual component instantiation is repeated pain. Do not launch it merely
  because ``spec_model.py`` exists or because a factory looks elegant.

Tooling and generated nodes
  Historical Sprint 15 is now deferred/conditional and should be treated as
  Sprint 20 or later. Launch only after examples, conventions, documentation,
  core API, and any ``lifecore_state`` boundary are stable.

Strategic architecture note
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``lifecore_ros2`` should remain focused on lifecycle component orchestration.
The future distributed typed state model should be developed as a separate
``lifecore_state`` track. This prevents the lifecycle core from becoming a
monolithic runtime framework.

Do not do now
^^^^^^^^^^^^^

* [ ] No full ``AppSpec`` system now.
* [ ] No generated nodes now.
* [ ] No plugin framework now.
* [ ] No ECS framework in core.
* [ ] No EventBus in core.
* [ ] No StateStore in core.
* [ ] No complex recovery automation now.
* [ ] No factory until repeated pain is proven.

Architecture rules
^^^^^^^^^^^^^^^^^^

Rule 1 — Keep ``lifecore_ros2`` small
  ``lifecore_ros2`` is a lifecycle runtime and component composition helper. It
  must stay explicit, testable, ROS-native, and minimal.

Rule 2 — Do not absorb every good idea into the core
  EventBus, ECS, StateStore, Codegen, DSL, diagnostics, and tooling may become
  separate modules. They must not automatically become part of ``lifecore_ros2``.

Rule 3 — Prefer proof before abstraction
  A new abstraction requires at least one concrete repeated pain point. Two
  independent use cases are preferred before adding core-level abstractions.

Rule 4 — Examples can outrank core features
  A companion example, documentation sprint, or RFC can be more important than a
  core feature if it reduces risk or improves adoption.

Rule 5 — Codegen follows conventions
  Generated code and CLI tooling must follow stabilized conventions. They must
  not be used to discover the architecture prematurely.

Rule 6 — Separate lifecycle from state
  Lifecycle drives systems. Systems modify state. State is the source of truth.
  Events describe what happened. ROS 2 exposes what must leave the process.

Rule 7 — Keep state architecture separate
  The future ``lifecore_state`` model must be designed as a separate
  architecture. Do not hide state-store concepts inside the lifecycle core.

Rule 8 — Prefer explicit transitions
  Do not hide lifecycle transitions behind too much automation. Lifecycle
  behavior must remain inspectable, debuggable, and predictable.

Rule 9 — Avoid manager classes with too many roles
  Avoid large Manager classes that handle lifecycle, state, ROS communication,
  callbacks, serialization, validation, timers, and logging all at once. Prefer
  small components with precise names.

Rule 10 — A sprint must have an acceptance criterion
  Every sprint must define track, priority, objective, scope, non-goals,
  acceptance criteria, and conditions when deferred.

Sprint archive rule
^^^^^^^^^^^^^^^^^^^

Completed sprints must be archived, not deleted.

Archived sprints are historical records. They should not drive current planning
directly. Any unfinished or still-relevant work discovered during sprint
archival must be moved into the active backlog as a new backlog item.

Sprint files may be moved between:

* ``active``
* ``planned``
* ``deferred``
* ``archived``

Sprint numbering should not be rewritten retroactively. If a planned sprint is
reclassified before execution, it may be moved to ``deferred/`` and renamed with
a ``former_sprint_XX`` prefix.

Sprint status values
^^^^^^^^^^^^^^^^^^^^

Use the following status values:

Active
  Currently being executed.

Planned
  Approved or likely upcoming work.

Completed
  Finished but not yet archived.

Archived
  Historical completed sprint. Not part of active planning.

Deferred
  Valid idea, but intentionally postponed.

Conditional
  Requires explicit launch conditions before execution.

Superseded
  Replaced by a newer plan.

Cancelled
  No longer relevant.

Prefer the smallest useful set of statuses. Do not create a complex
issue-tracking system inside the documentation.

Branching strategy
^^^^^^^^^^^^^^^^^^

The project uses a release-oriented branching model.

Branches
~~~~~~~~

``main``
  Release branch. Only stable, reviewed, release-ready work should be merged
  into ``main``.

``dev``
  Integration branch. Contains completed development work that is not
  necessarily released yet. Sprint branches must start from ``dev``.

Sprint branches
  Safe working branches created from ``dev`` for each sprint or coherent work
  package.

  Naming convention:

  .. code-block:: text

    sprint/<number>-<short-name>

  Examples:

  .. code-block:: text

    sprint/14-project-alignment
    sprint/15-companion-adoption
    sprint/16-test-ergonomics
    sprint/17-lifecore-state-rfc

Rules
~~~~~

* Never develop directly on ``main``.
* Avoid developing directly on ``dev`` except for very small documentation or
  emergency corrections.
* Create at least one dedicated sprint branch from ``dev`` for every sprint.
* A sprint branch must represent a coherent unit of work.
* Merge sprint branches back into ``dev`` after review and validation.
* Merge ``dev`` into ``main`` only for releases or release candidates.
* If a sprint is experimental or risky, keep it isolated until the direction is
  validated.
* If a sprint is cancelled or superseded, do not merge the branch blindly.
  Extract only the useful commits or documentation.
* If a sprint branch discovers follow-up work, move that work into the backlog
  instead of expanding the sprint indefinitely.

Recommended workflow
~~~~~~~~~~~~~~~~~~~~

Start a sprint:

.. code-block:: bash

  git checkout dev
  git pull
  git checkout -b sprint/14-project-alignment

Work normally on the sprint branch.

Before merging back to ``dev``:

.. code-block:: bash

  git checkout dev
  git pull
  git checkout sprint/14-project-alignment
  git rebase dev

Run checks:

.. code-block:: bash

  uv run pytest
  colcon test

Then merge into ``dev``:

.. code-block:: bash

  git checkout dev
  git merge --no-ff sprint/14-project-alignment

Release flow:

.. code-block:: bash

  git checkout main
  git pull
  git merge --no-ff dev

Release rule
~~~~~~~~~~~~

``main`` should only receive code from ``dev`` when the project is intentionally
preparing a release, release candidate, or stable checkpoint.

``dev`` may be ahead of ``main``.

Sprint branches may be ahead of ``dev``.

This means the expected flow is:

.. code-block:: text

  sprint/*  ->  dev  ->  main

Not:

.. code-block:: text

  sprint/*  ->  main

Branch cleanup
~~~~~~~~~~~~~~

After a sprint branch is merged into ``dev`` and no longer needed:

.. code-block:: bash

  git branch -d sprint/14-project-alignment

Remote cleanup, if applicable:

.. code-block:: bash

  git push origin --delete sprint/14-project-alignment

Do not delete branches that contain unmerged experimental work unless the work is
intentionally abandoned or safely extracted.

Sprint documentation link
~~~~~~~~~~~~~~~~~~~~~~~~~

Each sprint file should mention its working branch when applicable.

Example:

::

  Branch:
    sprint/14-project-alignment

For archived sprints, preserve the branch name if known.

Example:

::

  Branch:
    sprint/13-parameters

  Status:
    Archived / Completed

Acceptance criteria
~~~~~~~~~~~~~~~~~~~

The branching strategy is considered applied when:

* ``main`` is documented as the release branch.
* ``dev`` is documented as the integration branch.
* Sprint branches are documented as safe branches created from ``dev``.
* Sprint files can optionally record their branch name.
* The roadmap and backlog no longer imply that work happens directly on
  ``main``.
* Release work is explicitly separated from development work.

Archived sprint follow-up rule
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Archived sprint files must not contain active planning decisions. If unfinished
work remains relevant, it must be extracted into the backlog as a new item. The
archived sprint may keep a short "Follow-ups" section linking to the backlog
item.

---

Pre-release follow-ups
----------------------

Release status metadata
^^^^^^^^^^^^^^^^^^^^^^^

* [ ] Re-evaluate promotion from ``Development Status :: 3 - Alpha`` to
  ``Development Status :: 4 - Beta`` once the project is ready to signal usable,
  documented software whose API is still pre-``1.0.0`` but no longer broadly
  experimental.

**Rationale:** The current ``0.x`` series is documented and usable for evaluation,
but minor bumps may still include breaking changes. The package classifier should
stay conservative until that API-stability promise changes.

---

Strategic near-term backlog
---------------------------

These items are not post-1.0 by default. They are strategic candidates because
they make the value proposition visible and testable. Sprint priority is now
location-neutral; see :doc:`sprints/README`.

Lifecycle comparison example — baseline shipped; follow-up in Sprint 15
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/archived/sprint_04_lifecycle_comparison` for the
initial companion comparison baseline; :doc:`sprints/active/sprint_15_companion_adoption`
for the current adoption-polish follow-up.

* [x] Create ``lifecore_ros2_examples/examples/lifecycle_comparison/`` in the
  companion examples repository.
* [x] Implement the same sensor watchdog node three ways: plain ROS 2, classic
  ROS 2 lifecycle, and ``lifecore_ros2``.
* [x] Keep the example dependency-light even though it lives in the companion
  examples repo.
* [x] Show subscriber, publisher, and timer behavior across configure,
  activate, deactivate, and cleanup.
* [x] Document the observable difference: plain is simple but fragile, classic
  lifecycle is controlled but verbose, ``lifecore_ros2`` is structured and
  lifecycle-native.
* [ ] Tighten the shortest path so one new user can read and run the comparison
  as the primary adoption proof without needing broader architecture context.

**Rationale:** This is the strongest adoption asset. The project should not
publish broadly to ROS Discourse before the comparison example makes the value
obvious.

README and public signposting follow-up
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* [x] Link to the full comparison from core-facing README/docs surfaces instead
  of duplicating the full walkthrough.
* [ ] Decide whether ``README.md`` needs a dedicated concise comparison section
  or whether the current signposting is sufficient.
* [ ] Keep the adoption-facing message "build predictable ROS 2 nodes"
  prominent in public material without turning README into the technical
  reference.

**Rationale:** README should sell the concrete pain and point to the proof, not
become the technical reference.

Internal component cascade — *shipped in Sprint 5 (2026-05-04)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/archived/sprint_05_internal_cascade`.

* [x] Add component dependency metadata, likely by component name.
* [x] Add component priority metadata only as a secondary ordering hint.
* [x] Resolve transition order with dependencies first, priority second, and
  registration order as the stable fallback.
* [x] Apply normal order for configure / activate and reverse order for
  deactivate / cleanup.
* [x] Reject duplicate names, unknown dependencies, and dependency cycles with
  typed errors.

``dependencies`` and ``priority`` remain available on ``LifecycleComponent``.
Sprint 5.1 later added the registration-site form
``add_component(component, *, dependencies=None, priority=None)`` so node authors
can keep ordering intent visible without constructor pass-through. Typed errors
(``UnknownDependencyError``, ``CyclicDependencyError``) are exported from the
public surface. See :doc:`sprints/archived/sprint_05_internal_cascade` for the internal
ordering model and :doc:`sprints/archived/sprint_05_1_composition_surface` for the
composition-surface follow-up.

**Rationale:** Deterministic internal lifecycle ordering is the main
differentiator after activation gating. Keep this inside one node; do not turn it
into a system orchestrator.

Composition surface ergonomics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/archived/sprint_05_1_composition_surface`.

* [x] Let a node author declare ordering metadata at the registration site
  without modifying each component's ``__init__``.
* [x] Eliminate the constructor pass-through requirement for ``dependencies``
  and ``priority`` in application component subclasses.
* [x] Keep the library-first ergonomic property: a node that uses pre-built
  library components needs no ``_on_activate`` or ``_on_deactivate`` overrides.
* [x] Update or add a composition example that teaches the pattern without raw
  ``create_*`` calls.

**Rationale:** Sprint 5 proved that dependency ordering works.  The
constructor pass-through model is a usability friction point: metadata is
scattered across component definitions rather than visible at the assembly
site. Sprint 5.1 addresses this without changing the ordering algorithm.

**Delivered:** ``LifecycleComponentNode.add_component(...)`` now accepts
``dependencies`` and ``priority`` as optional registration-site metadata.
Conflicts between constructor-declared and registration-declared non-default
values raise ``TypeError``. ``add_components(...)`` remains intentionally
limited to bare components.

Cleanup and resource ownership API — *shipped in Sprint 7 (2026-05-06)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/archived/sprint_07_cleanup_api`.

* [x] Audit topic, timer, service, and client components for consistent cleanup
  semantics.
* [x] Clarify borrowed-vs-owned resources in API docs and docstrings.
* [x] No focused helpers needed; guard pattern is ``if x is not None`` / explicit raise.

**Delivered:** All 5 components have explicit cleanup semantics. ``_needs_cleanup``
reset unconditionally after cleanup/shutdown/error (even if release fails). Ownership
contract (owned ROS resources, borrowed callback_group/clock/executor) documented in
component docstrings and architecture. 38 regression tests lock the contract.

**Rationale:** Cleanup must stay predictable before adding health or watchdog
behavior. ROS resources should be created in configure and released in cleanup;
borrowed resources remain application-owned.

Minimal observability — *shipped in Sprint 9 (2026-05-08)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/archived/sprint_09_observability`.

* [x] Structured ``DEBUG`` log before and after each component hook (``component=``, ``hook=``, ``result=``, ``duration_ms=``).
* [x] ``DEBUG`` log before ``_release_resources`` (``component=``, ``action='release_resources'``).
* [x] Node-level ``DEBUG`` before transition propagation (``transition=``, ``component_count=``).
* [x] Node-level ``INFO`` after successful transitions; ``WARNING``/``INFO``/``ERROR`` for ``error_processing``.
* [x] Standardized activation-gating drop log: ``action='dropped'``, ``method=``, ``reason='not_active'``.
* [x] 15 regression tests asserting log field presence without brittle full-message matching.

**Delivered:** Lifecycle behavior is diagnosable from logs alone without ``print`` statements.
Hook timing (``duration_ms=``) is emitted unconditionally in the hook-end ``DEBUG`` message —
no flag, zero overhead when the logger is above ``DEBUG`` level (Option B).
``last_error`` deferred to Sprint 10 (as a ``HealthStatus`` field).
``transition_history`` deferred to backlog (`issue #14 <https://github.com/apajon/lifecore_ros2/issues/14>`_).

**Rationale:** Structured logs provide diagnosable lifecycle behavior for industrial debugging
without adding external dependencies or new public API surface.

Concurrency infrastructure — *shipped in Sprint 8 (2026-05-08)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/archived/sprint_08_concurrency`.

* [x] Implement ``LifecycleComponentNode.get_or_create_callback_group(component_name, group_type=None)``.
* [x] Default group type is ``MutuallyExclusiveCallbackGroup``; ``ReentrantCallbackGroup`` must be requested explicitly.
* [x] Protect ``_is_active`` with ``_active_lock: threading.Lock`` on every ``LifecycleComponent``.
* [x] Document the in-flight callback policy ("drop at next gate") in docstrings and architecture docs.
* [x] 13 new concurrency regression tests.

**Delivered:** ``get_or_create_callback_group`` helper on the node (idempotent, RLock-protected).
``_is_active`` reads and writes are GIL-independent. In-flight policy documented.
Thread-safety table in ``docs/architecture.rst`` extended. New pattern entry in
``docs/patterns.rst``.

**Rationale:** A documented, test-backed concurrency contract is required before
observability, health, or watchdog work can safely assume coherent state reads.

Publication gate
^^^^^^^^^^^^^^^^

* [ ] Publish to ROS Discourse only after the comparison example and README
  update are ready.
* [ ] Carry the message "build predictable ROS 2 nodes".
* [ ] Avoid claims about multi-node orchestration, process restart, or automatic
  recovery.

**Rationale:** The market need is implicit. Concrete proof should lead the
announcement.

---

Medium-term candidates
----------------------

Health / status API — *shipped in Sprint 10 (2026-05-08)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See :doc:`sprints/archived/sprint_10_health_status`.

* [x] ``HealthStatus`` frozen dataclass with ``level: HealthLevel``, ``reason: str``,
  ``last_error: str | None``.
* [x] ``HealthLevel`` enum: ``UNKNOWN | OK | DEGRADED | ERROR``.
* [x] ``last_error`` integrated as a field of ``HealthStatus``.
* [x] ``LifecycleComponent.health`` read-only property; updated by ``_guarded_call``
  and each ``on_*`` handler.
* [x] ``LifecycleComponentNode.health`` — worst-of aggregation across all components.
* [x] ``HealthStatus`` and ``HealthLevel`` exported from ``lifecore_ros2``.

**Delivered:** Applications and watchdogs can read component and node health without
accessing private state. Recovery behavior is out of scope.

Transition history
^^^^^^^^^^^^^^^^^^

Tracked in `GitHub issue #14 <https://github.com/apajon/lifecore_ros2/issues/14>`_.

* [ ] Bounded read-only history of lifecycle transitions per component or node.
* [ ] Implement only when a concrete use case (watchdog, diagnostics, test
  assertion) requires it.
* [ ] Size and ordering to be decided at sprint planning time.

**Rationale:** Logging covers the diagnostic need in Sprint 9. A structured
history surface adds public API surface and test complexity with no current
consumer. Deferred until a concrete use case arises.

Lightweight watchdog — *shipped in Sprint 11 (2026-05-10)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/archived/sprint_11_watchdog_light`.

* [x] Observe health and lifecycle state.
* [x] Report stale, warning, and error conditions.
* [ ] Optionally request a lifecycle transition through normal ROS 2 mechanisms.
* [x] Do not restart processes, kill nodes, or invent recovery workflows.

**Delivered:** ``LifecycleWatchdogComponent`` polls one or more targets exposing a
``.health`` property on a configurable interval. Logs ``DEGRADED`` at WARN level
(with reason), ``ERROR`` at ERROR level (with ``last_error`` if set), and emits an
additional WARN labelled ``STALE`` when a non-OK level persists beyond
``stale_threshold`` seconds. Staleness is tracked via the node clock
(``node.get_clock().now()``) for sim-time compatibility. Polling is
activation-gated; no ticks fire while deactivated. The watchdog is purely
read-only — it never triggers lifecycle transitions. ``LifecycleWatchdogComponent``
is exported from ``lifecore_ros2``. 25 regression tests in
``tests/components/test_watchdog_component.py`` and ``examples/minimal_watchdog.py``.

**Rationale:** Watchdog behavior is useful but risky. Version 1 observes and
reports; recovery and automatic transition requests remain deferred.

---

Long-term candidates
--------------------

Tooling and generated nodes — *deferred / conditional, Sprint 20+ or later*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/deferred/former_sprint_15_tooling_codegen`.

* [ ] Explore a Copilot skill or generator that creates ``lifecore_ros2`` node
  skeletons.
* [ ] Keep generated code aligned with the public API and examples.
* [ ] Treat MCP integration as a later tooling concern, not a runtime library
  dependency.

**Rationale:** AI-assisted scaffolding could fit the project well, but only once
the comparison examples, conventions, core API, documentation, and any
``lifecore_state`` boundary are stable enough to generate confidently.

---

Deferred backlog
----------------

Deliberately deferred. Do not implement until there is a concrete user need.

Lifecycle policies
^^^^^^^^^^^^^^^^^^

* [ ] ``ActivationPolicy``
* [ ] ``StartupPolicy``
* [ ] ``ShutdownPolicy``
* [ ] Optional activation/deactivation ordering rules

**Rationale:** Anticipates the question of component ordering and bootstrap automation already surfacing in user discussions.

Component dependencies and cascade — *core shipped in Sprint 5 (2026-05-04)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* [x] Basic ``dependencies`` and ``priority`` metadata shipped in Sprint 5.
* [ ] Registration-site declaration (visible at node assembly) tracked in Sprint 5.1.
* [ ] Keep broader lifecycle policies deferred until the Sprint 5.1 ergonomic
  surface is proven in examples.
* [ ] Do not add before/after policy variants unless dependency names and
  priority are insufficient.

**Rationale:** Component dependencies are likely central, but they should remain
small and deterministic before any policy layer exists.

Error handling — *shipped in Sprint 2 (2026-04-30)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Error propagation rules, partial-failure behavior (rollback policy B —
all-or-nothing), strict mode for invalid hook returns, ``LifecycleHookError``
for caught hook exceptions, and native rclpy ``ErrorProcessing``-driven
``_on_error`` are all locked and enforced. See
:doc:`../design_notes/error_handling_contract` for the ratified contract and
the propagation matrix.

Component state and health
^^^^^^^^^^^^^^^^^^^^^^^^^^

* [ ] Standard component state introspection
* [x] Component health/status reporting — shipped Sprint 10
* [x] Last error / last transition result per component — shipped Sprint 10 as ``HealthStatus.last_error``

**Rationale:** Essential for industrial debugging and operations.

Execution and timing
^^^^^^^^^^^^^^^^^^^^

* [x] Lifecycle-aware callback gating via ``when_active`` and component wrappers
* [ ] Optional callback duration tracking
* [ ] Optional missed tick tracking

**Rationale:** Callback gating is core behavior. Timing assumptions and missed
tick tracking remain optional future observability work.

Testing utilities
^^^^^^^^^^^^^^^^^

* [ ] Lifecycle component test fixtures
* [ ] Fake components for transition tests
* [ ] Helpers for callback gating tests

**Rationale:** Accelerates adoption and reduces friction for library-based testing across applications.

Observability
^^^^^^^^^^^^^

* [ ] Structured logging conventions
* [ ] Optional lifecycle transition tracing
* [ ] Optional component timing metrics

**Rationale:** Observability patterns deserve a reserved design space to avoid scattered instrumentation.

Parameters and runtime configuration — *``LifecycleParameterComponent`` shipped in Sprint 13 (2026-05-13); Sprint 13.1 planned*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/archived/sprint_13_parameters` (completed) and
:doc:`sprints/sprint_13_1_parameter_observer` (planned).

* [x] ``LifecycleParameterComponent`` for parameters owned by the local
  lifecycle node.
* [x] Declare local owned parameters during configure.
* [x] Read initial local values during configure.
* [x] Use ``STATIC`` / ``ACTIVE`` mutability instead of a broad policy matrix.
* [x] Accept runtime writes to mutable local parameters only while active.
* [x] Expose explicit owned-parameter hooks for pre-set, validation, and
  post-set behavior.
* [x] Scope owned parameter names by default as
  ``<component_name>.<parameter_name>``.
* [x] Ignore parameters not owned by the component so callbacks do not interfere
  across components.
* [ ] ``LifecycleParameterObserverComponent`` for parameters owned by other
  nodes.
* [ ] Observe remote parameter events without declaring, owning, validating, or
  rejecting remote updates.

**Delivered:** ``LifecycleParameterComponent``, ``LifecycleParameter``, and
``ParameterMutability`` exported from ``lifecore_ros2``. 12 regression tests in
``tests/components/test_lifecycle_parameter_component.py`` and example in
``examples/minimal_parameter.py``.

**Rationale:** Parameters are a first-class runtime concern, but local ownership
and remote observation have different ROS 2 authority boundaries. Keep them as
separate lifecycle-aware component concerns and do not turn them into an
application configuration system.

Config and specs — *deferred / conditional*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* [ ] ``SpecModel`` — deferred; ``src/lifecore_ros2/spec/spec_model.py`` is an
  empty experimental placeholder, not a committed architecture.
* [ ] ``AppSpec`` — do not implement now.
* [ ] ``ComponentSpec`` — do not implement now.
* [ ] Topic component specs — do not implement now.
* [ ] Add ``pydantic>=2.0`` to ``dependencies`` in ``pyproject.toml`` only if a
  later accepted sprint proves the need for schema validation.

**Rationale:** Deferred until concrete use case arrives; early config-driven design risks over-abstraction.

Factory and registry — *deferred / conditional, Sprint 19 or later*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* [ ] ``ComponentRegistry``
* [ ] ``ComponentFactory``
* [ ] ``SpecLoader`` — do not implement unless the deferred factory sprint proves
  a real loader need.

**Rationale:** A premature factory risks pulling the project toward
``AppSpec``, ``ComponentSpec``, ``SpecLoader``, Pydantic, generation, and a
configuration-driven runtime before user needs are proven. Enable only when at
least two real use cases show repeated manual-instantiation pain.

Callback group management — *shipped in Sprint 8 (2026-05-08)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* [x] ``get_or_create_callback_group(component_name, group_type=None)`` on ``LifecycleComponentNode`` — idempotent, ``threading.RLock``-protected.
* [x] ``MutuallyExclusiveCallbackGroup`` default; ``ReentrantCallbackGroup`` explicit.
* [x] Caller-owned constructor pattern preserved unchanged.
* [x] ``_is_active`` reads and writes GIL-independent (``_active_lock``).
* [x] In-flight callback policy documented.

See :doc:`sprints/archived/sprint_08_concurrency` for the implementation record and
:doc:`../design_notes/callback_groups` for the original design placeholder.

Additional components
^^^^^^^^^^^^^^^^^^^^^

* [x] ``LifecycleTimerComponent`` — shipped; activation-gated ``on_tick``, ROS timer created on configure and released on cleanup; example in ``examples/minimal_timer.py``
* [x] ``ServiceComponent`` — shipped (Sprint 1); abstract base + concrete ``LifecycleServiceServerComponent`` and ``LifecycleServiceClientComponent`` with activation gating; examples in ``examples/minimal_service_server.py`` and ``examples/minimal_service_client.py``
* [ ] ``ActionComponent``

**Rationale:** Each component type needs explicit activation gating and resource management.

Binding layer
^^^^^^^^^^^^^

* [ ] Decide whether a dedicated binding layer is needed
* [ ] Add it only if components become overloaded

**Rationale:** Prevents premature abstraction; surfaces only if component hierarchy grows unwieldy.

Companion examples repo
^^^^^^^^^^^^^^^^^^^^^^^

* [ ] See :doc:`examples_repo` for full planning.

README badges (post-release)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* [x] Add PyPI version badge (``shields.io/pypi/v/lifecore-ros2``) once published on PyPI
* [x] Add Python versions badge (``shields.io/pypi/pyversions/lifecore-ros2``) once on PyPI
* [x] Add GitHub latest release badge (``shields.io/github/v/release/apajon/lifecore_ros2``) after first tagged release

---

Design constraints — do not violate
------------------------------------

These are not tasks; they are guardrails for any future change.

* Do not recreate a parallel application state machine
* Do not reintroduce a vague "manager" abstraction
* Do not turn ``TopicComponent`` into a catch-all class
* Do not introduce magical configuration too early
* Do not hide state-store concepts inside the lifecycle core
* Do not hide lifecycle transitions behind too much automation
* Do not introduce dynamic plugin loading too early
* Stay lifecycle-native to ROS 2
* Keep the node light
* Keep components specialised and bounded
