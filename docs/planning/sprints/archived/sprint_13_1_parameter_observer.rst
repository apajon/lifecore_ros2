Sprint 13.1 - Parameter observer component
==========================================

Status:
  Archived / Completed

Branch:
  sprint/13.1-parameter-observer

Completed:
  2026-05-13

**Objective.** Add lifecycle-aware observation of parameters owned by other ROS
2 nodes without blurring ownership boundaries or adding configuration-system
behavior.

**Deliverable.** ``LifecycleParameterObserverComponent`` observes external
parameter values through ROS 2 remote parameter mechanisms. It may read initial
remote values and react to parameter events, but it never declares, owns,
validates, or rejects remote parameter updates.

**Progress.** Delivered in code, tests, examples, README, and Sphinx docs. The
component is exported from ``lifecore_ros2`` and documented in the generated
components API reference.

---

Core design decision
--------------------

Remote parameter observation is separate from local parameter ownership.

``LifecycleParameterObserverComponent`` is not a companion mode of
``LifecycleParameterComponent``. It is a distinct component concern with a
different authority boundary:

- ``LifecycleParameterComponent`` manages parameters owned by the local node.
- ``LifecycleParameterObserverComponent`` observes parameters owned by another
  node.

The remote node remains authoritative. Its own callbacks decide whether updates
are accepted.

---

Important ROS 2 distinction
---------------------------

External parameter events observe changes after they happen. They do not
participate in setting or validating remote parameters.

Implemented mechanisms:

- ``AsyncParameterClient`` for optional initial reads or remote requests
- ``/parameter_events`` subscription for change observation

Remote access can read or request updates on parameters owned by another node,
but the remote node remains the owner and applies its own validation callbacks.
This component must not present observation as ownership.

---

Decisions already made
----------------------

- Observation of external parameters is a separate component from local
  parameter ownership.
- The observer never declares remote parameters.
- The observer never owns remote parameters.
- The observer never validates or rejects remote parameter updates.
- ``configure()`` does not fail by default when an initial read cannot find the
  remote node or remote parameter.
- Initial-read outcomes are recorded as explicit, testable watch state:
  ``UNKNOWN_NODE``, ``UNKNOWN_PARAMETER``, ``UNAVAILABLE``, or
  ``VALUE_AVAILABLE``.
- User observer callbacks must be lifecycle-gated; snapshots may still update
  while inactive.
- Cleanup, shutdown, and error release observer-owned ROS handles created by the
  component.
- This sprint does not add config-file parsing, schemas, Pydantic models,
  persistence, registries, factories, or distributed configuration behavior.

Guiding rule:

::

    configure attaches observation
    active notifies user code
    cleanup releases observer-owned handles

Authority rule:

::

   observe facts already accepted by the remote node
   validate nothing
   block nothing
   correct nothing
   own nothing

---

Initial-read availability policy
--------------------------------

When ``read_initial=True`` and the remote node or parameter is absent,
``configure()`` must not fail by default. A remote observer does not own remote
availability, and failing local configuration would create a misleading
lifecycle dependency between the observer and the remote node.

The component must instead record an explicit state for each watch:

- ``UNKNOWN_NODE`` when the remote node cannot be identified as available.
- ``UNKNOWN_PARAMETER`` when the remote node is reachable but the watched
  parameter is absent or not returned.
- ``UNAVAILABLE`` when the initial read cannot complete for a transport,
  timeout, or other non-authoritative availability reason.
- ``VALUE_AVAILABLE`` when an initial value is read and stored.

These states must be queryable and testable. Logging may explain the condition,
but warnings are not the state contract.

---

LifecycleParameterObserverComponent
-----------------------------------

Purpose
^^^^^^^

Observe parameter values owned by another ROS 2 node as a lifecycle-aware
component concern.

Responsibilities
^^^^^^^^^^^^^^^^

- define remote parameters to observe
- optionally read initial values from a remote node during configure
- attach callbacks to parameter events
- store last observed snapshots locally
- expose a documented API for observed values
- gate user event callbacks by lifecycle state
- release observer-owned ROS handles during cleanup, shutdown, and error

Non-responsibilities
^^^^^^^^^^^^^^^^^^^^

- no declaration of remote parameters
- no ownership of remote parameters
- no validation of remote writes
- no rejection of remote updates
- no config-system behavior
- no guarantee that a remote value exists unless read or availability checks pass
- no remote lifecycle orchestration

---

Lifecycle contract
------------------

Construction
^^^^^^^^^^^^

- remote parameter watches may be registered locally
- do not assume the remote node is available
- do not create remote clients or event handlers unless that is proven safe
  before configure

Configure
^^^^^^^^^

- create the parameter-event subscription and initial-read client requests
- optionally read initial remote values
- store initial observed values if available
- record explicit watch state for missing nodes, missing parameters, and
  unavailable initial reads without failing by default
- do not call user event hooks as active runtime behavior
- handle missing remote node or parameter explicitly

Inactive / configured
^^^^^^^^^^^^^^^^^^^^^

- known values may be read through the component API
- event callbacks should not run user active behavior
- incoming events may still refresh queryable snapshots
- remote observation state may remain attached if the underlying ROS 2 handle
  requires it, but user behavior remains gated

Active
^^^^^^

