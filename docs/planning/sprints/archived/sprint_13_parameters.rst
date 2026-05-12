Sprint 13 - Parameters and runtime configuration
================================================

Status:
  Archived / Completed

Completed in:
  Unknown

Outcome:
  See sprint body.

Follow-ups:
  See docs/planning/backlog.rst if applicable.


**Objective.** Add lifecycle-aware parameter management when a concrete use case
requires it.

**Deliverable.** Parameters can be managed as lifecycle-aware component concerns
without turning the library into a config system.

---

Decisions already made
----------------------

- Parameter support must remain lifecycle-aware.
- This sprint does not introduce config-file parsing, schemas, or Pydantic
   models.
- Parameter ownership and cleanup must follow the component lifecycle contract.

Possible component responsibilities:

- declare parameters during configure
- read initial values during configure
- gate updates according to component lifecycle state
- clean local tracking during cleanup

Update policy candidates:

- read-only
- update any time
- active-only
- inactive-only

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

- [x] Parameters are declared during configure.
- [x] Values can be retrieved through a documented API.
- [x] Validation blocks invalid updates.
- [x] Update policy is enforced across lifecycle states.
- [x] Cleanup clears component-owned parameter tracking.

---

Risks and mitigation
--------------------

**Risk: namespace collisions.** Scope parameter names by component or document
the exact naming contract.

**Risk: config-system creep.** Do not add schema models, spec loaders, or file
parsing in this sprint.

---

Dependencies
------------

- Requires: stable component lifecycle semantics.
- Requires: Sprint 8 concurrency rules for update callbacks.
- Benefits from: Sprint 9 observability for rejected updates.

---

Scope boundaries
----------------

In scope:

- lifecycle-aware parameter declaration and validation
- update policy enforcement
- focused examples and tests

Out of scope:

- config file parsing
- Pydantic specs
- parameter persistence beyond ROS 2 native behavior

---

Success signal
--------------

- [x] Parameter behavior follows component lifecycle state.
- [x] The API does not become a general application configuration layer.
