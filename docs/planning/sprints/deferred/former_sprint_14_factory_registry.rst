Sprint 19 - Minimal factory and registry (conditional)
======================================================

Status:
  Deferred / Conditional

Reason:
  Deferred after Sprint 13 because factory and registry work should only start
  after repeated-instantiation pain is proven by concrete examples.

Launch condition:
  At least two concrete use cases must show that manual component instantiation
  creates repeated maintenance pain.

**Historical status.** This card used to be Sprint 14. It is now deferred and
conditional. It is not the default next sprint after Sprint 13.

**Track.** Core Extension.

**Priority.** P4 conditional - new core abstraction.

**Condition.** Start only if at least two real use cases prove that manual
component instantiation is repeated pain. Do not start this sprint just because
``src/lifecore_ros2/spec/spec_model.py`` exists or because a factory looks
elegant.

**Objective.** Enable dynamic component instantiation only after concrete specs
and examples justify it.

**Deliverable.** Components can be instantiated from a small registry without
introducing a plugin system.

---

Decisions already made
----------------------

- Registry and factory stay local and explicit.
- No plugin loading is introduced in this sprint.
- Dynamic creation must not hide component ownership or lifecycle registration.
- If specifications are involved, they are already-parsed data structures, not a
  new schema system.

Scope
-----

The likely scope is a small registry plus a thin factory that can create one
component, or a deterministic batch, from registered component types and
constructor data.

Spec loader boundary
^^^^^^^^^^^^^^^^^^^^

If a loader exists in this sprint, keep it minimal. Do not add schema validation
or a Pydantic dependency here.

To decide during sprint planning
--------------------------------

- Exact registry API and duplicate-registration behavior.
- Whether batch creation is necessary in the first version.
- Whether any spec loader belongs in this sprint at all.

---

Validation
----------

- [ ] Component types can be registered and retrieved.
- [ ] Duplicate registration behavior is documented and tested.
- [ ] Factory creates components with constructor kwargs.
- [ ] Unknown component types raise clear errors.
- [ ] Batch creation is deterministic.

---

Risks and mitigation
--------------------

**Risk: premature schema binding.** Keep specs free-form until real examples
show the shape.

**Risk: declarative-runtime creep.** A premature factory can pull the project
toward ``AppSpec``, ``ComponentSpec``, ``SpecLoader``, Pydantic, codegen, and a
configuration-driven runtime before the needs are proven.

**Risk: plugin-system creep.** Registry and factory stay local and explicit; no
dynamic plugin loading.

---

Dependencies
------------

- Requires: stable component constructors.
- Requires: examples proving repeated component instantiation is painful.
- Benefits from: parameter/configuration work if it exists.

---

Scope boundaries
----------------

In scope:

- local component registry
- thin factory
- clear errors

Out of scope:

- plugin loading
- schema validation
- full application spec model
- ``AppSpec`` / ``ComponentSpec`` / ``SpecLoader``
- codegen
- coupling with ``lifecore_state``
- runtime component removal

---

Success signal
--------------

- [ ] Dynamic creation reduces boilerplate without hiding component ownership.
- [ ] The factory simplifies at least two real examples.
- [ ] Manual APIs remain the reference path.
- [ ] Lifecycle transitions remain inspectable and explicit.
- [ ] The registry remains a simple tool, not a second abstraction layer.
