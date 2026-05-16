Sprint 17.10 — Documentary Consistency Pass
============================================

**Status.** Completed, awaiting validation.

**Track.** Architecture / Research.

**Type.** Quality Assurance.

**Objective.** Verify terminology consistency across all Sprint 17 documents
and resolve ambiguities before final review.

**Parent sprint.** :doc:`/planning/sprints/active/sprint_17_lifecore_state_rfc`.

Context
-------

Multiple documents use overlapping terminology. Consistency pass ensures:

- No contradictions
- No misleading variations
- Terms used consistently across all surfaces
- Lifecycle/state separation consistent
- Anti-goals reinforced

Document Location
------------------

**File:** ``lifecore_state/rfcs/sprint_17_consistency_review.rst``

Required Content
-----------------

This document reports findings and corrections:

1. **Purpose**
   Audit consistency across 8+ Sprint 17 documents

2. **Scope of review**
   - docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst (updated)
   - lifecore_state/README.rst
   - lifecore_state/rfcs/README.rst
   - lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst
   - lifecore_state/terminology.rst
   - lifecore_state/message_semantics.rst
   - lifecore_state/lifecycle_state_separation.rst
   - lifecore_state/anti_goals.rst
   - lifecore_state/package_boundaries.rst

3. **Terminology audit**

   Check for weak or ambiguous terms:
   - SmartValue (should be: StateSample, StateField, or StateDescriptor by context)
   - Register (should be: Registry)
   - CommManager (should be: StatePublisher, StateSubscriber, StateMirror, StateBridge by context)
   - Manager (should be avoided unless explicitly in anti-patterns)

   Report:
   - Each instance found
   - Intended meaning
   - Correction applied or reason for keeping
   - Document reference

4. **Architectural consistency**

   Verify consistently across all documents:
   - ``lifecore_state/`` always described as logical folder
   - Never as ROS 2 package
   - Never as functional package
   - Never contains ``package.xml`` parent
   - Future three-package split always mentioned
   - ``lifecore_ros2`` independence always maintained
   - ``lifecore_state_core`` always Python-only (no ROS/rclpy)

5. **Message semantic consistency**

   Verify:
   - StateCommand always "not truth"
   - StateUpdate always "observed truth"
   - Descriptor always "field definition"
   - Description always "versioned set of descriptors"
   - Snapshot/delta distinction always clear
   - Sequence/version always explained

6. **Lifecycle/state consistency**

   Verify:
   - StateDescription caching always allowed while inactive
   - StateUpdate delta always not applied while inactive
   - StateCommand always requires active
   - Never contradicted

7. **Anti-pattern consistency**

   Verify:
   - All anti-goals mentioned in RFC are reflected in anti_goals.rst
   - Giant manager never suggested anywhere
   - Magic observable never suggested
   - Auto-register never suggested
   - Codegen-first never suggested

8. **Open question consistency**

   Ensure open questions in RFC match those in message_semantics.rst
   and other documents. No orphaned questions.

9. **Mandatory phrase consistency**

   Verify that every document ends with the mandatory phrase::

       ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.

10. **Problems found and corrections applied**

    For each problem:
    - Problem description
    - Document(s) affected
    - Correction applied or reason for deferring
    - Impact assessment

11. **Remaining inconsistencies**

    If any cannot be resolved:
    - List them
    - Explain why
    - Flag for human review

12. **Recommendations for future review**

    - Which sections need peer review priority
    - Which architectural decisions need formal sign-off
    - Which ambiguities should be resolved before Sprint 18

Acceptance Criteria
-------------------

- [x] All documents checked for terminology consistency
- [x] Weak terms identified and corrected
- [x] No contradictions between documents
- [x] Architectural boundaries consistent
- [x] Message semantics aligned
- [x] Lifecycle/state separation consistent throughout
- [x] All mandatory phrases present
- [x] Report complete with findings and corrections
- [x] Remaining issues documented
- [x] Recommendations clear

Success Criteria
----------------

After this pass, all Sprint 17 documents:

- Use consistent terminology
- Agree on architectural boundaries
- Support each other without contradiction
- Are ready for formal architectural review

Implementation notes
--------------------

Completed in ``lifecore_state/rfcs/sprint_17_consistency_review.rst``. The
review found no weak terminology requiring replacement. Corrections were limited
to mandatory phrase normalization, open-question alignment between the RFC and
message semantics document, and adding the consistency report to the RFC index
and folder layout. No runtime code, tests, examples, ROS interfaces, or package
metadata were added.

Review requirement
------------------

Mandatory phrase:

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
