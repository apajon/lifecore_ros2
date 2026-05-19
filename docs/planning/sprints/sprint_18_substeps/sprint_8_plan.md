Voici les **prompts suivants** pour ton agent de coding, orientés **Sprint 18 lifecore_state_msgs ABI prototype**.

Objectif : créer uniquement le package ROS 2 de messages, aligné avec Sprint 17. Pas de core Python, pas de registry, pas de publishers/subscribers.

---

# Sprint 18 — Plan global

```text
Sprint 18 - lifecore_state_msgs ABI prototype

Context
=======

Sprint 17 closed the architecture/RFC phase for the future lifecore_state direction.

The accepted direction is:

- lifecore_state/ is a repository-level logical folder, not a ROS 2 package.
- lifecore_state_msgs will be the first real package.
- lifecore_state_core is deferred.
- lifecore_state_ros is deferred.
- lifecore_ros2 must remain independent from lifecore_state.
- StateDescription is a versioned collection of StateDescriptor entries.
- StateCommand v0 is single-target.
- Batched commands are deferred.
- StateCommand expresses intent.
- StateUpdate reports observed truth.

This sprint is NOT an implementation of lifecore_state runtime behavior.

Goal
====

Create a minimal ROS 2 message package:

  lifecore_state/lifecore_state_msgs/

The package must define the first prototype ABI for lifecore_state messages.

This sprint should answer:

  Are the lifecore_state ROS 2 message contracts coherent, compilable,
  readable, and aligned with the Sprint 17 RFC?

Strict non-goals
================

Do NOT:

- create lifecore_state_core;
- create lifecore_state_ros;
- implement StateRegistry;
- implement StateProjection;
- implement StatePublisher;
- implement StateSubscriber;
- implement DescriptionSubscriber;
- implement CommandSubscriber;
- implement lifecycle integration;
- implement CLI tools;
- implement code generation;
- implement tests for runtime behavior;
- add factories, managers, EventBus, ECS, orchestration, or plugin systems.

Allowed changes
===============

You may:

- create lifecore_state/lifecore_state_msgs/;
- create package.xml;
- create CMakeLists.txt;
- create msg/*.msg files;
- update documentation references if needed;
- add build/lint configuration only if consistent with the repository conventions;
- run colcon build to verify message generation.

Expected output
===============

A new ROS 2 interface package containing prototype messages:

- StateDescriptor.msg
- StateDescription.msg
- StateSample.msg
- StateUpdate.msg
- StateCommand.msg

Optional only if justified:

- StateType.msg
- StateQuality.msg
- StateDirection.msg
- StateSource.msg
- StateUpdateMode.msg

Prefer embedded constants in the primary messages unless separate enum-like messages are clearly better.

Acceptance criteria
===================

- lifecore_state/lifecore_state_msgs exists as a real ROS 2 package.
- lifecore_state/ parent still has no package.xml.
- messages compile with colcon.
- no runtime Python code is added.
- no lifecore_state_core package is created.
- no lifecore_state_ros package is created.
- no registry or publisher/subscriber behavior is implemented.
- message semantics match Sprint 17 docs.
- StateCommand v0 is single-target.
- StateDescription is a versioned collection of StateDescriptor entries.
- StateUpdate contains sequence, description_version, update_mode.
- StateSample carries type, quality, source, timestamp, and explicit variant fields.
- StateCommand is documented as intent, not observed truth.

Final note
==========

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.1 — Pré-audit avant création du package

```text
You are working in the lifecore_ros2 repository.

Task
====

Perform a pre-implementation audit for Sprint 18.

Sprint 18 goal:
Create only the lifecore_state_msgs ROS 2 message package under:

  lifecore_state/lifecore_state_msgs/

Before creating files, inspect the repository and identify:

1. existing ROS 2 package layout conventions;
2. existing package.xml style;
3. existing CMakeLists.txt style, if any;
4. existing interface/message packages, if any;
5. existing lint/test conventions;
6. where lifecore_state/ currently lives;
7. whether lifecore_state/ parent has package.xml;
8. whether the Sprint 17 docs already mention lifecore_state_msgs.

