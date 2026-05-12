Sprint 14 - Project Alignment and Roadmap Cleanup
=================================================

Status:
  Active

Branch:
  sprint/14-project-alignment

Track:
  Core / Documentation / Product planning

Priority:
  P0

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

Acceptance criteria
-------------------

- [ ] Sprint 1 to Sprint 13 are archived.
- [ ] Former Sprint 14 and Sprint 15 are marked deferred/conditional.
- [ ] Current sprint index clearly identifies Sprint 14 as active.
- [ ] ``ROADMAP.md`` reflects the post-Sprint-13 state.
- [ ] ``backlog.rst`` contains sprint track and priority rules.
- [ ] No main planning document presents obsolete sprint status as current.
