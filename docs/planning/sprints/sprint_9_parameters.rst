Sprint 9 — Parameters and runtime configuration
================================================

**Objectif.** Add lifecycle-aware parameter management; bind parameters to component lifecycle.

**Livrable.** "Parameters are managed as first-class lifecycle entities."

---

Content
-------

ParameterComponent base class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Abstract base class similar to ``TopicComponent``
- Lifecycle:

  - ``_on_configure``: declare parameters, retrieve initial values
  - ``_on_activate``: enable parameter update callbacks
  - ``_on_deactivate``: disable parameter update callbacks
  - ``_on_cleanup``: clean up parameter tracking

- API:

  - ``declare_parameter(name, value, descriptor=None)`` — declare and get initial value
  - ``get_parameter(name) -> ParameterValue`` — current value
  - ``set_parameter(name, value)`` — update (if allowed by policy)
  - ``on_parameter_updated(name, new_value)`` — hook (called if parameter changes)

Parameter validation hook
^^^^^^^^^^^^^^^^^^^^^^^^^

- ``validate_parameter(name, value) -> bool`` — return True if valid, False to reject
- Called before parameter is updated
- Raises exception or returns False to block update

Parameter update policy
^^^^^^^^^^^^^^^^^^^^^^^

- ``ParameterUpdatePolicy`` enum:

  - ``NONE`` — parameters are read-only
  - ``ANY_TIME`` — parameters can be updated any time
  - ``ACTIVE_ONLY`` — parameters can be updated only when component is active
  - ``INACTIVE_ONLY`` — parameters can be updated only when component is inactive

- Application specifies: ``self.parameter_update_policy = ParameterUpdatePolicy.ACTIVE_ONLY``

Parameter descriptor
^^^^^^^^^^^^^^^^^^^^

- Optional: ``ParameterDescriptor`` with type, bounds, description
- Used for validation and documentation

---

Tests to write
--------------

ParameterComponent unit tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [x] Parameter declared in ``_on_configure``, destroyed in ``_on_cleanup``
- [x] Parameter value retrieved with ``get_parameter()``
- [x] Parameter updated with ``set_parameter()`` (if policy allows)
- [x] ``on_parameter_updated`` hook called when parameter changes
- [x] Validation hook blocks invalid updates
- [x] Update policy enforced (``ACTIVE_ONLY`` blocks update when inactive)

Integration tests
^^^^^^^^^^^^^^^^^

- [x] Multiple ``ParameterComponent`` instances in same node
- [x] Parameter updates are independent
- [x] Lifecycle transitions clear parameter state correctly
- [x] Error in validation hook → update blocked and logged

Edge cases
^^^^^^^^^^

- [x] Update parameter during deactivate (blocked if ``ACTIVE_ONLY``)
- [x] Parameter update in ``on_parameter_updated`` callback (no reentrancy)
- [x] Delete component with active parameters → cleanup removes subscriptions

---

Risks and mitigation
--------------------

**Risk 1: Parameter namespace collisions**

- **Problem**: Multiple components declare parameter with same name.
- **Mitigation**:
  - Scope parameters to component name: ``/{node_name}/{component_name}/param_name``
  - Validation: component cannot declare parameter outside its namespace
  - Test: verify namespace isolation

**Risk 2: Update policy is not enforced**

- **Problem**: Application updates parameter when it shouldn't.
- **Mitigation**:
  - Check policy in ``set_parameter()`` before calling ROS 2 set
  - Raise ``ParameterUpdatePolicyViolationError`` if blocked
  - Test: all policy options

**Risk 3: Parameter update during transition**

- **Problem**: Parameter is updated while component is transitioning (e.g., configuring).
- **Mitigation**:
  - Use same RLock as component transitions (Sprint 5)
  - Documented contract: parameter updates are gated by component state
  - Test: concurrent update during transition

**Risk 4: On-change hook modifies component state**

- **Problem**: ``on_parameter_updated`` callback changes component behavior or state.
- **Mitigation**:
  - Documented contract: hook must be lightweight and non-blocking
  - Hook runs in callback thread (potential race if not careful)
  - Test: hook execution order and state isolation

---

Dependencies
------------

- Requires: ``LifecycleComponent`` (shipped)
- Requires: Error handling (Sprint 2) — parameter validation failure
- Requires: Concurrency (Sprint 6) — thread-safe parameter updates
- Requires: Testing utilities (Sprint 3) — fixtures for parameter testing
- Optionally: Lifecycle policies (Sprint 7) — if parameter is linked to activation

---

Scope boundaries
----------------

**In-scope:**

- ``ParameterComponent`` base class
- Parameter declaration and retrieval
- Validation hook
- Update policies (NONE, ANY_TIME, ACTIVE_ONLY, INACTIVE_ONLY)
- Parameter scoping (component namespace)
- On-change callback hook

**Out-of-scope:**

- Parameter server persistence (ROS 2 native responsibility)
- Parameter discovery and introspection beyond ROS 2 standard
- Configuration file parsing (application responsibility, or separate tool)
- Parameter binding to config specs (deferred to post-1.0 SpecModel)

---

Success signal
--------------

- [x] ``from lifecore_ros2 import ParameterComponent`` works
- [x] ``ParameterComponent`` can declare, retrieve, and update parameters
- [x] Validation hook works: invalid values are rejected
- [x] Update policies are enforced: ``ACTIVE_ONLY`` blocks updates when inactive
- [x] ``on_parameter_updated`` hook is called on changes
- [x] All tests pass (unit + integration + edge cases)
- [x] Example: ``examples/parameter_component.py`` (declares and uses parameters)
- [x] Ruff, Pyright, Pytest all green
- [x] Docstrings complete (Google style, Napoleon-ready)

---

Location
--------

- Module: ``src/lifecore_ros2/components/parameter_component.py`` or ``src/lifecore_ros2/core/parameter_component.py``
- Exports: ``src/lifecore_ros2/__init__.py``
- Tests: ``tests/test_parameter_component.py`` (new)
- Examples: ``examples/parameter_component.py`` (new)

---

Related design notes
--------------------

No specific design notes for this sprint (straightforward implementation).
