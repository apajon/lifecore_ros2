Sprint 5.1 - Composition surface
=================================

**Objective.** Make composition metadata visible and accessible at the point
where a node assembles its components, without requiring constructor
pass-through across every framework component subclass.

**Deliverable.** A minimal API surface lets a node author express composition
intent (ordering hints, dependency declarations, or equivalent metadata) in
one place, close to the registration site.  The first ordered composition
example in the framework repository teaches this pattern in a framework-first
way.

---

Why this sprint exists
----------------------

Sprint 5 delivered deterministic ordering through ``dependencies`` and
``priority`` metadata declared on each component constructor.  That approach
works but surfaces a usability gap: metadata is scattered across individual
component definitions rather than visible at the site where a node assembles
its components.

Sprint 5.1 addresses two follow-on concerns that Sprint 5 intentionally
deferred:

1. **API ergonomics.** Composition metadata should be visible where the node
   assembles components.  A reader of the node should understand ordering
   intent without tracing each component class.

2. **Subclass burden.** Adding composition metadata must not require
   constructor pass-through across every framework component subclass.  If
   every ``LifecycleComponent`` subclass must propagate ``dependencies`` and
   ``priority`` through its ``__init__``, the framework imposes a fragile
   boilerplate requirement on users.

The Sprint 5 example rewrites also surfaced a related, already-solved benefit:
using pre-built framework components as siblings eliminates ``_on_activate``
and ``_on_deactivate`` overrides entirely.  The rewritten ``minimal_publisher.py``
and ``composed_pipeline.py`` are shorter and clearer than their predecessors
not because of dependency ordering, but because the framework components own
the timer and topic lifecycle without any application hook code.  Sprint 5.1
should preserve and extend this property.

This sprint follows Sprint 5 and does not replace it.  The deterministic
ordering model introduced in Sprint 5 stays unchanged.  Sprint 5.1 only
refines where and how the metadata is expressed.

---

Scope
-----

Investigate and decide one ergonomic path for declaring composition metadata
without requiring constructor pass-through.

Candidates to evaluate during planning (not pre-decided):

- Registration-site declaration: metadata passed at the
  ``register_component`` call site in the node.
- Descriptor or class-level annotation: metadata attached to the component
  class without touching ``__init__``.
- Dedicated composition helper: a small structure that pairs a component
  instance with its ordering metadata.

The first ordered composition example (``examples/composed_ordered_pipeline.py``)
may be updated to reflect the chosen approach.  It should stay framework-first
and not teach composition through raw ROS ``create_*`` calls.

---

Decisions already made
-----------------------

- This sprint follows Sprint 5 and does not replace it.
- Deterministic ordering from Sprint 5 (dependency resolution, priority as
  secondary hint, registration order as final fallback, reverse order for
  deactivate and cleanup) stays unchanged.
- Composition metadata should be visible where the node assembles components,
  not only inside each component's constructor.
- Adding composition metadata must not require constructor pass-through across
  every framework component subclass.
- The framework example for ordered composition stays framework-first: it must
  not teach users to assemble components by calling raw ROS ``create_*``
  methods directly.
- ``LifecycleComponent`` itself stays minimal; no implicit behavior is added.

---

To decide during sprint planning
----------------------------------

- Exact API shape for expressing composition metadata at the registration site
  or an equivalent surface.
- Whether the existing ``composed_ordered_pipeline.py`` example is updated in
  place or superseded by a new example.
- Whether the subclass burden fix requires a breaking API change or can be
  additive.
- Error behavior when metadata conflicts with constructor-declared metadata.
- Whether ordering introspection surfaces need to be updated to reflect the
  new declaration site.

---

Validation
----------

- [ ] A node author can declare ordering metadata without subclassing
  ``LifecycleComponent`` and overriding ``__init__``.
- [ ] Deterministic ordering from Sprint 5 continues to work correctly.
- [ ] The updated or new composition example imports cleanly and the node
  configures, activates, deactivates, and cleans up without errors.
- [ ] The example does not use raw ROS ``create_*`` calls to demonstrate
  composition.
- [ ] Existing lifecycle and ordering tests pass without modification.
- [ ] ``uv run ruff check .`` passes for all touched files.
- [ ] ``uv run pyright`` reports no new errors.
- [ ] ``uv run pytest`` is green.

---

Risks and mitigation
--------------------

**Risk: the API change requires breaking constructor signatures in Sprint 5.**
Evaluate additive options first.  If a breaking change is unavoidable, scope
it narrowly and flag it explicitly before implementation.

**Risk: two metadata declaration sites (constructor and registration) produce
silent conflicts.**  Define a clear precedence rule during planning and make
conflicts detectable with a typed error.

**Risk: the example becomes too complex teaching both ordering and the new
API.**  Keep the example focused on one concept.  If two examples are needed,
keep them short and separate.

**Risk: the sprint drifts into a full API redesign of Sprint 5.**  Sprint 5.1
is a targeted ergonomics improvement.  The ordering model is not up for
redesign.

---

Dependencies
------------

- Requires Sprint 5 internal cascade to be complete and green.
- Depends on the public spelling of ``dependencies`` and ``priority`` metadata
  decided in Sprint 5 planning.
- Does not depend on Sprint 6 or later sprints.

---

Scope boundaries
----------------

In scope:

- API surface for expressing composition metadata at or near the registration
  site.
- Subclass burden reduction for ``LifecycleComponent`` subclasses.
- Update or replacement of the first ordered composition framework example.
- Focused tests for the new declaration surface.

Out of scope:

- Changes to the deterministic ordering algorithm from Sprint 5.
- Multi-node orchestration or cross-node composition.
- Conditional activation, startup policies, or workflow semantics.
- New lifecycle states or transitions.
- Companion repository example changes.

---

Success signal
--------------

- A node can declare the ordering relationship between its components in one
  readable location without modifying each component's constructor.
- A reader unfamiliar with the internals can understand component ordering
  intent from the node assembly code alone.
- The ordered composition example teaches the framework pattern without
  exposing raw ROS resource creation.
- Sprint 5 tests remain green with no regression.
