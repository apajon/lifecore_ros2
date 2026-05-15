Sprint 17 Sub-sprints Overview
==============================

**Note:** This folder is an execution plan for the coding agent. The expected
final deliverables are the Sprint 17 architecture documents under
``docs/planning/sprints/active/`` and ``lifecore_state/``. The
``sprint_17_substeps/`` folder itself is not necessarily committed to the
repository; it serves as a working guide for the systematic execution of
Sprint 17.
------------------------------

Sprint 17 is organized into 13 focused sub-sprints, each producing clear,
reviewable deliverables. **No implementation. Architecture and RFC only.**

Execution Order (Recommended)
------------------------------

Follow this sequence to build coherence:

1. **17.1: Repository Audit** — validated and archived.

   Archived planning card:
   ``docs/planning/sprints/archived/sprint_17_1_repository_audit.rst``

   Deliverable: ``docs/planning/sprints/sprint_17_repository_audit.rst``

   Audit current structure, identify risks, recommend placement for
   ``lifecore_state`` documentation.

   Output: Audit document with review notes.

2. **17.2: Create Documentation Structure** — archived after validation.

   Archived planning card:
   ``docs/planning/sprints/archived/sprint_17_2_documentation_structure.rst``

   Deliverable: ``lifecore_state/`` folder with skeleton files

   Set up folder structure, create skeleton RST files, ensure no ``package.xml``
   in parent. This is the home for all subsequent documentation.

   Output: Folder structure ready for content.

3. **17.3: Write Principal RFC** — promoted to active.

   Active planning card:
   ``docs/planning/sprints/active/sprint_17_3_rfc.rst``

   Deliverable: ``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst``

   This is the central document. Defines why ``lifecore_state`` exists,
   what it covers, boundaries, package split, message semantics, lifecycle/state
   separation, and anti-patterns. 26 mandatory sections.

   Output: Complete RFC 001.

4. **17.4: Write Accessible Glossary**

   Deliverable: ``lifecore_state/terminology.rst``

   Define 40+ terms in clear, pedagogical French accessible to people without
   formal CS background. Tie to ROS 2, robotics, lifecycle context.

   Output: Comprehensive glossary.

5. **17.5: Write Lifecycle/State Separation**

   Deliverable: ``lifecore_state/lifecycle_state_separation.rst``

   **Critical design issue:** Clarify why StateDescription can be cached while
   inactive, why deltas are not applied while inactive, why commands require
   active. Explain semantic gating (per-message-type) vs global gate.
   Include pseudo-code sketches.

   Output: Lifecycle/state design clarity.

6. **17.6: Write Package Boundaries**

   Deliverable: ``lifecore_state/package_boundaries.rst``

   Define three future packages (msgs, core, ros), their responsibilities,
   mandatory dependency rules, and forbidden patterns.

   Output: Clear package separation strategy.

7. **17.7: Write Message Semantics**

   Deliverable: ``lifecore_state/message_semantics.rst``

   Document five core message types (Descriptor, Description, Sample, Update,
   Command). Include design principles, field semantics, QoS recommendations,
   and non-final pseudo-sketches.

   Output: Message design blueprint.

8. **17.8: Write Anti-Goals**

   Deliverable: ``lifecore_state/anti_goals.rst``

   Explicitly reject bad architectural directions: no giant manager, no magic,
   no auto-register, no ECS runtime, no codegen-first, etc.
   Protect against scope creep and bad patterns.

   Output: Architectural guard rails.

9. **17.9: Update Main Sprint 17 File**

   Deliverable: Updated ``docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst``

   Transform main sprint file into a coordinator that:
   - Lists all deliverables
   - Documents acceptance criteria
   - Provides review checklist
   - Integrates sub-sprints

   Output: Main sprint file as coordination hub.

10. **17.10: Consistency Review Pass**

    Deliverable: ``lifecore_state/rfcs/sprint_17_consistency_review.rst``

    Audit all documents for:
    - Terminology consistency
    - Architectural alignment
    - No contradictions
    - Message semantics agreement
    - Lifecycle/state agreement
    - All mandatory phrases present

    Output: Consistency report with corrections applied.

