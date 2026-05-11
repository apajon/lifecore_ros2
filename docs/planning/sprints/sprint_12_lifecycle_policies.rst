Sprint 12 - Lifecycle policies
==============================

**Objective.** Make the intra-node lifecycle ordering contract deterministic,
documented, and test-backed without expanding ``lifecore_ros2`` into lifecycle
orchestration.

**Deliverable.** The existing ``dependencies`` + ``priority`` + registration
order model is documented as the supported ordering policy, with focused tests
covering order, reverse teardown, invalid rules, and partial activation
semantics.

---

Decisions already made
----------------------

- Policy work must build on the focused internal cascade instead of replacing
  it.
- Native ROS 2 lifecycle control remains the authority for node transitions.
- Policy combinations must stay small enough to avoid a parallel state machine.
- Sprint 12 starts with documentation and consolidation tests, not a new public
  policy API.
- A named policy API should be added only if tests or real usage reveal a gap in
  the current ``dependencies`` + ``priority`` + registration order model.

Policy areas
------------

Activation and startup policies remain out of scope until a concrete example
shows repeated application code. Manual lifecycle control remains the baseline.

Component ordering is the only Sprint 12 policy area.

Ordering builds on the focused internal cascade instead of replacing it:

- explicit dependencies may define required order
- priority may be a secondary ordering hint
- registration order remains the final stable fallback beneath explicit dependencies and priority
- configure and activate run in resolved order
- deactivate and cleanup run in reverse resolved order
- invalid dependency rules fail before component transition hooks run
- partial activation follows the existing error-handling contract; the sprint
  clarifies the behavior but does not add automatic compensation

Decided during sprint planning
------------------------------

- Deliver documentation and targeted consolidation tests first.
- Do not add a public policy API by default.
- Do not add deferred activation.
- Do not add auto-configure or auto-activate.
- Do not add a workflow engine, parallel state machine, or multi-node
  orchestration.

---

Validation
----------

- [x] Components configure and activate in the documented order.
- [x] Deactivate and cleanup order are documented and tested.
- [x] Invalid ordering rules fail before transitions run.
- [x] Partial activation semantics are explicit and test-backed.
- [x] Policies and error handling interact predictably without adding
  compensation behavior.

---

Risks and mitigation
--------------------

**Risk: policy combinations become a parallel state machine.** Keep policies
small, validate combinations early, and let native ROS 2 lifecycle remain in
control.

**Risk: ordering and rollback conflict.** Define failure behavior before adding
new knobs.

**Mitigation.** Sprint 12 does not add new knobs. It documents the existing
failure behavior: invalid ordering rules stop before hooks run, while runtime
activation failures stop propagation and rely on the existing error-handling
contract instead of reverse replay or compensation actions.

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
- partial activation documentation of the existing error-handling contract
- tests for deterministic ordering

Out of scope:

- public policy API by default
- deferred activation
- auto-configure / auto-activate
- workflow orchestration
- multi-node lifecycle management
- runtime policy changes
- compensation actions

---

Success signal
--------------

- [x] Ordering improves deterministic component lifecycle behavior.
- [x] Policy surface remains smaller than a custom state machine.
- [x] The docs clearly separate internal node ordering from system orchestration.
