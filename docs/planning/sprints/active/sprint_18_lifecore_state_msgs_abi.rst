Sprint 18 - lifecore_state_msgs ABI prototype
=============================================

**Status.** Active.

**Track.** State Architecture / ROS ABI.

**Type.** ROS 2 message ABI prototype.

**Branch.** ``sprint/18-lifecore-state-msgs-abi``.

**Priority.** P2.

**Condition.** Sprint 17 closed the architecture/RFC phase for the future
``lifecore_state`` direction and validated the go decision for a messages-only
ABI prototype.

**Objective.** Create the first compilable ROS 2 Jazzy interface package for
``lifecore_state`` while avoiding runtime behavior, Python core code, registry
logic, publishers, subscribers, lifecycle integration, and tooling.

Sprint lock
-----------

Sprint 18 is strictly **messages only**.

The only real package introduced by this sprint is expected to be:

``lifecore_state/lifecore_state_msgs/``

The parent ``lifecore_state/`` folder remains a repository-level logical folder.
It must not contain ``package.xml``, ``CMakeLists.txt``, Python package metadata,
or installable code.

Context inherited from Sprint 17
--------------------------------

Sprint 17 accepted these direction-setting decisions:

- ``lifecore_state/`` is a logical repository folder, not a ROS 2 package.
- ``lifecore_state_msgs`` is the first real package.
- ``lifecore_state_core`` is deferred.
- ``lifecore_state_ros`` is deferred.
- ``lifecore_ros2`` must remain independent from ``lifecore_state``.
- ``StateDescription`` is a versioned collection of ``StateDescriptor`` entries.
- ``StateCommand`` v0 is single-target.
- Batched commands are deferred.
- ``StateCommand`` expresses intent.
- ``StateUpdate`` reports observed truth.

Goal
----

Create a minimal ROS 2 interface package:

``lifecore_state/lifecore_state_msgs/``

This sprint should answer whether the ``lifecore_state`` ROS 2 message
contracts are coherent, compilable, readable, and aligned with the Sprint 17
RFC.

Expected package shape
----------------------

.. code-block:: text

    lifecore_state/
      lifecore_state_msgs/
        package.xml
        CMakeLists.txt
        msg/
          StateDescriptor.msg
          StateDescription.msg
          StateSample.msg
          StateUpdate.msg
          StateCommand.msg

Expected package name
---------------------

``lifecore_state_msgs``

Expected build type
-------------------

Use a standard ROS 2 interface package setup with
``rosidl_default_generators``.

Expected dependencies
---------------------

The dependency set should stay minimal. Candidate dependencies are:

- ``std_msgs``
- ``unique_identifier_msgs``
- ``builtin_interfaces`` only if needed beyond ``std_msgs/Header``
- ``rosidl_default_generators``
- ``rosidl_default_runtime``

Messages to create
------------------

- ``StateDescriptor.msg``
- ``StateDescription.msg``
- ``StateSample.msg``
- ``StateUpdate.msg``
- ``StateCommand.msg``

Optional enum-like messages should be added only if Sprint 18 explicitly decides
that embedded constants are too unclear or too repetitive:

- ``StateType.msg``
- ``StateQuality.msg``
- ``StateDirection.msg``
- ``StateSource.msg``
- ``StateUpdateMode.msg``

Default recommendation: keep constants embedded in primary messages for the v0
ABI prototype.

Message contracts
-----------------

``StateDescriptor``
  Defines one state field contract. It describes identity, type, direction,
  human metadata, constraints, writability, safety relevance, and persistence.
  It must not contain the current runtime value.

``StateDescription``
  Defines a versioned collection of ``StateDescriptor`` entries. It carries a
  schema UUID, description version, and descriptor list.

``StateSample``
  Defines one observed state value at a source timestamp. Its ``header.stamp``
  is the source observation timestamp, and ``type`` selects exactly one explicit
  variant value field.

``StateUpdate``
  Defines a published batch of observed ``StateSample`` values. Its
  ``header.stamp`` is the publish/batch timestamp. It carries ``source_uuid``,
  ``schema_uuid``, ``sequence``, ``description_version``, ``update_mode``, and
  ``samples``.

``StateCommand``
  Defines one requested mutation for one target descriptor. It expresses intent,
  not observed truth. Batched command semantics are deferred.

Strict non-goals
----------------

Do not create or implement:

- ``lifecore_state_core``
- ``lifecore_state_ros``
- ``StateRegistry``
- ``StateProjection``
- ``StatePublisher``
- ``StateSubscriber``
- ``DescriptionSubscriber``
- ``CommandSubscriber``
- lifecycle integration
- CLI tools
- code generation
- runtime behavior tests
- factories, managers, EventBus, ECS, orchestration, or plugin systems

