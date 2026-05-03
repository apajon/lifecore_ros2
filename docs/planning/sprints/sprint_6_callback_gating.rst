Sprint 6 - Unified callback gating
==================================

**Objective.** Extract activation-gating logic into a shared, reusable utility.
Remove duplication across publisher, subscriber, service, client, and timer
components.

**Deliverable.** Activation gating is consistent everywhere; no duplicate logic.

---

Decisions already made
----------------------

- Activation gating is a shared framework concern, not duplicated per
  component.
- Outgoing operations should keep their stricter inactive behavior, while
  incoming callbacks keep component-specific inactive behavior.
- Shared helpers may centralize state checks and log context, but each component
  keeps responsibility for its return value or exception policy.
- The sprint is behavior-preserving unless a mismatch is found and explicitly
  documented.

Components covered
------------------

Apply shared gating to:

- ``LifecyclePublisherComponent`` publish path
- ``LifecycleSubscriberComponent`` message callback
- service server callback
- service client calls
- ``LifecycleTimerComponent`` tick callback

To decide during sprint planning
--------------------------------

- Exact helper names and module placement.
- Whether a context manager, decorator, or direct function calls are clearest.
- How much node-level "fully active" terminology belongs in the first version.

---

Validation
----------

- [ ] ``is_active()`` returns the current activation state.
- [ ] ``require_active()`` raises if inactive and returns cleanly if active.
- [ ] Gated callbacks do not execute while inactive.
- [ ] Existing activation gating behavior remains unchanged.
- [ ] Logs are consistent across component types.

---

Risks and mitigation
--------------------

**Risk: behavior-preserving refactor changes semantics.** Keep old behavior as
the golden standard and compare component-by-component.

**Risk: overgeneralized gating hides component-specific behavior.** Keep the
shared utility small; component-specific inactive behavior stays in the
component.

---

Dependencies
------------

- Requires: publisher, subscriber, timer, service, and client component surfaces.
- Requires: error handling rules from Sprint 2.
- Requires: testing support from Sprint 3.

---

Scope boundaries
----------------

In scope:

- shared gating helpers
- component refactor to use those helpers
- behavior-preserving tests

Out of scope:

- new gating modes
- conditional application-specific gating
- performance work unless a regression is measured

---

Success signal
--------------

- [ ] Gating behavior is uniform across all component types.
- [ ] Duplicate gating logic is removed or clearly justified.
- [ ] Existing tests pass without semantic changes.
- [ ] Ruff, Pyright, and pytest are green.
