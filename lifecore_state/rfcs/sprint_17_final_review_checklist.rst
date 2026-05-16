Sprint 17.11 - Final Review Checklist
======================================

Status
------

Ready for reviewer use.

Purpose
-------

This checklist gives a final reviewer a compact way to verify Sprint 17
completeness before sign-off. It covers repository structure, scope control,
naming, package boundaries, message semantics, lifecycle/state separation,
anti-patterns, documentation quality, Sprint 18 readiness, mandatory phrases,
and build integrity.

Repository Structure Checklist
------------------------------

- [ ] ``lifecore_state/`` exists at the repository root.
- [ ] ``lifecore_state/`` has no parent-level ``package.xml``.
- [ ] No build metadata was added to ``lifecore_state/``.
- [ ] No ``.cmake`` files were added to ``lifecore_state/``.
- [ ] No ``setup.py`` was added to ``lifecore_state/``.
- [ ] No ``pyproject.toml`` was added to ``lifecore_state/``.
- [ ] ``lifecore_state/README.rst`` exists.
- [ ] ``lifecore_state/rfcs/README.rst`` exists.
- [ ] ``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst`` exists.
- [ ] ``lifecore_state/terminology.rst`` exists.
- [ ] ``lifecore_state/message_semantics.rst`` exists.
- [ ] ``lifecore_state/lifecycle_state_separation.rst`` exists.
- [ ] ``lifecore_state/anti_goals.rst`` exists.
- [ ] ``lifecore_state/package_boundaries.rst`` exists.
- [ ] No runtime code was added under ``lifecore_state/``.

Scope Checklist
---------------

- [ ] No registry implementation was added.
- [ ] No publishers or subscribers were implemented.
- [ ] No ROS messages were compiled or introduced as final ABI.
- [ ] No orchestration runtime was added.
- [ ] No ECS runtime was added.
- [ ] No EventBus was added.
- [ ] No code generation tool was added.
- [ ] No plugin framework was added.
- [ ] No factory system was added.
- [ ] ``src/``, ``tests/``, and ``examples/`` remain unchanged by Sprint 17.11.

Naming Checklist
----------------

- [ ] ``lifecore_state`` is chosen and justified in RFC 001.
- [ ] Rejected alternatives, including ``lifecore_io``, are documented.
- [ ] ``StateDescriptor`` is used consistently.
- [ ] ``StateDescription`` is used consistently.
- [ ] ``StateSample`` is used consistently.
- [ ] ``StateUpdate`` is used consistently.
- [ ] ``StateCommand`` is used consistently.
- [ ] ``manager`` terminology is avoided except in anti-pattern contexts.
- [ ] ``SmartValue`` is not used as accepted terminology.
- [ ] ``CommManager`` is not used.
- [ ] Vague registry or manager names are not introduced as accepted design.

Package Boundary Checklist
--------------------------

- [ ] ``lifecore_state_msgs`` is documented as the future ROS 2 ABI package.
- [ ] ``lifecore_state_core`` is documented as pure Python semantics.
- [ ] ``lifecore_state_ros`` is documented as the ROS 2 integration layer.
- [ ] Dependency rules are documented.
- [ ] No circular dependency direction is implied.
- [ ] ``lifecore_ros2`` independence is documented.
- [ ] Future extraction remains viable because Sprint 17 adds no runtime package.

Message Semantics Checklist
---------------------------

- [ ] Descriptor versus description is clarified.
- [ ] Sample versus update is clarified.
- [ ] Command versus observed truth is clarified.
- [ ] Snapshot versus delta is clarified.
- [ ] ``sequence`` is documented as ordering and continuity metadata.
- [ ] ``description_version`` is documented as schema compatibility metadata.
- [ ] Quality values describe value reliability, not business state.
- [ ] Source and publish timestamps are explained separately.
- [ ] QoS recommendations are provided as direction, not final ABI.
- [ ] Pseudo-sketches are marked as non-final.

Lifecycle/State Checklist
-------------------------

