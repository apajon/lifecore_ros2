Architecture
============

Overview
--------

.. Canonical positioning sentence — keep in sync with pyproject.toml project.description.

lifecore_ros2 is a minimal lifecycle composition library for ROS 2 Jazzy — no hidden state machine.

The architecture is centered on two layers:

- a lifecycle-aware core in ``src/lifecore_ros2/core``
- reusable topic-oriented components in ``src/lifecore_ros2/components``

Node–Component Ownership
------------------------

``LifecycleComponentNode`` owns and drives every registered ``LifecycleComponent``.
The relationship is one-to-many: one node, any number of named components.

.. code-block:: text

    LifecycleComponentNode
    │
    ├── owns: List[LifecycleComponent]
    │         (registered via add_component() before first transition)
    │
    └── drives: propagates on_configure / on_activate / on_deactivate
                         / on_cleanup / on_shutdown / on_error
                to each component in registration order

Key ownership rules:

- Components are registered by name via ``add_component(component)``. Names must be unique.
- Registration is closed after the first lifecycle transition. Any subsequent call to
  ``add_component()`` raises ``RegistrationClosedError``.
- Each component holds a back-reference to its parent node (``component.node``).
  Accessing ``node`` before attachment raises ``ComponentNotAttachedError``.
- The node calls each component's lifecycle hooks in registration order.
  If one component returns ``FAILURE`` or ``ERROR``, the node's transition result reflects
  the worst outcome across all components.

Thread-safety of ``add_component``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All accesses to the component registry and the registration gate are protected by an
internal ``threading.RLock`` (``self._lock`` on the node). This means ``add_component``
may be called safely from any thread, including threads that run before ``rclpy.spin``
starts.

The registration gate (``_registration_open``) is written and read inside the same lock,
so a thread calling ``add_component`` concurrently with the first lifecycle transition
will either succeed (if ``_close_registration`` has not yet acquired the lock) or raise
``RegistrationClosedError`` (if it has). There is no window where a component can be
partially registered.

Components registered before ``on_configure`` runs will have their hooks called during
the first transition. Components added after ``on_configure`` has been called raise
``RegistrationClosedError`` regardless of which thread makes the call.

.. note::

   The lock is reentrant (``RLock``), so application code that calls ``add_component``
   inside a node's own ``__init__`` or ``on_configure`` override is safe.

Transition Sequence
-------------------

The following sequence applies to every managed transition. The node is the single entry point
into the transition; component hooks are called inside it.

.. code-block:: text

    ROS 2 executor
        │
        ▼
    LifecycleComponentNode.on_configure(state)          ← rclpy calls this
        │
        ├── closes registration (no more add_component after this)
        │
        ├── for each component in registration order:
        │       component.on_configure(state)           ← @final; calls _guarded_call
        │           └── _guarded_call(component._on_configure, state)
        │                   catches exceptions → TransitionCallbackReturn.ERROR
        │                   returns SUCCESS / FAILURE / ERROR
        │
        └── returns worst(results) to rclpy

The same pattern repeats for ``on_activate``, ``on_deactivate``, ``on_cleanup``,
``on_shutdown``, and ``on_error``. Each uses ``_guarded_call`` so exceptions from hook
code never escape to the rclpy executor.

``on_activate`` additionally sets ``component._is_active = True`` on each component
whose hook returned ``SUCCESS``. ``on_deactivate`` clears it only on ``SUCCESS``.
``on_cleanup``, ``on_shutdown``, and ``on_error`` each clear ``_is_active = False``
**unconditionally before the hook runs**, then call ``_release_resources``
after the hook, regardless of the hook's return value, and propagate the worst of the
two results.

Topic-Resource Lifecycle
------------------------

``TopicComponent`` (and its subclasses ``LifecyclePublisherComponent`` and
``LifecycleSubscriberComponent``) follow a strict three-phase resource lifecycle:

.. code-block:: text

    configure                     activate                     deactivate
    ─────────                     ────────                     ──────────
    create publisher              _is_active = True            _is_active = False
    create subscription           start timers (app hook)      stop timers (app hook)
    store references              enable message dispatch       drop inbound messages

    cleanup / shutdown / error
    ──────────────────────────
    destroy publisher
    destroy subscription
    _release_resources() called automatically

The only state the framework tracks is ``_is_active``. There is no secondary resource-ready
flag. Whether a resource exists at runtime is determined entirely by whether ``_on_configure``
has run and ``_on_cleanup`` / ``_release_resources`` has not yet been called.

.. note::

   The framework does not own or start timers. The ``start timers`` and ``stop timers``
   entries above represent application code running inside ``_on_activate`` and
   ``_on_deactivate``. The framework has no built-in timer management.