Do not modify existing ``lifecore_ros2`` runtime behavior.

Sub-sprints
-----------

Sprint 18 is organized into focused execution cards under
:doc:`../sprint_18_substeps/README`.

**Current sub-sprint.** Sprint 18.6 - Define StateUpdate.msg is active.

Recommended execution order:

1. Sprint 18.1 - Pre-flight Check — archived
2. Sprint 18.2 - Package Scaffold — archived
3. Sprint 18.3 - Define StateDescriptor.msg — archived
4. Sprint 18.4 - Define StateDescription.msg — :doc:`archived/sprint_18_4_state_description`
5. Sprint 18.5 - Define StateSample.msg — :doc:`archived/sprint_18_5_state_sample`
6. Sprint 18.6 - Define StateUpdate.msg — :doc:`archived/sprint_18_6_state_update` (completed)
7. Sprint 18.7 - Define StateCommand.msg — :doc:`sprint_18_7_state_command` (active)
8. Sprint 18.8 - Constants Decision
9. Sprint 18.9 - Build Validation
10. Sprint 18.10 - Documentation Consistency Pass
11. Sprint 18.11 - Main Sprint Planning File
12. Sprint 18.12 - Pull Request Description
13. Sprint 18.13 - Final Review

Deliverables
------------

- ``lifecore_state/lifecore_state_msgs/package.xml``
- ``lifecore_state/lifecore_state_msgs/CMakeLists.txt``
- ``lifecore_state/lifecore_state_msgs/msg/StateDescriptor.msg``
- ``lifecore_state/lifecore_state_msgs/msg/StateDescription.msg``
- ``lifecore_state/lifecore_state_msgs/msg/StateSample.msg``
- ``lifecore_state/lifecore_state_msgs/msg/StateUpdate.msg``
- ``lifecore_state/lifecore_state_msgs/msg/StateCommand.msg``
- ``lifecore_state/rfcs/sprint_18_preflight_check.rst``
- ``lifecore_state/rfcs/sprint_18_package_scaffold.rst``
- ``lifecore_state/rfcs/sprint_18_message_notes.rst`` (Sprint 18.3 - StateDescriptor)
- ``lifecore_state/rfcs/sprint_18_4_state_description_design_notes.rst`` (Sprint 18.4 - StateDescription)
- ``lifecore_state/rfcs/sprint_18_5_state_sample_design_notes.rst`` (Sprint 18.5 - StateSample)
- ``lifecore_state/rfcs/sprint_18_constants_decision.rst``
- ``lifecore_state/rfcs/sprint_18_build_validation.rst``
- ``lifecore_state/rfcs/sprint_18_docs_consistency_review.rst``
- ``lifecore_state/rfcs/sprint_18_pr_description.md``
- ``lifecore_state/rfcs/sprint_18_final_review.rst``

Acceptance criteria
-------------------

- [x] ``lifecore_state/lifecore_state_msgs`` exists as a real ROS 2 package. (Sprint 18.2)
- [x] ``lifecore_state/`` parent has no ``package.xml``. (Sprint 18.2)
- [ ] Messages compile with ``colcon``. (Sprint 18.9)
- [x] No runtime Python code is added. (Verified)
- [x] No ``lifecore_state_core`` package is created. (Verified)
- [x] No ``lifecore_state_ros`` package is created. (Verified)
- [x] No registry, projection, publisher, subscriber, or command handling
      behavior is implemented. (Verified)
- [x] Message semantics match Sprint 17 docs. (Verified)
- [ ] ``StateCommand`` v0 is single-target. (Sprint 18.7 — active)
- [ ] Batched commands are deferred. (Sprint 18.7 — active)
- [x] ``StateDescription`` is a versioned collection of ``StateDescriptor``
      entries. (Sprint 18.4 completed)
- [x] ``StateUpdate`` contains ``sequence``, ``description_version``, and
      ``update_mode``. (Sprint 18.6 completed)
- [x] ``StateSample`` carries type, quality, source, timestamp, and explicit
      variant fields. (Sprint 18.5 completed)
- [ ] ``StateCommand`` is documented as intent, not observed truth. (Sprint 18.7 — active)
- [ ] Documentation consistency review is complete. (Sprint 18.10)

Open questions
--------------

- Whether embedded constants remain clear enough for the v0 ABI prototype.
- Whether ``builtin_interfaces`` is needed directly or only through
  ``std_msgs/Header``.
- Whether future compact update formats are needed after the readable ABI is
  reviewed.
- Which command feedback shape, if any, should be considered after Sprint 18.

Final review
------------

Sprint 18 is accepted only after the final review confirms structure, build,
message semantics, scope control, documentation consistency, and remaining ABI
risks.

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
