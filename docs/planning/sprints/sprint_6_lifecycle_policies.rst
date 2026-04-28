Sprint 6 — Lifecycle policies
==============================

**Objectif.** Make component ordering and activation semantics configurable without ad-hoc code.

**Livrable.** "Applications can define activation ordering and bootstrap rules declaratively."

---

Content
-------

ActivationPolicy
^^^^^^^^^^^^^^^^

- ``ActivationPolicy`` enum or class with options:

  - ``IMMEDIATE`` — component becomes active immediately when node activates
  - ``DEFERRED`` — component stays inactive until explicitly activated (by application)
  - ``CONDITIONAL`` — component active only if predicate is true (e.g., sensor available)

- Application specifies: ``node.add_component(..., activation_policy=ActivationPolicy.DEFERRED)``

StartupPolicy
^^^^^^^^^^^^^

- ``StartupPolicy`` enum or class with options:

  - ``MANUAL`` — application must call configure/activate (current default)
  - ``AUTO_CONFIGURE`` — node automatically configures all components on init
  - ``AUTO_ACTIVATE`` — node automatically activates all components after configure

- Application specifies: ``node.set_startup_policy(StartupPolicy.AUTO_CONFIGURE)``

Component ordering
^^^^^^^^^^^^^^^^^^

- Optional: ``registration_order: List[str]`` — specify activation order
- If not specified, use registration order (current default)
- Validate no cycles in ordering

Deactivation order
^^^^^^^^^^^^^^^^^^

- Optional: deactivate in reverse order (LIFO) for safer cleanup
- Default: same as activate order (current semantics)
- Configurable: ``node.set_deactivation_order('reverse')`` or similar

Full-activation semantics
^^^^^^^^^^^^^^^^^^^^^^^^^

- Define what "fully active" means:

  - Option A: Node is active (ROS 2 state) → all components are active
  - Option B: Node is active → at least one component is active
  - Option C: Node is active → configured components are active (deferred ones don't count)

- Document the choice; enforce in tests

---

Tests to write
--------------

ActivationPolicy tests
^^^^^^^^^^^^^^^^^^^^^^

- [x] ``IMMEDIATE`` component is active when node activates
- [x] ``DEFERRED`` component is inactive when node activates
- [x] Application can manually activate deferred component
- [x] Multiple policies in same node work independently

StartupPolicy tests
^^^^^^^^^^^^^^^^^^^^

- [x] ``MANUAL`` requires explicit configure/activate (current behavior)
- [x] ``AUTO_CONFIGURE`` configures all components on node configure
- [x] ``AUTO_ACTIVATE`` activates all components after configure

Ordering tests
^^^^^^^^^^^^^^

- [x] Components activate in specified order
- [x] Deactivate in reverse order (if enabled)
- [x] Cycle detection in ordering (if specified)

Full-activation tests
^^^^^^^^^^^^^^^^^^^^^

- [x] Verify "fully active" definition matches chosen semantics
- [x] Deferred components don't block full activation
- [x] Query node: ``is_fully_active() -> bool``

---

Risks and mitigation
--------------------

**Risk 1: Overly complex policy combinations**

- **Problem**: Allowing every combination of policies leads to unexpected state machines.
- **Mitigation**:
  - Document valid policy combinations
  - Validate on node init (raise on invalid combo)
  - Example: ``AUTO_CONFIGURE`` + ``IMMEDIATE`` is sensible; ``AUTO_CONFIGURE`` + ``DEFERRED`` needs clarification

**Risk 2: Policy does not match application intent**

- **Problem**: Application sets a policy but gets unexpected behavior.
- **Mitigation**:
  - Provide clear examples for common use cases
  - Log policy decisions on node startup
  - Recommend most common defaults

**Risk 3: Partial activation state is unclear**

- **Problem**: Some components active, others deferred — what is node considered?
- **Mitigation**:
  - Define "full activation" upfront (pick Option A/B/C)
  - Provide query methods: ``is_component_active(name)``, ``is_fully_active()``
  - Test all scenarios

**Risk 4: Ordering constraints conflict with error handling**

- **Problem**: Component A must activate before B; B fails → A is active and must clean up in reverse.
- **Mitigation**:
  - Error handling (Sprint 2) + ordering (Sprint 6) must be consistent
  - On activate failure, rollback uses reverse order (deactivate in reverse)
  - Test this combo: ordering + partial failure

---

Dependencies
------------

- Requires: Error handling (Sprint 2) — rollback must respect ordering
- Requires: Testing utilities (Sprint 3) — easy setup of policy scenarios
- Requires: All components (Sprints 1, 4)

---

Scope boundaries
----------------

**In-scope:**

- ActivationPolicy (IMMEDIATE, DEFERRED, conditional)
- StartupPolicy (MANUAL, AUTO_CONFIGURE, AUTO_ACTIVATE)
- Component ordering (registration order or explicit)
- Deactivation order (same or reverse)
- Full-activation semantics (define and query)

**Out-of-scope:**

- Runtime policy changes (policies are set once at init)
- Conditional activation based on sensor feedback (too domain-specific)
- Complex state machines or workflow orchestration (out of scope, see ROADMAP)
- Compensation actions (e.g., "on A failure, do B") — application responsibility

---

Success signal
--------------

- [x] ``ActivationPolicy`` and ``StartupPolicy`` are defined
- [x] ``node.add_component(..., activation_policy=...)`` works
- [x] ``node.set_startup_policy(...)`` works
- [x] All ordering tests pass (activate/deactivate order correct)
- [x] Full-activation semantics are defined and testable
- [x] Policies + error handling work together correctly (integration test)
- [x] Example: ``examples/ordered_components.py`` (demonstrates activation ordering)
- [x] Example: ``examples/auto_bootstrap.py`` (demonstrates StartupPolicy.AUTO_CONFIGURE)
- [x] Ruff, Pyright, Pytest all green
- [x] Design note: lifecycle policies (if future-proofing needed)

---

Location
--------

- Module: ``src/lifecore_ros2/core/_policies.py`` or extend ``core/__init__.py``
- Updated: ``src/lifecore_ros2/core/*.py``, ``LifecycleComponentNode``
- Tests: ``tests/test_lifecycle_policies.py`` (new)
- Examples: ``examples/ordered_components.py``, ``examples/auto_bootstrap.py`` (new)

---

Related design notes
--------------------

- :doc:`../design_notes/lifecycle_policies` — reference for policy design decisions
