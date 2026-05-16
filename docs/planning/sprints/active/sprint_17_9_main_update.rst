Sprint 17.9 — Update Main Sprint 17 File
========================================

**Status.** Active.

**Track.** Architecture / Research.

**Type.** Documentation update.

**Objective.** Keep the main Sprint 17 file accurate as a coordination hub for
all sub-sprints, with current status, deliverables, and review checklist.

**Parent sprint.** :doc:`sprint_17_lifecore_state_rfc`.

Feature goal
------------

Update ``docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst`` so the
main Sprint 17 coordinator reflects the completed sub-sprints (17.1 through
17.8), the current active sub-sprint (17.9), and the remaining sub-sprints
(17.10 through 17.13) without changing any runtime behavior.

Lifecycle behavior contract
---------------------------

Sprint 17.9 is documentation-only. It must not change configure, activate,
deactivate, cleanup, shutdown, or error behavior for any existing
``lifecore_ros2`` node or component.

- **configure:** no runtime resource creation changes.
- **activate:** no activation gate changes.
- **deactivate:** no deactivation behavior changes.
- **cleanup:** no cleanup behavior changes.
- **shutdown:** no shutdown behavior changes.
- **error:** no error recovery changes.

Context
-------

Sprint 17.8 archived the anti-goals deliverable. Sprint 17.9 now keeps the main
Sprint 17 file synchronized with the current state of sub-sprint deliverables
and acts as the source of truth for Sprint 17 coordination.

Document location
-----------------

**File:** ``docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst``

Required content
----------------

1. **Sprint title and metadata.** Track, branch, priority, type.
2. **Lifecycle behavior contract.** Restate non-impact rules for configure,
   activate, deactivate, cleanup, shutdown, and error transitions.
3. **Context.** Summarize current ``lifecore_ros2`` independence from future
   ``lifecore_state`` work.
4. **Goals and non-goals.** Keep both lists explicit.
5. **Impacted modules.** List documentation locations only.
6. **Active sub-sprint pointer.** Point to the current active sub-sprint card.
7. **Deliverables.** List 17.1 through 17.13 with their current status:
   archived, completed, active, or pending.
8. **Explicit decisions to capture.** Naming, package layout, descriptor and
   description semantics, snapshot and delta semantics, command intent versus
   observed truth, quality semantics, and inactive lifecycle rules per message
   type.
9. **Acceptance criteria.** Verifiable checklist for Sprint 17 as a whole.
10. **Validation plan.** Documentation-scoped validation while no Python code or
    project configuration changes.
11. **Sprint 18 candidate scope.** Conditional message ABI prototype only.
12. **Review checklist.** Reviewer-facing checklist.
13. **Mandatory review phrase.**

Acceptance criteria
-------------------

- [ ] Main Sprint 17 file lists 17.1 through 17.8 as archived or completed.
- [ ] Main Sprint 17 file lists 17.9 as the active sub-sprint.
- [ ] Main Sprint 17 file lists 17.10 through 17.13 as remaining work.
- [ ] Sprint coordinator points to the correct active sub-sprint card.
- [ ] Lifecycle non-impact rules remain explicit.
- [ ] Explicit decisions section stays consistent with the other Sprint 17
  documents.
- [ ] Review checklist covers anti-patterns, independence, and no-implementation
  rule.
- [ ] Mandatory review phrase present.

Content quality checklist
-------------------------

- [ ] Status values match the planning index (``archived``, ``active``,
  ``completed``).
- [ ] No sub-sprint is advanced ahead of validation.
- [ ] Wording stays consistent with sub-sprint deliverables.
- [ ] No runtime API, message ABI, or Python implementation is referenced as
  implemented.
- [ ] Document is usable as a single Sprint 17 review entry point.

Success criteria
----------------

A reviewer reading the main Sprint 17 file can:

- See which sub-sprints are done, in progress, or pending;
- Find the active sub-sprint card without searching the substeps folder;
- Cite the coordinator file when accepting or rejecting Sprint 17 deliverables;
- Confirm that Sprint 17 remains documentation-only.

Implementation notes
--------------------

This sub-sprint maintains the existing main Sprint 17 file rather than
creating a new one. It must not delete validated history from the deliverables
section and must not advance sub-sprints that have not been completed.

Review requirement
------------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."