Constraints
===========

Do not create or modify files yet.

Do not implement runtime code.

Do not create lifecore_state_core or lifecore_state_ros.

Do not create .msg files during this audit step.

Expected deliverable
====================

Create or update:

  lifecore_state/rfcs/sprint_18_pre_audit.rst

The document must contain:

- observed repository/package conventions;
- proposed package path;
- proposed package name;
- proposed build type;
- proposed dependencies;
- risks before implementation;
- confirmation that lifecore_state/ parent is not a ROS package;
- confirmation that Sprint 18 remains messages-only.

Recommended conclusion
======================

The expected implementation path is:

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

Final sentence
==============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.2 — Créer le package `lifecore_state_msgs`

```text
You are working in the lifecore_ros2 repository.

Task
====

Create the ROS 2 interface package:

  lifecore_state/lifecore_state_msgs/

This is the first real lifecore_state package.

Important architecture decision
===============================

The parent folder:

  lifecore_state/

is a repository-level logical folder only.

It must NOT contain:

- package.xml
- CMakeLists.txt
- Python package metadata
- installable code

Only the child folder:

  lifecore_state/lifecore_state_msgs/

becomes a ROS 2 package.

Package responsibilities
========================

lifecore_state_msgs defines ROS 2 message contracts only.

It must not contain:

- Python runtime logic;
- registry logic;
- lifecycle logic;
- publisher/subscriber code;
- QoS code;
- command handling logic;
- state synchronization logic.

Create
======

Create:

  lifecore_state/lifecore_state_msgs/package.xml
  lifecore_state/lifecore_state_msgs/CMakeLists.txt
  lifecore_state/lifecore_state_msgs/msg/

Use package conventions consistent with the repository and ROS 2 Jazzy.

Expected package name
=====================

  lifecore_state_msgs

Expected build type
===================

Use a standard ROS 2 interface package setup with:

  rosidl_default_generators

Expected dependencies
=====================

At minimum, consider:

- std_msgs
- unique_identifier_msgs
- builtin_interfaces if needed
- rosidl_default_generators
- rosidl_default_runtime

Do not add unnecessary dependencies.

Message files
=============

Do not populate the final message content yet if this step is only package scaffolding.

If creating placeholder files, keep them minimal and immediately follow with the next step.

Constraints
===========

Do not create lifecore_state_core.

Do not create lifecore_state_ros.

Do not modify lifecore_ros2 runtime code.

Do not add Python modules.

Do not add publishers/subscribers.

Do not modify existing package behavior.

Validation
==========

After creating the package scaffolding, verify that the repository still has:

- no package.xml directly under lifecore_state/;
- one package.xml under lifecore_state/lifecore_state_msgs/;
- no runtime Python code under lifecore_state/.

Update or create:

  lifecore_state/rfcs/sprint_18_package_scaffold.rst

Document:

- files created;
- dependencies chosen;
- why this is messages-only;
- what remains deferred.

Final sentence
==============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.3 — Définir `StateDescriptor.msg`

```text
You are working in the lifecore_ros2 repository.

Task
====

Create the message:

  lifecore_state/lifecore_state_msgs/msg/StateDescriptor.msg

Purpose
=======

StateDescriptor defines one state field contract.

It describes what a field is.

It must not contain the current runtime value.

StateDescriptor answers:

  What is this field?
  What is its identity?
  What is its type?
  What is its direction?
  Is it writable?
  What metadata helps humans and tools interpret it?

It does NOT answer:

  What is the current observed value?

Required semantics
==================

StateDescriptor must include:

- compact numeric id;
- stable UUID;
- canonical key;
- type;
- direction;
- human-readable metadata;
- optional constraints;
- writable flag;
- safety-related flag;
- persistent flag if useful.

Recommended fields
==================

