Sprint 17.10 Consistency Review
===============================

Status
------

Completed, awaiting validation.

Purpose
-------

This document records the Sprint 17.10 documentary consistency pass across the
Sprint 17 ``lifecore_state`` architecture documents. The review checks that
terminology, package boundaries, message semantics, lifecycle/state separation,
anti-goals, open questions, and mandatory review phrases agree before final
Sprint 17 review.

Scope of review
---------------

Reviewed documents:

- ``docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst``;
- ``lifecore_state/README.rst``;
- ``lifecore_state/rfcs/README.rst``;
- ``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst``;
- ``lifecore_state/terminology.rst``;
- ``lifecore_state/message_semantics.rst``;
- ``lifecore_state/lifecycle_state_separation.rst``;
- ``lifecore_state/anti_goals.rst``;
- ``lifecore_state/package_boundaries.rst``.

The review also checked the Sprint 17.10 planning card because it records the
acceptance criteria for this pass.

Terminology audit
-----------------

The weak or ambiguous terms from the Sprint 17.10 brief were searched across
the reviewed documents.

.. list-table::
   :header-rows: 1

   * - Term
     - Instances found
     - Intended meaning
     - Action
   * - ``SmartValue``
     - None in reviewed deliverables.
     - Not applicable.
     - No correction needed.
   * - ``Register``
     - None as a weak standalone architecture term. ``register_component()`` is
       an existing ``lifecore_ros2`` API reference, and ``auto-register`` appears
       only as an explicitly rejected anti-pattern.
     - Existing API name or rejected automatic registration behavior.
     - Kept.
   * - ``CommManager``
     - None in reviewed deliverables.
     - Not applicable.
     - No correction needed.
   * - ``Manager``
     - Present only in anti-pattern or warning contexts: ``giant managers``,
       ``hidden lifecycle manager``, ``StateManager``, and the glossary warning
       for ``Manager``.
     - Rejected broad runtime or warning vocabulary.
     - Kept because each occurrence explicitly rejects the pattern.

No terminology replacement was required. The accepted vocabulary remains
``StateDescriptor``, ``StateDescription``, ``StateSample``, ``StateUpdate``,
``StateCommand``, ``StateRegistry``, ``StateProjection``, ``StateSnapshot``,
``StateDelta``, and ``StateQuality``.

Architectural consistency
-------------------------

The reviewed documents consistently state that ``lifecore_state/`` is a
documentation-only logical folder during Sprint 17. They do not present it as a
ROS 2 package, a Python runtime package, a functional package, or an installed
submodule of ``lifecore_ros2``.

Verified architectural points:

- ``lifecore_state/`` remains a root-level documentation group.
- The parent folder must not contain ``package.xml``.
- No ``CMakeLists.txt``, ``pyproject.toml``, Python runtime module, ``.msg``,
  ``.srv``, or ``.action`` file exists in the folder.
- The future split is consistently named as ``lifecore_state_msgs``,
  ``lifecore_state_core``, and ``lifecore_state_ros``.
- ``lifecore_ros2`` remains independent from future ``lifecore_state`` packages
  by default.
- ``lifecore_state_core`` is consistently described as pure Python with no
  ROS 2, ``rclpy``, or ``lifecore_ros2`` dependency.

Message semantic consistency
----------------------------

Message semantics are aligned across the RFC, terminology, and message
semantics documents.

Verified message points:

- ``StateCommand`` is always requested intent, not observed truth.
- ``StateUpdate`` carries observed truth or synchronization events for observed
  changes, not command intent.
- ``StateDescriptor`` defines a field or stream contract.
- ``StateDescription`` is a versioned set of descriptors and metadata, not live
  observed truth.
- Snapshot and delta semantics remain distinct: snapshots are complete for a
  declared scope, while deltas require continuity from a known prior state.
- ``sequence`` and ``description_version`` are explained as separate ordering
  and schema-compatibility mechanisms.

Lifecycle/state consistency
---------------------------

Lifecycle/state separation is consistent across the main sprint coordinator,
RFC, message semantics, lifecycle separation, anti-goals, and package boundary
documents.

Verified lifecycle points:

- ``StateDescription`` metadata may be cached while inactive.
- ``StateUpdate`` deltas are not applied while inactive.
- Snapshot-like inactive refresh is optional and narrower than a global live
  update rule.
- ``StateCommand`` handling requires active lifecycle readiness.
- Active lifecycle state is not proof of valid state.
- Valid state is not proof of active lifecycle state.
- No document introduces a hidden lifecycle manager, parallel lifecycle state
  machine, or automatic recovery/orchestration behavior.

