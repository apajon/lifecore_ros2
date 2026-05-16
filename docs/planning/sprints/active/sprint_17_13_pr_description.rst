Sprint 17.13 — Prepare PR Description Draft
============================================

**Status.** Active.

**Track.** Architecture / Research.

**Type.** Final deliverable summary.

**Objective.** Prepare a draft Pull Request description that summarizes Sprint 17
and explains what reviewers should focus on.

Context
-------

The PR description is the face of Sprint 17 to reviewers. It must be clear,
complete, and set expectations for review scope.

PR Description Location
-----------------------

**File:** ``lifecore_state/rfcs/sprint_17_pr_description.md``

Required Content
-----------------

The PR description should contain:

1. **Title**

   .. code-block:: text

       Sprint 17: lifecore_state architecture RFC

2. **Summary section**

   Explain briefly that this PR adds architecture documentation only for
   the future ``lifecore_state`` direction.

   Key facts:
   - No implementation
   - No new ROS 2 package
   - No new message compilation
   - No runtime behavior change
   - Documentation only

3. **Context section**

   Explain why this matters:
   - ``lifecore_state`` is a future direction for distributed typed state
   - Clarification needed before implementation
   - RFC-style collaboration on architecture
   - Protects against scope creep
   - Guides Sprint 18+

4. **What changed section**

   List deliverables:
   - Repository audit
   - Documentation structure
   - RFC 001 (principal architecture)
   - Terminology glossary
   - Lifecycle/state separation clarification
   - Package boundaries
   - Message semantics
   - Anti-goals
   - Consistency review
   - Final checklist
   - Static verification
   - This PR description

5. **What did not change section**

   Explicitly state:
   - ``lifecore_ros2`` has no code changes
   - No packages created
   - No build configuration changes
   - No dependencies added
   - No runtime behavior modified
   - Public APIs untouched

6. **Architecture decisions section**

   Summarize key decisions:
   - ``lifecore_state`` is the chosen name
   - Logical folder structure (no package.xml parent)
   - Three future packages: msgs, core, ros
   - Lifecycle and state cleanly separated
   - Anti-patterns explicitly rejected

7. **Critical lifecycle decision section**

   Highlight the most important design decision:

   .. code-block:: text

       StateDescription Lifecycle Behavior:

       - StateDescription subscriber can receive transient_local messages
         while the node is inactive (during configure)
       - Descriptions may be cached while inactive
       - StateUpdate deltas are NOT applied while inactive
       - StateCommand requires active lifecycle

       This semantic gating (per-message-type) is critical and differs
       from a global "ignore all callbacks while inactive" approach.

8. **Package boundary decision section**

   .. code-block:: text

       Future package separation ensures:

       - lifecore_state_msgs: ABI and message contracts only
       - lifecore_state_core: pure Python, no ROS 2 dependencies
       - lifecore_state_ros: ROS 2 integration only

       Dependency rule: lifecore_ros2 must remain independent of
       all lifecore_state packages.

9. **Anti-goals section**

   Explicitly state rejected patterns:
   - No giant StateManager
   - No magical observable values
   - No auto-register unknown fields
   - No orchestration runtime
   - No codegen-first design
   - No ECS framework
   - No hidden synchronization

10. **Review focus section**

    Guide reviewers on where to concentrate:

    .. code-block:: text

        **Key areas for review:**

        1. Architectural boundaries (RFC sections 3-6)
           Are the goals/non-goals clear and acceptable?

        2. Lifecycle/state separation (dedicated document)
           Is the StateDescription caching rule justified?
           Is semantic gating the right approach?

        3. Package boundaries (dedicated document)
           Are the three packages clearly separated?
           Are dependencies acyclic?

        4. Message semantics (dedicated document)
           Do the five message types cover the scope?
           Are QoS recommendations justified?

        5. Terminology (glossary)
           Are all terms accessible and consistent?

        6. Anti-patterns (dedicated document)
           Do the anti-goals protect against known risks?

11. **Acceptance checklist**

    .. code-block:: markdown

        ## Acceptance Checklist

        - [ ] No implementation added
        - [ ] No package.xml under lifecore_state/
        - [ ] No .msg files added
        - [ ] No runtime behavior changed
        - [ ] RFC is complete and reviewable
        - [ ] Terminology is consistent
        - [ ] Lifecycle/state separation is sound
        - [ ] Package boundaries are clear
        - [ ] Message semantics are complete
        - [ ] Anti-goals protect the architecture
        - [ ] All documents end with mandatory review phrase
        - [ ] No architectural contradictions

12. **File listing**

    List all files created or modified:

    .. code-block:: text

        New files:
        - lifecore_state/README.rst
        - lifecore_state/rfcs/README.rst
        - lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst
        - lifecore_state/terminology.rst
        - lifecore_state/message_semantics.rst
        - lifecore_state/lifecycle_state_separation.rst
        - lifecore_state/anti_goals.rst
        - lifecore_state/package_boundaries.rst
        - docs/planning/sprints/sprint_17_substeps/ (13 sub-sprint files)
        - And this PR description

        Modified files:
        - docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst (updated)

13. **Open questions**

    If any architectural decisions remain open:
    - List them
    - Explain why they are deferred
    - Propose decision timeline

14. **Related issues/PRs**

    Link to:
    - Original Sprint 17 issue if any
    - Related Sprint 18 issues
    - Related architecture discussions

15. **Final notes**

    .. code-block:: text

        ## Final Notes

        This PR is intentionally documentation-only and proposes no code.

        It is designed for architectural review and discussion before
        any implementation commitment.

        Sprint 18 will evaluate implementation of the message ABI first,
        pending acceptance of this RFC.

Acceptance Criteria
-------------------

- [ ] PR description is clear and complete
- [ ] All deliverables listed
- [ ] Key architectural decisions highlighted
- [ ] Review focus areas identified
- [ ] Acceptance checklist present
- [ ] No ambiguity about scope or intent
- [ ] Mandatory review phrase included

Content Quality Checklist
-------------------------

- [ ] Title is descriptive
- [ ] Summary is concise but complete
- [ ] Sections are well-organized
- [ ] Critical decisions highlighted
- [ ] Reviewers know where to focus
- [ ] No unnecessary detail
- [ ] Professional tone

Success Criteria
----------------

A reviewer reading this PR description understands:

- What was done (documentation and architecture)
- What was NOT done (no implementation)
- What key decisions were made
- Where to focus review effort
- How to accept or request changes

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."
