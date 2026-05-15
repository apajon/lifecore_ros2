Sprint 17.6 — Write Package Boundaries
======================================

**Track.** Architecture / Research.

**Type.** Documentation.

**Objective.** Define future package separation for ``lifecore_state`` clearly,
with precise dependency rules and responsibility boundaries.

Context
-------

Decision: ``lifecore_state/`` is a logical folder at repository level, NOT a
ROS 2 package.

Future structure: ``lifecore_state/`` may contain three separate packages:

- ``lifecore_state_msgs`` (ROS 2 ABI)
- ``lifecore_state_core`` (pure Python)
- ``lifecore_state_ros`` (ROS 2 integration)

Each must have clear, non-circular responsibilities and dependencies.

Document Location
------------------

**File:** ``lifecore_state/package_boundaries.rst``

Required Sections
------------------

1. **Purpose**
   Clarify future package split

2. **Repository-level grouping**
   - ``lifecore_state/`` is a logical folder
   - No ``package.xml`` in parent
   - Not discovered by colcon as package
   - Can be extracted later as separate repo

3. **Future package: lifecore_state_msgs**

   Responsibilities:
   - ``.msg`` definitions only
   - ROS 2 public message contracts
   - Stable ABI
   - No Python runtime logic
   - No registry behavior
   - No lifecycle behavior

   Dependencies:
   - std_msgs (for Header, if needed)
   - No Python libraries except ROS message generation

4. **Future package: lifecore_state_core**

   Responsibilities:
   - Pure Python
   - Descriptor model
   - Sample model
   - Registry
   - Projection
   - Identity
   - Quality
   - Policies
   - Snapshot/delta logic
   - Testable without ROS

   Dependencies:
   - Python 3.12+
   - No rclpy
   - No ROS 2
   - Standard library only recommended
   - Optional small dependencies if justified

5. **Future package: lifecore_state_ros**

   Responsibilities:
   - rclpy integration
   - QoS profiles
   - DescriptionPublisher
   - DescriptionSubscriber
   - StatePublisher
   - StateSubscriber
   - CommandSubscriber
   - StateMirror
   - Optional integration with ``lifecore_ros2`` LifecycleComponent

   Dependencies:
   - rclpy (required)
   - ``lifecore_state_msgs`` (required)
   - ``lifecore_state_core`` (required)
   - Optional: ``lifecore_ros2`` for component integration

6. **Existing package: lifecore_ros2**

   No change. Remains:
   - Lifecycle-native composition
   - Explicit component model
   - No ownership of ``lifecore_state`` concepts

   May optionally consume ``lifecore_state_ros`` later for stateful components

7. **Mandatory dependency rules**

   These must never be broken:

   - ``lifecore_ros2`` must NOT depend on ``lifecore_state_*``
   - ``lifecore_state_core`` must NOT depend on ROS 2 or rclpy
   - ``lifecore_state_msgs`` must NOT depend on ``lifecore_state_core``
   - ``lifecore_state_msgs`` must NOT contain registry logic
   - ``lifecore_state_ros`` may depend on ``lifecore_state_msgs`` and ``lifecore_state_core``
   - Optional lifecycle integration must remain thin and non-invasive

8. **Forbidden dependencies**

   Explicitly forbidden:

   - No circular dependencies
   - No registry logic inside messages
   - No lifecycle logic inside core
   - No message definitions inside core
   - No giant parent ``lifecore_state`` package
   - No implicit state sharing across packages

9. **Future extraction path**

   Describe how ``lifecore_state/`` could become separate repo:

   - Clone folder to new repo
   - Each subfolder becomes independent package
   - No monorepo tooling required
   - ROS 2 workspaces can mix repos

10. **Decision summary**

Acceptance Criteria
-------------------

- [ ] Future package roles clearly documented
- [ ] Dependency rules explicit and mandatory
- [ ] No circular dependencies possible
- [ ] ``lifecore_state/`` confirmed as logical grouping
- [ ] ``lifecore_ros2`` independence documented
- [ ] ``lifecore_state_core`` Python-only documented
- [ ] Extraction path viable
- [ ] Mandatory review phrase included

Content Validation Checklist
-----------------------------

- [ ] Each package has clear, non-overlapping responsibility
- [ ] Dependency direction is acyclic
- [ ] ``lifecore_ros2`` needs not change
- [ ] Future packages can be developed independently
- [ ] ABI boundaries are explicit
- [ ] Python boundaries are explicit

Success Criteria
----------------

A future developer reading this document can:

- Explain why three packages exist
- Implement each without depending on each other (except as documented)
- Avoid architectural mistakes (circular deps, cross-contamination)
- Extract to separate repos if needed