Use a ROS 2 .msg-compatible structure similar to:

  std_msgs/Header header

  uint32 id
  unique_identifier_msgs/UUID uuid
  string key

  uint8 type
  uint8 direction

  string display_name
  string description
  string group
  string unit

  bool writable
  bool safety_related
  bool persistent

  float64 min_value
  float64 max_value
  bool has_min_value
  bool has_max_value

Constants
=========

Include type constants unless separate enum messages are introduced:

  uint8 TYPE_UNKNOWN=0
  uint8 TYPE_BOOL=1
  uint8 TYPE_INT64=2
  uint8 TYPE_UINT64=3
  uint8 TYPE_FLOAT64=4
  uint8 TYPE_STRING=5

Include direction constants:

  uint8 DIR_UNKNOWN=0
  uint8 DIR_INPUT=1
  uint8 DIR_OUTPUT=2
  uint8 DIR_INOUT=3
  uint8 DIR_INTERNAL=4

Important design constraints
============================

Do NOT include current value fields in StateDescriptor.

Do NOT include default_value unless clearly justified.

Do NOT use JSON strings.

Do NOT add arbitrary metadata maps.

Do NOT add command semantics here.

Do NOT add lifecycle semantics here.

If default value is considered, leave it deferred and document as an open question.

Documentation
=============

Update:

  lifecore_state/message_semantics.rst

if the actual .msg differs from the documented sketch.

Update:

  lifecore_state/rfcs/sprint_18_message_notes.rst

with rationale for this message.

Final sentence
==============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.4 — Définir `StateDescription.msg`

```text
You are working in the lifecore_ros2 repository.

Task
====

Create the message:

  lifecore_state/lifecore_state_msgs/msg/StateDescription.msg

Purpose
=======

StateDescription is a versioned collection of StateDescriptor entries.

It represents a coherent schema/scope description.

It is not one descriptor.
It is not runtime state.
It is not a state value.
It is not a command.

Required semantics
==================

StateDescription must include:

- header;
- schema UUID;
- description version;
- list of StateDescriptor entries.

Recommended fields
==================

Use a ROS 2 .msg-compatible structure similar to:

  std_msgs/Header header

  unique_identifier_msgs/UUID schema_uuid
  uint64 description_version

  StateDescriptor[] descriptors

Semantics
=========

- header.stamp is the time this description was published or generated.
- schema_uuid identifies the schema/scope.
- description_version increments when the descriptor set or descriptor meaning changes.
- descriptors contains the coherent collection of StateDescriptor entries.

QoS note
========

Do not implement QoS in this package.

But documentation should say StateDescription is intended for:

- reliable
- transient_local
- keep_last(1)

Lifecycle note
==============

StateDescription may be received and cached while a lifecycle node/component is inactive.

This is required because transient_local delivery may occur as soon as a subscription is created during configure.

Constraints
===========

Do NOT add runtime sample values.

Do NOT add command values.

Do NOT add registry logic.

Do NOT add QoS code.

Do NOT split into StateDescriptionArray unless there is a strong reason.

Documentation
=============

Ensure all docs consistently say:

  StateDescription = versioned collection of StateDescriptor entries.

Update:

  lifecore_state/message_semantics.rst
  lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst
  lifecore_state/rfcs/sprint_18_message_notes.rst

Final sentence
==============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.5 — Définir `StateSample.msg`

```text
You are working in the lifecore_ros2 repository.

Task
====

Create the message:

  lifecore_state/lifecore_state_msgs/msg/StateSample.msg

Purpose
=======

StateSample represents one observed state value at a source timestamp.

It is runtime truth as observed by a source, but only for one field.

It is not metadata.
It is not a descriptor.
It is not a command.

Required semantics
==================

StateSample must include:

- header;
- descriptor identity reference;
- type;
- quality;
- source;
- explicit variant value fields.

Recommended fields
==================

Use a ROS 2 .msg-compatible structure similar to:

  std_msgs/Header header

  uint32 descriptor_id
  unique_identifier_msgs/UUID descriptor_uuid
  string key

  uint8 type
  uint8 quality
  uint8 source

  bool bool_value
  int64 int_value
  uint64 uint_value
  float64 float_value
  string string_value

