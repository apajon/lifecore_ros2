Sprint 17.9 — Update Main Sprint 17 File
========================================

**Track.** Architecture / Research.

**Type.** Documentation Update.

**Objective.** Transform the main Sprint 17 file into a clear, actionable
architecture plan that coordinates all sub-sprints.

Context
-------

The main Sprint 17 file currently exists with basic skeleton. This sub-sprint
updates it to:

- Reflect full RFC scope
- List all deliverables clearly
- Document acceptance criteria
- Establish review checklist

Document Location
------------------

**File:** ``docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst``

This file replaces or extends the current Sprint 17 definition.

Required Content
-----------------

1. **Sprint title**
   "Sprint 17: lifecore_state architecture and RFC"

2. **Sprint metadata**
   - Track: Architecture / RFC / no implementation
   - Branch: ``sprint/17-lifecore-state-rfc``
   - Priority: P2 - separate future architecture
   - Type: Documentation + Architecture (no code)

3. **Context section**
   Summarize:
   - ``lifecore_ros2`` is today an explicit lifecycle-native framework
   - ``lifecore_state`` is a future direction
   - Purpose: clarify before implementation
   - No implementation in this sprint

4. **Goals section**
   - Architecture boundaries clear
   - Terminology stable
   - Package separation planned
   - Message semantics defined
   - Lifecycle/state separation clear
   - Anti-goals documented
   - Future constraints understood

5. **Non-goals section**
   - No implementation
   - No packages created
   - No messages compiled
   - No EventBus
   - No ECS runtime
   - No codegen
   - No orchestration
   - No giant manager

6. **Deliverables section**
   List:
   - 17.1: repository audit
   - 17.2: documentation structure
   - 17.3: RFC 001
   - 17.4: terminology glossary
   - 17.5: lifecycle/state separation
   - 17.6: package boundaries
   - 17.7: message semantics
   - 17.8: anti-goals
   - 17.9: main sprint coordination (this file)
   - 17.10: consistency review
   - 17.11: final checklist
   - 17.12: static checks
   - 17.13: PR description draft

7. **Explicit decisions to capture**
   - Name: ``lifecore_state`` chosen
   - Repo organization: logical folder, no package.xml
   - Future packages: msgs/core/ros
   - StateDescription: can be cached while inactive
   - StateUpdate delta: not applied while inactive
   - StateCommand: active only
   - Command: not truth
   - Quality: describes reliability, not business state
   - Snapshot/delta distinction clear
   - Descriptor/description distinction clear

8. **Acceptance criteria**

   - [ ] ``lifecore_state/`` exists as logical group
   - [ ] No ``package.xml`` in parent
   - [ ] No runtime code added
   - [ ] ``lifecore_ros2`` unchanged behaviorally
   - [ ] Package dependency rules documented
   - [ ] Lifecycle/state separation documented
   - [ ] StateDescription inactive caching documented
   - [ ] Sprint 18 entry criteria documented
   - [ ] All sub-sprint deliverables exist
   - [ ] All documents include mandatory review phrase

9. **Out of scope**
   Reiterate what is NOT done:
   - No package creation
   - No message compilation
   - No Python runtime
   - No orchestration framework
   - No ECS system
   - No codegen tools
   - No build changes

10. **Sprint 18 candidate scope**
    Propose (but do not commit):
    - Message ABI prototype only
    - Maybe pure Python sketch later
    - No ROS integration until reviewed

11. **Review checklist**
    Include a checklist for reviewers to verify:
    - [ ] Repository audit exists and is accurate
    - [ ] RFC is complete and reviewable
    - [ ] Glossary is accessible
    - [ ] Package boundaries are clear
    - [ ] Message semantics are consistent
    - [ ] Lifecycle/state separation is sound
    - [ ] Anti-patterns are rejected
    - [ ] No implementation present
    - [ ] ``lifecore_ros2`` independence maintained
    - [ ] All mandatory phrases present

Acceptance Criteria
-------------------

- [ ] Main Sprint 17 file updated to coordinate all sub-sprints
- [ ] All deliverables listed
- [ ] Acceptance criteria clear and verifiable
- [ ] Review checklist present
- [ ] No code changes in any file
- [ ] Mandatory review phrase included

Success Criteria
----------------

The main Sprint 17 file becomes the source of truth for:

- Sprint 17 scope
- Coordination of 13 sub-sprints
- Acceptance verification
- Ready-to-review sign-off
