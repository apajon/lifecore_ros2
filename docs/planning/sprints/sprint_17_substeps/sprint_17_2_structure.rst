Sprint 17.2 — Create Documentation Structure for lifecore_state/
==================================================================

**Track.** Architecture / Research.

**Type.** Documentation Structure Setup.

**Objective.** Prepare the documentation folder structure for Sprint 17 and
future ``lifecore_state`` architecture, without creating any functional packages
or runtime code.

Context
-------

The decision: ``lifecore_state/`` is a logical grouping at the repository level,
NOT a ROS 2 installable package.

This sprint creates only the folder structure and README files that explain
the purpose and organization.

Constraints
-----------

- Do not create ``package.xml`` in ``lifecore_state/`` parent folder
- Do not create Python runtime code
- Do not create compilable ROS 2 ``.msg`` files
- Do not create actual packages like ``lifecore_state_msgs/``, ``lifecore_state_core/``, or ``lifecore_state_ros/`` as real packages — document them as future structure only
- All documents must be reStructuredText format
- Clear, technical but accessible style
- No orchestration, plugin frameworks, giant managers, ECS runtimes, or codegen

Target Structure
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

1. **lifecore_state/README.rst**

   - Explains that ``lifecore_state`` is a future direction
   - States this folder is documentation-only for Sprint 17
   - Clarifies this is NOT a ROS 2 package
   - Summarizes objectives and non-objectives

2. **lifecore_state/rfcs/README.rst**

   - Explains what an RFC is in this project
   - Clarifies RFC purpose: clarify before implementation

3. **lifecore_state/terminology.rst** (skeleton, will be completed in 17.4)

   - Empty or with section headers for future content

4. **lifecore_state/message_semantics.rst** (skeleton, will be completed in 17.7)

   - Empty or with section headers for future content

5. **lifecore_state/lifecycle_state_separation.rst** (skeleton, will be completed in 17.5)

   - Empty or with section headers for future content

6. **lifecore_state/anti_goals.rst** (skeleton, will be completed in 17.8)

   - Empty or with section headers for future content

7. **lifecore_state/package_boundaries.rst** (skeleton, will be completed in 17.6)

   - Empty or with section headers for future content

Acceptance Criteria
-------------------

- [ ] Directory structure created under ``docs/planning/`` or at repo root
- [ ] All required RST skeleton files exist
- [ ] ``lifecore_state/`` has no ``package.xml``
- [ ] All folders have minimal README explaining content
- [ ] No build metadata added
- [ ] No Python code added
- [ ] Each file ends with mandatory review phrase
- [ ] Folder is NOT discovered by ``colcon`` as a package

Key Decision to Document
------------------------

``lifecore_state/`` is a documentation-only folder for Sprint 17.

Later, this folder might contain three separate ROS 2 packages:

- ``lifecore_state_msgs`` (messages and ABI)
- ``lifecore_state_core`` (pure Python logic)
- ``lifecore_state_ros`` (ROS 2 integration)

But for now, it is a logical grouping, not a functional package.

Mandatory phrase in each file:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."

Success Criteria
----------------

All future documentation (17.3–17.13) has a clear home in this structure without
polluting ``lifecore_ros2/`` or creating broken package hierarchies.