Timestamp semantics
===================

StateSample.header.stamp is the source timestamp.

It means:

  the time when this value was true or observed at the source.

It is not necessarily the publication time of the containing StateUpdate.

Variant semantics
=================

type selects exactly one active value field.

Examples:

- TYPE_BOOL uses bool_value
- TYPE_INT64 uses int_value
- TYPE_UINT64 uses uint_value
- TYPE_FLOAT64 uses float_value
- TYPE_STRING uses string_value

Never interpret multiple value fields at the same time.

Quality constants
=================

Include quality constants unless separate enum messages are created:

  uint8 QUALITY_UNKNOWN=0
  uint8 QUALITY_VALID=1
  uint8 QUALITY_STALE=2
  uint8 QUALITY_INVALID=3
  uint8 QUALITY_COMM_ERROR=4
  uint8 QUALITY_OUT_OF_RANGE=5
  uint8 QUALITY_FORCED=6
  uint8 QUALITY_SIMULATED=7
  uint8 QUALITY_DISABLED=8
  uint8 QUALITY_NOT_AVAILABLE=9

Source constants
================

Include source constants unless separate enum messages are created:

  uint8 SOURCE_UNKNOWN=0
  uint8 SOURCE_HARDWARE=1
  uint8 SOURCE_SOFTWARE=2
  uint8 SOURCE_SIMULATION=3
  uint8 SOURCE_OPERATOR=4
  uint8 SOURCE_REPLAY=5

Type constants
==============

To avoid duplication, evaluate whether StateSample should repeat TYPE_* constants or whether type constants should live in a separate StateType.msg.

If no separate StateType.msg is created, include TYPE_* constants consistently.

Important constraints
=====================

Do NOT add metadata.

Do NOT add descriptor fields such as unit or description.

Do NOT add command semantics.

Do NOT add lifecycle semantics.

Do NOT add callback or registry behavior.

Documentation
=============

Update:

  lifecore_state/message_semantics.rst
  lifecore_state/rfcs/sprint_18_message_notes.rst

Final sentence
==============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.6 — Définir `StateUpdate.msg`

```text
You are working in the lifecore_ros2 repository.

Task
====

Create the message:

  lifecore_state/lifecore_state_msgs/msg/StateUpdate.msg

Purpose
=======

StateUpdate represents a published batch of observed StateSample values.

It reports observed truth.

It does not express requested mutation.
It is not a command.
It is not a descriptor list.

Required semantics
==================

StateUpdate must include:

- header;
- source UUID;
- schema UUID;
- sequence;
- description version;
- update mode;
- array of StateSample entries.

Recommended fields
==================

Use a ROS 2 .msg-compatible structure similar to:

  std_msgs/Header header

  unique_identifier_msgs/UUID source_uuid
  unique_identifier_msgs/UUID schema_uuid

  uint64 sequence
  uint64 description_version
  uint8 update_mode

  StateSample[] samples

  uint8 UPDATE_UNKNOWN=0
  uint8 UPDATE_FULL=1
  uint8 UPDATE_DELTA=2

Timestamp semantics
===================

StateUpdate.header.stamp is the publish/batch timestamp.

Each StateSample.header.stamp is the source observation timestamp.

These timestamps may differ.

Sequence semantics
==================

sequence is per source_uuid stream.

It is used to detect:

- lost updates;
- duplicated updates;
- out-of-order updates;
- stream discontinuity.

Description version semantics
=============================

description_version identifies the StateDescription version used to interpret descriptor ids, types, and semantics.

If a receiver has a different description_version, it must not blindly apply the update.

Update mode semantics
=====================

UPDATE_FULL:

- contains a complete snapshot for the publisher’s scope;
- useful for startup, resynchronization, debugging.

UPDATE_DELTA:

- contains only changed samples;
- assumes receiver has compatible prior state;
- should not be applied after unknown history unless sequence/schema checks allow it.

Lifecycle semantics
===================

Do not implement lifecycle behavior here.

But documentation must preserve:

- delta updates should not be applied while inactive;
- full snapshots may be cached while inactive only by explicit policy.

Constraints
===========

Do NOT add command fields.

Do NOT add registry behavior.

Do NOT add QoS implementation.

Do NOT add lifecycle implementation.

Documentation
=============

Update:

  lifecore_state/message_semantics.rst
  lifecore_state/rfcs/sprint_18_message_notes.rst

Final sentence
==============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.7 — Définir `StateCommand.msg`

```text
You are working in the lifecore_ros2 repository.