- [ ] Lifecycle active state is not documented as proof of state validity.
- [ ] Valid state is not documented as proof of active lifecycle state.
- [ ] ``StateDescription`` may be cached while inactive.
- [ ] ``StateUpdate`` deltas are not applied while inactive.
- [ ] ``StateCommand`` handling requires active lifecycle readiness.
- [ ] ``InactiveMessagePolicy`` is explained.
- [ ] Semantic gating by message type is documented.
- [ ] No global gate for every message type is implied.
- [ ] ``transient_local`` implications are explained.

Anti-Pattern Checklist
----------------------

- [ ] Giant manager architecture is rejected.
- [ ] Magical observable value architecture is rejected.
- [ ] Automatic publish-on-set in core is rejected.
- [ ] Auto-registering unknown fields by default is rejected.
- [ ] Codegen-first design is rejected.
- [ ] ECS runtime design is rejected.
- [ ] Hidden synchronization framework is rejected.
- [ ] Plugin framework design is rejected.
- [ ] Each rejected direction has a concrete justification.

Documentation Quality Checklist
-------------------------------

- [ ] All documents use clear French.
- [ ] Documents are accessible to a robotics or ROS 2 reviewer.
- [ ] The glossary provides at least 40 terms.
- [ ] Pseudo-code sketches are clear and marked as non-final.
- [ ] Examples are tied to ROS 2 or robotics context.
- [ ] Documents avoid unnecessary implementation detail.
- [ ] RFC 001 is reviewable by architects.
- [ ] Open questions are listed explicitly.
- [ ] Future directions are clarified without becoming commitments.

Sprint 18 Readiness Checklist
-----------------------------

- [ ] Entry criteria for Sprint 18 are documented.
- [ ] Open questions are documented.
- [ ] Implementation is intentionally deferred.
- [ ] Message ABI prototype work can be considered next.
- [ ] Pure Python semantics remain deferred unless explicitly approved.
- [ ] No premature optimization is introduced.
- [ ] Risks are identified and documented.

Mandatory Review Phrase Checklist
---------------------------------

- [ ] ``docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst`` ends
  with the mandatory phrase.
- [ ] ``docs/planning/sprints/sprint_17_repository_audit.rst`` ends with the
  mandatory phrase.
- [ ] ``lifecore_state/README.rst`` ends with the mandatory phrase.
- [ ] ``lifecore_state/rfcs/README.rst`` ends with the mandatory phrase.
- [ ] ``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst`` ends with
  the mandatory phrase.
- [ ] ``lifecore_state/terminology.rst`` ends with the mandatory phrase.
- [ ] ``lifecore_state/message_semantics.rst`` ends with the mandatory phrase.
- [ ] ``lifecore_state/lifecycle_state_separation.rst`` ends with the mandatory
  phrase.
- [ ] ``lifecore_state/anti_goals.rst`` ends with the mandatory phrase.
- [ ] ``lifecore_state/package_boundaries.rst`` ends with the mandatory phrase.
- [ ] ``lifecore_state/rfcs/sprint_17_consistency_review.rst`` ends with the
  mandatory phrase.
- [ ] ``lifecore_state/rfcs/sprint_17_final_review_checklist.rst`` ends with the
  mandatory phrase.

Build Integrity Checklist
-------------------------

- [ ] No compilation errors are introduced.
- [ ] No new build files are introduced.
- [ ] Sphinx build succeeds if documentation validation is run.
- [ ] RST syntax is valid.
- [ ] Internal links resolve.
- [ ] Generated documentation output is not treated as source deliverable.

Reviewer Notes
--------------

.. code-block:: text

    Reviewer Name: _______________
    Review Date: _______________

    General notes:


    Concerns:


    Approved: [ ] Yes [ ] No

    Sign-off:

Acceptance Criteria
-------------------

- [ ] Checklist is complete.
- [ ] All required sections are present.
- [ ] No blocker is found during final review.
- [ ] All mandatory phrases are present.
- [ ] Reviewer can sign off from this file.

Content Quality Checklist
-------------------------

- [ ] Checklist items are specific.
- [ ] Checklist covers all Sprint 17 review areas.
- [ ] Checklist stays concise enough to complete in less than one hour.
- [ ] Checklist can be automated later if Sprint 17.12 needs it.

Success Criteria
----------------

A reviewer using this checklist can verify Sprint 17 completeness in less than
one hour, find any missing deliverable, confirm the architectural decisions, and
sign off with confidence.

Mandatory phrase
----------------

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.