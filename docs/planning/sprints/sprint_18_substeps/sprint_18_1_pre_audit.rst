Sprint 18.1 - Pre-implementation Audit
======================================

**Status.** Active.

**Track.** State Architecture / ROS ABI.

**Type.** Audit.

**Parent sprint.** :doc:`../active/sprint_18_lifecore_state_msgs_abi`.

Objective
---------

Inspect the repository before creating the ``lifecore_state_msgs`` package.
This step must produce facts, not implementation.

Scope
-----

Audit and record:

- existing ROS 2 package layout conventions;
- existing ``package.xml`` style;
- existing ``CMakeLists.txt`` style, if any;
- existing interface/message packages, if any;
- existing lint and test conventions;
- where ``lifecore_state/`` currently lives;
- whether ``lifecore_state/`` parent has ``package.xml``;
- whether Sprint 17 docs already mention ``lifecore_state_msgs``.

Constraints
-----------

- Do not create or modify package files.
- Do not create ``.msg`` files.
- Do not implement runtime code.
- Do not create ``lifecore_state_core`` or ``lifecore_state_ros``.

Deliverable
-----------

Create or update ``lifecore_state/rfcs/sprint_18_pre_audit.rst`` with:

- observed repository/package conventions;
- proposed package path;
- proposed package name;
- proposed build type;
- proposed dependencies;
- risks before implementation;
- confirmation that ``lifecore_state/`` parent is not a ROS package;
- confirmation that Sprint 18 remains messages-only.

Expected conclusion
-------------------

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

Review Requirement
------------------

ChatGPT or Codex will review and control the deliverables before Sprint 18 is accepted.