Task
====

Create the message:

  lifecore_state/lifecore_state_msgs/msg/StateCommand.msg

Purpose
=======

StateCommand v0 represents a single-target requested mutation.

It expresses intent.

It is not observed truth.

Batched command semantics are explicitly deferred until a concrete future need reopens the decision.

Required semantics
==================

StateCommand must include:

- header;
- source UUID;
- target UUID;
- schema UUID;
- sequence;
- description version;
- target descriptor identity;
- type;
- desired value as explicit variant fields.

Recommended fields
==================

Use a ROS 2 .msg-compatible structure similar to:

  std_msgs/Header header

  unique_identifier_msgs/UUID source_uuid
  unique_identifier_msgs/UUID target_uuid
  unique_identifier_msgs/UUID schema_uuid

  uint64 sequence
  uint64 description_version

  uint32 target_descriptor_id
  unique_identifier_msgs/UUID target_descriptor_uuid
  string target_key

  uint8 type

  bool bool_value
  int64 int_value
  uint64 uint_value
  float64 float_value
  string string_value

Semantics
=========

StateCommand means:

  I request this target field to change to this desired value.

It does not mean:

  this value is already true.

Command acceptance
==================

Acceptance or rejection is not encoded by StateCommand itself.

Future feedback may be represented through:

- StateUpdate reflecting observed change;
- service response;
- action feedback;
- dedicated command status message.

Do not implement feedback in Sprint 18 unless already explicitly scoped.

Validation expectations
=======================

Future receivers should validate commands against:

- known descriptor;
- type match;
- writable flag;
- direction;
- description_version;
- target ownership;
- lifecycle active state.

But do not implement this validation in Sprint 18.

Variant semantics
=================

type selects exactly one active value field.

Lifecycle semantics
===================

StateCommand should require active runtime behavior.

Commands received while inactive should be rejected or ignored according to explicit policy.

Do not implement this behavior in the message package.

Constraints
===========

Do NOT make StateCommand a batch.

Do NOT include StateSample[] in v0.

Do NOT describe command as truth.

Do NOT implement command handling logic.

Do NOT add lifecycle behavior.

Do NOT add registry behavior.

Documentation
=============

Update:

  lifecore_state/message_semantics.rst
  lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst
  lifecore_state/rfcs/sprint_18_message_notes.rst

Ensure docs say:

  StateCommand v0 is single-target.
  Batched commands are deferred.

Final sentence
==============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.8 — Choisir constantes embarquées ou messages enum séparés

