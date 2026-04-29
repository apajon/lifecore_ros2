Sprint 8 — Minimal observability
=================================

**Objectif.** Add structured logging and lifecycle tracing for industrial debugging.

**Livrable.** "Lifecycle behavior is debuggable without print statements."

---

Content
-------

Structured logging
^^^^^^^^^^^^^^^^^^

- Standardized log format for all lifecycle events:

  - Transition start: ``"node.transition_start: target_state={state} components={count}"``
  - Transition complete: ``"node.transition_complete: state={state} result={result} duration_ms={ms}"``
  - Component hook: ``"component.hook: name={comp} hook={hook_name} state_before={state}"``
  - Component hook result: ``"component.hook_result: name={comp} hook={hook_name} result={result} duration_ms={ms}"``
  - Activation gating: ``"component.gating: name={comp} action={action} active={is_active} result={allowed|denied}"``

- Use Python logging levels:

  - DEBUG: all hook calls and gating decisions
  - INFO: transition start/end, significant events
  - WARNING: non-fatal errors (e.g., gate deny), edge cases
  - ERROR: hook failures, invalid transitions

Lifecycle transition tracing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Optional: emit ROS 2 ``/diagnostics`` messages for each transition
- Or: structured logs that can be post-processed into diagnostics
- Minimal: just logging is enough for this sprint

Component timing metrics
^^^^^^^^^^^^^^^^^^^^^^^

- Track per-hook execution time (optional, not required for MVP)
- Hook duration in debug logs: ``"component.hook_result: ... duration_ms=45"``

Last error tracking (per-component)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Component stores last exception from hook
- Query: ``component.last_error -> Optional[Exception]``
- Query: ``component.last_error_message -> Optional[str]``
- Cleared on successful transition

Node transition history
^^^^^^^^^^^^^^^^^^^^^^^

- Optional: keep a ring buffer of last N transitions (e.g., 10)
- Each entry: timestamp, target state, result, duration
- Query: ``node.transition_history -> List[TransitionRecord]``
- Useful for post-mortem debugging

---

Tests to write
--------------

Logging tests
^^^^^^^^^^^^^

- [x] Transition logs include state and component count
- [x] Hook execution logs include component name, hook type, result
- [x] Gating logs include action name and decision (allowed/denied)
- [x] All logs go through Python logging (not print)
- [x] Log level DEBUG shows all details
- [x] Log level INFO shows only transitions

Structured data tests
^^^^^^^^^^^^^^^^^^^^^

- [x] Last error is captured on hook failure
- [x] Last error is cleared on successful transition
- [x] Transition history ring buffer works (capacity limit)
- [x] Querying history returns correct order (newest first or oldest first, pick one)

Timing tests
^^^^^^^^^^^^

- [x] Hook duration is measured and logged
- [x] Duration is reasonable (not zero or huge)

---

Risks and mitigation
--------------------

**Risk 1: Performance impact of logging**

- **Problem**: Structured logging adds overhead to every transition.
- **Mitigation**:
  - Use lazy logging (log at DEBUG level by default, off in production)
  - Measure performance (probably negligible for lifecycle ops)
  - Document: "use log level DEBUG for development, INFO for production"

**Risk 2: Ring buffer bloats memory**

- **Problem**: Keeping transition history uses unbounded memory.
- **Mitigation**:
  - Fixed-size ring buffer (e.g., 10 entries)
  - Each entry is lightweight (timestamp, state, duration, status)

**Risk 3: Logs are too verbose**

- **Problem**: Too many log lines make it hard to find actual problems.
- **Mitigation**:
  - Use log levels correctly (DEBUG for all, INFO for summaries)
  - Provide log level configuration to application
  - Example: ``logger.setLevel(logging.WARNING)`` in production

**Risk 4: Last error is not always set (race condition)**

- **Problem**: Error occurs, but last error is not captured.
- **Mitigation**:
  - Capture in exception handler of ``_guarded_call`` (centralized)
  - No race: error is set atomically when hook fails

---

Dependencies
------------

- Requires: All components (Sprints 1–7)
- Requires: Error handling (Sprint 2) — capture and log failures
- Requires: Testing utilities (Sprint 3) — verify logs in tests

---

Scope boundaries
----------------

**In-scope:**

- Structured logging (standard format)
- Transition tracing (start/end events)
- Hook timing metrics
- Last error tracking (per-component)
- Transition history (ring buffer)
- Log level configuration

**Out-of-scope:**

- ROS 2 diagnostic aggregator integration (future, separate sprint)
- Custom visualization tools (application responsibility)
- Distributed tracing (out of scope for core library)
- Metrics export to Prometheus, etc. (application responsibility)

---

Success signal
--------------

- [x] Structured logging is enabled by default
- [x] Logs follow standard format (documented)
- [x] All tests verify expected logs are emitted
- [x] Last error query works: ``component.last_error``, ``component.last_error_message``
- [x] Transition history query works: ``node.transition_history``
- [x] Hook timing is logged at DEBUG level
- [x] Example: ``examples/observability_demo.py`` (runs node with debug logging, shows output)
- [x] Ruff, Pyright, Pytest all green
- [x] Documentation: logging levels, what each message means, debugging tips

---

Location
--------

- Module: ``src/lifecore_ros2/core/_logging.py`` (or extend ``core/__init__.py``)
- Updated: ``src/lifecore_ros2/core/*.py``, ``src/lifecore_ros2/components/*.py``
- Tests: ``tests/test_observability.py`` (new)
- Examples: ``examples/observability_demo.py`` (new)
- Docs: Add observability section to ``docs/architecture.rst``

---

Related design notes
--------------------

- :doc:`../design_notes/observability` — reference for observability design decisions
