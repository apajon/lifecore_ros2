Sprint 17.5 — Write Lifecycle/State Separation
==============================================

**Status.** Active.

**Track.** Architecture / Research.

**Type.** Documentation.

**Parent sprint.** :doc:`sprint_17_lifecore_state_rfc`.

Feature goal
------------

Write ``lifecore_state/lifecycle_state_separation.rst`` so Sprint 17 clearly
separates ROS 2 lifecycle readiness from future
``lifecore_state`` truth, caching, update, and command semantics before any
implementation is proposed.

Lifecycle behavior contract
---------------------------

Sprint 17.5 is documentation-only. It must not change configure, activate,
deactivate, cleanup, shutdown, or error behavior for any existing
``lifecore_ros2`` node or component.

The document must clarify the expected semantic boundary:

- **configure:** subscribers and publishers may be created by future designs,
  but Sprint 17.5 changes no runtime creation path.
- **activate:** activation enables runtime behavior and command handling, but
  Sprint 17.5 changes no activation gate in code.
- **deactivate:** deactivation stops active behavior, but does not by itself
  prove that remote truth, cached description, or registry knowledge vanished.
- **cleanup:** cleanup releases local resources, but does not imply that a
  remote state source was cleared.
- **shutdown:** shutdown semantics remain unchanged.
- **error:** error transition and recovery remain unchanged.

Context
-------

Sprint 17.4 stabilized the glossary so the next document can use terms such as
``StateDescription``, ``StateUpdate``, ``StateCommand``, snapshot, delta,
registry, projection, authority, and quality without redefining them.

The critical design issue is that a transient_local description message may be
received as soon as a subscriber exists, including while a component is still
inactive. A global "ignore everything while inactive" rule is therefore too
blunt for the future state architecture.

Impacted modules
----------------

``lifecore_state/lifecycle_state_separation.rst``
  Primary deliverable for Sprint 17.5.

``docs/planning/sprints/active/``
  Hosts this active planning card and the main Sprint 17 coordinator.

``docs/planning/sprints/sprint_17_substeps/``
  Retains the execution guide used to derive this active card.

``src/``, ``tests/``, and ``examples/``
  Not impacted. Sprint 17.5 must not change runtime behavior, public API,
  examples, or test behavior.

Document location
-----------------

**File:** ``lifecore_state/lifecycle_state_separation.rst``

Required sections
-----------------

1. **Purpose**
   Explain why lifecycle and state truth need different responsibilities.
2. **Definitions**
   Distinguish lifecycle readiness, runtime state, description, update, and
   command.
3. **What lifecycle controls**
   Clarify resource existence, behavior readiness, command handling gates, and
   update application gates.
4. **What lifecore_state controls**
   Clarify known fields, samples, quality, staleness, projection, snapshot,
   delta, identity, and schema version.
5. **Important separation rules**
   Document the non-equivalences between active lifecycle, valid state, cleanup,
   and remote truth.
6. **Callback categories**
   Separate configuration, runtime, command, and diagnostics callbacks.
7. **StateDescription lifecycle behavior**
   Explain why cached description updates may be accepted while inactive.
8. **StateUpdate lifecycle behavior**
   Explain why deltas are not applied while inactive and when snapshots may be
   cached.
9. **StateCommand lifecycle behavior**
   Explain why commands require active lifecycle state.
10. **InactiveMessagePolicy enum**
    Document ``IGNORE``, ``CACHE_LATEST``, ``BUFFER_UNTIL_ACTIVE``, and
    ``REJECT`` together with the recommended defaults per message type.
11. **Recommended pseudo-code**
    Provide non-executable sketches that illustrate semantic gating.
12. **Design decision summary**
    Summarize the boundary in short reviewable statements.

Acceptance criteria
-------------------

- [ ] Lifecycle controls clearly separated from state controls
- [ ] StateDescription caching rule explained
- [ ] StateUpdate delta rule explained
- [ ] StateCommand activation requirement explained
- [ ] Pseudo-code sketches present and marked non-final
- [ ] InactiveMessagePolicy enum documented
- [ ] Defaults recommended for each message type
- [ ] Mandatory review phrase included

Success criteria
----------------

Developers reading this document understand:

- Why global activation gates do not work for all callback categories
- When a callback may fire before active state
- What can remain cached across lifecycle changes
- Why transient_local delivery matters for future design

Review requirement
------------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."