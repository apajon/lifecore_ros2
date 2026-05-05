Sprint 12 - Lifecycle policies
==============================

**Objective.** Make component ordering and activation semantics configurable
without ad-hoc application code.

**Deliverable.** Applications can define simple ordering and bootstrap rules
without introducing a hidden state machine.

---

Decisions already made
----------------------

- Policy work must build on the focused internal cascade instead of replacing
  it.
- Native ROS 2 lifecycle control remains the authority for node transitions.
- Policy combinations must stay small enough to avoid a parallel state machine.

Policy areas
------------

Activation and startup policies are candidates only when a concrete example
shows repeated application code. Manual lifecycle control remains the baseline.

Component ordering remains the most likely first policy area.

Ordering builds on the focused internal cascade instead of replacing it:

- registration order remains the final stable fallback beneath explicit dependencies and priority
- explicit dependencies may define required order
- priority may be a secondary ordering hint
- deactivate and cleanup may run in reverse order when ownership requires it

To decide during sprint planning
--------------------------------

- Whether this sprint introduces an API or only documents policy constraints.
- Whether deferred activation belongs in scope.
- Whether auto-configure or auto-activate are justified by real examples.

---

Validation
----------

- [ ] Components activate in the documented order.
- [ ] Deactivate and cleanup order are documented and tested.
- [ ] Invalid ordering rules fail before transitions run.
- [ ] Partial activation semantics are explicit and test-backed.
- [ ] Policies and error handling interact predictably.

---

Risks and mitigation
--------------------

**Risk: policy combinations become a parallel state machine.** Keep policies
small, validate combinations early, and let native ROS 2 lifecycle remain in
control.

**Risk: ordering and rollback conflict.** Define failure behavior before adding
new knobs.

---

Dependencies
------------

- Requires: Sprint 2 error handling.
- Requires: Sprint 3 test utilities.
- Requires: Sprint 5 internal cascade if ordering becomes more than registration order.

---

Scope boundaries
----------------

In scope:

- minimal ordering policy
- activation policy discussion only when directly useful
- tests for deterministic ordering

Out of scope:

- workflow orchestration
- multi-node lifecycle management
- runtime policy changes
- compensation actions

---

Success signal
--------------

- [ ] Ordering improves deterministic component lifecycle behavior.
- [ ] Policy surface remains smaller than a custom state machine.
- [ ] The docs clearly separate internal node ordering from system orchestration.
