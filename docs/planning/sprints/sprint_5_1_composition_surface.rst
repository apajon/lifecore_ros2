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

**Status.** Delivered 2026-05-05.

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

Implemented approach: registration-site declaration on
``LifecycleComponentNode.add_component(...)``.

Delivered API shape::

    node.add_component(component, *, dependencies=None, priority=None)

The first ordered composition example (``examples/composed_ordered_pipeline.py``)
was updated in place to reflect this approach. It stays framework-first and
does not teach composition through raw ROS ``create_*`` calls.

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

Decisions made during sprint
----------------------------

- API shape: ``LifecycleComponentNode.add_component(component, *, dependencies=None, priority=None)``.
- Compatibility: additive only; constructor-declared metadata remains supported.
- Conflict rule: if the constructor and the registration site both declare a non-default value
  for the same field, ``TypeError`` is raised immediately.
- Example strategy: ``examples/composed_ordered_pipeline.py`` was updated in place.
- Batch API: ``add_components(...)`` remains unchanged and accepts bare components only.

---

Validation
----------

- [ ] A node author can declare ordering metadata without subclassing
- [x] A node author can declare ordering metadata without subclassing
  ``LifecycleComponent`` and overriding ``__init__``.
- [x] Deterministic ordering from Sprint 5 continues to work correctly.
- [x] The updated or new composition example imports cleanly and the node
  configures, activates, deactivates, and cleans up without errors.
- [x] The example does not use raw ROS ``create_*`` calls to demonstrate
  composition.
- [x] Existing lifecycle and ordering tests pass without modification.
- [x] ``uv run ruff check .`` passes for all touched files.
- [x] ``uv run pyright`` reports no new errors.
- [x] ``uv run pytest`` is green.

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
