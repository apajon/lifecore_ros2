Package Boundaries
==================

Purpose
-------

This document defines the proposed future package boundaries for
``lifecore_state`` before any package, message ABI, or runtime module is
created. The goal is to keep ABI contracts, pure state semantics, and ROS 2
integration separate enough that each concern can be reviewed, tested, and
evolved without turning ``lifecore_ros2`` into a broad runtime platform.

Current scope
-------------

These boundaries are architectural planning labels only. Sprint 17 does not
create directories, packages, package metadata, import paths, or public exports
for them. This document records the dependency direction and responsibility
split that later sprints must preserve if packages are eventually created.

Repository-level grouping
-------------------------

During Sprint 17, ``lifecore_state/`` remains a logical documentation group at
repository level. It is not a ROS 2 package and not a Python runtime package.

This grouping is intentional:

- the parent folder must not contain ``package.xml``;
- the parent folder must not be discoverable by ``colcon`` as a package;
- the parent folder must not contain ``pyproject.toml``, ``setup.py``,
  ``CMakeLists.txt``, or compilable ROS interface files;
- the folder groups architecture documents in one place without pretending that
  the runtime split already exists;
- the documented split should remain extractable later into separate packages or
  even separate repositories.

This rule protects Sprint 17 from accidentally creating a monolithic parent
package before the package boundaries themselves are accepted.

Future package: lifecore_state_msgs
-----------------------------------

``lifecore_state_msgs`` is the future ROS 2 ABI package.

Responsibilities
~~~~~~~~~~~~~~~~

- own ``.msg`` definitions and any future ROS 2 wire contracts;
- own public transport-level message compatibility review;
- provide stable ABI-oriented message names and field layouts;
- expose message contracts for state description, updates, snapshots, deltas,
  commands, and related transport needs only if later sprints approve them.

Non-responsibilities
~~~~~~~~~~~~~~~~~~~~

``lifecore_state_msgs`` must not own:

- Python runtime logic;
- registry behavior;
- projection behavior;
- lifecycle behavior;
- quality interpretation logic beyond what is encoded in the wire contract;
- command handling policy;
- snapshot or delta application logic.

Dependencies
~~~~~~~~~~~~

- ROS 2 message generation dependencies only;
- ``std_msgs`` only if a future ``Header`` use is explicitly justified;
- no dependency on ``lifecore_state_core``;
- no dependency on ``lifecore_state_ros``;
- no dependency on ``lifecore_ros2``.

Future package: lifecore_state_core
-----------------------------------

``lifecore_state_core`` is the future pure Python semantics package.

Responsibilities
~~~~~~~~~~~~~~~~

- own descriptors and descriptions as semantic concepts;
- own sample, update, snapshot, delta, and command interpretation rules;
- own registry scope, projection, identity, and authority rules;
- own quality, freshness, and staleness interpretation;
- own policy objects or helper logic that can be tested without ROS;
- remain usable from plain Python tests without a ROS installation.

Non-responsibilities
~~~~~~~~~~~~~~~~~~~~

``lifecore_state_core`` must not own:

- ROS 2 node integration;
- topic publishers or subscribers;
- QoS configuration;
- message definitions;
- lifecycle transitions;
- hidden orchestration behavior.

Dependencies
~~~~~~~~~~~~

- Python 3.12+;
- standard library preferred;
- optional small pure-Python dependencies only if justified by clear value;
- no ``rclpy``;
- no ROS 2 package dependency;
- no dependency on ``lifecore_ros2``.

Future package: lifecore_state_ros
----------------------------------

``lifecore_state_ros`` is the future ROS 2 integration package.

Responsibilities
~~~~~~~~~~~~~~~~

- adapt pure state semantics to ROS 2 transport and node APIs;
- define QoS defaults or helpers for state-specific transport patterns;
- provide description publishers and subscribers;
- provide state publishers and subscribers;
- provide command subscribers or request adapters;
- provide state mirror or bridge integration for ROS-facing synchronization;
- optionally offer thin, explicit integration points for ``lifecore_ros2``
  components.

Non-responsibilities
~~~~~~~~~~~~~~~~~~~~

``lifecore_state_ros`` must not become:

