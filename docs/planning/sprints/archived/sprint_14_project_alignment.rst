Sprint 14 - Project Alignment and Roadmap Cleanup
=================================================

Status:
  Archived / Completed

Completed in:
  2026-05-12

Branch:
  sprint/14-project-alignment

Track:
  Core / Documentation / Product planning

Priority:
  P0

Outcome:
  Planning docs now reflect the post-Sprint-14 state, historical Sprint 14 and
  Sprint 15 factory/tooling cards remain deferred, and the companion comparison
  baseline is tracked as shipped rather than as missing work.

Follow-ups:
  Sprint 15 remains planned under ``docs/planning/sprints/planned/``.

Goal:
  Reconcile roadmap, backlog, sprint history, and documentation with the real
  project state after Sprint 13.

Scope
-----

- Update ``ROADMAP.md``.
- Correct stale references to the old Sprint 8 / 0.4.0 planning state.
- Synchronize ``README.md``, ``CHANGELOG.md``, and ``docs/planning`` where needed.
- Set up the sprint archive structure.
- Reclassify the historical Sprint 14 and Sprint 15 cards as deferred/conditional.
- Add the rule that sprints may target core, companion, docs, architecture,
  tooling, DX, external modules, or research.
- Add planning tracks and the P0-P5 priority model.
- Mark already-delivered backlog items as shipped or moved.
- Identify obsolete items without inventing completed work.
- Document the strategic separation between ``lifecore_ros2`` and future
  ``lifecore_state`` work.
- Treat ``src/lifecore_ros2/spec/spec_model.py`` as an experimental placeholder
  unless a later deferred factory sprint proves the need.

Non-goals
---------

- No new runtime API.
- No factory implementation.
- No ``AppSpec`` / ``ComponentSpec`` / ``SpecLoader`` system.
- No generated nodes.
- No ``lifecore_state`` implementation.

Sprint outcome
--------------

- Archived Sprint 1 through Sprint 14 and removed Sprint 14 from the active
  sprint slot.
- Kept the historical factory and tooling cards deferred/conditional instead of
  presenting them as the default next steps.
- Updated roadmap, backlog, and planning pages to describe the post-Sprint-14
  sequence rather than the post-Sprint-13 transition.
- Reclassified the companion lifecycle comparison baseline as shipped and left
  remaining adoption polish to Sprint 15.

Execution plan
--------------

Work package 1 - Planning state audit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Verify that Sprint 1 through Sprint 13 are archived under ``sprints/archived``.
- Verify that the former Sprint 14 and Sprint 15 cards live under
  ``sprints/deferred`` and clearly state their conditional launch criteria.
- Search main planning documents for stale Sprint 8 / ``0.4.0`` framing,
  obsolete next-sprint claims, and factory/tooling work presented as current.

Validation:
  ``docs/planning/sprints/README.rst`` lists the active, planned, deferred, and
  archived sprint groups without presenting historical cards as current work.

Work package 2 - Roadmap and backlog alignment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Keep ``ROADMAP.md`` focused on public status, near-term sequence, non-goals,
  and links to deeper planning docs.
- Keep ``docs/planning/backlog.rst`` as the detailed planning source for tracks,
  priorities, shipped items, deferred items, and architecture guardrails.
- Ensure delivered work is marked as shipped only when it is already supported
  by existing implementation, sprint records, or changelog history.

Validation:
  The roadmap and backlog both describe the post-Sprint-13 state without
  inventing completed work or making deferred factory/codegen work sound active.

Work package 3 - Strategic boundary cleanup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Keep ``lifecore_ros2`` scoped to lifecycle component orchestration inside one
  ROS 2 lifecycle node.
- Keep future typed state work on a separate ``lifecore_state`` track.
- Treat ``src/lifecore_ros2/spec/spec_model.py`` as an experimental placeholder
  unless a later conditional factory sprint proves the need for specs.

Validation:
  Planning docs consistently separate lifecycle orchestration, future state
  architecture, factory work, specs, and tooling/codegen.

Work package 4 - Documentation consistency pass
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Check ``README.md``, ``CHANGELOG.md``, ``ROADMAP.md``, and ``docs/planning``
  for contradictory planning status.
- Prefer links over duplicating long technical explanations across README,
  roadmap, backlog, and sprint files.
- Keep branch strategy and sprint status rules in planning docs, not README.

Validation:
  No main planning document presents obsolete sprint status as current, and the
  README stays concise and onboarding-focused.

Recommended commit grouping
---------------------------

Use small documentation commits if this sprint is split for review:

- ``docs(planning): archive completed sprint history``
- ``docs(roadmap): align roadmap after sprint 13``
- ``docs(backlog): add tracks and priority model``
- ``docs(planning): defer historical factory and tooling sprints``

Validation checklist
--------------------

- Run a text search for stale planning phrases such as ``Sprint 8 / 0.4.0``,
  ``former Sprint 14``, ``former Sprint 15``, ``AppSpec``, ``ComponentSpec``,
  ``SpecLoader``, and ``spec_model.py``.
- Review each match and classify it as either intentional historical context or
  stale current-state wording.
- Build Sphinx if RST structure, toctrees, or cross-references changed.
- Do not run runtime tests unless code or examples are modified.

Acceptance criteria
-------------------

- [x] Sprint 1 to Sprint 13 are archived.
- [x] Former Sprint 14 and Sprint 15 are marked deferred/conditional.
- [x] Current sprint index clearly identifies Sprint 14 as active.
- [x] ``ROADMAP.md`` reflects the post-Sprint-13 state.
- [x] ``backlog.rst`` contains sprint track and priority rules.
- [x] No main planning document presents obsolete sprint status as current.
