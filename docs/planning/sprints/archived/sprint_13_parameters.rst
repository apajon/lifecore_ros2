Sprint 13 - Owned parameters and runtime configuration
======================================================

Status:
  Archived / Completed

Completed in:
  May 2026

Outcome:
  See sprint body.

Follow-ups:
  See docs/planning/backlog.rst if applicable.


**Objective.** Add lifecycle-aware support for parameters owned by the local
``LifecycleComponentNode`` while keeping a hard boundary between local parameter
ownership and remote parameter observation.

**Deliverable.** ``LifecycleParameterComponent`` manages local ROS 2 parameters
as a bounded component concern: configure initializes, active mutates, cleanup
forgets. The library remains a lifecycle component toolkit, not an application
configuration system.

---

Core design decision
--------------------

Owned parameters and observed external parameters are separate component
concerns.

Do not mix local parameter ownership with remote parameter observation in the
same component. Sprint 13 covers only ``LifecycleParameterComponent``. Remote
parameter observation is split into
:doc:`../active/sprint_13_1_parameter_observer`.

The local component owns parameters on the same lifecycle node that owns the
component. It may declare, read, validate, and track those owned parameters. It
must ignore parameters it does not own so multiple components can safely attach
callbacks to the same node.

---

Important ROS 2 distinction
---------------------------

ROS 2 local parameter callbacks and external parameter events are different
mechanisms.

Local set callbacks attach to the local node and participate in mutation of
parameters owned by that node:

- ``pre_set_parameters_callback``
- ``on_set_parameters_callback``
- ``post_set_parameters_callback``

These callbacks belong in ``LifecycleParameterComponent``. They may inspect,
transform, validate, reject, or react to local owned parameter updates according
to the exact support exposed by ``rclpy``.

External parameter observation uses mechanisms such as ``ParameterEventHandler``
or ``/parameter_events``. Those mechanisms observe changes published by other
nodes. They cannot declare, own, validate, or reject those remote updates, and
therefore do not belong in Sprint 13.

---

Decisions already made
----------------------

- Parameter support must remain lifecycle-aware.
- Sprint 13 introduces ``LifecycleParameterComponent`` for local owned
   parameters.
- Remote parameter observation is a separate component concern and is deferred
   to Sprint 13.1.
- Parameter ownership and cleanup must follow the component lifecycle contract.
- The default namespace convention is ``<component_name>.<parameter_name>``.
- Runtime parameter writes are accepted only while the owning component is
   active.
- The initial mutability model is deliberately small: ``STATIC`` and ``ACTIVE``.
- Components must ignore parameters they do not own.
- This sprint does not introduce config-file parsing, schemas, Pydantic models,
   parameter persistence, registries, factories, or plugin systems.

Guiding rule:

::

    configure initializes
    active mutates
    cleanup forgets

---

LifecycleParameterComponent
---------------------------

Purpose
^^^^^^^

Manage ROS 2 parameters owned by the local lifecycle node as a
lifecycle-aware component concern.

Responsibilities
^^^^^^^^^^^^^^^^

- register parameter definitions before or during configure
- declare owned ROS 2 parameters during configure
- read initial values from the local node during configure
- expose a documented API to read tracked values
- allow runtime writes only while the owning component is active
- expose explicit hooks for local owned parameter updates
- clean component-owned tracking during cleanup, shutdown, and error

Non-responsibilities
^^^^^^^^^^^^^^^^^^^^

- no config-file parsing
- no YAML, TOML, or JSON loading
- no Pydantic
- no schemas
- no parameter persistence beyond ROS 2 native behavior
- no global config registry
- no factory or plugin system
- no remote parameter observation
- no remote parameter ownership

---

Lifecycle contract
------------------

Construction
^^^^^^^^^^^^

- parameter definitions may be registered locally
- no ROS 2 parameter declaration is required in ``__init__``
- no runtime write is accepted
- no update callback should run as lifecycle behavior

Configure
^^^^^^^^^

