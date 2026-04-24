Dynamic Components — Design Note
=================================

.. admonition:: Audience
   :class: note

   Internal contributors of ``lifecore_ros2``. This is a **design note**, not
   user documentation. No code under ``src/lifecore_ros2/`` exists for this
   feature yet. ``remove_component`` already exists but is gated to the
   pre-transition window only — see :ref:`dynamic-components-current-state`.

.. admonition:: Status
   :class: important

   Draft — gated on §4 (concurrency), §5 (strict lifecycle contract), and §6
   (test coverage) being green. See
   :ref:`dynamic-components-prerequisite-gates`.

Intent
------

Allow ``add_component`` and ``remove_component`` to be called at runtime,
i.e. **after the first lifecycle transition has occurred**, while keeping
the framework's core invariants intact:

* native ``rclpy`` lifecycle semantics stay in control,
* no parallel hidden state machine,
* no ghost or partially-registered entries.

Goal: make a node hot-reloadable in the small (replace one component, add a
new pipeline stage, drop a deprecated subscriber) without restarting the
process or destroying the node.

.. _dynamic-components-current-state:

Current state — what already exists
-----------------------------------

Read this before proposing anything. The codebase already encodes a partial
answer.

Registration gate
~~~~~~~~~~~~~~~~~

:class:`lifecore_ros2.LifecycleComponentNode` keeps an
``_registration_open`` flag that flips to ``False`` on the first lifecycle
transition (``on_configure``) and on ``on_shutdown``. After closure,
``add_component`` raises :class:`RegistrationClosedError`. This is documented
in :doc:`../architecture` and validated by
``tests/test_regression_add_component.py``.

Rationale (recovered from the registration-gate ADR): rclpy does not
catch a late-added managed entity up to the node's current lifecycle state.
A component added after ``on_configure`` would miss its own ``_on_configure``
and enter activation in an inconsistent state.

``remove_component`` — pre-transition only
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``remove_component(name)`` method exists on
:class:`LifecycleComponentNode`. It is currently restricted to the
pre-transition window (``_registration_open is True``); calling it later
raises :class:`RegistrationClosedError`.

Implementation uses a ``_withdrawn`` flag on the component so that, even if
the component remains in rclpy's managed-entity list, all subsequent
transition callbacks return ``SUCCESS`` as a silent no-op. This is the
**Option B** sketched in ``TODO_adoption_hardening.md`` (repo root):

   *Option B (current): ``_withdrawn`` flag silences the component as a
   ghost managed entity — acceptable for pre-transition use, not clean
   post-transition.*

The same TODO file documents that runtime removal is not safe under Option B
because rclpy still owns the entity reference, and that **Option C**
(framework-driven propagation) is the path forward:

   *Option C (future): take over propagation from rclpy, iterate
   ``_components.values()`` directly in each ``on_*`` method. Enables true
   runtime removal.*

This note specifies Option C and the runtime-add side that mirrors it.

Why Option B is insufficient post-transition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* The withdrawn component stays in rclpy's managed-entity list. Memory and
  reference are not actually released until the node is destroyed.
* Any introspection that walks rclpy's list (rather than ``_components``)
  still sees a ghost. This breaks the introspection note's "no ghost
  entries" invariant.
* Resource release is never triggered for a withdrawn component if the node
  never reaches ``on_cleanup`` / ``on_shutdown`` after withdrawal — by Error
  Policy Rule D, ``_release_resources`` runs only inside those hooks. A
  component withdrawn while the node is *active* would leak its
  publishers/subscribers until the node terminates.
* The "non-atomic add" anti-pattern (orchestration room) extends symmetrically
  to remove: a partial removal that leaves the entity in rclpy but absent
  from ``_components`` is a ghost in the other direction.

Proposed contract — Option C
----------------------------

The framework takes over lifecycle propagation. ``rclpy``'s native
managed-entity propagation is bypassed for components; transitions iterate
``_components.values()`` directly. This unlocks both runtime removal
(release resources cleanly) and runtime add (replay missed transitions).

API surface
~~~~~~~~~~~

.. code-block:: python

   class LifecycleComponentNode:

       def add_component(self, component: LifecycleComponent) -> None:
           """Register a component.

           Pre-transition: as today. Post-transition: the new component is
           caught up to the node's current state by replaying transitions
           in order. Replay sequence depends on the node's current state
           (see *Replay semantics for runtime add* below). Replay is
           atomic: failure rolls back fully and raises, leaving no entry
           in ``_components``.
           """

       def remove_component(self, name: str) -> None:
           """Unregister a component.

           Pre-transition: as today. Post-transition: the framework drives
           the component down to ``Unconfigured`` through the lifecycle
           (``_on_deactivate`` if active, then ``_on_cleanup``), releasing
           resources via the normal ``_release_resources`` path. The
           node-level ``on_shutdown`` is *not* run — the node itself is
           not shutting down. Then detach and drop from ``_components``.
           """

