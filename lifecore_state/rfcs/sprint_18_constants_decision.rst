Sprint 18.8 — Constants Decision: Embedded (Option A)
=====================================================

**Status.** Decided.

**Track.** State Architecture / ROS ABI.

**Type.** ABI decision.

**Parent sprint.** Sprint 18 — lifecore_state_msgs ABI prototype.

**Date.** 2026-06-05.

Decision
--------

**Option A: embedded constants.** All type, quality, direction, source, and
update mode constants remain embedded directly in their primary message files.
No separate enum-like message files are created for v0.

Rationale
---------

1. **Minimalism for v0.** The message set is intentionally small (five
   messages). Extracting constants into separate files would increase the file
   count from 5 to 10 without reducing conceptual complexity. The ABI prototype
   should stay as simple as possible while remaining reviewable.

2. **Duplication is acceptable at this scale.** The ``TYPE_*`` constants are
   duplicated in three files (``StateDescriptor.msg``, ``StateSample.msg``,
   ``StateCommand.msg``). This is 14 constants × 3 = 42 lines of duplication.
   At v0 scale, this is easier to review and understand than an indirection
   through a separate ``StateType.msg``. The other constant groups
   (``QUALITY_*``, ``DIR_*``, ``SOURCE_*``, ``UPDATE_*``) appear in exactly one
   message each, so there is no duplication to eliminate.

3. **Self-contained messages.** A reader can understand a single ``.msg`` file
   without cross-referencing auxiliary enum files. This matters during early
   review cycles when the ABI shape is still being validated.

4. **No tooling benefit yet.** ROS 2 code generation does not produce
   materially better Python/C++ APIs from separate enum messages compared to
   embedded constants. The generated constants are accessible in the same
   namespace regardless. Extracting them would add indirection without
   improving the developer experience at this stage.

5. **Reversible decision.** If future sprints add more messages that duplicate
   constants, or if tooling improves to leverage separate enum messages, the
   decision can be revisited. Extracting constants from existing messages is a
   compatible change (old constants can be deprecated but kept).

Alternatives Considered
-----------------------

Option B: Separate Enum-Like Messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating ``StateType.msg``, ``StateQuality.msg``, ``StateDirection.msg``,
``StateSource.msg``, and ``StateUpdateMode.msg`` as standalone message files.

**Rejected for v0 because:**

- Adds 5 files with no new semantic content.
- Requires import/reference indirection in every consumer.
- The ``TYPE_*`` constants are the only duplicated group; the other groups
  appear once. Extracting only ``StateType.msg`` would create inconsistency
  (one extracted, others embedded). Extracting all would create five files
  with minimal content each.
- At v0 scale, the indirection cost outweighs the deduplication benefit.

**May be reconsidered when:**

- A fourth or fifth message duplicates ``TYPE_*`` constants.
- A future code generator or validation tool benefits from separate enum
  definitions.
- The message set stabilizes and maintenance of duplicated constants becomes
  a real friction point (not hypothetical).

Option C: Hybrid (Extract Only TYPE_*)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extracting only ``StateType.msg`` while keeping ``QUALITY_*``, ``DIR_*``,
``SOURCE_*``, and ``UPDATE_*`` embedded.

**Rejected because:**

- Creates an inconsistent pattern (one extracted, others embedded).
- The ``QUALITY_*``, ``DIR_*``, ``SOURCE_*``, and ``UPDATE_*`` constants
  each appear in exactly one message — no duplication to solve.
- Splitting only ``TYPE_*`` suggests a problem that does not yet exist at v0
  scale.

Impact on Message Files
-----------------------

No changes required. The current ``.msg`` files already implement Option A:

- ``StateDescriptor.msg``: ``TYPE_*`` (14 constants), ``DIR_*`` (3 constants)
- ``StateSample.msg``: ``TYPE_*`` (14 constants), ``QUALITY_*`` (10 constants), ``SOURCE_*`` (6 constants)
- ``StateCommand.msg``: ``TYPE_*`` (14 constants)
- ``StateUpdate.msg``: ``UPDATE_*`` (3 constants)
- ``StateDescription.msg``: no constants

The existing comments referencing "Sprint 18.8 may extract a shared
StateType.msg; until then, constants are duplicated" remain accurate and will
not be removed — they serve as signposts for future reviewers.

Current Constant Inventory
--------------------------

Type constants (``TYPE_*``, duplicated in StateDescriptor, StateSample, StateCommand):
  ``TYPE_UNKNOWN=0``, ``TYPE_BOOL=1``, ``TYPE_INT8=2``, ``TYPE_INT16=3``,
  ``TYPE_INT32=4``, ``TYPE_INT64=5``, ``TYPE_UINT8=6``, ``TYPE_UINT16=7``,
  ``TYPE_UINT32=8``, ``TYPE_UINT64=9``, ``TYPE_FLOAT32=10``, ``TYPE_FLOAT64=11``,
  ``TYPE_STRING=12``, ``TYPE_BYTES=13``

Direction constants (``DIR_*``, in StateDescriptor only):
  ``DIR_OUT=0``, ``DIR_IN=1``, ``DIR_INOUT=2``

Quality constants (``QUALITY_*``, in StateSample only):
  ``QUALITY_UNKNOWN=0``, ``QUALITY_VALID=1``, ``QUALITY_STALE=2``,
  ``QUALITY_INVALID=3``, ``QUALITY_COMM_ERROR=4``, ``QUALITY_OUT_OF_RANGE=5``,
  ``QUALITY_FORCED=6``, ``QUALITY_SIMULATED=7``, ``QUALITY_DISABLED=8``,
  ``QUALITY_NOT_AVAILABLE=9``

Source constants (``SOURCE_*``, in StateSample only):
  ``SOURCE_UNKNOWN=0``, ``SOURCE_HARDWARE=1``, ``SOURCE_SOFTWARE=2``,
  ``SOURCE_SIMULATION=3``, ``SOURCE_OPERATOR=4``, ``SOURCE_REPLAY=5``

Update mode constants (``UPDATE_*``, in StateUpdate only):
  ``UPDATE_UNKNOWN=0``, ``UPDATE_FULL=1``, ``UPDATE_DELTA=2``

Deferred Decisions
------------------

1. **Extraction trigger.** The exact threshold for revisiting Option B
   (e.g., "N messages duplicate TYPE_*") is not defined. This will be
   evaluated when a concrete duplication pain point arises.

2. **Deprecation strategy.** If constants are extracted in the future, the
   deprecation path for embedded constants (keep + mark deprecated vs.
   remove) is deferred.

3. **Constant value stability.** The integer values assigned to constants
   are considered stable for v0, but no formal ABI stability contract is
   declared yet. This belongs to a future ABI versioning policy.

4. **Cross-package constant sharing.** If future packages (e.g.,
   ``lifecore_state_core``) need the same constants in Python, the strategy
   for sharing (generate from .msg vs. maintain parallel Python enums) is
   deferred to the sprint that creates those packages.

5. **Additional constant groups.** New constant categories (e.g., command
   status, projection mode) will follow the same embedded-by-default rule
   unless a clear extraction benefit exists when they are introduced.

Constraints Respected
---------------------

- No runtime code added.
- No ``lifecore_state_core`` or ``lifecore_state_ros`` created.
- No code generation introduced.
- No message file modifications.
- No change to ``lifecore_ros2`` behavior or dependencies.
