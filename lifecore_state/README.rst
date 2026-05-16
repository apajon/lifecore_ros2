lifecore_state
==============

Purpose
-------

``lifecore_state`` is a future architecture direction for typed distributed
state in the Lifecore ecosystem. During Sprint 17, this folder is a
documentation-only home for architecture notes and RFC material.

This folder is not a ROS 2 package, not a Python package, and not part of the
installed ``lifecore_ros2`` runtime package.

Objectives
----------

- define shared terminology before implementation;
- document state message semantics before message ABI work;
- keep lifecycle orchestration and state truth separate;
- record package boundary decisions before creating packages;
- keep Sprint 17 reviewable as architecture and RFC work only.

Non-objectives
--------------

- no runtime code;
- no ROS 2 package metadata;
- no Python packaging metadata;
- no compiled message, service, or action definitions;
- no public exports from ``lifecore_ros2``;
- no lifecycle behavior changes.

Folder layout
-------------

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

Sprint 17 rule
--------------

If future work requires packages, runtime modules, ROS 2 interfaces, or build
metadata, that work belongs in a later sprint after the architecture review is
accepted.

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
