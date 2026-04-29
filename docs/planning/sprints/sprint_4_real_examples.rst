Sprint 4 — Real examples v1
===========================

**Objectif.** Validate that the API works for non-trivial real use cases; reveal API friction early.

**Livrable.** "Examples prove the API is usable and scalable beyond toy scenarios."

---

Why now?
--------

Real examples between error handling (S2) and callback gating refactor (S5) serve a critical purpose:

- **Early validation**: Before refactoring internals, prove the public API works at scale
- **API friction detection**: Real use cases reveal what's awkward or missing
- **Guidance for future sprints**: Examples inform design of Policies (S7), Observability (S8), Parameters (S9)
- **User confidence**: Developers see lifecore is not just theory

**Principle.** Each example must reveal an architectural choice or edge case. If it's too simple, it's a toy.

---

Candidate examples
------------------

All candidates should integrate multiple component types (Pub, Sub, Timer, Service, Client).

io_gateway_node ⭐ (primary target)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose.** I/O gateway: transforms external inputs into processable outputs with async control.

**Topology.**

- 1× ``LifecycleSubscriberComponent`` from ``~/input`` (external data)
- 1× ``LifecyclePublisherComponent`` to ``~/output`` (transformed result)
- 1× ``LifecycleTimerComponent`` for heartbeat (10 Hz, lifecycle-gated)
- 1× ``ServiceComponent`` for ``~/enable`` (runtime control)
- 1× internal stateful component (buffer, transform, error handling)

**Lifecycle teaching.**

- Configure: create ROS resources (sub, pub, service)
- Activate: start timer, begin processing
- Deactivate: flush buffer, stop timer, reject new requests
- Cleanup: destroy all ROS resources

**API friction it reveals.**

- How does a component manage internal state across transitions?
- How does a component coordinate between multiple ROS resources?
- What happens if input subscription arrives during deactivate?
- How does service callback behave if component is inactive?
- Error in timer callback — does it crash the node or isolate?

**Expected size.** 100–150 lines of code + docstring (non-trivial but not huge).

robot_state_monitor ⭐ (secondary)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose.** Health monitor: reads sensor data, tracks state, reports diagnostics.

**Topology.**

- 2–3× ``LifecycleSubscriberComponent`` from sensor topics
- 1× ``LifecyclePublisherComponent`` to ``~/status`` (aggregated health)
- Last-error tracking, state history

**Lifecycle teaching.**

- Partial failure: one sensor fails, others continue (isolation)
- Health state: what does "active" mean when one sub-component is failed?
- Async error recovery: sensor goes offline, comes back online

**API friction.**

- How to compose multiple subscribers into one health model?
- How to expose component state for external queries?
- Integration with ``/diagnostics`` (future, but hint it now)

command_gateway
^^^^^^^^^^^^^^^

**Purpose.** Command validation and dispatch.

**Topology.**

- 1× ``ServiceComponent`` for ``~/execute_command`` (request/response)
- 1× ``ClientComponent`` calling internal service (e.g., robot driver)
- Validation hook on incoming requests

**Lifecycle teaching.**

- Validation hook before processing (API friction: where does validation live?)
- Client request while service is inactive (error handling)
- Async command execution (future: action components)

fanuc_io_bridge_mock
^^^^^^^^^^^^^^^^^^^^

**Purpose.** Mock industrial I/O bridge (without real hardware).

**Topology.**

- Simulated I/O state machine (mock hardware)
- Components that read/write I/O
- Timer that simulates hardware updates

**Lifecycle teaching.**

- Component lifecycle vs external state machine (separation of concerns)
- Simulation support (mock vs real — same API)

minimal_supervised_node
^^^^^^^^^^^^^^^^^^^^^^^

**Purpose.** Multiple components with supervised error recovery.

**Topology.**

- 3 simple components
- Orchestration: one component fails → supervisor decides next step

**Lifecycle teaching.**

- Error propagation (S2 will refine this)
- Partial activation recovery
- Rollback semantics

---

Sprint scope: io_gateway_node
----------------------------

This sprint focuses on **io_gateway_node** as the primary deliverable. Others are sketches.

