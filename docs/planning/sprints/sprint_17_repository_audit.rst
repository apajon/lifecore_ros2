Sprint 17.1 - Repository Audit
==============================

**Status.** Validated.

**Track.** Architecture / Research.

**Scope.** Documentation audit only. No implementation, no runtime package, no
message package, no behavior change.

Purpose
-------

This audit records the current repository structure before Sprint 17 creates the
future ``lifecore_state`` documentation set. Its purpose is to keep the future
state architecture separate from the existing ``lifecore_ros2`` lifecycle core.

Summary
-------

The repository is currently organized as a Python ``src/`` layout package named
``lifecore_ros2``. It is a lifecycle composition library for ROS 2 Jazzy, not a
ROS 2 workspace package with ``package.xml`` metadata. The package is typed,
minimal, and explicit: runtime code lives under ``src/lifecore_ros2/``, examples
live under ``examples/``, tests live under ``tests/``, and project planning lives
under ``docs/planning/``.

No ``lifecore_state/`` folder exists yet. ``lifecore_state`` is currently a
planning and architecture topic documented in roadmap, backlog, and Sprint 17
planning files. That is the right state before Sprint 17.2: Sprint 17.1 should
recommend where to place future documents, not create implementation structure.

Current repository structure observed
-------------------------------------

Top-level repository structure:

.. code-block:: text

    lifecore_ros2/
      .github/
      docs/
      examples/
      scripts/
      src/
      tests/
      tools/
      CHANGELOG.md
      CONTRIBUTING.md
      LICENSE
      pyproject.toml
      README.md
      ROADMAP.md
      uv.lock

Important observations:

- ``pyproject.toml`` is the source of package metadata and tool configuration.
- Runtime source code uses the Python ``src/`` layout.
- ``docs/`` contains user documentation, architecture notes, planning, and
  Sprint files.
- ``examples/`` contains small runnable examples for lifecycle component usage.
- ``tests/`` contains focused pytest coverage for core behavior, components,
  smoke imports, integration, and testing helpers.
- No ``package.xml`` file was found in the repository.
- No ``lifecore_state/`` directory was found during this audit.

Existing package layout
-----------------------

The installed Python package is ``lifecore_ros2`` under ``src/lifecore_ros2/``:

.. code-block:: text

    src/lifecore_ros2/
      __init__.py
      _version.py
      py.typed
      components/
      core/
      spec/
      testing/

Core lifecycle primitives live under ``src/lifecore_ros2/core/``:

.. code-block:: text

    core/
      activation_gating.py
      exceptions.py
      health.py
      lifecycle_component.py
      lifecycle_component_node.py

Lifecycle-aware reusable components live under
``src/lifecore_ros2/components/``:

.. code-block:: text

    components/
      lifecycle_parameter_component.py
      lifecycle_parameter_observer_component.py
      lifecycle_publisher_component.py
      lifecycle_service_client_component.py
      lifecycle_service_server_component.py
      lifecycle_subscriber_component.py
      lifecycle_timer_component.py
      lifecycle_watchdog_component.py
      service_component.py
      topic_component.py

The package exposes public symbols from ``src/lifecore_ros2/__init__.py``,
``src/lifecore_ros2/core/__init__.py``, and
``src/lifecore_ros2/components/__init__.py`` using explicit ``__all__`` lists.
That makes public API stability visible and reviewable.

ROS 2 package observation
-------------------------

The repository depends conceptually on ROS 2 Jazzy and ``rclpy`` at runtime, but
it is packaged as a Python library. ``rclpy`` is intentionally absent from normal
PyPI dependencies because it comes from the system ROS installation.

No ROS 2 package marker was found:

- no repository-level ``package.xml``;
- no component-level ``package.xml``;
- no current ``lifecore_state`` ROS package;
- no current ``lifecore_state_msgs`` message package;
- no current ``lifecore_state_core`` package;
- no current ``lifecore_state_ros`` package.

This is important for Sprint 17: creating a parent ``lifecore_state/`` folder
must not accidentally make it discoverable as a ROS 2 package. It must remain a
documentation-only logical group during Sprint 17.

Tooling and validation conventions
----------------------------------

The repository uses:

- Python ``>=3.12``;
- setuptools with setuptools-scm;
- ``uv`` for build and validation workflows;
- Ruff with line length 119 and Python 3.12 target;
- Pyright in strict mode with selected ROS stub noise downgraded to warnings;
- pytest with ROS launch and ament plugins disabled for local test ergonomics;
- Sphinx for documentation.

