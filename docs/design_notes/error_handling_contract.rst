Error handling contract
=======================

**Status**: Ratified — Sprint 2, 2026-04-30.

**Purpose**: Define error propagation semantics and rollback policy for ``LifecycleComponent``
hooks. This note supersedes the pre-implementation placeholder and is the single authoritative
source for the decisions below. The propagation matrix is reproduced in
:ref:`Error Policy <architecture-error-policy>` for quick reference.

---

Propagation matrix
------------------

.. list-table:: Hook outcome → library action
   :header-rows: 1
   :widths: 30 20 20 15 15

   * - Event in hook
     - Wrapper return
     - rclpy next state
     - ``_on_error``?
     - ``_release_resources``?
   * - ``SUCCESS``
     - ``SUCCESS``
     - target state
     - no
     - per transition
   * - explicit ``FAILURE``
     - ``FAILURE``
     - previous state
     - no
     - no (failed configure)
   * - explicit ``ERROR``
     - ``ERROR``
     - ``ErrorProcessing``
     - yes
     - yes
   * - caught exception
     - ``ERROR`` + log
     - ``ErrorProcessing``
     - yes
     - yes
   * - invalid return value
     - ``ERROR`` + log
     - ``ErrorProcessing``
     - yes
     - yes

---

Locked decisions
----------------

Decision 1 — Rollback policy B: all-or-nothing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A composite node transition (``on_configure``, ``on_activate``, etc.) fails as soon as
any registered component returns ``FAILURE`` or ``ERROR``. The node propagates the worst
result across all components. Siblings that already completed their hook are **not**
reversed: no ``_on_cleanup`` is replayed, no "undo" hooks are called.

For ``configure`` specifically, ``LifecycleComponentNode._rollback_failed_configure``
calls ``_release_resources`` on every component to restore a coherent unconfigured state.
This is a resource release, not a hook replay.

**Rationale.** Reverse replay of hooks introduces ordering complexity, idempotence
requirements, and partial-state hazards that outweigh the benefit for the current use
cases. The node either succeeds atomically or returns to an unconfigured (cleanable) state.

Decision 2 — ``LifecycleHookError`` wraps caught hook exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a ``_on_*`` hook raises an uncaught exception, ``_guarded_call`` creates a
:class:`~lifecore_ros2.LifecycleHookError` with ``__cause__`` set to the original
exception, logs it at ``ERROR`` level with component name and hook name, and returns
``TransitionCallbackReturn.ERROR``. The ``LifecycleHookError`` is never re-raised to
the caller of ``trigger_*``.

**Rationale.** Wrapping in a typed exception class enables future aggregation (e.g.
collecting all hook errors from a composite transition) without requiring callers to
inspect raw tracebacks.

Decision 3 — Strict mode is the default and is non-configurable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any ``_on_*`` hook that returns a value outside ``{SUCCESS, FAILURE, ERROR}`` is
treated as ``ERROR`` immediately. The library logs the component name, hook name,
``type(value).__name__``, ``repr(value)``, and a message stating that
``TransitionCallbackReturn`` was expected. There is no lenient mode, no
``strict=False`` flag, and no per-component override.

**Rationale.** An invalid return value is always a programming error. Silently
mapping it to ``SUCCESS`` or ``FAILURE`` would hide bugs. Strict mode surfaces
them immediately with an actionable error log.

Decision 4 — ``_on_error`` is driven only by native rclpy ``ERROR_PROCESSING``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The library never synthesises a call to ``_on_error`` in response to a caught
exception. The native rclpy flow is:

.. code-block:: text

    hook raises exception
        → _guarded_call returns ERROR
        → rclpy state machine enters ErrorProcessing
        → rclpy calls LifecycleComponentNode.on_error
        → on_error propagates to each component's on_error entry point
        → @final on_error clears _is_active, calls _on_error, calls _release_resources

This path is complete and correct. Adding a library-side ``_on_error`` invocation
would duplicate the call, violating the idempotence contract.

**Rationale.** Staying on the native rclpy ``ErrorProcessing`` path preserves
standard lifecycle semantics and keeps the library free of a hidden parallel state
machine.

---

Implementation notes
--------------------

- ``_guarded_call`` in :mod:`lifecore_ros2.core.lifecycle_component` is the single
  enforcement point for decisions 2, 3, and 4.
- ``LifecycleComponentNode._rollback_failed_configure`` enforces decision 1 for the
  ``configure`` transition. Other transitions (``activate``, etc.) do not perform
  resource rollback — the node simply returns the worst result and rclpy handles the
  state transition.
- ``LifecycleHookError`` is exported from the top-level package so application code
  can optionally catch it, though doing so is rarely necessary.

---

Related
-------

- :doc:`/architecture` — Error Policy section and propagation matrix (authoritative summary)
- :doc:`lifecycle_policies` — ordering semantics for component transitions