Lifecycle Design
----------------

The repository follows native ROS 2 lifecycle semantics.
LifecycleComponentNode registers each component as a managed entity and relies on the underlying lifecycle node behavior to propagate transitions.

LifecycleComponent remains intentionally small:

- it is a managed entity
- it knows its parent node
- it exposes explicit lifecycle hooks
- it avoids introducing a parallel hidden state machine

Topic Components
----------------

Topic-oriented components should follow these rules:

- create ROS publishers and subscriptions during configure
- gate publication or message handling with activation state
- release ROS resources during cleanup

This keeps runtime behavior explicit and consistent with ROS 2 lifecycle expectations.

Lifecycle Invariants
--------------------

The following invariants are binding for all ``LifecycleComponent`` subclasses.

**configure**
  Allocate ROS resources: create publishers, subscriptions, timers.
  Do not enable runtime behavior. Do not set ``_is_active``.

**activate**
  Enable runtime behavior. Start publishing, accept message callbacks.
  Do not call ``super()._on_activate(state)`` — the framework sets ``_is_active = True``
  automatically after the hook returns SUCCESS.
  Do not allocate new ROS resources here.

**deactivate**
  Disable runtime behavior. Stop publishing, ignore incoming messages.
  ``_is_active`` is cleared to ``False`` only after ``_on_deactivate`` returns SUCCESS.
  A FAILURE or ERROR result leaves ``_is_active`` unchanged — the component stays active.
  Do not release ROS resources here — that is cleanup's responsibility.

**cleanup**
  Release all ROS resources allocated during configure.
  ``_release_resources()`` is called automatically by the framework after ``_on_cleanup`` returns.
  No explicit call is needed in the override.

**shutdown / error**
  ``_release_resources()`` is called automatically. No override needed for most subclasses.

**No parallel lifecycle**
  No component may introduce an internal state machine that diverges from or shadows
  the node lifecycle. ``_is_active`` is the only lifecycle-adjacent flag. It is
  managed exclusively by the ``@final`` framework entry points:

  - ``on_activate`` sets ``_is_active = True`` after ``_on_activate`` returns ``SUCCESS``.
  - ``on_deactivate`` clears ``_is_active = False`` after ``_on_deactivate`` returns ``SUCCESS``.
  - ``on_cleanup``, ``on_shutdown``, and ``on_error`` each clear ``_is_active = False``
    **unconditionally before** the ``_on_*`` hook runs, regardless of its return value.

  Subclasses must not read or write ``_is_active`` directly. Do not call
  ``super()._on_activate()`` or ``super()._on_deactivate()`` to manage the flag —
  the framework handles it.

**Activation gating**
  ``LifecyclePublisherComponent.publish()`` raises ``RuntimeError`` when inactive.
  ``LifecycleSubscriberComponent`` silently drops incoming messages when inactive.
  Both behaviors are intentional and consistent with explicit activation semantics.

Error Policy
------------

The framework enforces one coherent error policy across four axes.

**Rule A — Boundary violations raise**
  Misuse of the public API by application code raises a typed subclass of
  :class:`~lifecore_ros2.LifecoreError`. All concrete subclasses also inherit from
  the matching standard Python exception for backward-compatibility.

  .. list-table::
     :header-rows: 1

     * - Exception
       - Standard parent
       - When raised
     * - ``RegistrationClosedError``
       - ``RuntimeError``
       - ``add_component`` called after the first lifecycle transition
     * - ``DuplicateComponentError``
       - ``ValueError``
       - ``add_component`` called with a name that is already registered
     * - ``ComponentNotAttachedError``
       - ``RuntimeError``
       - ``.node`` accessed on a component not attached to a node
     * - ``ComponentNotConfiguredError``
       - ``RuntimeError``
       - ``publish()`` called before ``_on_configure`` created the publisher

  Catch ``LifecoreError`` to handle any framework misuse in one place.

**Rule B — Inside lifecycle hooks: never raise outward**
  ``_guarded_call`` wraps every ``_on_*`` hook invocation. Uncaught exceptions and
  invalid return values are both converted to ``TransitionCallbackReturn.ERROR`` with
  a logged traceback. Hook authors choose:

  - Return ``FAILURE`` — transition fails, node stays in its current state.
  - Return ``ERROR`` or raise — transition fails, node enters ``ErrorProcessing``.
  - Return ``SUCCESS`` — transition proceeds.

  The framework never lets an exception escape from a lifecycle hook into rclpy.

