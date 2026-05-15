RFC 001: lifecore_state Architecture
====================================

Status
------

Draft skeleton for Sprint 17.

Summary
-------

This RFC will propose the architecture for ``lifecore_state`` as a future typed
distributed state model that remains separate from ``lifecore_ros2`` lifecycle
orchestration.

Goals
-----

- define the architecture vocabulary;
- describe message semantics before ABI work;
- preserve lifecycle and state separation;
- propose package boundaries before packages exist;
- document anti-goals and review criteria.

Non-goals
---------

- no runtime implementation;
- no ROS 2 package creation;
- no Python package creation;
- no ``lifecore_ros2`` public API changes;
- no lifecycle transition behavior changes.

Architecture questions
----------------------

- What is the smallest useful model for typed observed state?
- Which concepts belong in message contracts?
- Which concepts belong in pure core semantics?
- Which concepts belong in ROS 2 integration?
- How should optional integration with ``lifecore_ros2`` remain explicit?

Review criteria
---------------

- the RFC keeps ``lifecore_ros2`` independent from ``lifecore_state``;
- the RFC does not imply hidden lifecycle behavior;
- the RFC does not create package metadata or runtime files;
- the RFC is precise enough to guide later Sprint 18 message ABI decisions.

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
