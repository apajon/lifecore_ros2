Observability — Design Note
============================

.. admonition:: Audience
   :class: note

  Contributors and advanced readers evaluating future directions of
  ``lifecore_ros2``. This is a **design note**, not committed user
  documentation. No code under ``src/lifecore_ros2/`` exists for this feature
  yet.

.. admonition:: Status
   :class: important

   Draft — gated on §4 (concurrency) and §5 (strict lifecycle contract) being
   green. See :ref:`observability-prerequisite-gates`.

Intent
------

Define a small, stable observability surface for ``lifecore_ros2``:

1. **Structured logging** — make existing transition and error log lines
   parseable, with stable field names, so operators can filter and alert
   without scraping free-form messages.
2. **Lifecycle tracing** — expose a passive event stream describing
   transition starts, ends, failures, and rejections, so external code can
   record traces or feed dashboards without polling.

Goal: turn the library into a *passive observer* of native rclpy lifecycle
behavior. Never own the state machine; never duplicate it.

Proposed contract
-----------------

Two layers, both opt-in.

Layer A — structured logging (always on)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Existing log sites in ``_guarded_call``, ``_release_resources``, and the
direct-call rejection paths emit messages with a **stable field set**. The
field set is the contract; the human-readable template can evolve.

Mandatory fields (every transition-related log line):

* ``component`` — registered name, or ``"<node>"`` for node-level lines.
* ``transition`` — one of ``configure``, ``activate``, ``deactivate``,
  ``cleanup``, ``shutdown``, ``error``.
* ``from_state`` / ``to_state`` — rclpy state labels (read at log time, not
  cached).
* ``outcome`` — one of ``success``, ``failure``, ``error``, ``rejected``.
* ``error_class`` — fully qualified exception class name when ``outcome`` is
  ``error`` or ``rejected``; absent otherwise.
* ``duration_ms`` — wall-clock duration of the hook for ``success`` /
  ``failure`` / ``error``; absent for ``rejected``.

Implementation detail (informative, not contractual): use rclpy's structured
logger with key/value extras where supported, and fall back to a stable
``key=value`` suffix in the message string. A single helper produces both.

Layer B — lifecycle event stream (opt-in)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A read-only observer interface on :class:`lifecore_ros2.LifecycleComponentNode`
that lets external code subscribe to lifecycle events as Python objects
(no ROS topics, no IPC).

.. code-block:: python

   from dataclasses import dataclass
   from typing import Callable, Literal

   Outcome = Literal["success", "failure", "error", "rejected"]

   @dataclass(frozen=True)
   class LifecycleEvent:
       component: str               # "<node>" for node-level events
       transition: str              # configure | activate | deactivate | cleanup | shutdown | error
       from_state: str
       to_state: str
       outcome: Outcome
       error_class: str | None
       duration_ms: float | None
       monotonic_ns: int            # event timestamp from time.monotonic_ns()


   class LifecycleComponentNode:

       def add_lifecycle_observer(
           self, callback: Callable[[LifecycleEvent], None]
       ) -> Callable[[], None]:
           """Register a passive observer. Returns an unsubscribe callable.

           Observers are invoked synchronously from the lifecycle guard,
           after rclpy has produced the transition outcome. Observer
           exceptions are caught, logged at debug, and dropped.
           """

The observer is a notification channel. It does not influence transitions,
does not gate them, does not see ``rclpy`` internals.

Emission sites
~~~~~~~~~~~~~~

Single emission chokepoint: the existing lifecycle guard
(``_guarded_call`` + ``_worst_of`` per Error Policy Rule D). Events are
emitted *after* ``_worst_of`` so that ``cleanup`` / ``shutdown`` / ``error``
events reflect the merged result, not the raw hook return.

Direct-call rejection paths (``InvalidLifecycleTransitionError``,
``ConcurrentTransitionError``) emit one ``rejected`` event before raising.

No emission anywhere else. In particular: no emission inside ``_on_*``
hooks, no emission inside ``publish``, no emission inside subscription
callbacks.

Invariants preserved
--------------------

* **Passive observer.** Observability never drives transitions, never
  derives state, never queues work that could reorder the native lifecycle.
* **No parallel state machine.** All fields (``from_state``, ``to_state``,
  ``outcome``) are read from rclpy / the guard's already-computed result.
  No shadow FSM.
