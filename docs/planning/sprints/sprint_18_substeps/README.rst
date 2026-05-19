Sprint 18 Sub-sprints Overview
==============================

This folder is the execution plan for Sprint 18. The sprint creates only the
``lifecore_state_msgs`` ROS 2 interface package and the review documents needed
to control that ABI prototype.

Sprint 18 is organized into 13 focused sub-sprints. The lock for every step is:
**messages only**. Do not create ``lifecore_state_core``,
``lifecore_state_ros``, registries, publishers, subscribers, lifecycle
integration, CLI tools, code generation, or runtime behavior.

**Current sub-sprint.** :doc:`../active/sprint_18_1_preflight_check` is active.

.. toctree::
   :maxdepth: 1
   :hidden:

   ../active/sprint_18_1_preflight_check
   sprint_18_2_package_scaffold
   sprint_18_3_state_descriptor
   sprint_18_4_state_description
   sprint_18_5_state_sample
   sprint_18_6_state_update
   sprint_18_7_state_command
   sprint_18_8_constants_decision
   sprint_18_9_build_validation
   sprint_18_10_docs_consistency
   sprint_18_11_main_sprint_file
   sprint_18_12_pr_description
   sprint_18_13_final_review

Execution Order
---------------

1. :doc:`../active/sprint_18_1_preflight_check` — active.

   Run the Sprint 18 pre-flight check only. Confirm that the repository still
   matches the Sprint 17 closure assumptions before creating
   ``lifecore_state_msgs``.

2. :doc:`sprint_18_2_package_scaffold`

   Create only ``lifecore_state/lifecore_state_msgs/`` with ``package.xml``,
   ``CMakeLists.txt``, and ``msg/``. Keep the parent ``lifecore_state/`` as a
   logical folder with no package metadata.

3. :doc:`sprint_18_3_state_descriptor`

   Define ``StateDescriptor.msg`` as one state field contract. It describes
   identity, type, direction, metadata, constraints, and flags. It carries no
   current runtime value.

4. :doc:`sprint_18_4_state_description`

   Define ``StateDescription.msg`` as a versioned collection of
   ``StateDescriptor`` entries with ``schema_uuid`` and ``description_version``.

5. :doc:`sprint_18_5_state_sample`

   Define ``StateSample.msg`` as one observed state value at a source timestamp
   with type, quality, source, and explicit variant value fields.

6. :doc:`sprint_18_6_state_update`

   Define ``StateUpdate.msg`` as a batch of observed truth with source/schema
   identity, sequence, description version, update mode, and samples.

7. :doc:`sprint_18_7_state_command`

   Define ``StateCommand.msg`` as a single-target requested mutation. It
   expresses intent, not observed truth. Batched commands remain deferred.

8. :doc:`sprint_18_8_constants_decision`

   Decide whether Sprint 18 keeps constants embedded in primary messages or
   extracts enum-like messages. Default recommendation: embedded constants.

9. :doc:`sprint_18_9_build_validation`

   Validate package discovery and message generation with ``colcon`` when the
   environment supports it. Document exact limitations otherwise.

10. :doc:`sprint_18_10_docs_consistency`

    Review ``lifecore_state`` documents and Sprint planning docs for consistency
    with the final message package shape.

11. :doc:`sprint_18_11_main_sprint_file`

    Keep the active Sprint 18 planning file synchronized with accepted Sprint
    17 decisions, Sprint 18 deliverables, and acceptance criteria.

12. :doc:`sprint_18_12_pr_description`

    Prepare a PR description that highlights message contracts, key decisions,
    non-goals, validation, and review focus.

13. :doc:`sprint_18_13_final_review`

    Perform the final Sprint 18 review across structure, build, message
    semantics, field-level ABI, scope control, documentation, risks, and Sprint
    19 readiness.

Parallelization Guidance
------------------------

- Sprint 18.1 must happen first.
- Sprint 18.2 must precede any final ``.msg`` content.
- Sprint 18.3 through 18.7 should be reviewed in message dependency order.
- Sprint 18.8 should happen after the first message draft shows the real
  constant duplication.
- Sprint 18.9 through 18.13 are sequential validation and review gates.

Success Criteria
----------------

- [ ] All 13 sub-sprints have clear deliverables.
- [ ] ``lifecore_state_msgs`` builds and generates messages.
- [ ] ``lifecore_state/`` parent remains non-package.
- [ ] No runtime Python code is added.
- [ ] No ``lifecore_state_core`` or ``lifecore_state_ros`` package is created.
- [ ] Message semantics match Sprint 17.
- [ ] Documentation is consistent after implementation.
- [ ] PR description and final review are ready for external review.

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
