Sprint 5 - Internal component cascade
=====================================

**Objective.** Turn the ordering ideas surfaced by examples into a focused,
minimal internal cascade.

**Deliverable.** Components can declare simple dependencies, and
``LifecycleComponentNode`` resolves a stable transition order.

---

Scope
-----

Add a minimal internal cascade model:

- ``dependencies``: component names that must transition first
- ``priority``: secondary ordering hint when dependencies do not decide order
- registration order: final stable fallback

Transition order:

- configure / activate: dependency-resolved order
- deactivate / cleanup: reverse resolved order

Invalid configurations:

- duplicate component names remain invalid
- unknown dependencies are invalid
- dependency cycles are invalid
- same graph produces the same order every time

---

Design constraints
------------------

- Stay inside one ``LifecycleComponentNode``.
- Do not orchestrate multiple ROS nodes.
- Do not add startup policies, conditional activation, or workflow semantics in
  this sprint.
- Keep native ROS 2 lifecycle semantics in control.

Decisions already made
----------------------

- Dependencies are declared between components inside one node.
- Priority is only a secondary ordering hint; it does not override explicit
  dependencies.
- Registration order remains the stable fallback.
- Reverse order is required for deactivate and cleanup.

Decisions made during sprint
----------------------------

- Dependencies: ``dependencies=("name",)`` keyword argument on ``LifecycleComponent.__init__``,
  forwarded through the full component hierarchy (``TopicComponent``, ``ServiceComponent``,
  ``LifecycleTimerComponent``, and all concrete subclasses).
- Priority: ``priority: int = 0`` keyword argument; higher value means earlier in the resolved
  order. Default 0.
- Error types: ``ComponentDependencyError`` (base, ``ValueError``), ``UnknownDependencyError``
  (unknown dependency name), ``CyclicDependencyError`` (cycle detected). All exported from the
  public package surface.
- Ordering resolution is kept internal: ``_resolved_order`` on ``LifecycleComponentNode`` is
  private and not exposed for introspection in this sprint.

---

Deliverable note
----------------

``examples/composed_ordered_pipeline.py`` ships as part of Sprint 5.  It
demonstrates timer → publisher → subscriber ordering via explicit
``dependencies`` on each component constructor.  ``priority`` is not used;
the example is intentionally limited to dependencies so the first reading
stays focused.

Registration order in the node is deliberately scrambled (sink first, timer
second, publisher last) to make clear that dependencies -- not registration
order -- drive the transition sequence.

The framework-first rewrite of this example also demonstrated a concrete
ergonomic benefit: by using ``LifecycleTimerComponent``,
``LifecyclePublisherComponent``, and ``LifecycleSubscriberComponent`` as
sibling components, no ``_on_activate`` or ``_on_deactivate`` overrides
appear anywhere in the example.  The framework gates each component
automatically based on activation state.

Validation
----------

- [x] Components transition in dependency order.
- [x] Priority only applies when dependencies do not decide order.
- [x] Registration order is stable as the final fallback.
- [x] Deactivate and cleanup run in reverse order.
- [x] Unknown dependency and cycle errors are typed and actionable.
- [x] Existing lifecycle tests continue to pass.
- [x] ``examples/composed_ordered_pipeline.py`` imports cleanly and the node
  configures, activates, deactivates, and cleans up without errors.

---

Success signal
--------------

- [x] A node with subscriber, processor, and publisher components can declare
  its internal order explicitly.
- [x] The implementation reads as deterministic ordering, not a hidden state
  machine.

*Delivered 2026-05-04.  All validation items green.  Ruff, Pyright, and pytest
(158 tests) pass.*
