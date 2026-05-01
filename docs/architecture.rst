Architecture
============

This page is the contract surface for how the framework behaves during lifecycle transitions.
Read it after :doc:`Mental Model <concepts/mental_model>` and before treating the API reference as authoritative lookup.

.. raw:: html

   <div class="lifecycle-map">
     <div class="lifecycle-step"><strong>⚙ Configure</strong><p>Registration closes, components attach to the node, and resource ownership becomes explicit.</p></div>
     <div class="lifecycle-step"><strong>▶ Activate</strong><p>Successful hooks mark managed entities active and open runtime behavior.</p></div>
     <div class="lifecycle-step"><strong>▶ Run</strong><p>Hooks execute in order, results are aggregated, and the node remains the only entry point.</p></div>
     <div class="lifecycle-step lifecycle-step--transition"><strong>🔁 Transition</strong><p>Concurrency, propagation, and error policy define what happens when transitions overlap or fail.</p></div>
     <div class="lifecycle-step"><strong>■ Shutdown</strong><p>Cleanup, shutdown, and error handling clear active state and release resources deterministically.</p></div>
   </div>

Overview
--------

.. Canonical positioning sentence — keep in sync with pyproject.toml project.description.

lifecore_ros2 is a minimal lifecycle composition library for ROS 2 Jazzy — no hidden state machine.

The architecture is centered on two layers:

- a lifecycle-aware core in ``src/lifecore_ros2/core``
- reusable topic-oriented components in ``src/lifecore_ros2/components``

If you need the conceptual model before the structural details on this page, read
:doc:`Mental Model <concepts/mental_model>` first.

What this page answers
----------------------

- Who owns components and when registration closes.
- How transitions propagate and how results are aggregated.
- Which operations are thread-safe and which are intentionally single-threaded.
- When resources are created, gated, released, and considered invalid.

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

.. raw:: html

   <div class="state-box">
     <strong>Ownership rule.</strong>
     The node owns lifecycle entry, registration, and result aggregation. Components own focused behavior inside hooks, not the transition control plane.
   </div>

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

Read the sequence as a lifecycle pipeline: node entry, registration gate, ordered hook calls,
result aggregation, then a single return to ``rclpy``.

``on_activate`` additionally sets ``component._is_active = True`` on each component
whose hook returned ``SUCCESS``. ``on_deactivate`` clears it only on ``SUCCESS``.
``on_cleanup``, ``on_shutdown``, and ``on_error`` each clear ``_is_active = False``
**unconditionally before the hook runs**, then call ``_release_resources``
after the hook, regardless of the hook's return value, and propagate the worst of the
two results.

Concurrency Contract
--------------------

This section exists to keep the lifecycle readable under pressure.
The framework allows thread-safe registration before the first transition, but it does not normalize concurrent transition execution as a supported runtime pattern.

.. rubric:: ADR — Threading model: single-threaded executor with thread-safe registration

**Decision:** lifecore_ros2 targets the ROS 2 ``SingleThreadedExecutor`` model.
Lifecycle transitions are driven sequentially by the ROS 2 executor and must not be
called concurrently from multiple threads. Component registration (``add_component``)
is additionally protected by an internal ``threading.RLock`` to allow calling from
any thread before the first transition starts.

**Rationale:**
``SingleThreadedExecutor`` is the default for lifecycle nodes in ROS 2. Introducing
mutex-based protection around every transition would add overhead and complexity for
a scenario that is not part of standard ROS 2 usage. The existing ``RLock`` on the
registration gate already handles the common pre-spin setup pattern, where an
application may register components from a constructor or a setup thread before
calling ``rclpy.spin``.

**Consequences:**
Application code that runs ``LifecycleComponentNode`` under a
``MultiThreadedExecutor`` must not trigger lifecycle transitions concurrently. The
framework enforces this with ``ConcurrentTransitionError``, described below.

