Sprint 17.1 - Repository Audit and Framework
============================================

**Status.** Archived.

**Track.** Architecture / Research.

**Type.** Investigation and documentation.

**Parent sprint.** :doc:`../active/sprint_17_lifecore_state_rfc`.

Feature goal
------------

Audit the current repository structure and identify where future
``lifecore_state`` documentation should live, without changing
``lifecore_ros2`` runtime behavior or creating any installable
``lifecore_state`` package.

Lifecycle behavior contract
---------------------------

This sub-sprint had no runtime lifecycle behavior. It did not change configure,
activate, deactivate, cleanup, shutdown, or error behavior for any
``lifecore_ros2`` node or component.

The expected lifecycle impact was explicit non-impact:

- **configure:** no code path changed; no resources created.
- **activate:** no activation behavior changed.
- **deactivate:** no deactivation behavior changed.
- **cleanup:** no cleanup behavior changed.
- **shutdown:** no shutdown behavior changed.
- **error:** no error transition behavior changed.

Context
-------

Before proposing a future ``lifecore_state`` architecture and RFC, the project
needed a clear understanding of:

- current repository structure and organization;
- existing ROS 2 package layout and conventions;
- documentation, roadmap, and sprint file organization;
- current naming and dependency conventions;
- safe placement for future ``lifecore_state`` documentation.

Impacted modules
----------------

``docs/planning/sprints/``
  The planning area records the archived sub-sprint and links it to the broader
  Sprint 17 coordination plan.

``docs/planning/sprints/archived/``
  This folder contains the archived Sprint 17.1 planning card.

``docs/planning/sprints/sprint_17_repository_audit.rst``
  Audit deliverable produced by this sub-sprint:
  :doc:`../sprint_17_repository_audit`.

``lifecore_state/``
  Not impacted by 17.1. Future Sprint 17 sub-steps may create this as a
  documentation-only structure after the audit confirms placement.

``src/``, ``tests/``, and ``examples/``
  Not impacted. Sprint 17.1 did not change runtime code, public APIs, tests, or
  examples.

Constraints
-----------

- Do not create functional ``lifecore_state`` packages.
- Do not modify runtime behavior of ``lifecore_ros2``.
- Do not touch public APIs.
- Do not create frameworks, factories, spec systems, EventBus, ECS, or codegen.
- Keep the work purely preparatory and documentary.

Deliverable
-----------

**Document:** :doc:`../sprint_17_repository_audit`

Acceptance criteria
-------------------

- [x] Audit document created.
- [x] Current package structure clearly identified.
- [x] Naming conventions documented.
- [x] Risks of mixing architectures identified.
- [x] Placement recommendation clear and actionable.
- [x] Document includes mandatory review notes section.
- [x] Document ends with review requirement phrase.
- [x] No runtime code changed.
- [x] No ``lifecore_state`` package created.

Validation plan
---------------

Documentation-scoped validation was used for Sprint 17.1:

- produced RST inspected for coherent headings and internal references;
- Sphinx documentation build run after linking the audit into the docs tree;
- forbidden package files checked for ``lifecore_state``;
- runtime code, tests, and examples left untouched.

Archive notes
-------------

Sprint 17.1 audit was validated by the project owner on 2026-05-15 and archived
after validation.

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."