Both calls hold the existing ``threading.RLock`` for the entire mutate +
replay sequence. They are forbidden from inside a lifecycle hook (would
deadlock or reorder transitions) — see Open question 1.

Replay semantics for runtime add
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Map of node state → replay sequence applied to the new component:

* ``Unconfigured`` — none (matches current pre-transition behavior).
* ``Inactive`` — ``_on_configure`` only.
* ``Active`` — ``_on_configure`` then ``_on_activate``.
* ``Finalized`` — refuse with :class:`RegistrationClosedError`.
* During a transition — refuse with
  :class:`ConcurrentTransitionError` (existing exception).

Each replayed step uses the existing guard (``_guarded_call``) so
observability (Layer A logs and Layer B events from the observability note)
covers replays without special-casing.

Removal semantics for runtime remove
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Symmetric tear-down driven by the node:

* ``Unconfigured`` / pre-transition — drop from ``_components``, detach;
  no hooks run.
* ``Inactive`` — run ``_on_cleanup`` (with ``_release_resources`` per Rule D),
  then drop and detach.
* ``Active`` — run ``_on_deactivate``, then ``_on_cleanup``, then drop and
  detach. ``_on_shutdown`` is not run because the node itself is not
  shutting down.
* ``Finalized`` — refuse with :class:`RegistrationClosedError` (the node is
  done; nothing to remove).
* During a transition — refuse with :class:`ConcurrentTransitionError`.

Failure of any teardown hook follows Rule D: ``_release_resources`` still
runs; the worst result is logged. Even on failure, the component is removed
from ``_components`` and detached, because retaining it would create the
ghost case forbidden by the non-atomic-add anti-pattern.

Atomicity contract
~~~~~~~~~~~~~~~~~~

Mirror of the existing add anti-pattern:

* **Add success** — component is in ``_components`` *and* attached *and*
  caught up to current state.
* **Add failure** — component is *not* in ``_components`` *and* detached;
  any partially-allocated resources are released via the same path
  ``_on_cleanup`` would use.
* **Remove success** — component is *not* in ``_components`` *and* detached
  *and* its resources are released.
* **Remove failure of a teardown hook** — component is still removed from
  ``_components`` and detached (forced); the failure is reported via the
  observer event (``outcome=error``). This is the only place the framework
  proceeds past a hook failure to preserve the "no ghost" invariant.

Typed exceptions
~~~~~~~~~~~~~~~~

* :class:`RegistrationClosedError` — already exists; reused for
  ``Finalized`` state.
* :class:`ConcurrentTransitionError` — already exists; reused for
  mid-transition mutation.
* New: ``ComponentNotFoundError(LifecoreError, KeyError)`` — replaces the
  current bare ``KeyError`` raised by ``remove_component`` for unknown
  names. Multi-inherits ``KeyError`` per Error Policy Rule A pattern.

Invariants preserved
--------------------

* **Native rclpy lifecycle stays in control of the node.** Option C
  bypasses rclpy *only* for component-level propagation; the underlying
  ``rclpy.lifecycle.LifecycleNode`` itself still drives its own state
  machine. There is no parallel state machine on the node side.
* **No ghost entries.** Add is atomic; remove is forced past hook failure
  precisely to avoid ghosts.
* **Resource release goes through the lifecycle path.** Runtime remove
  triggers the existing ``_on_cleanup`` → ``_release_resources`` chain; no
  new direct-call to ``_release_resources`` from outside a hook.
* **Concurrency contract intact.** All mutation is under the existing
  ``RLock``; reentrancy from hooks is forbidden via the existing
  ``ConcurrentTransitionError``.
* **Error policy unchanged.** Boundary errors (Rule A), hook exceptions
  (Rule B), activation gating (Rule C), and worst-of teardown propagation
  (Rule D) all apply unmodified to runtime add/remove.
* **Observer events.** Layer B emits one event per replayed step on add and
  per teardown step on remove. No new emission site.
* **Public API stability.** ``ComponentNotFoundError`` is additive; the
  semantic change to ``add_component`` / ``remove_component`` (gate
  relaxation) is opt-in by virtue of being post-transition — pre-transition
  callers see no behavioral change.

.. _dynamic-components-prerequisite-gates:

Prerequisite gates
------------------

* §4 — :doc:`../architecture` *Concurrency Contract*: Option C reuses the
  ``RLock`` and the single-threaded executor ADR. Without §4 green, the
  reentrancy and lock-ordering questions are unanswerable.