- update last observed values
- call user observer hooks for watched parameters

Deactivate
^^^^^^^^^^

- stop running user observer callbacks
- optionally keep last observed values
- do not attempt to alter remote parameters

Cleanup
^^^^^^^

- destroy the parameter-event subscription if configured
- keep registered watches so a later configure can recreate handles and reread values
- return to a reconfigurable state

Shutdown
^^^^^^^^

- use the same cleanup intent
- release observer-owned ROS handles if configured
- leave the component in a safe terminal state

Error
^^^^^

- release observer-owned ROS handles if configured
- avoid corrective lifecycle transitions
- log useful diagnostics when relevant

---

Delivered public API
--------------------

The delivered API uses explicit remote-node and parameter names for each watch:

.. code-block:: python

   class LifecycleParameterObserverComponent(LifecycleComponent):
       def watch_parameter(
           self,
           *,
           node_name: str,
           parameter_name: str,
           read_initial: bool = True,
           callback: Callable[[ObservedParameterEvent], None] | None = None,
       ) -> ParameterWatchHandle: ...

       def get_observed_parameter(
           self,
           node_name: str,
           parameter_name: str,
       ) -> ObservedParameterSnapshot | None: ...

       def on_observed_parameter_event(
           self,
           node_name: str,
           parameter_name: str,
           event: ObservedParameterEvent,
       ) -> None: ...

Delivered event shape:

.. code-block:: python

   @dataclass(frozen=True)
   class ObservedParameterEvent:
       node_name: str
       parameter_name: str
       value: object
       previous_value: object | None
       source: Literal["initial_read", "parameter_event"]

``ObservedParameterSnapshot`` exposes the latest value, previous value if
known, and explicit watch state. Initial reads update snapshots and do not run
user event hooks as active runtime behavior. The snapshot API is the preferred
way for tests and callers to inspect initial-read availability outcomes.

---

Validation
----------

- [x] External parameter watches can be registered.
- [x] Optional initial values can be read from a remote node.
- [x] Missing remote node or parameter records explicit watch state without
  failing ``configure()`` by default.
- [x] Unavailable initial reads record ``UNAVAILABLE`` without hiding the
  condition behind logging only.
- [x] Available initial values record ``VALUE_AVAILABLE``.
- [x] Parameter events update local observed values.
- [x] User event callbacks are gated by lifecycle state.
- [x] Observer never declares remote parameters.
- [x] Observer never rejects remote updates.
- [x] Cleanup removes observer-owned ROS handles while keeping watches reconfigurable.
- [x] Shutdown and error also release observer-owned ROS handles.
- [x] Tests distinguish remote observation from local ownership.
- [x] No config-file, schema, Pydantic, registry, factory, persistence, or
  distributed configuration feature is introduced.

---

Risks and mitigation
--------------------

**Risk: remote observation is mistaken for ownership.** Document that observer
callbacks are post-fact event reactions. The remote node remains authoritative.

**Risk: confusing local callbacks with remote events.** Keep this component
separate from ``LifecycleParameterComponent`` and use explicit observed-parameter
API names.

**Risk: remote availability creates lifecycle flakiness.** Treat missing remote
nodes or parameters as explicit outcomes during configure. Do not hide retries or
recovery workflows inside the component.

**Risk: config-system creep.** Do not add file parsing, schemas, Pydantic,
config registries, persistence layers, or spec loaders in this sprint.

---

Dependencies
------------

- Requires: stable component lifecycle semantics.
- Requires: Sprint 8 concurrency rules for callback gating.
- Benefits from: Sprint 9 observability for diagnostic logs.
- Benefits from: Sprint 13 local parameter ownership documentation so ownership
  boundaries are already explicit.

---

Scope boundaries
----------------

In scope:

- remote parameter watches
- optional initial remote reads
- parameter event observation
- active-gated observer callbacks
- local tracking of last observed values
- cleanup of observer-owned ROS handles
- focused examples and tests

Out of scope:

- declaration of remote parameters
- ownership of remote parameters
- validation or rejection of remote updates
- remote lifecycle orchestration
- config file parsing
- YAML, TOML, or JSON loading
- Pydantic specs
- parameter schema models
- application-level config registry
- persistence beyond ROS 2 native behavior
- distributed configuration framework

---

Delivered implementation
------------------------

Component location:

::

   src/lifecore_ros2/components/lifecycle_parameter_observer_component.py

Focused tests:

::

   tests/components/test_lifecycle_parameter_observer_component.py

Validation commands used for this sprint scope:

.. code-block:: bash

   uv run ruff check src/lifecore_ros2/components tests/components
   uv run pyright
   uv run pytest tests/components/test_lifecycle_parameter_observer_component.py

If docs are updated:

.. code-block:: bash

   uv run --group docs python -m sphinx -b html docs docs/_build/html

---

Success signal
--------------

- [x] External parameters are observed through a dedicated component.
- [x] Optional initial remote reads are lifecycle-aware.
- [x] Remote parameter events update local observed state, with user callbacks
  gated by active lifecycle state.
- [x] Observer callbacks never imply ownership or validation authority.
- [x] Cleanup, shutdown, and error release observer-owned ROS handles.
- [x] The library remains a ROS 2 lifecycle component toolkit, not a
  distributed configuration framework.
