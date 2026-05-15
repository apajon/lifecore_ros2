Sprint 17.2 - Create Documentation Structure for lifecore_state/
=================================================================

**Status.** Active.

**Track.** Architecture / Research.

**Type.** Documentation structure setup.

**Parent sprint.** :doc:`sprint_17_lifecore_state_rfc`.

Feature goal
------------

Prepare the documentation-only ``lifecore_state/`` folder structure for Sprint
17 and future architecture review, without creating functional packages,
runtime code, compiled messages, or ROS 2 package metadata.

Lifecycle behavior contract
---------------------------

This sub-sprint has no runtime lifecycle behavior. It must not change configure,
activate, deactivate, cleanup, shutdown, or error behavior for any
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

Sprint 17.1 validated the recommended placement: create ``lifecore_state/`` at
the repository root as a documentation-only logical folder during Sprint 17.
That folder is not a ROS 2 installable package.

Sprint 17.2 creates only the folder structure and skeleton RST files that
explain purpose and organization. Later sub-sprints fill the architecture
content.

Impacted modules
----------------

``lifecore_state/``
  New documentation-only logical folder for Sprint 17 architecture documents.

``lifecore_state/rfcs/``
  New documentation-only RFC folder for Sprint 17 RFC and review artifacts.

``docs/planning/sprints/``
  Planning files track Sprint 17.2 as the active sub-sprint and keep Sprint 17.1
  archived.

``src/``, ``tests/``, and ``examples/``
  Not impacted. Sprint 17.2 must not change runtime code, public APIs, tests, or
  examples.

Constraints
-----------

- Do not create ``package.xml`` in ``lifecore_state/``.
- Do not create ``CMakeLists.txt`` in ``lifecore_state/``.
- Do not create ``setup.py`` or ``pyproject.toml`` in ``lifecore_state/``.
- Do not create Python runtime code.
- Do not create compilable ROS 2 ``.msg``, ``.srv``, or ``.action`` files.
- Do not create actual packages named ``lifecore_state_msgs``,
  ``lifecore_state_core``, or ``lifecore_state_ros``.
- All Sprint 17.2 documents must be reStructuredText.
- Keep the style clear, technical, and accessible.
- Do not add orchestration, plugin frameworks, giant managers, ECS runtimes, or
  codegen.

Target structure
----------------

.. code-block:: text

    lifecore_state/
      README.rst
      rfcs/
        README.rst
        rfc_001_lifecore_state_architecture.rst
      terminology.rst
      message_semantics.rst
      lifecycle_state_separation.rst
      anti_goals.rst
      package_boundaries.rst

Deliverables
------------

``lifecore_state/README.rst``
  Explains that ``lifecore_state`` is a future direction, states that this
  folder is documentation-only for Sprint 17, clarifies that it is not a ROS 2
  package, and summarizes objectives and non-objectives.

``lifecore_state/rfcs/README.rst``
  Explains what an RFC is in this project and why RFCs clarify architecture
  before implementation.

``lifecore_state/terminology.rst``
  Skeleton for the glossary completed in Sprint 17.4.

``lifecore_state/message_semantics.rst``
  Skeleton for message semantics completed in Sprint 17.7.

``lifecore_state/lifecycle_state_separation.rst``
  Skeleton for lifecycle/state separation completed in Sprint 17.5.

``lifecore_state/anti_goals.rst``
  Skeleton for anti-goals completed in Sprint 17.8.

``lifecore_state/package_boundaries.rst``
  Skeleton for package boundaries completed in Sprint 17.6.

Acceptance criteria
-------------------

- [ ] Directory structure created at repository root.
- [ ] All required RST skeleton files exist.
- [ ] ``lifecore_state/`` has no ``package.xml``.
- [ ] ``lifecore_state/`` has no build metadata.
- [ ] ``lifecore_state/`` has no Python runtime code.
- [ ] ``lifecore_state/`` has no compilable ROS 2 interface files.
- [ ] All folders have minimal README explaining content.
- [ ] Each file ends with mandatory review phrase.
- [ ] Folder is not discoverable by ``colcon`` as a package.

Validation plan
---------------

For Sprint 17.2 execution, use documentation-scoped validation:

- inspect the produced RST files for coherent headings and internal references;
- run a Sphinx documentation build if the new folder is linked into the docs
  tree;
- verify no forbidden files exist under ``lifecore_state/``;
- confirm ``src/``, ``tests/``, and ``examples/`` remain untouched.

Full Python validation with ``uv run ruff check .``, ``uv run pyright``, and
``uv run pytest`` is not required unless Sprint 17.2 unexpectedly touches Python
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
- No Sprint 18 implementation work.

Clarifications needed
---------------------

None for activation. Sprint 17.1 validated root-level, documentation-only
placement for ``lifecore_state/``.

Review notes
------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."
