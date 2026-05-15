Sprint 17.1 - Repository Audit and Framework
============================================

**Status.** Active.

**Track.** Architecture / Research.

**Type.** Investigation and documentation.

**Parent sprint.** :doc:`sprint_17_lifecore_state_rfc`.

Feature goal
------------

Audit the current repository structure and identify where future
``lifecore_state`` documentation should live, without changing
``lifecore_ros2`` runtime behavior or creating any installable
``lifecore_state`` package.

Lifecycle behavior contract
---------------------------

This sub-sprint has no runtime lifecycle behavior. It must not change configure,
activate, deactivate, cleanup, shutdown, or error behavior for any
``lifecore_ros2`` node or component.

The expected lifecycle impact is therefore explicit non-impact:

- **configure:** no code path changed; no resources created.
- **activate:** no activation behavior changed.
- **deactivate:** no deactivation behavior changed.
- **cleanup:** no cleanup behavior changed.
- **shutdown:** no shutdown behavior changed.
- **error:** no error transition behavior changed.

Context
-------

Before proposing a future ``lifecore_state`` architecture and RFC, the project
needs a clear understanding of:

- current repository structure and organization;
- existing ROS 2 package layout and conventions;
- documentation, roadmap, and sprint file organization;
- current naming and dependency conventions;
- safe placement for future ``lifecore_state`` documentation.

Impacted modules
----------------

``docs/planning/sprints/``
  The active planning area records this sub-sprint and links it to the broader
  Sprint 17 coordination plan.

``docs/planning/sprints/active/``
  This folder contains the active Sprint 17 coordinator and the active Sprint
  17.1 planning card.

``docs/planning/sprints/sprint_17_repository_audit.rst``
  Expected deliverable for the audit itself. This file is not created by merely
  activating Sprint 17.1; it is produced when the audit work is executed.

``lifecore_state/``
  Not impacted by 17.1 activation. Future Sprint 17 sub-steps may create this
  as documentation-only structure after the audit confirms placement.

``src/``, ``tests/``, and ``examples/``
  Not impacted. Sprint 17.1 must not change runtime code, public APIs, tests, or
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

**Document:** ``docs/planning/sprints/sprint_17_repository_audit.rst``

The audit document must include:

1. Current repository structure observed.
2. Existing ROS 2 packages and their layout.
3. Conventions for naming, imports, and organization.
4. Risks of architectural mixing.
5. Recommendation for ``lifecore_state`` documentation placement.
6. Explicit reminder that ``lifecore_ros2`` must remain independent from
   ``lifecore_state``.
7. Mandatory review notes section.

Acceptance criteria
-------------------

- [ ] Audit document created.
- [ ] Current package structure clearly identified.
- [ ] Naming conventions documented.
- [ ] Risks of mixing architectures identified.
- [ ] Placement recommendation clear and actionable.
- [ ] Document includes mandatory review notes section.
- [ ] Document ends with review requirement phrase.
- [ ] No runtime code changed.
- [ ] No ``lifecore_state`` package created.

Validation plan
---------------

For Sprint 17.1 execution, use documentation-scoped validation:

- inspect the produced RST for coherent headings and internal references;
- run a Sphinx documentation build if the audit is linked into the docs tree;
- verify no forbidden package files were created for ``lifecore_state``;
- confirm ``src/``, ``tests/``, and ``examples/`` remain untouched.

Full Python validation with ``uv run ruff check .``, ``uv run pyright``, and
``uv run pytest`` is not required unless later Sprint 17 work unexpectedly
touches Python code or project configuration.

Non-goals
---------

- No implementation.
- No package creation.
- No message definitions.
- No lifecycle behavior changes.
- No public API changes.
- No example changes.
- No dependency changes.
- No Sprint 18 implementation decisions beyond documenting entry criteria.

Clarifications needed
---------------------

None for activation. The audit content itself should remain evidence-based and
may raise follow-up questions if the repository structure suggests competing
placement options.

Review notes
------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."