Anti-pattern consistency
------------------------

The anti-patterns mentioned in RFC 001 are reflected in
``lifecore_state/anti_goals.rst``.

Verified anti-pattern points:

- No robotics operating system direction.
- No global orchestration runtime.
- No hidden synchronization framework.
- No giant ECS platform.
- No EventBus architecture.
- No plugin framework.
- No factory/spec system as the primary construction path.
- No codegen-first design.
- No giant ``StateManager``.
- No magical ``StateField``.
- No automatic publish-on-set in core.
- No auto-register unknown fields by default.
- No command-as-truth semantics.
- No lifecycle or ROS 2 contamination in ``lifecore_state_core``.

The review found no place where a giant manager, magic observable, automatic
registration, or codegen-first path was suggested as an accepted direction.

Open question consistency
-------------------------

The only open-question sections are in RFC 001 and
``lifecore_state/message_semantics.rst``. Before this pass, they overlapped but
were not synchronized. This pass replaced both lists with the same shared set of
open questions covering descriptor identity, ABI versus pure semantics fields,
compact samples, command feedback, quality representation, delta continuity,
version compatibility, timestamp naming, projection declaration, and whether
``StateStore`` or ``StateMirror`` need explicit Sprint 18 terminology.

There are no orphaned open questions after this correction.

Mandatory phrase consistency
----------------------------

The required phrase is:

    ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.

Before this pass, RFC 001 ended with a Sprint-specific variant that said
``Sprint 17.3``. The main Sprint 17 coordinator also ended with the phrase in
quotation marks, and the Sprint 17.10 planning card did not end with the phrase.

Corrections applied:

- RFC 001 now ends with the exact mandatory Sprint 17 phrase.
- The main Sprint 17 coordinator now ends with the exact phrase without quotes.
- The Sprint 17.10 planning card now ends with the exact phrase.
- The new consistency report ends with the exact phrase.

Problems found and corrections applied
--------------------------------------

.. list-table::
   :header-rows: 1

   * - Problem
     - Documents affected
     - Correction
     - Impact
   * - Mandatory phrase variant used ``Sprint 17.3``.
     - ``lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst``
     - Replaced with the exact Sprint 17 mandatory phrase.
     - Removes a review-gate inconsistency.
   * - Mandatory phrase formatting included trailing quotation marks.
     - ``docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst``
     - Rewrote the ending so the document ends with the exact phrase.
     - Makes automated or manual phrase checks simpler.
   * - Sprint 17.10 planning card did not end with the mandatory phrase.
     - ``docs/planning/sprints/active/sprint_17_10_consistency.rst``
     - Added implementation notes and a review requirement ending with the exact
       phrase.
     - Keeps the execution card consistent with the reviewed deliverables.
   * - Open questions overlapped but did not match exactly.
     - RFC 001 and ``lifecore_state/message_semantics.rst``
     - Replaced both lists with the same shared open-question set.
     - Removes orphaned questions before Sprint 18 planning.
   * - Consistency report was missing.
     - ``lifecore_state/rfcs/``
     - Added this report and linked it from ``lifecore_state/rfcs/README.rst``;
       updated the root folder layout in ``lifecore_state/README.rst``.
     - Completes the Sprint 17.10 deliverable.

Remaining inconsistencies
-------------------------

No unresolved documentary inconsistencies remain in the reviewed scope.

The remaining open questions are design questions for review and Sprint 18
entry planning, not contradictions between Sprint 17 documents.

Recommendations for future review
---------------------------------

Peer review should prioritize:

- the shared open-question list in RFC 001 and ``message_semantics.rst``;
- descriptor identity and compact-ID strategy;
- ``description_version`` compatibility rules;
- delta continuity and resynchronization semantics;
- command feedback shape;
- the optional inactive snapshot-like refresh policy;
- the formal package split between ``lifecore_state_msgs``,
  ``lifecore_state_core``, and ``lifecore_state_ros``.

Formal sign-off should happen before Sprint 18 on these decisions:

- whether Sprint 18 starts with message ABI only or also sketches pure Python
  semantics;
- whether ``StateStore`` and ``StateMirror`` become accepted terminology;
- whether command feedback belongs in messages, services, or actions;
- which compatibility rules apply to descriptor and description versioning.

Validation summary
------------------

This pass was documentation-only. It did not add runtime code, Python modules,
ROS interfaces, package metadata, tests, or examples.

Manual checks completed:

- reviewed the required Sprint 17 documents;
- searched for weak terminology;
- checked mandatory phrase presence;
- checked open-question sections;
- checked forbidden package metadata references and actual file presence under
  ``lifecore_state/``.

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.