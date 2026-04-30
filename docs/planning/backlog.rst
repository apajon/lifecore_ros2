Post-1.0 backlog
================

The first public release scope is implemented. What remains is split into pre-release follow-ups and post-1.0 backlog.

See :doc:`../../ROADMAP` for the public-facing scope and :doc:`../../CHANGELOG` for shipped changes.

---

Pre-release follow-ups
----------------------

All pre-release follow-ups are complete. See commit history for details.

---

Post-1.0 backlog
----------------

Deliberately deferred. Do not implement until there is a concrete user need.

Lifecycle policies
^^^^^^^^^^^^^^^^^^

* [ ] ``ActivationPolicy``
* [ ] ``StartupPolicy``
* [ ] ``ShutdownPolicy``
* [ ] Optional activation/deactivation ordering rules

**Rationale:** Anticipates the question of component ordering and bootstrap automation already surfacing in user discussions.

Component dependencies
^^^^^^^^^^^^^^^^^^^^^^

* [ ] Optional component dependency declaration
* [ ] Optional before/after ordering constraints

**Rationale:** Naturally arises when components need to depend on each other; placeholder prevents architectural rework later.

Error handling
^^^^^^^^^^^^^^

* [ ] Define error propagation rules for component hooks
* [ ] Define behavior on partial configure/activate failure
* [ ] Optional rollback policy

**Rationale:** Error semantics are easy to defer and hard to fix once implicit. Setting the rule now prevents tangled recovery logic later.

See :doc:`../design_notes/error_handling_contract` for the design note placeholder.

Component state and health
^^^^^^^^^^^^^^^^^^^^^^^^^^

* [ ] Standard component state introspection
* [ ] Component health/status reporting
* [ ] Last error / last transition result per component

**Rationale:** Essential for industrial debugging and operations.

Execution and timing
^^^^^^^^^^^^^^^^^^^^

* [ ] Standard lifecycle-aware callback gating utility
* [ ] Optional callback duration tracking
* [ ] Optional missed tick tracking

**Rationale:** Callback groups, timing assumptions, and multi-threading will resurface as applications grow.

Testing utilities
^^^^^^^^^^^^^^^^^

* [ ] Lifecycle component test fixtures
* [ ] Fake components for transition tests
* [ ] Helpers for callback gating tests

**Rationale:** Accelerates adoption and reduces friction for framework-based testing across applications.

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

Callback group management
^^^^^^^^^^^^^^^^^^^^^^^^^

* [ ] Helper for ``LifecycleComponentNode`` to create and track ``CallbackGroup`` instances per component
* [ ] Optional: provide convenience constructors for common patterns (e.g., ``create_exclusive_group_for_component(name)``)

**Rationale:** Applications currently create callback groups manually. Framework support awaits clarified threading model (see Adoption Hardening §4).

See :doc:`../design_notes/callback_groups` for the design placeholder.

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
^^^^^^^^^^^^^^^^^^^^^^

* [ ] See :doc:`examples_repo` for full planning.

README badges (post-release)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* [ ] Add PyPI version badge (``shields.io/pypi/v/lifecore-ros2``) once published on PyPI
* [ ] Add Python versions badge (``shields.io/pypi/pyversions/lifecore-ros2``) once on PyPI
* [ ] Add GitHub latest release badge (``shields.io/github/v/release/apajon/lifecore_ros2``) after first tagged release

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
