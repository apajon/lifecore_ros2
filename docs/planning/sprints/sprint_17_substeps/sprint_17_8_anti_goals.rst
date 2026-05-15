Sprint 17.8 — Write Anti-Goals and Anti-Patterns
=================================================

**Track.** Architecture / Research.

**Type.** Documentation.

**Objective.** Explicitly define what ``lifecore_state`` must NOT become, acting
as a defensive guard against architectural scope creep and bad decisions.

Context
-------

The term "state" is broad. Anti-goals protect the project by being explicit
about rejection of certain directions.

This document is direct, almost defensive. It protects against:

- Hidden complexity
- Over-engineering
- Scope creep
- Pattern mistakes from other systems

Document Location
------------------

**File:** ``lifecore_state/anti_goals.rst``

Required Sections
------------------

1. **Purpose**
   Explain why anti-goals matter

2. **Why anti-goals matter**
   - "state" is a broad term → risk of mission creep
   - Anchors architecture to avoid worse alternatives
   - Enables reviewers to reject bad PRs with justification

3. **Not a robotics operating system**
   - No global orchestration
   - No mission planning
   - No replacement for ROS 2 itself
   - No global middleware

4. **Not a global orchestration runtime**
   - No workflows
   - No planning
   - No global decision engine
   - Scope: local, explicit, per-node

5. **Not a hidden synchronization framework**
   All synchronization must be explicit:
   - Topics visible
   - Registries visible
   - Policies visible
   - Versions trackable
   - Sequences detectable

6. **Not a giant ECS platform**
   - ECS ideas may inspire design
   - But NOT an ECS runtime
   - No Entity-wide queries
   - No System scheduling
   - Data-oriented without the framework overhead

7. **Not an EventBus**
   - Events useful later for diagnostics
   - But NOT for every state mutation
   - No publish-on-set
   - No magic observable properties
   - No implicit listeners

8. **Not a plugin framework**
   - No dynamic behavior loading
   - No .so/.dll plugins
   - No plugin registry
   - No convention-over-configuration magic

9. **Not a factory/spec system**
   - No central factories
   - No global spec that creates the app
   - No declarative instantiation
   - Imperative code preferred

10. **Not codegen-first**
    - Codegen useful later
    - But NOT before message/concept stability
    - NOT before human review cycle matures
    - Hand-written code first

11. **No giant StateManager class**
    Explicitly forbidden: a class that does:
    - Registry management
    - Publishers
    - Subscribers
    - Lifecycle
    - Callbacks
    - Stale monitoring
    - Command handling
    - Validation
    - Logging
    - Orchestration

    Instead: separate classes with clear, single responsibilities

12. **No magical StateField**
    Forbidden properties:
    - Automatic publish-on-set
    - Complex callbacks
    - Lifecycle awareness in core
    - Registry awareness in core
    - Descriptor awareness in core
    - Global registry knowledge

13. **No automatic publish-on-set in core**
    Prefer:
    - Explicit set()
    - Mark dirty
    - Flush delta explicitly
    - Keep core and publishing separated

14. **No auto-register unknown fields by default**
    Dangerous because:
    - Breaks API contracts
    - Enables typos
    - Defeats static schemas
    - Creates implicit coupling
    - Makes debugging hard

15. **No command-as-truth**
    - StateCommand is intent, not reality
    - StateUpdate is truth
    - Commands require feedback
    - Accepted command must be visible in later state

16. **No lifecycle contamination**
    - ``lifecore_state_core`` pure Python
    - No rclpy imports
    - No ROS 2 awareness
    - No lifecycle imports
    - Clean separation enables testing

17. **Safe future directions** (not anti-goals, but not now)
    What CAN be explored later:
    - Diagnostics events (but not state mutations)
    - Tools (CLI, visualization)
    - Codegen (after stabilization)
    - Compact messages (optimization, not design)
    - Visualization dashboards
    - Command-line inspection

18. **Decision summary**

Acceptance Criteria
-------------------

- [ ] All major anti-patterns explicitly rejected
- [ ] Rationale for each rejection clear
- [ ] "No giant manager" pattern documented
- [ ] "No magic" principle stated
- [ ] Lifecycle/core separation enforced
- [ ] "Safe future directions" listed
- [ ] Mandatory review phrase included

Content Quality Checklist
-------------------------

- [ ] Anti-goals are specific, not vague
- [ ] Each rejection has justification
- [ ] Patterns are tied to real risks
- [ ] Language is direct but not hostile
- [ ] Document is usable as PR review reference

Success Criteria
----------------

Reviewers can cite this document to:

- Reject architectural overreach
- Require simpler alternatives
- Enforce separation of concerns
- Prevent hidden complexity
