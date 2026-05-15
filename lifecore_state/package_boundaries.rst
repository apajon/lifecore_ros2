Package Boundaries
==================

Purpose
-------

This document will describe possible future package boundaries for
``lifecore_state``. Sprint 17.6 will complete the boundary proposal before any
package is created.

Candidate future boundaries
---------------------------

``lifecore_state_msgs``
  Future ROS 2 ABI contracts only.

``lifecore_state_core``
  Future pure Python state semantics with no ROS 2 or ``rclpy`` dependency.

``lifecore_state_ros``
  Future ROS 2 integration layer that may depend on ROS 2 contracts and pure
  core semantics.

Current scope
-------------

These names are planning labels only. Sprint 17.2 does not create directories,
packages, package metadata, import paths, or public exports for them.

Review questions
----------------

- Which boundary should own message ABI compatibility?
- Which boundary should own pure state semantics?
- What dependency direction keeps ``lifecore_ros2`` independent?

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