- declare owned ROS 2 parameters on the local node
- read initial values from the local node
- store tracked values locally
- install or enable local parameter callbacks if needed
- reject duplicate component-owned parameter definitions
- do not treat runtime update hooks as active behavior

Inactive / configured
^^^^^^^^^^^^^^^^^^^^^

- values may be read through the component API
- runtime writes are rejected
- owned pre-set, validation, and post-set hooks must not perform active runtime
   behavior

Active
^^^^^^

- values may be read
- runtime writes to writable owned parameters may be accepted
- owned pre-set, validation, and post-set hooks are active
- validation can reject invalid local updates
- accepted updates refresh local tracking

Deactivate
^^^^^^^^^^

- stop accepting runtime writes
- keep tracked values
- do not undeclare ROS 2 parameters
- callbacks may remain registered but must gate behavior by lifecycle state

Cleanup
^^^^^^^

- clear local tracking owned by the component
- clear definitions, values, and callback handles as appropriate
- return to a reconfigurable state
- do not become a persistence layer
- do not rely on undeclare behavior unless ``rclpy`` support is safe and
   explicitly tested

Shutdown
^^^^^^^^

- use the same cleanup intent
- release callback handles if possible
- clear local tracking

Error
^^^^^

- clear local tracking
- avoid corrective lifecycle transitions
- log useful diagnostics when relevant

---

Parameter mutability
--------------------

Avoid the broader update-policy set for the first implementation:

- read-only
- update any time
- active-only
- inactive-only

Instead, use a smaller model:

``STATIC``
   Declared during configure, read during configure, readable while configured,
   and rejects all runtime writes, including while active. No before/after
   runtime update behavior is required.

``ACTIVE``
   Declared during configure, read during configure, readable while configured,
   and accepts valid runtime writes only while the component is active. Accepted
   writes update local tracking.

Possible enum shape:

.. code-block:: python

    class ParameterMutability(Enum):
         STATIC = "static"
         ACTIVE = "active"

Possible parameter definition shape:

.. code-block:: python

    @dataclass(frozen=True)
    class LifecycleParameter:
         name: str
         default_value: Any
         mutability: ParameterMutability = ParameterMutability.STATIC
         description: str | None = None

---

Suggested public API
--------------------

Exact signatures are decided during implementation planning, but ownership must
be explicit in public hook names.

.. code-block:: python

    class LifecycleParameterComponent(LifecycleComponent):
         def declare_lifecycle_parameter(
            self,
            name: str,
            default_value: Any,
            *,
            mutability: ParameterMutability = ParameterMutability.STATIC,
            description: str | None = None,
         ) -> None: ...

         def get_parameter_value(self, name: str) -> Any: ...

         def has_parameter(self, name: str) -> bool: ...

         def on_pre_set_owned_parameters(self, parameters: list[Parameter]) -> list[Parameter]:
            return parameters

         def on_validate_owned_parameters(self, parameters: list[Parameter]) -> SetParametersResult:
            return SetParametersResult(successful=True)

         def on_post_set_owned_parameters(self, parameters: list[Parameter]) -> None: ...

Prefer explicit owned-parameter names:

- ``on_pre_set_owned_parameters``
- ``on_validate_owned_parameters``
- ``on_post_set_owned_parameters``

Avoid ambiguous names such as ``pre_set_parameters``, ``on_set_parameters``, and
``post_set_parameters`` because those can be confused with raw ROS 2 node
callbacks.

An ergonomic per-parameter validation hook may be added if it remains a thin
adapter over the internal batch-aware ROS 2 callback path:

.. code-block:: python

    def validate_parameter_update(self, name: str, old_value: Any, new_value: Any) -> str | None:
         return None

``None`` means accepted. A string means rejected with that reason.

---

Namespace convention
--------------------

Default parameter names are scoped by component:

::

    <component_name>.<parameter_name>

Examples:

- ``camera_fusion.max_latency_ms``
- ``planner.replan_period_s``
- ``controller.kp``