* **Single chokepoint.** All transition events flow through the existing
  guard. This avoids the drift risk explicitly forbidden by the
  *ComposedLifecycleNode does NOT introduce custom transition logic*
  contract.
* **Hot-path logging policy unchanged.** Per Error Policy Rule C, gated
  inbound drops stay at ``debug`` and caught ``on_message`` exceptions stay
  at ``error``. No event is emitted on the message hot path.
* **Hooks never raise outward** (Rule B). Observer callbacks are wrapped:
  exceptions caught, logged at debug, dropped. An observer cannot crash a
  transition.
* **Tolerant of skipped component shutdown.** Per ros2 transverse note,
  managed-entity ``on_shutdown`` may be skipped from Unconfigured/Inactive.
  Consumers MUST treat the event stream as best-effort for terminal
  transitions.
* **Stable error vocabulary.** ``error_class`` uses the existing
  :class:`lifecore_ros2.LifecoreError` hierarchy and stdlib classes; no new
  exception types are introduced for observability.
* **Public API stability.** ``LifecycleEvent`` and
  ``add_lifecycle_observer`` are additive in ``__all__``.
* **No new runtime dependency.** No OpenTelemetry, no ``tracetools``, no
  third-party tracing library. Adapters to such backends are user code.

.. _observability-prerequisite-gates:

Prerequisite gates
------------------

* §4 — :doc:`../architecture` *Concurrency Contract*: observer callbacks run
  under the same threading guarantees as the guard. The reused ``RLock``
  bounds reentrancy; observer authors must respect "do not call back into
  the node from the callback".
* §5 — :doc:`../architecture` *Strict direct-call contract*: rejection
  events depend on the typed exceptions
  (:class:`InvalidLifecycleTransitionError`,
  :class:`ConcurrentTransitionError`) being the canonical signal.
* §6 — Lifecycle test coverage: observer behavior reuses the existing walks
  (full cycle, double activate, deactivate-without-activate, configure
  failure rollback) as fixtures.

Open questions
--------------

These are explicitly unresolved. To be answered in the implementation PR.

1. **Synchronous vs. queued delivery.** Sync keeps ordering trivial and
   avoids a side queue (fits "passive observer"). Queued isolates slow
   observers but creates a parallel buffer. *Tentative*: synchronous, with
   a documented "do fast work or hand off" rule.
2. **Observer reentrancy.** Should an observer be allowed to call
   ``list_components`` (introspection note)? Reading is safe under the
   ``RLock``; writing (``add_component``) is forbidden because the gate may
   already be closed.
3. **Per-component vs. node-level subscription.** Single
   ``add_lifecycle_observer`` on the node only, or also a per-component
   variant? *Tentative*: node-level only; consumers filter by
   ``component`` field.
4. **Logger choice for Layer A.** ``self.get_logger()`` (node logger) for
   every line, or a child logger ``self.get_logger().get_child("lifecycle")``
   for transition events? *Tentative*: child logger, to allow operators to
   tune the lifecycle category independently.
5. **Field stability commitment.** Are the mandatory fields part of the
   stable public contract (semver-protected) or best-effort? *Tentative*:
   stable; additions are non-breaking, removals require a major bump.
6. **Adapter examples.** Should ``examples/`` ship a tiny ros2_tracing
   adapter or an OpenTelemetry adapter? *Tentative*: no — keep adapters
   out-of-tree until at least one real consumer exists.
7. **Time source.** ``time.monotonic_ns()`` (process-local, monotonic) vs
   ``rclpy.Clock`` (sim-time aware). *Tentative*: ``monotonic_ns`` for
   ``duration_ms`` math; sim-time is irrelevant to wall-clock duration of
   a Python hook.

Non-goals
---------

* **No new write API.** Observers cannot influence, cancel, or reorder
  transitions.
* **No ROS topic / service for events.** The event stream is a Python API
  on the node instance. ROS-graph publication is user adapter code.
* **No third-party tracing dependency.** OpenTelemetry, ``tracetools``,
  ``ros2_tracing`` integration — out of scope. Stay rclpy-only.
* **No metric counters.** No library-side aggregation (counts,
  histograms). Observability stays event-shaped.
* **No on-message-hot-path events.** Activation gating drops stay at
  ``debug``; nothing is added on the per-message path.
* **No state cache for fast queries.** Snapshots come from the
  introspection note's read-through API; observability does not duplicate
  it.
* **No log message template freeze.** Only the structured field set is
  contractual.
