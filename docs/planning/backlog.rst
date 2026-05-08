Planning backlog
================

The first public release scope is implemented. What remains is split into
strategic near-term work, future feature candidates, and deliberately deferred
ideas.

See `ROADMAP.md <https://github.com/apajon/lifecore_ros2/blob/main/ROADMAP.md>`_ for the public-facing scope and `CHANGELOG.md <https://github.com/apajon/lifecore_ros2/blob/main/CHANGELOG.md>`_ for shipped changes.

See :doc:`strategy` for the product cap that explains why the backlog is ordered this way.

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
they make the value proposition visible and testable. Sprint numbers remain the
source of truth for priority order; see :doc:`sprints/README`.

Lifecycle comparison example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* [ ] Create ``lifecore_ros2_examples/examples/lifecycle_comparison/`` in the
  companion examples repository.
* [ ] Implement the same sensor watchdog node three ways: plain ROS 2, classic
  ROS 2 lifecycle, and ``lifecore_ros2``.
* [ ] Keep the example dependency-light even though it lives in the companion
  examples repo.
* [ ] Show subscriber, publisher, and timer behavior across configure,
  activate, deactivate, and cleanup.
* [ ] Document the observable difference: plain is simple but fragile, classic
  lifecycle is controlled but verbose, ``lifecore_ros2`` is structured and
  lifecycle-native.

**Rationale:** This is the strongest adoption asset. The project should not
publish broadly to ROS Discourse before the comparison example makes the value
obvious.

README comparison update
^^^^^^^^^^^^^^^^^^^^^^^^

* [ ] Add a concise comparison section after the example exists.
* [ ] Lead with "build predictable ROS 2 nodes" instead of a generic toolkit
  claim.
* [ ] Link to the full comparison instead of duplicating long explanations in
  README.

**Rationale:** README should sell the concrete pain and point to the proof, not
become the technical reference.

Internal component cascade — *shipped in Sprint 5 (2026-05-04)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/sprint_5_internal_cascade`.

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
public surface. See :doc:`sprints/sprint_5_internal_cascade` for the internal
ordering model and :doc:`sprints/sprint_5_1_composition_surface` for the
composition-surface follow-up.

**Rationale:** Deterministic internal lifecycle ordering is the main
differentiator after activation gating. Keep this inside one node; do not turn it
into a system orchestrator.

Composition surface ergonomics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/sprint_5_1_composition_surface`.

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

Sprint mapping: :doc:`sprints/sprint_7_cleanup_api`.

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

Concurrency infrastructure — *shipped in Sprint 8 (2026-05-08)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/sprint_8_concurrency`.

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

Health / status API
^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/sprint_10_health_status`.

* [ ] Define a small ``HealthStatus`` value object with level and reason.
* [ ] Add ``component.health() -> HealthStatus`` or equivalent only after the
  state model is clear.
* [ ] Keep the first version read-only.

**Rationale:** Health is the base for diagnostics and watchdog behavior, but it
should expose state before trying to repair anything.

Lightweight watchdog
^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/sprint_11_watchdog_light`.

* [ ] Observe health and lifecycle state.
* [ ] Report stale, warning, and error conditions.
* [ ] Optionally request a lifecycle transition through normal ROS 2 mechanisms.
* [ ] Do not restart processes, kill nodes, or invent recovery workflows.

**Rationale:** Watchdog behavior is useful but risky. Version 1 should observe
and report before any automatic recovery is considered.

---

Long-term candidates
--------------------

Tooling and generated nodes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sprint mapping: :doc:`sprints/sprint_15_tooling_generation`.

* [ ] Explore a Copilot skill or generator that creates ``lifecore_ros2`` node
  skeletons.
* [ ] Keep generated code aligned with the public API and examples.
* [ ] Treat MCP integration as a later tooling concern, not a runtime library
  dependency.

**Rationale:** AI-assisted scaffolding could fit the project well, but only once
the comparison example, cascade, cleanup, health, and watchdog contracts are
stable enough to generate confidently.

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
* [ ] Component health/status reporting
* [ ] Last error / last transition result per component

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

Parameters and runtime configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* [ ] ``ParameterComponent``
* [ ] Parameter declaration helper
* [ ] Parameter validation hook
* [ ] Optional lifecycle-aware parameter update policy

**Rationale:** Parameters are a first-class runtime concern, not just another component type.

Config and specs
^^^^^^^^^^^^^^^^

* [ ] ``SpecModel``
* [ ] ``AppSpec``
* [ ] ``ComponentSpec``
* [ ] Topic component specs
* [ ] Add ``pydantic>=2.0`` to ``dependencies`` in ``pyproject.toml`` when ``spec_model.py`` is implemented

**Rationale:** Deferred until concrete use case arrives; early config-driven design risks over-abstraction.

Factory and registry
^^^^^^^^^^^^^^^^^^^^

* [ ] ``ComponentRegistry``
* [ ] ``ComponentFactory``
* [ ] ``SpecLoader``

**Rationale:** Maturity marker; enable once specifications and use cases are validated.

Callback group management — *shipped in Sprint 8 (2026-05-08)*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* [x] ``get_or_create_callback_group(component_name, group_type=None)`` on ``LifecycleComponentNode`` — idempotent, ``threading.RLock``-protected.
* [x] ``MutuallyExclusiveCallbackGroup`` default; ``ReentrantCallbackGroup`` explicit.
* [x] Caller-owned constructor pattern preserved unchanged.
* [x] ``_is_active`` reads and writes GIL-independent (``_active_lock``).
* [x] In-flight callback policy documented.

See :doc:`sprints/sprint_8_concurrency` for the implementation record and
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
* Do not introduce dynamic plugin loading too early
* Stay lifecycle-native to ROS 2
* Keep the node light
* Keep components specialised and bounded
