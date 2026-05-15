Sprint 17.3 — Write Principal Architecture RFC
===============================================

**Track.** Architecture / Research.

**Type.** RFC Design.

**Objective.** Write the principal RFC document that clarifies the future
``lifecore_state`` direction, boundaries, and constraints.

Context
-------

This is the central deliverable of Sprint 17.

``lifecore_state`` is NOT an implementation. It is a clarification of direction
before code.

The RFC must answer: why does ``lifecore_state`` exist, what does it cover, what
does it not cover, and how does it separate from ``lifecore_ros2``?

Constraints
-----------

- No implementation
- No real packages
- No compilable ``.msg`` files
- No executable code
- Non-final sketches only, clearly marked
- Must be complete enough to guide Sprint 18

RFC Document Location
---------------------

**File:** ``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst``

Required Sections
------------------

1. **Title**
   "RFC 001: lifecore_state architecture direction"

2. **Status**
   - Draft
   - Sprint 17
   - Architecture only
   - No implementation commitment

3. **Context**
   - ``lifecore_ros2`` is today an explicit composition framework native to ROS 2 lifecycle
   - It intentionally avoids: hidden state machines, orchestration runtimes, plugin frameworks, ECS runtimes, giant managers, code generation

4. **Problem statement**
   - Typed distributed state
   - Registry-scoped synchronization
   - State projection
   - Snapshot/delta synchronization
   - Quality-aware transport
   - Deterministic identity
   - ROS-native message contracts

5. **Goals**
   - Architecture boundaries
   - Package separation
   - Message semantics
   - Lifecycle/state separation
   - Terminology stabilization
   - Risk reduction for future implementation

6. **Non-goals**
   - Not a robotics operating system
   - Not a global orchestration runtime
   - Not a hidden synchronization framework
   - Not a giant ECS platform
   - Not an EventBus
   - Not codegen-first
   - Not a plugin framework
   - Not a factory/spec system
   - Not a global blackboard runtime

7. **Naming decision**
   - Recommend ``lifecore_state``
   - Explain why ``lifecore_io`` is too narrow
   - List alternatives rejected: ``lifecore_io``, ``lifecore_signals``, ``lifecore_registry``, ``lifecore_datapoints``, ``lifecore_fields``

8. **Repository organization decision**
   - Structure: ``lifecore_state/`` as logical grouping → ``lifecore_state_msgs/``, ``lifecore_state_core/``, ``lifecore_state_ros/``
   - Parent ``lifecore_state/`` has no ``package.xml``
   - During Sprint 17, ``lifecore_state/`` is documentation-only

9. **Future package boundaries**
   - ``lifecore_state_msgs``: ROS 2 ABI only
   - ``lifecore_state_core``: pure Python, no rclpy
   - ``lifecore_state_ros``: rclpy integration

10. **Dependency rules**
    - ``lifecore_ros2`` must not depend on ``lifecore_state``
    - ``lifecore_state_core`` must not depend on ROS 2
    - ``lifecore_state_msgs`` defines message contracts only
    - ``lifecore_state_ros`` may depend on rclpy, core, msgs
    - Optional integration with ``lifecore_ros2`` later only

11. **Conceptual model**
    - StateDescriptor
    - StateDescription
    - StateSample
    - StateUpdate
    - StateCommand
    - StateRegistry
    - StateProjection
    - StateSnapshot
    - StateDelta
    - StateQuality

12. **Descriptor vs description**
    - Descriptor = field definition
    - Description = versioned set of descriptors

13. **State vs command**
    - StateUpdate = observed truth
    - StateCommand = requested mutation
    - Command must not be treated as truth

14. **Snapshot vs delta**
    - Full snapshot = complete state
    - Delta = partial changes
    - Deltas unsafe after missing unknown history unless sequence/schema rules allow

15. **Identity model**
    - ``id``, ``uuid``, ``key`` definitions
    - Deterministic identity and path-derived UUID
    - Risk of identity change on key rename

16. **Quality model**
    - Quality describes value reliability, not business state
    - Example: ``VALID`` + temperature too high

17. **Registry-scoped synchronization**
    - One shared topic
    - Multiple local registries
    - Intersection principle: ``incoming_samples ∩ local_registry = applied_samples``

18. **Lifecycle/state separation**
    - Lifecycle answers: are resources active?
    - State answers: what values are known?
    - Important: activation ≠ valid state, valid state ≠ active

19. **Description subscriber lifecycle behavior**
    - StateDescription subscriber must receive/cache while inactive (transient_local)
    - StateUpdate deltas not applied while inactive
    - StateCommand not handled while inactive

20. **QoS direction**
    - StateDescription: reliable, transient_local, keep_last(1)
    - StateUpdate: volatile, keep_last(1), best_effort or reliable
    - StateCommand: reliable, volatile

21. **Policies**
    - UnknownStatePolicy, MissingStatePolicy, TypeMismatchPolicy, StalePolicy, InactiveMessagePolicy
    - Defaults: unknown=WARN_ONCE, mismatch=REJECT, inactive_desc=CACHE_LATEST, inactive_delta=IGNORE, inactive_cmd=REJECT

22. **Anti-patterns**
    - Giant StateManager
    - Magical ObservableValue
    - Auto publish-on-set
    - Hidden synchronization
    - EventBus for mutations
    - ECS inside lifecycle
    - Codegen-first design
    - Auto-register unknown fields

23. **Future implementation phases**
    - Phase 1: Messages only
    - Phase 2: Pure Python core
    - Phase 3: ROS integration
    - Phase 4: Tools
    - Phase 5: Lifecycle integration

24. **Sprint 18 entry criteria**

25. **Open questions**

26. **Decision summary**

Acceptance Criteria
-------------------

- [ ] RFC document exists and is complete
- [ ] All 26 sections covered
- [ ] No implementation code present
- [ ] No real packages created
- [ ] No compilable messages
- [ ] Lifecycle/state separation is crystal clear
- [ ] Anti-patterns explicitly rejected
- [ ] Pseudo-sketches clearly marked as non-final
- [ ] Document is reviewable by architects and developers
- [ ] Mandatory review phrase included

Success Criteria
----------------

The RFC is the central reference for Sprint 18+ decisions. It enables
peer review and buy-in before implementation starts.