Validation commands should remain proportional to the touched files. For Sprint
17 documentation-only work, RST checks and Sphinx builds are more relevant than
full Python quality gates unless code or project configuration is touched.

Documentation and planning organization
---------------------------------------

The documentation root contains guides, API references, architecture documents,
planning documents, and design notes:

.. code-block:: text

    docs/
      api.rst
      architecture.rst
      concepts/
      design_notes/
      examples.rst
      planning/
      quickstart.rst
      testing.rst

Sprint planning is organized under ``docs/planning/sprints/``:

.. code-block:: text

    docs/planning/sprints/
      README.rst
      active/
      archived/
      deferred/
      planned/
      sprint_17_substeps/

At Sprint 17.1 validation time, the active Sprint 17 files were:

.. code-block:: text

    docs/planning/sprints/active/
      sprint_17_lifecore_state_rfc.rst
      sprint_17_1_repository_audit.rst

After validation, the Sprint 17.1 planning card moved to
``docs/planning/sprints/archived/`` and Sprint 17.2 became the active
sub-sprint.

This organization is already suitable for Sprint coordination. The future
``lifecore_state/`` documentation set should not be mixed into
``src/lifecore_ros2/`` or the existing lifecycle user guides.

Examples and companion repository observation
---------------------------------------------

The main repository examples are simple lifecycle usage examples under
``examples/``. They demonstrate existing ``lifecore_ros2`` behavior such as
minimal nodes, publishers, subscribers, timers, services, parameters, watchdogs,
and composed pipelines.

The workspace also contains a separate companion repository,
``lifecore_ros2_examples``. It is a non-package example repository
(``tool.uv.package = false``) that depends on ``lifecore-ros2`` and contains
applied lifecycle comparison examples. This confirms a useful separation:

- ``lifecore_ros2`` owns the reusable lifecycle library and its internal docs;
- ``lifecore_ros2_examples`` owns applied comparison examples;
- future ``lifecore_state`` architecture documents should begin in
  ``lifecore_ros2`` planning/docs, not in the companion examples repository.

Naming and import conventions
-----------------------------

Observed naming conventions:

- Core managed entity: ``LifecycleComponent``.
- Framework base node: ``LifecycleComponentNode``.
- Framework-provided components follow ``Lifecycle<Capability>Component``.
- Topic and service base components use direct capability names such as
  ``TopicComponent`` and ``ServiceComponent``.
- Application examples use domain-oriented filenames and node names instead of
  adding extra lifecycle prefixes everywhere.

Observed import conventions:

- Public exports are explicit through package ``__init__.py`` files and
  ``__all__``.
- Public names are re-exported from the top-level package for user ergonomics.
- Type information is part of the package contract through ``py.typed``.
- ``_version.py`` is generated by setuptools-scm and should not be treated as a
  hand-authored architecture file.

These conventions argue against hiding a future state framework inside existing
core modules or exporting speculative ``lifecore_state`` names from
``lifecore_ros2`` before the architecture is accepted.

Existing lifecore_state references
----------------------------------

``lifecore_state`` already appears in planning material:

- ``ROADMAP.md`` treats it as a separate State Architecture track.
- ``docs/planning/backlog.rst`` states that the future distributed typed state
  model should remain separate from ``lifecore_ros2``.
- ``docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst`` coordinates
  the active architecture sprint.
- ``docs/planning/sprints/planned/sprint_18_lifecore_state_msgs_abi.rst`` is a
  conditional future sprint for message ABI work.
- ``docs/planning/lifecore_state_architecture_report_en_v3.md`` exists as prior
  planning context, not as an implementation package.

The repository therefore already points toward separation. Sprint 17 should
make that separation reviewable and precise.

Risks of architectural mixing
-----------------------------

The main risk is turning ``lifecore_ros2`` from a small lifecycle composition
library into a broad runtime framework. Specific risks:

- adding state-store concepts directly under ``src/lifecore_ros2/core/``;
- making ``LifecycleComponentNode`` own state registry semantics too early;
- exporting speculative ``StateDescriptor`` or ``StateRegistry`` names from
  ``lifecore_ros2`` before the RFC is accepted;
- adding ``rclpy``-bound state transport before pure message and core boundaries
  are defined;
- treating commands as observed state instead of requested mutation;
- treating lifecycle activation as proof that state values are valid;
- treating valid state values as proof that a lifecycle component is active;
- creating a parent ``lifecore_state/`` folder with ``package.xml`` and thereby
  making it a ROS 2 package before package boundaries are reviewed;
