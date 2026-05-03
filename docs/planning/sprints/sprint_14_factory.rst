Sprint 14 - Minimal factory and registry
========================================

**Objective.** Enable dynamic component instantiation only after concrete specs
and examples justify it.

**Deliverable.** Components can be instantiated from a small registry without
introducing a plugin framework.

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
- runtime component removal

---

Success signal
--------------

- [ ] Dynamic creation reduces boilerplate without hiding component ownership.
- [ ] The registry remains a simple tool, not a second framework.