* §5 — :doc:`../architecture` *Strict direct-call contract*: rejection
  paths (``Finalized``, mid-transition) and rollback semantics depend on
  the strict typed-exception contract.
* §6 — Lifecycle test coverage: replay correctness can only be claimed if
  the existing full-cycle, double-activate, and concurrent-registration
  tests are stable as the regression baseline. The §6 deferred item
  (inter-component pub/sub interaction) does *not* gate this note.
* :doc:`runtime_introspection` — ``list_components`` /
  ``get_component_state`` are the natural way to verify add/remove from
  outside; the introspection note must land first or in parallel.
* :doc:`observability` — replay and teardown events ride the existing
  Layer B channel; the observability note must land first or in parallel.

Open questions
--------------

To be answered in the implementation PR, not silently in code.

1. **Reentrancy from hooks.** ``add_component`` / ``remove_component``
   from inside an ``_on_*`` hook: forbid (raise
   :class:`ConcurrentTransitionError`) or allow (run after current
   transition completes)? *Tentative*: forbid. Allowing it implies a
   queue, which is the parallel state machine the project rejects.
2. **Replay granularity for runtime add in ``Active``.** Run
   ``_on_configure`` then ``_on_activate`` as two separate guarded calls
   (two events, clear failure point) or one fused step? *Tentative*: two
   separate guarded calls.
3. **Failure of replay during runtime add.** If ``_on_configure`` succeeds
   but ``_on_activate`` fails, do we leave the new component ``Inactive``
   (asymmetric with siblings) or roll all the way back? *Tentative*: roll
   back — call ``_on_cleanup`` to release resources, detach, drop from
   ``_components``, raise.
4. **Forced removal on teardown hook failure.** Confirmed above as the
   chosen rule. Document as an explicit exception to "no proceed past a
   failed hook" or generalize? *Tentative*: explicit, narrow exception.
5. **Interaction with rclpy's managed-entity list.** Option C bypasses
   rclpy propagation but rclpy still references the components it was
   given via ``add_managed_entity``. Do we (a) keep them in rclpy's list
   inert, (b) remove them via a private rclpy API, or (c) never call
   ``add_managed_entity`` in the first place? *Tentative*: (c) — Option
   C means the framework owns propagation end to end; passing components
   to rclpy is what created Option B's ghost problem. Verify this is
   actually possible without breaking rclpy lifecycle node assumptions.
6. **Concurrent runtime add and remove.** Two threads call
   ``add_component`` and ``remove_component`` simultaneously. RLock
   serialises them, so order is non-deterministic but consistent.
   Document as "serialised, order is observation order" rather than
   inventing a priority.
7. **Naming.** Should runtime-only behavior be exposed under
   ``add_component`` / ``remove_component`` (overloaded semantics) or
   under explicit ``add_component_runtime`` / ``remove_component_runtime``
   variants? *Tentative*: same name. Two names imply two contracts; the
   contract is uniform once Option C ships.
8. **Test surface.** Concrete regression tests required: runtime-add in
   ``Inactive``, runtime-add in ``Active``, runtime-remove in
   ``Inactive``, runtime-remove in ``Active``, replay failure rollback,
   teardown failure forced removal, mid-transition rejection, concurrent
   add/remove. Match these against §6's existing structure.
9. **MemPalace persistence.** The "Option B vs Option C" deferred ADR is
   currently only in ``TODO_adoption_hardening.md`` (repo root). Once Option C
   is decided, persist via the MemPalace Knowledge Writer agent. Until
   then, this note is the canonical source.

Non-goals
---------

* **No live reconfiguration of an existing component.** Replace by
  ``remove_component`` + ``add_component``; do not introduce a
  ``replace_component`` shortcut.
* **No partial-state add.** A new component cannot be inserted "directly
  in ``Active``" without going through ``_on_configure``; replay is the
  only path.
* **No proceed-past-failure on add.** Asymmetric with the forced-removal
  rule, intentionally — adds that fail must roll back fully.
* **No new dependency.** Option C is implementable with the existing
  rclpy + stdlib surface.
* **No promotion of ``_withdrawn`` to a public concept.** Option B is
  internal scaffolding for the pre-transition window; once Option C
  ships, ``_withdrawn`` is removed.
* **No ROS-graph control surface.** No service / topic to add or remove
  components remotely. Consumers wrap the Python API themselves.
* **No batch operations.** ``add_components([...])`` /
  ``remove_components([...])`` are out of scope; consumers loop.
* **No re-entry for the §6 deferred item.** Inter-component pub/sub
  interaction tests remain out of scope; this note does not pull them in.