- creating ``lifecore_state_msgs``, ``lifecore_state_core``, or
  ``lifecore_state_ros`` as real packages during Sprint 17;
- moving companion examples or applied demos into the core repository as part of
  architecture planning.

These risks all point to the same guard rail: keep Sprint 17 as documentation
and RFC work only.

Recommendation for lifecore_state documentation placement
---------------------------------------------------------

Create ``lifecore_state/`` at the repository root as a documentation-only
logical folder during Sprint 17.

Recommended Sprint 17 structure:

.. code-block:: text

    lifecore_state/
      README.rst
      terminology.rst
      message_semantics.rst
      lifecycle_state_separation.rst
      anti_goals.rst
      package_boundaries.rst
      rfcs/
        README.rst
        rfc_001_lifecore_state_architecture.rst
        sprint_17_consistency_review.rst
        sprint_17_final_review_checklist.rst
        sprint_17_static_check.rst
        sprint_17_pr_description.md

Rules for this folder during Sprint 17:

- It must be documentation-only.
- It must not contain ``package.xml``.
- It must not contain ``CMakeLists.txt``.
- It must not contain ``setup.py``.
- It must not contain ``pyproject.toml``.
- It must not contain ``.msg``, ``.srv``, or ``.action`` files.
- It must not contain Python runtime modules.
- It must not be imported from ``lifecore_ros2``.
- It must not change public exports in ``src/lifecore_ros2/__init__.py``.

This placement has three advantages:

1. It makes the future architecture visible at repository level.
2. It avoids implying that ``lifecore_state`` is already part of the installed
   ``lifecore_ros2`` Python package.
3. It gives Sprint 17 documents a stable home before Sprint 18 considers any
   message ABI prototype.

Rejected placements
-------------------

``src/lifecore_ros2/lifecore_state/``
  Rejected because it would imply the state architecture belongs inside the
  current lifecycle runtime package.

``src/lifecore_ros2/core/state/``
  Rejected because it would mix lifecycle orchestration with state as source of
  truth.

``docs/lifecore_state/``
  Acceptable as pure documentation, but weaker than a root-level logical folder
  because Sprint 17 explicitly plans future package boundaries. A root-level
  documentation folder makes the future split easier to review while still
  avoiding package metadata.

``lifecore_ros2_examples/``
  Rejected because the companion repository is for applied examples, not core
  architecture decisions.

``docs/planning/sprints/sprint_17_substeps/``
  Rejected for final deliverables because this folder is an execution guide for
  the coding agent, not the stable architecture documentation home.

Independence reminder
---------------------

``lifecore_ros2`` must remain independent from ``lifecore_state``.

During Sprint 17, that means:

- no imports from ``lifecore_state`` into ``lifecore_ros2``;
- no public re-exports of ``lifecore_state`` names;
- no changes to lifecycle transition semantics;
- no new lifecycle manager, state manager, registry runtime, EventBus, ECS, or
  code generation system;
- no dependency from ``lifecore_ros2`` to future ``lifecore_state`` packages.

For future sprints, the recommended direction is:

- ``lifecore_state_msgs`` owns ROS 2 ABI contracts only;
- ``lifecore_state_core`` owns pure Python state semantics and has no ROS 2 or
  ``rclpy`` dependency;
- ``lifecore_state_ros`` owns ROS 2 integration and may depend on ``rclpy``,
  message contracts, and pure core semantics;
- optional integration with ``lifecore_ros2`` must remain explicit and reviewed.

Audit outcome
-------------

Sprint 17.1 is complete and validated from a documentation-planning
perspective.

- The current package structure is identified.
- No existing ROS 2 package metadata was found.
- Naming and public import conventions are documented.
- Risks of mixing lifecycle and state architecture are identified.
- Root-level documentation-only ``lifecore_state/`` placement is recommended.
- The independence of ``lifecore_ros2`` from future ``lifecore_state`` work is
  explicitly restated.

Validation
----------

Validated by the project owner on 2026-05-15.

Review notes
------------

Reviewer focus:

- Confirm that root-level ``lifecore_state/`` is the desired documentation home
  for Sprint 17.2.
- Confirm that Sprint 17 should remain architecture and RFC only.
- Confirm that no package metadata should be created before Sprint 18 or later.
- Confirm that ``lifecore_ros2`` public exports must remain unchanged during
  Sprint 17.

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."