**Rule C — Activation gating: outbound raises, inbound drops**
  - **Outbound calls** initiated by application code (e.g. ``publish()``) raise
    ``RuntimeError`` by default via ``@when_active``. Application code can guard
    before calling; raising surfaces lifecycle programming errors early.
  - **Inbound callbacks** driven by the middleware (subscription callbacks, timer
    callbacks) silently drop the message when the component is inactive.
    The drop is logged at ``DEBUG`` level. Raising into the rclpy executor would
    crash the spin loop.
  - Both defaults are configurable via ``@when_active(when_not_active=...)``.
  - **Exceptions inside ``on_message``** are in a separate category: the message was
    delivered (the component was active), but the user's ``on_message`` implementation
    raised. These are caught by ``_on_message_wrapper``, logged at ``ERROR`` level
    with the exception type and message, and dropped. They never propagate to the
    executor. See the *Handle on_message exceptions inside the method* entry in
    :doc:`patterns` for guidance.

**Rule D — Error entry points and worst-result propagation**

  *When does rclpy call ``on_error``?*
  Any lifecycle transition that returns ``ERROR`` (or whose hook raises an uncaught
  exception, which the framework converts to ``ERROR`` via ``_guarded_call``) moves
  the node into the ``ErrorProcessing`` state. rclpy then calls ``on_error`` on the
  node, which in turn calls each component's ``on_error`` entry point.

  The return value of ``on_error`` determines the next node state:

  - ``SUCCESS`` — node returns to ``Unconfigured`` (resources have been released;
    the node can be reconfigured).
  - ``FAILURE`` or ``ERROR`` — node transitions to ``Finalized`` (terminal state;
    the process must be restarted to reuse the node).

  *How the framework handles the error entry point:*
  For each component, the framework's ``@final on_error`` entry point:

  1. Clears ``_is_active = False`` **unconditionally** (before the hook runs).
  2. Calls ``_on_error`` via ``_guarded_call`` (catches exceptions, converts to ``ERROR``).
  3. Calls ``_release_resources`` regardless of the hook result.
  4. Returns the *worst* of the two results (``SUCCESS < FAILURE < ERROR``).

  The same worst-result rule applies to ``on_cleanup`` and ``on_shutdown``:
  ``_on_cleanup``, ``_on_shutdown``, and ``_on_error`` each run the hook and then
  call ``_release_resources``. A failing hook does **not** skip ``_release_resources``.

  *Difference between returning ``ERROR`` from a hook and overriding ``_on_error``:*
  Returning ``ERROR`` from any ``_on_*`` hook is how application code signals an
  unrecoverable transition failure — rclpy handles the state transition. Overriding
  ``_on_error`` is how a component performs cleanup work *after* the node has already
  entered ``ErrorProcessing``. Most components do not need to override ``_on_error``;
  the default returns ``SUCCESS``, and ``_release_resources`` is called automatically.

Member Convention
-----------------

Every class in ``lifecore_ros2`` assigns each method and attribute to exactly one
of four buckets. This is the authoritative guide for contributors and subclassers.

**Bucket 1 — Public API**
  Stable surface for direct use by application code. No leading underscore.
  Included in ``__all__`` at module level. Examples: ``name``, ``is_active``,
  ``add_component``, ``publish``, ``on_message``.

**Bucket 2 — Protected extension points**
  Override in subclasses; never call directly from application code. Single leading
  underscore. Docstring starts with ``Extension point.`` Examples: ``_on_configure``,
  ``_on_activate``, ``_on_deactivate``, ``_on_cleanup``, ``_on_shutdown``, ``_on_error``,
  ``_release_resources``. Rendered in API docs.

**Bucket 3 — Framework-controlled entry points**
  Implement the ``rclpy`` ``ManagedEntity`` / ``LifecycleNode`` protocol. Decorated with
  ``@typing.final`` on ``LifecycleComponent`` so pyright catches accidental overrides.
  On ``LifecycleComponentNode``, ``on_configure`` and ``on_shutdown`` are not sealed because
  application nodes legitimately call ``super()`` inside them; those carry an explicit
  "override with super" contract in their docstring. Examples: ``LifecycleComponent.on_configure``,
  ``on_activate``, ``on_deactivate``, ``on_cleanup``, ``on_shutdown``, ``on_error``.

**Bucket 4 — Framework-internal**
  Implementation details with no user contract. Single leading underscore. Docstring starts
  with ``Framework-internal. Do not call from user code.`` Excluded from API docs.
  Examples: ``_attach``, ``_detach``, ``_guarded_call``, ``_safe_release_resources``,
  ``_resolve_logger``, ``_close_registration``, ``_on_message_wrapper``.

When adding a new method, assign it to one bucket before writing the docstring.