Thread-safety guarantees
~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 20 40

   * - Operation
     - Thread-safe?
     - Mechanism
   * - ``add_component`` (before first transition)
     - Yes
     - ``threading.RLock`` — safe from any thread, including pre-spin setup
   * - ``add_component`` (after first transition)
     - Yes (raises)
     - ``RegistrationClosedError`` raised inside the lock — no partial state
   * - ``get_component``, ``components`` property
     - Yes
     - ``threading.RLock``
   * - Lifecycle transitions (``on_configure``, ``on_activate``, etc.)
     - Single-thread only
     - Relies on the ROS 2 executor; concurrent calls raise ``ConcurrentTransitionError``
   * - Component hook execution (``_on_configure``, etc.)
     - Single-thread only
     - Called synchronously inside the transition; no cross-thread dispatch

Forbidden concurrent transitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Calling any lifecycle hook (``on_configure``, ``on_activate``, ``on_deactivate``,
``on_cleanup``, ``on_shutdown``) while another transition is already running is a
programming error. The framework detects this via an internal ``_in_transition`` flag
guarded by ``_lock`` and raises :exc:`~lifecore_ros2.ConcurrentTransitionError`:

.. code-block:: text

    Thread A: on_configure()  ──────────────────────────────────►
    Thread B:        on_activate()  ← raises ConcurrentTransitionError immediately

The flag is set atomically at the start of each hook entry point and cleared in a
``finally`` block so it is always released, even if the transition fails.

.. note::

   ``on_error`` is **not** guarded by ``_in_transition``. rclpy calls ``on_error``
   as part of the error-recovery path after a failed transition. Guarding it would
   interfere with normal error handling.

Reentrancy from callbacks
~~~~~~~~~~~~~~~~~~~~~~~~~

Lifecycle hooks are called synchronously by the ROS 2 executor. A component's
``_on_configure`` (or any other ``_on_*`` hook) must not call back into a lifecycle
transition on the same node — doing so would trigger ``ConcurrentTransitionError``
because ``_in_transition`` is still set.

Calling ``add_component`` from within a lifecycle hook is safe (the ``RLock`` is
reentrant), but any component added after ``_close_registration`` has run will be
rejected with ``RegistrationClosedError``. ``_close_registration`` is called at the
start of ``on_configure`` and ``on_shutdown``.

Component destruction during active callbacks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The framework does not manage component lifetime beyond the lifecycle transitions it
drives. If application code destroys a component object while a subscription or timer
callback is executing on that component, the result is undefined. The contract is:

- Release component resources explicitly in ``_on_cleanup`` / ``_on_shutdown``.
- Do not hold external references to component objects beyond the node's lifetime.
- Do not destroy a node while it is still being spun. Call ``rclpy.shutdown()`` or
  stop the executor before releasing the node object.

Topic-Resource Lifecycle
------------------------

This is the resource contract that should shape how you read component code.
If resource lifetime is unclear in an implementation, check it against this section first.

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

**Strict direct-call contract**
  ``LifecycleComponent.on_*`` remains framework-owned. When a component hook entry point is
  called directly in an invalid order, lifecore_ros2 now raises
  ``InvalidLifecycleTransitionError`` instead of silently accepting the sequence.

  The node-driven path stays lifecycle-native: invalid node transitions are still rejected by
  the native rclpy state machine, and the framework logs the attempted transition, current node
  state, and attached components before re-raising the native error. The extra component-side
  bookkeeping is limited to boundary checks for direct calls plus a cleanup-needed flag used to
  prevent direct reconfigure before resources are released. This is not an independent lifecycle
  controller.

  .. list-table:: Invalid transition handling
     :header-rows: 1

     * - Invalid case
       - Node-level path
       - Direct ``LifecycleComponent.on_*`` path
     * - ``activate`` before ``configure``
       - Native rclpy rejection
       - ``InvalidLifecycleTransitionError``
     * - repeated ``configure`` without ``cleanup``
       - Native rclpy rejection
       - ``InvalidLifecycleTransitionError``
     * - repeated ``activate`` without ``deactivate``
       - Native rclpy rejection
       - ``InvalidLifecycleTransitionError``
     * - ``deactivate`` without prior ``activate``
       - Native rclpy rejection
       - ``InvalidLifecycleTransitionError``
     * - ``cleanup`` before ``configure``
       - Native rclpy rejection
       - ``InvalidLifecycleTransitionError``
     * - ``cleanup`` while active
       - Native rclpy rejection
       - ``InvalidLifecycleTransitionError``

  Every direct rejection logs the component name, attempted transition, current contract state,
  and rejection reason before raising.