11. **17.11: Final Review Checklist**

    Deliverable: ``lifecore_state/rfcs/sprint_17_final_review_checklist.rst``

    Create concise checklist for reviewers to verify Sprint 17 completeness.
    Enables rapid sign-off. Covers structure, scope, naming, packages, messages,
    lifecycle, anti-patterns, documentation, Sprint 18 readiness.

    Output: Reviewer-friendly checklist.

12. **17.12: Static Verification**

    Deliverable: ``lifecore_state/rfcs/sprint_17_static_check.rst``

    Lightweight automated checks:
    - File/folder existence
    - Forbidden files absent (no package.xml, .msg, CMakeLists.txt)
    - Weak terminology absent
    - Mandatory phrases present
    - Build integrity

    Output: Verification report.

13. **17.13: PR Description Draft**

    Deliverable: ``lifecore_state/rfcs/sprint_17_pr_description.md``

    Draft PR summary for GitHub:
    - What changed (architecture, documentation)
    - What did not change (no implementation)
    - Key decisions
    - Review focus areas
    - Acceptance checklist

    Output: Ready-to-use PR description.

Total Estimated Effort
-----------------------

The scope of Sprint 17 is comprehensive but deliberately documentation-focused,
with no implementation.

Parallelization Opportunity
----------------------------

Some tasks can overlap:

- 17.4 (glossary) can start after 17.2 (structure) is ready
- 17.6 (packages) can start after 17.2 (structure) is ready
- 17.7 (messages) can start after 17.3 (RFC) sketches exist
- 17.10 (consistency) should wait until 17.1–17.8 drafts are mostly done
- 17.11–17.13 should be sequential (depend on earlier work)

Key Principles
--------------

1. **No implementation.** Architecture and RFC only.

2. **Documentation-first.** Every decision produces a written document.

3. **Consistency.** Later sprints build on earlier ones. Cross-reference always.

4. **Reviewability.** Each document must be independently reviewable.

5. **Clarity.** Write for developers who are not specialists in this domain.

6. **Actionable.** Each deliverable should guide Sprint 18+ decisions.

7. **Defensive.** Anti-goals protect against bad architectural directions.

Mandatory Phrase in Key Documents
----------------------------------

The phrase "ChatGPT ou Codex relira et contrôlera les livrables avant validation
finale du Sprint 17" must appear in:

- The main Sprint 17 file (``docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst``)
- The final review checklist (``sprint_17_11_checklist.rst``)
- The PR description draft (``sprint_17_13_pr_description.rst``)

Architecture documents (terminology, message semantics, package boundaries,
lifecycle/state separation, anti-goals) remain clean and reusable without this
phrase.

Integration with Main Sprint
----------------------------

Sub-sprints 17.4–17.13 remain **separate files** in the
``sprint_17_substeps/`` folder. Sprint 17.1 and Sprint 17.2 have been archived
after validation, and Sprint 17.3 has been promoted to
``docs/planning/sprints/active/`` for execution.

The main Sprint 17 file (``docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst``)
coordinates the active sub-sprint and the remaining sub-sprints.

Review Flow
-----------

1. **Initial review:** 17.1 audit → ensures foundation
2. **Structure review:** 17.2 layout → enables parallel work
3. **RFC review:** 17.3 RFC → most critical, longest
4. **Terminology review:** 17.4 glossary → foundation for later docs
5. **Design review:** 17.5, 17.6, 17.7 (lifecycle, packages, messages)
6. **Guard rails review:** 17.8 anti-goals
7. **Coordination review:** 17.9 main sprint file
8. **Consistency pass:** 17.10 consistency review
9. **Final gate:** 17.11 checklist → sign-off
10. **Verification:** 17.12 static checks
11. **PR preparation:** 17.13 PR description

Success Criteria for Sprint 17
------------------------------

- [ ] All 13 sub-sprints produce deliverables
- [ ] No implementation code added
- [ ] No packages created
- [ ] ``lifecore_state/`` exists as logical folder only
- [ ] All documents include mandatory phrase
- [ ] Terminology consistent across all documents
- [ ] Lifecycle/state separation explained clearly
- [ ] Anti-patterns explicitly rejected
- [ ] Sprint 18 entry criteria documented
- [ ] Ready for formal architecture review

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."