- a hidden lifecycle manager;
- an orchestration runtime;
- a global state blackboard;
- a replacement for ``lifecore_ros2`` component composition;
- a reason to pull pure semantics into ROS-specific code.

Dependencies
~~~~~~~~~~~~

- ``rclpy`` required;
- ``lifecore_state_msgs`` required when ROS wire contracts are needed;
- ``lifecore_state_core`` required for pure semantic interpretation;
- optional ``lifecore_ros2`` only for explicit, additive component integration;
- no reverse dependency from ``lifecore_state_core`` or ``lifecore_state_msgs``
  back to ``lifecore_state_ros``.

Existing package: lifecore_ros2
-------------------------------

``lifecore_ros2`` remains the existing lifecycle-native composition framework.
Sprint 17 does not move ``lifecore_state`` concepts into it.

It remains responsible for:

- explicit lifecycle transitions;
- managed entities and component registration;
- activation gating and lifecycle-owned readiness;
- clear resource ownership through lifecycle hooks.

It does not become the owner of:

- state registries;
- state descriptions or projections as core runtime concerns;
- hidden cross-node state synchronization;
- package management for future ``lifecore_state`` concerns.

Later work may let ``lifecore_ros2`` consume ``lifecore_state_ros`` through thin,
reviewed integration points, but that integration must remain optional and
non-invasive.

Mandatory dependency rules
--------------------------

The following dependency directions are mandatory and must not be broken:

- ``lifecore_ros2`` must not depend on ``lifecore_state_*`` by default;
- ``lifecore_state_core`` must not depend on ROS 2 or ``rclpy``;
- ``lifecore_state_msgs`` must not depend on ``lifecore_state_core``;
- ``lifecore_state_msgs`` must not contain registry or lifecycle logic;
- ``lifecore_state_ros`` may depend on ``lifecore_state_msgs`` and
  ``lifecore_state_core``;
- optional ``lifecore_ros2`` integration must remain thin, explicit, and
  additive;
- no package may introduce a parallel lifecycle state machine.

These rules keep the future split acyclic and stop semantics, wire contracts,
and framework integration from collapsing into one broad package.

Forbidden dependencies and anti-patterns
----------------------------------------

The following directions are explicitly rejected:

- circular dependencies between future packages;
- registry logic inside message definitions;
- lifecycle logic inside ``lifecore_state_core``;
- message definitions inside ``lifecore_state_core``;
- a giant parent ``lifecore_state`` runtime package that reabsorbs all three
  concerns;
- implicit state sharing hidden across packages;
- ROS-specific helper code leaking into the pure core package;
- policy encoded only in ABI contracts when it belongs in semantics or ROS
  integration.

Future extraction path
----------------------

The repository-level logical grouping is designed so later extraction stays
possible without architectural rewrites.

A future extraction path may look like this:

1. keep Sprint 17 documents as the source of truth for package roles;
2. create independent package folders only after the split is accepted;
3. move ``lifecore_state_msgs``, ``lifecore_state_core``, and
   ``lifecore_state_ros`` into separate repositories or a reviewed multi-package
   repository;
4. preserve the same dependency direction after extraction;
5. allow ROS 2 workspaces to combine those repos explicitly rather than relying
   on one giant parent package;
6. keep ``lifecore_ros2`` optional in that future workspace composition.

This path matters because it avoids locking the architecture to monorepo-only
tooling or to a single release train for every concern.

Decision summary
----------------

Sprint 17.6 records the following package boundary decisions:

- ``lifecore_state/`` remains a documentation-only logical folder during Sprint
  17;
- the future split is between ``lifecore_state_msgs``, ``lifecore_state_core``,
  and ``lifecore_state_ros``;
- ``lifecore_state_msgs`` owns ROS 2 ABI contracts only;
- ``lifecore_state_core`` owns pure Python state semantics only;
- ``lifecore_state_ros`` owns ROS 2 integration only;
- ``lifecore_ros2`` remains independent and lifecycle-focused;
- dependency direction must remain acyclic;
- optional integration with ``lifecore_ros2`` must stay thin and explicit.

Review note
-----------

This document defines package responsibilities and dependency rules only. It
does not create packages, public APIs, ROS interfaces, or runtime code.

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