Implementation
^^^^^^^^^^^^^^

Create ``examples/io_gateway_node.py`` with:

1. **GatewayInputSubscriber** (LifecycleSubscriberComponent)

   - Subscribes to ``~/input``
   - Caches latest message
   - Traces on_message calls

2. **GatewayOutputPublisher** (LifecyclePublisherComponent)

   - Publishes to ``~/output``
   - Gated: only publishes if component active

3. **GatewayHeartbeat** (LifecycleTimerComponent)

   - Timer at 10 Hz
   - Publishes heartbeat on ``~/heartbeat``
   - Only active during ACTIVE state

4. **GatewayService** (ServiceComponent from S1)

   - Service at ``~/enable``
   - Request: empty (just a trigger)
   - Response: status (OK or ERROR)
   - Logic: start/stop processing

5. **GatewayProcessor** (LifecycleComponent)

   - Owns the transformation logic
   - Reads from subscribers (via shared node)
   - Writes to publishers (via shared node)
   - Stateful: buffer, error count, last timestamp

6. **Main node** (LifecycleComponentNode)

   - Registers all 5 components
   - Lifecycle: configure → activate → [spin] → deactivate → cleanup

Module docstring
^^^^^^^^^^^^^^^^

::

   """
   IO Gateway Node — Integration example for lifecore_ros2.

   Demonstrates:
   - Multiple component types (Sub, Pub, Timer, Service, custom)
   - Component coordination (shared access patterns)
   - Activation gating across timer and callbacks
   - Service requests during different lifecycle states
   - Structured logging (see logs for state transitions)

   Usage:
       ros2 run lifecore_ros2 io_gateway_node.py

   Topics:
       /input [std_msgs.msg.Float32] — input data
       /output [std_msgs.msg.Float32] — transformed output
       /heartbeat [std_msgs.msg.Empty] — 10 Hz lifecycle-gated heartbeat

   Services:
       /enable [std_srvs.srv.Empty] — trigger processing

   Lifecycle:
       UNCONFIGURED → INACTIVE → ACTIVE → INACTIVE → UNCONFIGURED

   Expected logs:
       - Component configure: subscriber created, publisher ready, timer ready, service registered
       - Node activate: all components activated, heartbeat starts
       - Service call while inactive: rejected with logged reason
       - Node deactivate: heartbeat stops, subscriptions keep working (data dropped if inactive)
       - Node cleanup: all ROS resources destroyed
   """

---

Tests for io_gateway_node
--------------------------

Unit tests
^^^^^^^^^^

- [x] Each component (Sub, Pub, Timer, Service) individually in isolation
- [x] Lifecycle transitions: configure → activate → deactivate → cleanup
- [x] Component gating: timer only ticks if active, service rejects if inactive

Integration tests
^^^^^^^^^^^^^^^^^

- [x] All 5 components together in same node
- [x] Service call while active → success
- [x] Service call while inactive → failure (gated)
- [x] Input message arrives, output is published (nominal flow)
- [x] Input arrives during deactivate → dropped (not processed)
- [x] Heartbeat timer ticks during active, stops during inactive

Edge cases
^^^^^^^^^^

- [x] Service call during transition (should block or return error consistently)
- [x] Error in subscriber callback → node state stable
- [x] Error in timer callback → node state stable
- [x] Rapid activate/deactivate cycles → no crashes

---

Risks and mitigation
--------------------

**Risk 1: Example is still too simple**

- **Problem**: Doesn't force any real architectural decisions.
- **Mitigation**:
  - io_gateway_node has 5 components + state coordination → complex enough
  - Coordinates Pub, Sub, Timer, Service (all types)
  - Tests edge cases (gating, errors, transitions)

**Risk 2: Example drives future sprints wrongly**

- **Problem**: Example assumes a feature that S5–S10 will change.
- **Mitigation**:
  - Example uses only shipped functionality (Pub, Sub, Timer from core; Service from S1)
  - No assumption of future features (policies, parameters, factory)
  - Refactor example if API changes (treat as regression test)

**Risk 3: Example is unmaintainable**