This avoids collisions when multiple components share one lifecycle node,
preserves component ownership, and keeps diagnostics readable. Do not add a
global unscoped opt-out in the first version unless a concrete use case requires
it.

---

Callback behavior for owned parameters
--------------------------------------

The local parameter callback path should:

1. receive a batch of parameter updates from ``rclpy``
2. inspect or split parameters owned by this component
3. ignore parameters not owned by this component
4. reject owned runtime writes if the component is not active
5. reject writes to ``STATIC`` parameters
6. run validation for ``ACTIVE`` parameters only while active
7. update local tracking after successful accepted updates
8. run post-set behavior only after success
9. return useful rejection reasons

Critical rule: a component must ignore parameters it does not own. If one
component rejects unknown parameters, it can accidentally block updates owned by
another component on the same node.

---

Instead, use a smaller model:

``STATIC``
   Declared during configure, read during configure, readable while configured,
   and rejects all runtime writes, including while active. No before/after
   runtime update behavior is required.

``ACTIVE``
   Declared during configure, read during configure, readable while configured,
   and accepts valid runtime writes only while the component is active. Accepted
   writes update local tracking.

Possible enum shape:

.. code-block:: python

    class ParameterMutability(Enum):
         STATIC = "static"
         ACTIVE = "active"

Possible parameter definition shape:

.. code-block:: python

    @dataclass(frozen=True)
    class LifecycleParameter:
         name: str
         default_value: Any
         mutability: ParameterMutability = ParameterMutability.STATIC
         description: str | None = None

---

Suggested public API
--------------------

Exact signatures are decided during implementation planning, but ownership must
be explicit in public hook names.

.. code-block:: python

    class LifecycleParameterComponent(LifecycleComponent):
         def declare_lifecycle_parameter(
            self,
            name: str,
            default_value: Any,
            *,
            mutability: ParameterMutability = ParameterMutability.STATIC,
            description: str | None = None,
         ) -> None: ...

         def get_parameter_value(self, name: str) -> Any: ...

         def has_parameter(self, name: str) -> bool: ...

         def on_pre_set_owned_parameters(self, parameters: list[Parameter]) -> list[Parameter]:
            return parameters

         def on_validate_owned_parameters(self, parameters: list[Parameter]) -> SetParametersResult:
            return SetParametersResult(successful=True)

         def on_post_set_owned_parameters(self, parameters: list[Parameter]) -> None: ...

Prefer explicit owned-parameter names:

- ``on_pre_set_owned_parameters``
- ``on_validate_owned_parameters``
- ``on_post_set_owned_parameters``

Avoid ambiguous names such as ``pre_set_parameters``, ``on_set_parameters``, and
``post_set_parameters`` because those can be confused with raw ROS 2 node
callbacks.

An ergonomic per-parameter validation hook may be added if it remains a thin
adapter over the internal batch-aware ROS 2 callback path:

.. code-block:: python

    def validate_parameter_update(self, name: str, old_value: Any, new_value: Any) -> str | None:
         return None

``None`` means accepted. A string means rejected with that reason.

---

Namespace convention
--------------------

Default parameter names are scoped by component:

::

    <component_name>.<parameter_name>

Examples:

- ``camera_fusion.max_latency_ms``
- ``planner.replan_period_s``
- ``controller.kp``

This avoids collisions when multiple components share one lifecycle node,
preserves component ownership, and keeps diagnostics readable. Do not add a
global unscoped opt-out in the first version unless a concrete use case requires
it.

---

Callback behavior for owned parameters
--------------------------------------

The local parameter callback path should:

1. receive a batch of parameter updates from ``rclpy``
2. inspect or split parameters owned by this component
3. ignore parameters not owned by this component
4. reject owned runtime writes if the component is not active
5. reject writes to ``STATIC`` parameters
6. run validation for ``ACTIVE`` parameters only while active
7. update local tracking after successful accepted updates
8. run post-set behavior only after success
9. return useful rejection reasons

