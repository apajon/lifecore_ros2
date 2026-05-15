Sprint 17.3 - Write Principal Architecture RFC
==============================================

**Status.** Active.

**Track.** Architecture / Research.

**Type.** RFC design.

**Parent sprint.** :doc:`sprint_17_lifecore_state_rfc`.

Feature goal
------------

Write the principal architecture RFC in
``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst`` so Sprint 17
has a central, reviewable reference for the future ``lifecore_state``
direction, boundaries, constraints, and non-goals before any implementation
work begins.

Lifecycle behavior contract
---------------------------

This sub-sprint has no runtime lifecycle behavior. It must not change
configure, activate, deactivate, cleanup, shutdown, or error behavior for any
``lifecore_ros2`` node or component.

The expected lifecycle impact is explicit non-impact:

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

Sprint 17.3 turns that skeleton into the principal architecture RFC. The RFC
must explain why ``lifecore_state`` exists, what it covers, what it does not
cover, and how it remains separate from ``lifecore_ros2``.

Decisions inherited from Sprint 17.2
------------------------------------

Sprint 17.3 must keep the decisions already validated by Sprint 17.2:

- ``lifecore_state/`` remains a documentation-only logical folder at the
   repository root during Sprint 17;
- ``lifecore_state/`` is not a ROS 2 installable package and is not part of
   the installed ``lifecore_ros2`` runtime package;
- the RFC must extend the existing skeleton in
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

``docs/planning/sprints/active/``
  Planning files track Sprint 17.3 as the active Sprint 17 sub-sprint.

``docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst``
  Main Sprint 17 coordinator must reflect that RFC work is now active.

``src/``, ``tests/``, and ``examples/``
  Not impacted. Sprint 17.3 must not change runtime code, public APIs, tests,
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
- All Sprint 17.3 deliverables must remain reStructuredText at this stage.
- Non-final sketches only, clearly marked.
- Must be complete enough to guide Sprint 18.
- Must preserve separation between ``lifecore_ros2`` and ``lifecore_state``.

RFC document location
---------------------

**File.** ``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst``

Required sections
-----------------

1. **Title**
   "RFC 001: lifecore_state architecture direction"
2. **Status**
   Draft, Sprint 17, architecture only, no implementation commitment.
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
   ``lifecore_state/`` as logical grouping during Sprint 17, later split into
   ``lifecore_state_msgs/``, ``lifecore_state_core/``, and
   ``lifecore_state_ros/``.
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
24. **Sprint 18 entry criteria**
25. **Open questions**
26. **Decision summary**

Acceptance criteria
-------------------

- [ ] RFC document exists and is complete.
- [ ] All 26 sections are covered.
- [ ] No implementation code is present.
- [ ] No real packages are created.
- [ ] ``lifecore_state/`` remains a documentation-only logical group at the
   repository root.
- [ ] No ``package.xml`` exists in the ``lifecore_state/`` parent folder.
- [ ] No build metadata is added under ``lifecore_state/``.
- [ ] No compilable messages are created.
- [ ] Lifecycle/state separation is explicit and reviewable.
- [ ] Anti-patterns are explicitly rejected.
- [ ] Pseudo-sketches are clearly marked as non-final.
- [ ] Document is reviewable by architects and developers.
- [ ] Mandatory review phrase is included where required.

Validation plan
---------------

Use documentation-scoped validation while Sprint 17 remains documentation-only:

- inspect changed RST files for coherent headings, links, and section order;
- verify the RFC stays aligned with the Sprint 17 parent file and audit;
- verify the existing ``lifecore_state/`` structure remains unchanged except
   for the intended RFC content updates;
- run a Sphinx documentation build if the RFC is linked into the docs tree;
- confirm no forbidden files appear under ``lifecore_state/``.

Full Python validation with ``uv run ruff check .``, ``uv run pyright``, and
``uv run pytest`` is not required unless Sprint 17.3 unexpectedly touches
Python code or project configuration.

Non-goals
---------

- No implementation.
- No package creation.
- No message compilation.
- No lifecycle behavior changes.
- No public API changes.
- No example changes.
- No dependency changes.
- No Sprint 18 implementation work.

Clarifications needed
---------------------

None for activation. Sprint 17.1 fixed the repository placement and Sprint 17.2
created the documentation structure needed to begin RFC writing.

Review notes
------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."
