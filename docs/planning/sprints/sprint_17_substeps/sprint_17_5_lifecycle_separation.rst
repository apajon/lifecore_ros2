Sprint 17.5 — Write Lifecycle/State Separation
===============================================

**Track.** Architecture / Research.

**Type.** Documentation.

**Objective.** Clarify the precise separation between ROS 2 lifecycle /
``lifecore_ros2`` and the future ``lifecore_state`` layer.

Context
-------

**Critical design issue:**

A StateDescription subscriber can receive the last transient_local message
as soon as it is created during configure(). If the component ignores all
callbacks while inactive, it may lose the description needed for activation.

This sprint clarifies:

- Why a global "active gate" on all callbacks is too blunt
- Why semantic gating per message type is needed
- Why StateDescription can be received/cached while inactive
- Why StateUpdate deltas must not be applied while inactive
- Why StateCommand only works while active

Document Location
------------------

**File:** ``lifecore_state/lifecycle_state_separation.rst``

Required Sections
------------------

1. **Purpose**
   Explain the need for clear boundaries

2. **Definitions**
   - Lifecycle state = resource/behavior readiness
   - Runtime state = values known/valid
   - Description = schema
   - Update = sample batch
   - Command = requested change

3. **What lifecycle controls**
   - Whether publishers/subscribers/timers exist
   - Whether behavior is active
   - Whether command handling allowed
   - Whether runtime updates applied

4. **What lifecore_state controls**
   - Known fields
   - Latest samples
   - Quality/staleness
   - Projection
   - Snapshot/delta
   - Identity
   - Schema version

5. **Important separation rules**
   - Active lifecycle ≠ valid state
   - Valid state ≠ node active
   - Cleanup ≠ remote truth cleared
   - Deactivate ≠ registry cleared

6. **Callback categories**
   - Configuration callbacks
   - Runtime callbacks
   - Command callbacks
   - Diagnostics callbacks

7. **StateDescription lifecycle behavior** (CRITICAL)
   - Subscriber created in configure
   - Transient_local message may arrive immediately
   - Caching/updating allowed while inactive
   - Must not trigger runtime behavior
   - Activation may require valid cached description

8. **StateUpdate lifecycle behavior**
   - Delta ignored while inactive
   - Full snapshot may cache only if policy allows
   - Updates applied only while active

9. **StateCommand lifecycle behavior**
   - Commands require active state
   - Inactive commands rejected or ignored by policy

10. **InactiveMessagePolicy enum**
    - ``IGNORE`` – discard while inactive
    - ``CACHE_LATEST`` – keep latest, update when received
    - ``BUFFER_UNTIL_ACTIVE`` – queue, apply on activation
    - ``REJECT`` – fail if inactive

    Recommendations:
    - StateDescription: ``CACHE_LATEST``
    - StateUpdate delta: ``IGNORE``
    - StateUpdate snapshot: ``CACHE_LATEST`` (optional)
    - StateCommand: ``REJECT`` or ``IGNORE``

11. **Recommended pseudo-code** (non-executable sketches)

    Example callbacks showing activation gates:

    .. code-block:: python

        # Pseudo-code (non-final sketch)
        def on_description_msg(self, msg):
            # Can cache while inactive
            self._cached_description = msg.description
            if self.is_active:
                self._apply_description(msg.description)

        def on_state_update_msg(self, msg):
            # Ignore delta while inactive
            if msg.update_mode == "DELTA" and not self.is_active:
                return
            if self.is_active:
                self._apply_update(msg)

        def on_command_msg(self, msg):
            # Reject commands while inactive
            if not self.is_active:
                self._log_rejected_command(msg)
                return
            self._handle_command(msg)

12. **Design decision summary**

Acceptance Criteria
-------------------

- [ ] Lifecycle controls clearly separated from state controls
- [ ] StateDescription caching rule explained
- [ ] StateUpdate delta rule explained
- [ ] StateCommand activation requirement explained
- [ ] Pseudo-code sketches present and marked non-final
- [ ] InactiveMessagePolicy enum documented
- [ ] Defaults recommended for each message type
- [ ] Mandatory review phrase included

Success Criteria
----------------

Developers reading this document understand:

- Why global activation gates don't work
- When callbacks can fire
- What state persists across lifecycle changes
- How transient_local delivery affects design
