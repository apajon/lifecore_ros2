Sprint 4.5 - State-only component example
=========================================

**Objective.** Add an explicit core example for a ``LifecycleComponent`` that
owns lifecycle-managed state without owning ROS resources.

**Deliverable.** A minimal, single-file core example demonstrates a state-only
component with clear reset behavior and no concrete application scenario.

---

Why this sprint exists
----------------------

Sprint 4 introduced the pattern in the companion ``sensor_watchdog`` comparison:
a component can own domain state while other components own subscriptions,
publishers, or timers. That pattern is useful enough to teach directly in the
core repository, but it should stay minimal there.

This sprint keeps the concrete watchdog scenario in ``lifecore_ros2_examples``
and adds the smallest core example that explains the abstraction by itself.

---

Scope
-----

Add one core example under ``lifecore_ros2/examples/``. The working target is:

::

   examples/minimal_state_component.py

The example should show:

- a state-only ``LifecycleComponent`` with private state and read-only
  properties
- an explicit ``update()`` or similarly small mutation method
- deterministic reset on cleanup, shutdown, and error
- a minimal ``LifecycleComponentNode`` that registers the component
- log output or a short docstring that makes the lifecycle behavior observable

The example should not become a sensor watchdog, processing pipeline, or
multi-component applied scenario.

---

Decisions already made
----------------------

- State-only components are valid framework components even when they do not
  allocate ROS resources.
- The component owns its state; other components may depend on it but should not
  mutate its internals directly.
- Configure, cleanup, shutdown, and error transitions reset the state in the
  minimal example.
- The core example teaches one abstraction: lifecycle-managed state.
- Concrete uses of this pattern remain in the companion examples repository.

---

Decisions made during sprint planning
--------------------------------------

- Filename: ``examples/minimal_state_component.py``.
- Classes: ``CounterStateComponent`` (component), ``StateComponentDemoNode`` (node).
- Deactivation does **not** reset state (Option A): count preserved across deactivate / re-activate.
- Mutation visible in the node (Option A): ``StateComponentDemoNode.on_activate`` calls
  ``self._counter.update(1)`` after ``super().on_activate(state)`` succeeds.
- Expected log lines documented in the module docstring.

---

Execution plan
--------------

- [x] Review existing core examples for naming, module docstring, and runnable
  ``main()`` style.
- [x] Add the minimal state-only component example in ``examples/``.
- [x] Keep the example import-safe for smoke tests.
- [x] Add or update focused smoke coverage for the new example.
- [x] Update docs or example indexes if the repository lists core examples.
- [x] Run targeted validation for the touched example and tests.

---

Validation
----------

- [x] ``uv run ruff check examples tests`` passes for the touched scope.
- [x] ``uv run pyright`` reports no new errors.
- [x] ``uv run pytest`` passes any tests touched or added by the example.
- [x] The example can be imported without starting ROS side effects.
- [x] The component resets its state on cleanup, shutdown, and error.

---

Risks and mitigation
--------------------

**Risk: the example becomes another concrete scenario.** Keep the file focused
on the state component itself. Move applied behavior to the companion examples
repository.

**Risk: reset semantics imply a framework rule that does not exist.** Make the
example explicit that cleanup, shutdown, and error reset state because this
component chooses to do so.

**Risk: the node starts doing component work.** Keep state ownership inside the
component and use the node only for registration and demonstration wiring.

---

Dependencies
------------

- Requires the existing ``LifecycleComponent`` and ``LifecycleComponentNode``
  APIs.
- Benefits from Sprint 4's companion example, which surfaced the pattern.
- Can be implemented before or after Sprint 5 internal cascade work because it
  does not require dependency resolution.

---

Scope boundaries
----------------

In scope:

- one minimal core example
- small smoke or regression coverage for import/reset behavior
- docs/index update if examples are listed

Out of scope:

- new framework APIs
- dependency graph or priority behavior
- watchdog, sensor, or pipeline scenarios
- companion repository changes

---

Success signal
--------------

- [x] A reader can understand that ``LifecycleComponent`` may own plain Python
  state, not only ROS resources.
- [x] The example clearly shows where state is updated and where it is reset.
- [x] The core/companion example boundary remains clear.
- [x] Ruff, Pyright, and pytest are green for the touched scope.
