Runtime Introspection — Design Note
====================================

.. admonition:: Audience
   :class: note

  Contributors and advanced readers evaluating future directions of
  ``lifecore_ros2``. This is a **design note**, not committed user
  documentation. No code under ``src/lifecore_ros2/`` exists for this feature
  yet.

.. admonition:: Status
   :class: important

   Draft — gated on §4 (concurrency) and §5 (strict lifecycle contract) being
   green. See :ref:`runtime-introspection-prerequisite-gates`.

Intent
------

Provide a small, **read-only** API to answer three questions from outside the
node:

1. *Which components are currently registered with this*
   :class:`lifecore_ros2.LifecycleComponentNode` *?*
2. *What is the lifecycle state of the node and of each component?*
3. *Which ROS resources (publishers, subscribers) does each component
   currently hold?*

Goal: support diagnostics, debugging, and external orchestration without
forcing callers to reach into private attributes (``_components``,
``_registration_open``, ``_resources``).

Proposed contract
-----------------

Surface added to :class:`lifecore_ros2.LifecycleComponentNode`. All methods are
read-only and side-effect free.

.. code-block:: python

   class LifecycleComponentNode:

       def list_components(self) -> tuple[str, ...]:
           """Return the names of currently registered components.

           Order is registration order. Returned tuple is a snapshot; it does
           not track subsequent registrations.
           """

       def get_component_state(self, name: str) -> State:
           """Return the rclpy lifecycle ``State`` of the named component.

           Reads through to ``rclpy``; never returns a library-cached value.
           Raises ``ComponentNotFoundError`` if the name is unknown.
           """

       def is_registration_open(self) -> bool:
           """Return whether ``add_component`` would currently be accepted.

           Equivalent to: "no lifecycle transition has occurred yet".
           """

Surface added to :class:`lifecore_ros2.LifecycleComponent`. Optional, opt-in
per concrete component.

.. code-block:: python

   class LifecycleComponent:

       def describe_resources(self) -> Mapping[str, str]:
           """Return a name -> ROS topic/type description of held resources.

           Default implementation returns an empty mapping. Concrete components
           (e.g. ``LifecyclePublisherComponent``) override to expose their
           topic, message type, and QoS profile name. Must not return live
           handles to the underlying rclpy objects.
           """

Return-type discipline
~~~~~~~~~~~~~~~~~~~~~~

* Snapshots only. ``list_components`` returns a ``tuple``, never the live
  internal collection.
* No live handles. ``describe_resources`` returns descriptions
  (strings / dataclasses), never the rclpy publisher or subscriber object.
* Lifecycle state is **always** read from rclpy at call time. No library
  field shadows the node's lifecycle state machine.

Invariants preserved
--------------------

* **Single source of truth.** rclpy is the source of truth for lifecycle
  state; the node's ``_components`` registry is the source of truth for the
  set of managed entities. Introspection reads through these — it never
  caches, mirrors, or precomputes.
* **No parallel state machine.** Reading ``get_component_state`` must not
  build any state outside what ``rclpy`` already exposes. (See
  :doc:`../architecture` — *Core principle: native ROS 2 lifecycle semantics
  stay in control*.)
* **Transparent component state** (lifecycle component contract): the
  introspection surface only exposes what is already conceptually visible;
  it does not promote private fields to public.
* **No ghost entries.** Introspection must never observe a component that is
  not fully registered. Implementation reads under the existing
  ``threading.RLock`` documented in
  :doc:`../architecture` — *Concurrency Contract*.
* **Registration gate is read-only-friendly.** ``is_registration_open`` is a
  pure read; calling it never closes the gate or otherwise mutates state.
* **Public API stability.** New symbols are additive. ``__all__`` in
  :mod:`lifecore_ros2` is extended, not reordered or pruned.

.. _runtime-introspection-prerequisite-gates:

Prerequisite gates
------------------

This note assumes the following are already in place:

* §4 — :doc:`../architecture` *Concurrency Contract*: defines the
  ``threading.RLock`` and the single-threaded executor ADR. Introspection
  reuses that lock; it does not introduce a new synchronisation primitive.
* §5 — :doc:`../architecture` *Strict direct-call contract*: guarantees that
  observable state is coherent (no half-configured components leaking through
  a failed transition). Introspection's correctness depends on this rollback
  guarantee.
* §6 — Test coverage for lifecycle walks and concurrent registration: any
  introspection implementation reuses these tests as the baseline observable
  behavior.

Implementation must not be opened until these gates are still green at the
time of work.

Open questions
--------------

These are explicitly unresolved. They must be answered in the implementation
PR, not silently in code:

1. **Component-side state accessor.** Should ``LifecycleComponent`` expose a
   ``state`` property mirroring ``get_component_state(name)``, or should
   callers always go through the node? *Tentative*: through the node only,
   to avoid duplicating the same read in two places.
2. **Iteration vs. snapshot.** Is ``tuple[str, ...]`` sufficient, or should
   we offer ``items() -> Mapping[str, LifecycleComponent]``? Returning
   component instances exposes more surface; weigh against the "transparent
   component state" invariant.
3. **Resource description schema.** Free-form ``Mapping[str, str]`` vs. a
   typed dataclass (``ResourceDescriptor(kind, topic, msg_type, qos)``)?
   Typed is friendlier but locks the schema early.
4. **Behavior during shutdown.** After ``on_shutdown``, should
   ``list_components`` return ``()`` or the last known set? *Tentative*:
   last known set, until ``destroy_node``; behavior after ``destroy_node``
   is undefined.
5. **Error type.** Reuse :class:`lifecore_ros2.LifecoreError` hierarchy with
   a new ``ComponentNotFoundError``, or rely on ``KeyError``? Consistency
   with existing :class:`ComponentNotAttachedError` suggests a typed error.
   *Resolved by* :doc:`dynamic_components` — a typed
   ``ComponentNotFoundError(LifecoreError, KeyError)`` is introduced there
   and reused here.
6. **Thread-safety guarantee under spin.** The current ``RLock`` covers
   registration; reads from a separate thread during ``spin`` are *believed*
   safe but not exercised by tests. Confirmation requires a regression test
   in the implementation PR.

Non-goals
---------

* **No write API.** Nothing here removes, replaces, or reconfigures
  components. Runtime mutation belongs to the *Dynamic components* design
  note.
* **No event stream.** Introspection is pull-based. Push notifications,
  subscriptions to lifecycle changes, and tracing belong to the
  *Observability* design note.
* **No new dependency.** ``pyproject.toml`` is unchanged.
* **No exposure of rclpy internals.** Live handles to publishers,
  subscribers, or the state machine object are out of scope.
* **No ROS service / topic facade.** Introspection is a Python API on the
  node instance, not a ROS-graph-level interface.
* **No promotion of private attributes.** ``_components``,
  ``_registration_open``, ``_resources``, and ``_lock`` remain private.