Critical rule: a component must ignore parameters it does not own. If one
component rejects unknown parameters, it can accidentally block updates owned by
another component on the same node.

---

Sprint outcome
--------------

- Implemented as ``LifecycleParameterComponent``.
- Validation surface: ``validate_parameter_update(...)`` for per-parameter rules,
  with ``on_validate_owned_parameters(...)`` available for batch validation.
- Parameter names are scoped as ``<component_name>.<parameter_name>``.
- First implementation ships two update policies: ``STATIC`` and ``ACTIVE``.

---

Validation
----------

- [x] Parameter definitions can be registered before configure.
- [x] ROS 2 parameters are declared during configure.
- [x] Initial values are read during configure.
- [x] Values can be retrieved through a documented API after configure.
- [x] Reading before configure fails clearly.
- [x] Duplicate owned parameter names fail clearly.
- [x] Runtime writes are rejected while inactive.
- [x] ``STATIC`` parameters reject all runtime writes.
- [x] ``ACTIVE`` parameters accept valid writes only while active.
- [x] Validation blocks invalid active updates.
- [x] Accepted active updates refresh local tracking.
- [x] Post-set behavior runs only after successful active updates.
- [x] Parameters not owned by the component are ignored by this component.
- [x] Cleanup clears component-owned runtime tracking.
- [x] Shutdown and error also clear tracking.
- [x] No config-file, schema, Pydantic, registry, factory, or persistence
   feature is introduced.

---

Risks and mitigation
--------------------

**Risk: namespace collisions.** Scope owned parameters as
``<component_name>.<parameter_name>``, track ownership explicitly, and ignore
non-owned parameters in callbacks.

**Risk: config-system creep.** Do not add file parsing, schemas, Pydantic,
config registries, persistence layers, or spec loaders in this sprint.

**Risk: callback interference between components.** Each component must ignore
parameters it does not own and reject only its own parameters. Add a
multi-component coexistence test if practical.

**Risk: local callbacks are confused with remote events.** Keep
``LifecycleParameterComponent`` limited to local owned parameters and split
remote observation into Sprint 13.1.

---

Dependencies
------------

- Requires: stable component lifecycle semantics.
- Requires: Sprint 8 concurrency rules for update callbacks.
- Benefits from: Sprint 9 observability for rejected updates.
- Feeds: Sprint 13.1 remote parameter observation.

---

Scope boundaries
----------------

In scope:

- local lifecycle-aware parameter declaration and validation
- ``STATIC`` / ``ACTIVE`` mutability
- active-only runtime writes for mutable owned parameters
- explicit owned-parameter hooks
- component-scoped parameter names
- focused examples and tests

Out of scope:

- config file parsing
- YAML, TOML, or JSON loading
- Pydantic specs
- parameter schema models
- application-level config registry
- persistence beyond ROS 2 native behavior
- remote parameter ownership
- remote parameter observation
- remote update validation
- lifecycle state machine changes unless strictly required
- distributed configuration framework

---

Implementation notes
--------------------

Prefer the first component location:

::

    src/lifecore_ros2/components/lifecycle_parameter_component.py

Add focused tests under:

::

    tests/components/test_lifecycle_parameter_component.py

Suggested validation commands for component-only implementation:

.. code-block:: bash

    uv run ruff check src/lifecore_ros2/components tests/components
    uv run pyright
    uv run pytest tests/components/test_lifecycle_parameter_component.py

If docs are updated:

.. code-block:: bash

    uv run --group docs python -m sphinx -b html docs docs/_build/html

---

Success signal
--------------

- [x] A component owns local parameters.
- [x] Those parameters are declared and initialized during configure.
- [x] Static parameters remain immutable at runtime.
- [x] Active parameters can be changed only while the component is active.
- [x] Local parameter callbacks are explicit and lifecycle-gated.
- [x] External parameter observation is kept out of this component.
- [x] The library remains a ROS 2 lifecycle component toolkit, not a config
   framework.