**Configure failure rollback**
  A failed node-driven ``configure`` no longer leaves half-configured components visible to the
  node. After a managed ``configure`` returns ``FAILURE`` or ``ERROR``,
  ``LifecycleComponentNode`` calls ``_release_resources()`` on every attached component to
  restore a coherent unconfigured state before returning the final result.

**Activation gating**
  ``LifecyclePublisherComponent.publish()`` raises ``RuntimeError`` when inactive.
  ``LifecycleSubscriberComponent`` silently drops incoming messages when inactive.
  ``LifecycleServiceClientComponent.call()`` and ``call_async()`` raise
  ``RuntimeError`` when inactive; in-flight futures are not cancelled on
  deactivate (the application owns them).
  ``LifecycleServiceServerComponent`` does not silently drop inactive requests:
  it logs a warning and returns a default-constructed response, populating
  ``success=False`` / ``message="component inactive"`` when those fields exist.
  All four behaviors are intentional and consistent with explicit activation
  semantics.

Naming Conventions
------------------

Framework type names are stable and must not be changed or aliased.

**Fixed names:**

- ``LifecycleComponent`` — the core reusable abstraction for a lifecycle-aware modular unit.
- ``LifecycleComponentNode`` — the framework base node that owns and drives registered components.

**Application node names** must use domain/business names, not framework names:

.. code-block:: python

    # Correct
    class CameraNode(LifecycleComponentNode): ...
    class NavigationNode(LifecycleComponentNode): ...

    # Wrong — do not embed framework terms in application class names
    class LifecycleCameraNode(LifecycleComponentNode): ...

**Framework-provided components** follow the pattern ``Lifecycle<Capability>Component``:

- ``LifecyclePublisherComponent``
- ``LifecycleSubscriberComponent``
- ``LifecycleTimerComponent``
- ``LifecycleServiceServerComponent``
- ``LifecycleServiceClientComponent``

**Explicit rules:**

- No ``Abstract`` prefix. Use ``Base`` or no prefix if a base class is needed.
- No ``*Manager``, ``*Handler``, ``*Core`` synonyms without explicit review justification.
  These terms signal hidden complexity; prefer a descriptive name tied to one responsibility.
- No redundant qualifiers (``Impl``, ``Mixin``, ``Core``) appended mechanically to a type name.

These rules are enforced in pull request review. Any new class that violates them
must include an explicit justification in the PR description.

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

**Error Propagation Contract**

  The following table is the authoritative propagation matrix for all ``_on_*`` hooks.
  See :doc:`design_notes/error_handling_contract` for the full rationale.

  .. list-table:: Hook outcome → framework action
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

  **Locked decisions (Sprint 2, ratified 2026-04-30):**

  1. **Rollback policy B — all-or-nothing.** A composite transition fails as soon as one
     component fails. The node returns ``FAILURE``; siblings that already transited are not
     externalised as partial. No reverse replay of ``_on_cleanup`` hooks.
  2. **``LifecycleHookError`` wraps caught hook exceptions.** The framework creates a
     :class:`~lifecore_ros2.LifecycleHookError` (``__cause__`` set to the original exception)
     for logging context. It is never propagated to ``trigger_*`` callers.
  3. **Strict mode is the default and is non-configurable.** Any ``_on_*`` hook that returns
     a value outside ``{SUCCESS, FAILURE, ERROR}`` is logged at ``ERROR`` and treated as
     ``ERROR``. There is no lenient mode.
  4. **``_on_error`` is driven only by native rclpy ``ERROR_PROCESSING``.** The framework
     never synthesises an extra call to ``_on_error`` on caught exceptions. The native flow
     (exception → wrapper returns ``ERROR`` → rclpy enters ``ErrorProcessing`` → ``on_error``
     → ``_release_resources``) provides the full guarantee.

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