```text
You are working in the lifecore_ros2 repository.

Task
====

Review the message constants used by lifecore_state_msgs and decide whether to keep constants embedded in primary messages or extract enum-like messages.

Context
=======

Possible constants include:

- type constants;
- quality constants;
- direction constants;
- source constants;
- update mode constants.

Options
=======

Option A:
Keep constants embedded in messages:

- TYPE_* in StateDescriptor / StateSample / StateCommand
- QUALITY_* in StateSample
- DIR_* in StateDescriptor
- SOURCE_* in StateSample
- UPDATE_* in StateUpdate

Option B:
Create enum-like messages:

- StateType.msg
- StateQuality.msg
- StateDirection.msg
- StateSource.msg
- StateUpdateMode.msg

Decision criteria
=================

Prefer Option A if:

- the message set remains simple;
- duplication is acceptable;
- readability is good;
- users do not need to import separate constants;
- ABI prototype should remain minimal.

Prefer Option B if:

- constants are repeated too much;
- future tools will need common symbolic definitions;
- generated code readability improves;
- consistency outweighs file count.

Sprint 18 recommendation
========================

For v0, prefer embedded constants unless duplication becomes clearly ugly.

Do not over-engineer enum-like messages prematurely.

Deliverable
===========

Create or update:

  lifecore_state/rfcs/sprint_18_constants_decision.rst

The document must include:

- chosen option;
- rationale;
- alternatives considered;
- impact on message files;
- deferred decisions.

If files are changed, update them consistently.

Constraints
===========

Do not add runtime code.

Do not add lifecore_state_core.

Do not add lifecore_state_ros.

Do not introduce code generation.

Final sentence
==============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.9 — Build et validation colcon

```text
You are working in the lifecore_ros2 repository.

Task
====

Build and validate the Sprint 18 lifecore_state_msgs package.

Validation goals
================

Verify that:

1. lifecore_state/lifecore_state_msgs is discovered as a ROS 2 package.
2. lifecore_state/ parent is not discovered as a package.
3. messages generate successfully.
4. colcon build succeeds.
5. no runtime Python package was accidentally added.
6. no lifecore_state_core or lifecore_state_ros package exists.
7. no existing lifecore_ros2 package behavior was modified.
8. package.xml dependencies are minimal and correct.
9. CMakeLists.txt uses standard rosidl generation patterns.
10. generated interfaces are importable/visible according to normal ROS 2 tooling if the environment allows it.

Commands to consider
====================

Use commands appropriate to the repository environment, for example:

  colcon list
  colcon build --packages-select lifecore_state_msgs
  colcon test --packages-select lifecore_state_msgs
  colcon test-result --verbose

If the environment does not support full ROS 2 build, document exactly what could not be run and why.

Deliverable
===========

Create:

  lifecore_state/rfcs/sprint_18_build_validation.rst

Include:

- commands run;
- results;
- failures if any;
- warnings;
- generated package discovery results;
- confirmation of no parent package;
- confirmation of no runtime implementation.

Constraints
===========

Do not implement missing runtime code to satisfy build.

Do not create unrelated packages.

Do not change lifecore_ros2 behavior.

Final sentence
==============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.10 — Cohérence docs après création des messages

```text
You are working in the lifecore_ros2 repository.

Task
====

Perform a documentation consistency pass after creating lifecore_state_msgs.

Documents to review
===================

- lifecore_state/README.rst
- lifecore_state/message_semantics.rst
- lifecore_state/package_boundaries.rst
- lifecore_state/lifecycle_state_separation.rst
- lifecore_state/anti_goals.rst
- lifecore_state/terminology.rst
- lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst
- docs/planning/sprints/sprint_18_lifecore_state_msgs.rst if it exists

Check consistency for
=====================

1. StateDescription is always a versioned collection of StateDescriptor entries.
2. StateCommand v0 is always single-target.
3. Batched commands are always deferred.
4. StateCommand is always intent, not truth.
5. StateUpdate is observed truth.
6. StateSample carries source timestamp semantics.
7. StateUpdate carries publish/batch timestamp semantics.
8. StateUpdate has sequence, description_version, update_mode.
9. StateDescription has schema_uuid and description_version.
10. StateDescriptor does not carry current runtime value.
11. lifecore_state_msgs is now a real package.
12. lifecore_state_core is still deferred.
13. lifecore_state_ros is still deferred.
14. lifecore_state/ parent is still not a package.
15. No docs imply runtime registry behavior exists.
16. No docs imply publishers/subscribers exist.
17. No docs imply lifecycle integration exists.

Deliverable
===========

Create:

  lifecore_state/rfcs/sprint_18_docs_consistency_review.rst

Include:

- inconsistencies found;
- corrections applied;
- unresolved questions;
- recommended review focus.

Constraints
===========

Do not expand the scope.

Do not add new architecture beyond Sprint 18.

Do not implement runtime behavior.

Final sentence
==============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.11 — Créer le fichier de sprint 18

```text
You are working in the lifecore_ros2 repository.

