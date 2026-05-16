Sprint 17.4 — Write Accessible Glossary
========================================

**Status.** Archived.

**Track.** Architecture / Research.

**Type.** Documentation.

**Parent sprint.** :doc:`../active/sprint_17_lifecore_state_rfc`.

**Objective.** Define all terms used in Sprint 17 in clear, pedagogical French
accessible to people without formal CS background.

Context
-------

The glossary enables future developers and architects to understand Sprint 17
concepts without jargon barriers.

Style Guidance
--------------

- Clear French
- Technical but pedagogical
- No academic tone
- Concrete examples tied to ROS 2, robotics, lifecycle, and ``lifecore_state``
- State clearly when terms are ambiguous
- Avoid over-definition

Document Location
-----------------

**File:** ``lifecore_state/terminology.rst``

Required Terminology
--------------------

1. **RFC** – Request For Comments, design document submitted for discussion before implementation
2. **API** – contract used by source code (Python method example)
3. **ABI** – binary/public contract at lower level; ROS 2 ``.msg`` become hard-to-change contracts
4. **ROS 2 package** – directory with ``package.xml``, discoverable by colcon
5. **Python package** – Python module with ``__init__.py``
6. **Repository** – single git repo
7. **Monorepo** – one repository with multiple packages
8. **ROS 2 Workspace** – directory containing ``src/`` for colcon to discover
9. **colcon** – ROS 2 build tool
10. **rclpy** – ROS 2 Python client library
11. **Lifecycle node** – ROS 2 node with lifecycle transitions (configure, activate, deactivate, cleanup, shutdown)
12. **LifecycleComponent** – in ``lifecore_ros2``, a behavior object attached to node lifecycle
13. **Component** – explain multiple meanings: ROS 2 component, lifecore LifecycleComponent, ECS component
14. **ECS** – Entity Component System; explain Entity, Component, System; why not what we want to implement now
15. **ECS Component** – data packet in ECS; do not confuse with LifecycleComponent
16. **Descriptor** – definition of a field
17. **Description** – versioned set of descriptors
18. **State** – known values
19. **StateSample** – one observed value
20. **StateUpdate** – batch of samples
21. **StateCommand** – requested mutation
22. **Snapshot** – full state
23. **Delta** – partial changes
24. **Registry** – collection of known descriptors/fields
25. **Projection** – view of registry filtered by role/authority
26. **Registry-scoped synchronization** – multiple registries apply same topic intersection
27. **Quality** – reliability of value (not business state)
28. **QoS** – reliable, best_effort, volatile, transient_local, keep_last definitions
29. **Schema** – message structure definition
30. **description_version** – schema version marker
31. **sequence** – order marker for detecting loss/duplication
32. **deterministic identity** – identity derived from path or logic, not randomness
33. **path-derived UUID** – UUID computed from stable path/key
34. **source timestamp** – when value observed (hardware)
35. **publish timestamp** – when message sent
36. **stale** – value too old to trust
37. **manager** – explain why term is architecturally dangerous
38. **orchestration** – centralized control of workflows
39. **plugin framework** – dynamic behavior loading
40. **code generation / codegen** – automatic code from declarations

Acceptance Criteria
-------------------

- [x] All 40 required terms defined
- [x] Definitions use clear French, not academic jargon
- [x] Examples tie to ROS 2, robotics, or ``lifecore_state`` context
- [x] Ambiguous terms explicitly flagged as such
- [x] No tutorial tangents
- [x] Focused on Sprint 17 context
- [x] Mandatory review phrase included
- [x] Authority, canonical path, and wire format added to reduce future ambiguity

Content Quality Checklist
-------------------------

For each term:

- [x] Definition is 1–3 sentences
- [x] At least one concrete example
- [x] Confusions with similar terms addressed
- [x] Accessible to non-CS background readers
- [x] Tied to ``lifecore_state`` or lifecycle concepts where applicable

Implementation Notes
--------------------

Completed in ``lifecore_state/terminology.rst``. The glossary keeps Sprint 17
documentation-only scope and does not create any runtime class, package,
message ABI, or public API change.

Success Criteria
----------------

The glossary enables all future developers to read Sprint 17 and 18 documents
without external lookups. It is the single source of truth for project terminology.

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.