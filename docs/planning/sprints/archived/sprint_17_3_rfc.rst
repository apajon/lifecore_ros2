Sprint 17.3 - Write Principal Architecture RFC
==============================================

**Status.** Archived.

**Track.** Architecture / Research.

**Type.** RFC design.

**Parent sprint.** :doc:`../active/sprint_17_lifecore_state_rfc`.

Feature goal
------------

Write the principal architecture RFC in
``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst`` so Sprint 17
has a central, reviewable reference for the future ``lifecore_state``
direction, boundaries, constraints, and non-goals before any implementation
work begins.

Lifecycle behavior contract
---------------------------

This sub-sprint had no runtime lifecycle behavior. It did not change
configure, activate, deactivate, cleanup, shutdown, or error behavior for any
``lifecore_ros2`` node or component.

The expected lifecycle impact was explicit non-impact:

- **configure:** no code path changed; no resources created by runtime code.
- **activate:** no activation behavior changed.
- **deactivate:** no deactivation behavior changed.
- **cleanup:** no cleanup behavior changed.
- **shutdown:** no shutdown behavior changed.
- **error:** no error transition behavior changed.

Context
-------

Sprint 17.1 validated repository placement and separation constraints.
Sprint 17.2 created the documentation-only ``lifecore_state/`` structure and
the RFC skeleton file.

Sprint 17.3 turned that skeleton into the principal architecture RFC. The RFC
explains why ``lifecore_state`` exists, what it covers, what it does not cover,
and how it remains separate from ``lifecore_ros2``.

Decisions inherited from Sprint 17.2
------------------------------------

Sprint 17.3 kept the decisions already validated by Sprint 17.2:

- ``lifecore_state/`` remains a documentation-only logical folder at the
  repository root during Sprint 17;
- ``lifecore_state/`` is not a ROS 2 installable package and is not part of the
  installed ``lifecore_ros2`` runtime package;
- the RFC extended the existing skeleton in
  ``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst`` instead of
  creating a new package, module, or alternate document location;
- Sprint 17 keeps the validated root structure in place: ``README.rst``,
  ``terminology.rst``, ``message_semantics.rst``,
  ``lifecycle_state_separation.rst``, ``anti_goals.rst``,
  ``package_boundaries.rst``, and ``rfcs/``;
- future names such as ``lifecore_state_msgs``, ``lifecore_state_core``, and
  ``lifecore_state_ros`` remain planning labels only during Sprint 17.

Impacted modules
----------------

``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst``
  Primary deliverable for Sprint 17.3.

``docs/planning/sprints/archived/``
  This folder now contains the archived Sprint 17.3 planning card.

``docs/planning/sprints/active/``
  Planning files archive Sprint 17.3 and promote Sprint 17.4 as the active
  sub-sprint.

``docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst``
  Main Sprint 17 coordinator now reflects Sprint 17.4 as active.

``src/``, ``tests/``, and ``examples/``
  Not impacted. Sprint 17.3 did not change runtime code, public APIs, tests,
  or examples.

Constraints
-----------

- No implementation.
- No real packages.
- Do not create ``package.xml`` in ``lifecore_state/``.
- Do not create ``CMakeLists.txt`` in ``lifecore_state/``.
- Do not create ``setup.py`` or ``pyproject.toml`` in ``lifecore_state/``.
- Do not create Python runtime code.
- No compilable ``.msg`` files.
- Do not create compilable ROS 2 ``.srv`` or ``.action`` files.
- No executable code.
- All Sprint 17.3 deliverables remained reStructuredText.
- Non-final sketches were clearly marked.
- Preserve separation between ``lifecore_ros2`` and ``lifecore_state``.

RFC document location
---------------------

**File.** ``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst``

Required sections
-----------------

1. **Title**
   "RFC 001: lifecore_state architecture direction"
2. **Status**
   Draft, Sprint 17.3, architecture only, no implementation commitment.
3. **Context**
   ``lifecore_ros2`` is an explicit composition framework native to ROS 2
   lifecycle and intentionally avoids hidden runtimes and giant managers.
4. **Problem statement**
   Typed distributed state, registry-scoped synchronization, state projection,
   snapshot and delta synchronization, quality-aware transport, deterministic
   identity, ROS-native message contracts.
5. **Goals**
   Architecture boundaries, package separation, message semantics,
   lifecycle/state separation, terminology stabilization, implementation risk
   reduction.
6. **Non-goals**
   Not a robotics operating system, orchestration runtime, EventBus, ECS,
   codegen-first design, plugin framework, factory/spec system, or global
   blackboard runtime.
7. **Naming decision**
   Recommend ``lifecore_state`` and explain why ``lifecore_io`` is too narrow.
8. **Repository organization decision**
   ``lifecore_state/`` as logical grouping during Sprint 17.3, later split into
   ``lifecore_state_msgs``, ``lifecore_state_core``, and
   ``lifecore_state_ros``.
9. **Future package boundaries**
   Responsibilities of msgs, core, and ros packages.
10. **Dependency rules**
    ``lifecore_ros2`` independence, pure Python core, ABI-only messages, ROS
    integration dependencies, optional future integration only.
11. **Conceptual model**
    StateDescriptor, StateDescription, StateSample, StateUpdate, StateCommand,
    StateRegistry, StateProjection, StateSnapshot, StateDelta, StateQuality.
12. **Descriptor vs description**
13. **State vs command**
14. **Snapshot vs delta**
15. **Identity model**
16. **Quality model**
17. **Registry-scoped synchronization**
18. **Lifecycle/state separation**
19. **Description subscriber lifecycle behavior**
20. **QoS direction**
21. **Policies**
22. **Anti-patterns**
23. **Future implementation phases**
24. **Next sprint entry criteria**
25. **Open questions**
26. **Decision summary**

Acceptance criteria
-------------------

- [x] RFC document exists and is complete.
- [x] All 26 sections are covered.
- [x] No implementation code is present.
- [x] No real packages are created.
- [x] ``lifecore_state/`` remains a documentation-only logical group at the
  repository root.
- [x] No ``package.xml`` exists in the ``lifecore_state/`` parent folder.
- [x] No build metadata is added under ``lifecore_state/``.
- [x] No compilable messages are created.
- [x] Lifecycle/state separation is explicit and reviewable.
- [x] Anti-patterns are explicitly rejected.
- [x] Pseudo-sketches are clearly marked as non-final.
- [x] Document is reviewable by architects and developers.
- [x] Mandatory review phrase is included where required.

Validation
----------

Documentation-scoped validation was used while Sprint 17 remained
documentation-only:

- inspected changed RST files for coherent headings, links, and section order;
- verified the RFC stayed aligned with the Sprint 17 parent file and audit;
- verified the existing ``lifecore_state/`` structure remained unchanged except
  for the intended RFC content updates;
- confirmed no forbidden files appeared under ``lifecore_state/``.

Full Python validation with ``uv run ruff check .``, ``uv run pyright``, and
``uv run pytest`` was not required because Sprint 17.3 did not touch Python
code or project configuration.

Non-goals
---------

- No implementation.
- No package creation.
- No message compilation.
- No lifecycle behavior changes.
- No public API changes.
- No example changes.
- No dependency changes.
- No implementation sprint work.

Clarifications needed
---------------------

None. Sprint 17.1 fixed repository placement and Sprint 17.2 created the
documentation structure needed for RFC writing.

Review notes
------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.3."