Task
====

Create the Sprint 18 planning file:

  docs/planning/sprints/sprint_18_lifecore_state_msgs.rst

or place it according to the repository’s existing sprint organization.

Sprint title
============

Sprint 18 - lifecore_state_msgs ABI prototype

Sprint type
===========

ROS 2 message ABI prototype.
No runtime implementation.

Context
=======

Sprint 17 closed the architecture/RFC phase for lifecore_state.

Sprint 18 turns the accepted message semantics into a first compilable ROS 2 interface package.

Goals
=====

- Create lifecore_state_msgs package.
- Define prototype .msg contracts.
- Validate colcon build.
- Keep lifecore_state_core deferred.
- Keep lifecore_state_ros deferred.
- Preserve lifecore_ros2 independence.
- Keep parent lifecore_state/ as logical grouping only.

Non-goals
=========

- no StateRegistry;
- no StateProjection;
- no Python core;
- no rclpy integration;
- no publishers/subscribers;
- no lifecycle integration;
- no command handling;
- no QoS implementation;
- no CLI tools;
- no codegen;
- no EventBus;
- no ECS runtime;
- no orchestration.

Deliverables
============

- lifecore_state/lifecore_state_msgs/package.xml
- lifecore_state/lifecore_state_msgs/CMakeLists.txt
- lifecore_state/lifecore_state_msgs/msg/StateDescriptor.msg
- lifecore_state/lifecore_state_msgs/msg/StateDescription.msg
- lifecore_state/lifecore_state_msgs/msg/StateSample.msg
- lifecore_state/lifecore_state_msgs/msg/StateUpdate.msg
- lifecore_state/lifecore_state_msgs/msg/StateCommand.msg
- sprint_18_build_validation.rst
- sprint_18_docs_consistency_review.rst
- sprint_18_constants_decision.rst if needed

Acceptance criteria
===================

- Package builds.
- Messages generate.
- Parent lifecore_state/ has no package.xml.
- No runtime Python code added.
- No lifecore_state_core package.
- No lifecore_state_ros package.
- StateDescription semantics match Sprint 17.
- StateCommand v0 is single-target.
- StateUpdate reports observed truth.
- StateCommand expresses intent.
- Docs updated where necessary.

Open questions
==============

List any remaining message ABI questions.

Final review
============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.12 — Préparer la description de PR Sprint 18

```text
You are working in the lifecore_ros2 repository.

Task
====

Prepare a Pull Request description for Sprint 18.

Create:

  lifecore_state/rfcs/sprint_18_pr_description.md

Title
=====

Sprint 18: lifecore_state_msgs ABI prototype

Summary
=======

This PR introduces the first compilable ROS 2 message package for lifecore_state.

It turns the Sprint 17 message semantics into a prototype message ABI.

Important:
This PR does not implement runtime state behavior.

Sections required
=================

1. Context

Mention:

- Sprint 17 closed the architecture/RFC phase.
- lifecore_state_msgs is the first real package under lifecore_state/.
- parent lifecore_state/ remains a logical folder only.

2. What changed

List:

- package.xml
- CMakeLists.txt
- msg files
- docs updates
- build validation docs

3. Message contracts added

List:

- StateDescriptor
- StateDescription
- StateSample
- StateUpdate
- StateCommand

4. Key decisions

Mention:

- StateDescription is a versioned collection of StateDescriptor entries.
- StateCommand v0 is single-target.
- Batched commands are deferred.
- StateCommand is intent.
- StateUpdate is observed truth.
- StateSample timestamp is source timestamp.
- StateUpdate timestamp is publish/batch timestamp.

5. What did not change

Mention:

- no lifecore_state_core
- no lifecore_state_ros
- no registry
- no projection
- no publisher/subscriber
- no lifecycle integration
- no runtime Python code
- no behavior change in lifecore_ros2

6. Validation

Include:

- colcon build result
- colcon test result if applicable
- package discovery result
- any limitations

7. Review focus

Ask reviewers to focus on:

- message semantics;
- ABI shape;
- naming;
- field types;
- command semantics;
- timestamp semantics;
- sequence/version semantics;
- package boundaries.

8. Checklist

Include:

- [ ] lifecore_state_msgs builds
- [ ] messages generate
- [ ] parent lifecore_state/ has no package.xml
- [ ] no runtime code added
- [ ] no lifecore_state_core added
- [ ] no lifecore_state_ros added
- [ ] StateCommand is single-target
- [ ] StateDescription is descriptor collection
- [ ] docs are consistent
- [ ] Sprint 18 acceptance criteria met

Final sentence
==============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Prompt 18.13 — Revue finale Sprint 18

```text
You are working in the lifecore_ros2 repository.