- **Problem**: 150 lines of custom logic is hard to follow.
- **Mitigation**:
  - Each component is ~ 20–30 lines (focused responsibility)
  - Docstrings explain lifecycle transitions
  - Logs are comprehensive (debugging aid)
  - Test coverage is high (each path verified)

**Risk 4: Example doesn't run**

- **Problem**: Missing imports, ROS2 not set up, etc.
- **Mitigation**:
  - Smoke test in CI: import the module, no exceptions
  - Manual test: run with ``ros2 run`` (developer responsibility)
  - Clear README.md with setup instructions

---

Dependencies
------------

- Requires: ``LifecycleComponent``, ``LifecycleComponentNode``, ``LifecyclePublisherComponent``, ``LifecycleSubscriberComponent``, ``LifecycleTimerComponent`` (shipped)
- Requires: ``ServiceComponent`` from S1 (must be completed first)
- Requires: Error handling from S2 (for robust error propagation)
- Requires: Testing utilities from S3 (for test fixtures)

---

Scope boundaries
----------------

**In-scope:**

- Primary example: ``io_gateway_node.py`` (100–150 lines)
- Tests for io_gateway_node (unit + integration)
- Docstrings and inline comments explaining lifecycle
- Structured logging showing state transitions
- Setup and run instructions in ``examples/io_gateway_node.py`` docstring

**Out-of-scope:**

- Other example files (robot_state_monitor, etc. — for future sprints)
- Launch files (application responsibility, not framework)
- ROS 2 graph setup (manual or user's launch file)
- Performance testing
- Real hardware integration

---

Success signal
--------------

- [x] ``examples/io_gateway_node.py`` runs without errors (smoke test)
- [x] All 5 components are used together (Pub, Sub, Timer, Service, custom)
- [x] Lifecycle transitions work (configure → activate → deactivate → cleanup)
- [x] Service gating is enforced (inactive → rejected)
- [x] Timer gating is enforced (inactive → no ticks)
- [x] Input/output flow is correct (messages transform and publish)
- [x] Error handling is robust (callback errors don't crash node)
- [x] All tests pass (unit + integration)
- [x] Docstring is comprehensive (explains teaching goals + usage)
- [x] Logs are clear (state transitions visible)
- [x] Ruff, Pyright, Pytest all green
- [x] Example is added to ``docs/examples.rst`` with explanation

---

API friction detection checklist
--------------------------------

As io_gateway_node is implemented, watch for:

- [ ] Is it hard to coordinate multiple publishers/subscribers in one component?
- [ ] Do lifecycle transitions feel natural or verbose?
- [ ] Is activation gating obvious, or do callbacks need extra checks?
- [ ] Are error messages clear when something fails?
- [ ] Is it hard to debug state transitions (need better logging)?
- [ ] Is there friction in the Service component API?
- [ ] Do we need helpers for common patterns (e.g., "process one input per activate")?

**Action.** If any friction detected, file a GitHub issue or design note for future sprints.

---

Location
--------

- Example: ``examples/io_gateway_node.py`` (150 lines including docstring)
- Tests: ``tests/test_examples_io_gateway.py`` (new, comprehensive)
- Docs: Update ``docs/examples.rst`` to link and explain

---

Sequencing
----------

This sprint **must execute after S1, S2, S3** are complete:

- S1 (Service/Client) → ServiceComponent available
- S2 (Error handling) → robust error propagation
- S3 (Testing utilities) → easy test setup

Once S4 is done, proceed to S5 (Callback gating) and beyond with API confidence.

---

Expected API friction to guide future sprints
----------------------------------------------

This example likely reveals:

1. **Callback gating**: Timer and Service both need to know "am I active?" — S5 refactor makes this clear
2. **Observability**: Need to see state transitions and errors — S8 adds logging
3. **Callback groups**: Processing sub + timer might need independent threads — S6 adds helpers
4. **Parameters**: Gateway behavior (e.g., output topic, heartbeat rate) should be configurable — S9
5. **Policies**: When should gateway auto-start? Manual or declarative? — S7 answer
6. **Factory**: Templating multiple gateway nodes with different configs — S10 answer

Each friction discovered informs the next sprint's design.
