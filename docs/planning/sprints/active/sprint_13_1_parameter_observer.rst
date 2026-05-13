Sprint 13.1 - Parameter observer component
==========================================

Status:
  Active

Branch:
  sprint/13.1-parameter-observer

**Objective.** Add lifecycle-aware observation of parameters owned by other ROS
2 nodes without blurring ownership boundaries or adding configuration-system
behavior.

**Deliverable.** ``LifecycleParameterObserverComponent`` observes external
parameter values through ROS 2 remote parameter mechanisms. It may read initial
remote values and react to parameter events, but it never declares, owns,
validates, or rejects remote parameter updates.

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

Expected mechanisms:

- ``AsyncParameterClient`` for optional initial reads or remote requests
- ``ParameterEventHandler`` or ``/parameter_events`` for change observation

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
- Event processing or user observer callbacks must be lifecycle-gated.
- Cleanup, shutdown, and error release event/client tracking owned by the
  component.
- This sprint does not add config-file parsing, schemas, Pydantic models,
  persistence, registries, factories, or distributed configuration behavior.

Guiding rule:

::

   configure initializes observation
   active observes
   cleanup forgets

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
- store last observed values locally if requested
- expose a documented API for observed values
- gate user event callbacks by lifecycle state
- clean event handles, clients, and tracking during cleanup, shutdown, and error

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

- create required remote client or event-handler plumbing
- optionally read initial remote values
- store initial observed values if available
- do not call user event hooks as active runtime behavior
- handle missing remote node or parameter explicitly

Inactive / configured
^^^^^^^^^^^^^^^^^^^^^

- known values may be read through the component API
- event callbacks should not run user active behavior
- remote observation state may remain attached if the underlying ROS 2 handle
  requires it, but user behavior remains gated

Active
^^^^^^

- process remote parameter events
- update last observed values
- call user observer hooks for watched parameters

Deactivate
^^^^^^^^^^

- stop running user observer callbacks
- optionally keep last observed values
- do not attempt to alter remote parameters

Cleanup
^^^^^^^

- remove event callback handles if possible
- clear local watch, value, client, and event-handler tracking as appropriate
- return to a reconfigurable state

Shutdown
^^^^^^^^

- use the same cleanup intent
- release event/client tracking if possible
- clear local tracking

Error
^^^^^

- clear local tracking
- avoid corrective lifecycle transitions
- log useful diagnostics when relevant

---

Suggested public API
--------------------

Exact signatures are decided during implementation planning. The public names
must make observation explicit.

General multi-node shape:

.. code-block:: python

   class LifecycleParameterObserverComponent(LifecycleComponent):
       def watch_parameter(
           self,
           *,
           node_name: str,
           parameter_name: str,
           read_initial: bool = True,
       ) -> None: ...

       def get_observed_parameter_value(self, node_name: str, parameter_name: str) -> Any: ...

       def on_observed_parameter_event(
           self,
           node_name: str,
           parameter_name: str,
           value: Any,
       ) -> None: ...

Alternative one-remote-node shape:

.. code-block:: python

   class LifecycleParameterObserverComponent(LifecycleComponent):
       def __init__(self, ..., remote_node_name: str) -> None: ...

       def watch_parameter(self, parameter_name: str, *, read_initial: bool = True) -> None: ...

Use the simpler one-node shape only if early examples show that most observers
target a single remote node.

---

Validation
----------

- [ ] External parameter watches can be registered.
- [ ] Optional initial values can be read from a remote node.
- [ ] Missing remote node or parameter is handled explicitly.
- [ ] Parameter events update local observed values.
- [ ] User event callbacks are gated by lifecycle state.
- [ ] Observer never declares remote parameters.
- [ ] Observer never rejects remote updates.
- [ ] Cleanup removes event handles and local tracking.
- [ ] Shutdown and error also clear tracking.
- [ ] Tests distinguish remote observation from local ownership.
- [ ] No config-file, schema, Pydantic, registry, factory, persistence, or
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
- cleanup of event/client tracking
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

Implementation notes
--------------------

Prefer the component location:

::

   src/lifecore_ros2/components/lifecycle_parameter_observer_component.py

Add focused tests under:

::

   tests/components/test_lifecycle_parameter_observer_component.py

Suggested validation commands if this sprint is implemented:

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

- [ ] External parameters are observed through a dedicated component.
- [ ] Optional initial remote reads are lifecycle-aware.
- [ ] Remote parameter events update local observed state while active.
- [ ] Observer callbacks never imply ownership or validation authority.
- [ ] Cleanup, shutdown, and error clear observer-owned tracking.
- [ ] The library remains a ROS 2 lifecycle component toolkit, not a
  distributed configuration framework.