Task
====

Perform the final Sprint 18 review.

Create:

  lifecore_state/rfcs/sprint_18_final_review.rst

Review areas
============

1. Repository structure

Check:

- lifecore_state/ parent has no package.xml.
- lifecore_state/lifecore_state_msgs has package.xml.
- lifecore_state/lifecore_state_msgs has CMakeLists.txt.
- lifecore_state/lifecore_state_msgs/msg contains expected messages.
- no lifecore_state_core exists unless explicitly deferred as docs only.
- no lifecore_state_ros exists unless explicitly deferred as docs only.

2. Build

Check:

- colcon list sees lifecore_state_msgs.
- colcon build --packages-select lifecore_state_msgs succeeds.
- colcon test succeeds or limitations are documented.

3. Message semantics

Check:

- StateDescriptor = one field contract.
- StateDescription = versioned descriptor collection.
- StateSample = one observed value.
- StateUpdate = batch of observed truth.
- StateCommand = single-target intent.
- Batch commands deferred.

4. Field-level review

Check:

- identity fields are coherent.
- type fields are coherent.
- quality fields are coherent.
- timestamps are coherent.
- sequence is present.
- description_version is present.
- schema_uuid is present where needed.
- update_mode is present in StateUpdate.

5. Scope control

Check:

- no registry behavior.
- no projection behavior.
- no publisher/subscriber behavior.
- no command handling.
- no lifecycle integration.
- no QoS implementation.
- no codegen.

6. Documentation consistency

Check:

- message_semantics updated.
- package_boundaries updated if needed.
- RFC references still correct.
- PR description ready.

7. Risks and follow-ups

List:

- ABI concerns;
- field naming concerns;
- future compact message concerns;
- future command feedback concerns;
- future core implementation concerns.

8. Sprint 19 recommendation

Recommend next step only if Sprint 18 passes.

Likely next sprint:

  Sprint 19 - lifecore_state_core pure Python model

But explicitly state that Sprint 19 should not start until message ABI review is accepted.

Final decision
==============

Write one of:

- Sprint 18 accepted.
- Sprint 18 accepted with minor follow-ups.
- Sprint 18 not accepted.

Final sentence
==============

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
```

---

# Ordre recommandé

```text
18.1  Pre-audit
18.2  Package scaffold
18.3  StateDescriptor.msg
18.4  StateDescription.msg
18.5  StateSample.msg
18.6  StateUpdate.msg
18.7  StateCommand.msg
18.8  Constants decision
18.9  Build validation
18.10 Documentation consistency
18.11 Sprint 18 planning file
18.12 PR description
18.13 Final review
```

---

# Décision stratégique

Pour Sprint 18, le verrou à maintenir est :

```text
messages only
```

Pas de `StateRegistry`.

Pas de `StatePublisher`.

Pas de `DescriptionSubscriber`.

Pas de `lifecore_state_core`.

Pas de `lifecore_state_ros`.

Le but est de faire une ABI ROS 2 propre avant d’empiler du code dessus.
