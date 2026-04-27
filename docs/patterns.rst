Recommended Patterns and Anti-Patterns
=======================================

This page documents concrete patterns and anti-patterns for extending lifecore_ros2.
Each entry references the lifecycle invariant it upholds or violates (defined in :doc:`architecture`).

Recommended Patterns
--------------------

**Allocate ROS resources during configure, not in the constructor**

  Create publishers, subscriptions, and timers inside ``_on_configure``, not in ``__init__``.
  This keeps the component's constructor free of ROS dependencies and aligns with the
  **configure** invariant: resources exist if and only if a successful configure has run.

  .. code-block:: python

      class TelemetryComponent(LifecyclePublisherComponent[BatteryState]):
          def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
              result = super()._on_configure(state)  # creates the ROS publisher
              if result != TransitionCallbackReturn.SUCCESS:
                  return result
              self._diagnostics_timer = self.node.create_timer(5.0, self._publish_diagnostics)
              return TransitionCallbackReturn.SUCCESS

          def _release_resources(self) -> None:
              if self._diagnostics_timer is not None:
                  self.node.destroy_timer(self._diagnostics_timer)
                  self._diagnostics_timer = None
              super()._release_resources()  # destroys the ROS publisher

  Invariant upheld: **configure** (allocate in configure) and **cleanup** (release in
  ``_release_resources``, called automatically).

  .. seealso::

     :doc:`architecture` — Member Convention table for the ``super()._on_configure`` call
     contract on ``LifecyclePublisherComponent``.

**Gate runtime behavior with ``is_active`` or ``@when_active``**

  Any method that performs work driven by the node (timers, callbacks, periodic outputs) must
  be guarded by activation state. Use ``@when_active`` for application-level outbound calls
  or check ``self.is_active`` explicitly in timer callbacks.

  .. code-block:: python

      def _tick(self) -> None:
          if not self.is_active:
              return
          # publish only while active
          self.publish(build_message())

  Invariant upheld: **Activation gating**.

**Keep ``_on_*`` hooks deterministic and side-effect-free**

  Lifecycle hooks should only manage resource setup, teardown, or state flags.
  They should not call external services, perform I/O, or block. Blocking inside a hook
  blocks the executor.

  Invariant upheld: **activate**, **deactivate** — hooks are called synchronously inside
  the rclpy executor spin loop.

.. _patterns:borrow-only-contract:

**Treat ``callback_group`` (and other injected handles) as borrow-only**

  The optional ``callback_group`` accepted by ``LifecycleComponent`` and the topic
  components is **borrowed** from the application. The component stores a reference and
  forwards it to ``create_publisher`` / ``create_subscription``, but it never creates,
  reassigns, or destroys it. Lifetime belongs to the caller (typically the node or the
  application that built the component).

  Practical consequences:

  - The same callback group instance can be shared across multiple components to
    coordinate their executor scheduling (e.g. a single
    ``MutuallyExclusiveCallbackGroup`` shared between a subscriber and a timer).
  - Passing ``None`` selects the node's default group; this is the recommended choice
    when no specific concurrency policy is required.
  - The borrow contract holds across the whole lifecycle: configure / activate /
    deactivate / cleanup all see the same reference. ``cleanup`` releases the ROS
    publisher or subscription that referenced the group; it never touches the group
    itself.

  .. code-block:: python

      # Application owns the callback group; components borrow it.
      cb_group = MutuallyExclusiveCallbackGroup()
      sensor_sub = LifecycleSubscriberComponent(
          name="sensor",
          topic_name="/sensor",
          msg_type=Float64,
          callback_group=cb_group,
      )
      command_pub = LifecyclePublisherComponent(
          name="command",
          topic_name="/command",
          msg_type=Float64,
          callback_group=cb_group,
      )

  Invariant upheld: **cleanup** — components release only what they allocated; borrowed
  handles outlive the component instance.

Anti-Patterns
-------------

**Allocating ROS resources in ``__init__``**

  Creating publishers or subscriptions in the constructor bypasses the lifecycle
  contract entirely. The resource exists before configure, persists through cleanup,
  and cannot be released by the framework.

  .. code-block:: python

      # WRONG: resource created outside configure
      class BadComponent(LifecycleComponent):
          def __init__(self) -> None:
              super().__init__("bad")
              self._pub = self.node.create_publisher(String, "/topic", 10)  # node not attached yet

  Invariant violated: **configure** (allocate in configure), **cleanup** (release what configure
  allocated).

**Treating deactivate as cleanup**

  ``_on_deactivate`` must only stop runtime behavior. It must not destroy publishers,
  cancel subscriptions, or release memory. Releasing resources in deactivate means they are
  gone before cleanup, so a re-activation cycle (deactivate → activate → deactivate) will
  operate on destroyed resources.

  .. code-block:: python

      # WRONG: resource released in deactivate instead of cleanup
      def _on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
          self.node.destroy_publisher(self._pub)  # too early — cleanup's job
          self._pub = None
          return TransitionCallbackReturn.SUCCESS

  Invariant violated: **deactivate** (do not release resources here), **cleanup** (cleanup
  must release what configure allocated).

**Introducing a secondary internal state machine**

  Adding a component-level state variable that shadows or diverges from ``_is_active`` creates
  a second lifecycle model. This is the core anti-pattern lifecore_ros2 exists to prevent.
  The framework's ``_is_active`` flag is the only lifecycle-adjacent state a component should
  track. Additional "ready", "running", or "initialized" flags that are not driven by the
  lifecycle transitions are symptoms of this pattern.

  .. code-block:: python

      # WRONG: hidden secondary state
      class HiddenStateMachineComponent(LifecycleComponent):
          def __init__(self) -> None:
              super().__init__("bad")
              self._is_ready = False      # diverges from lifecycle state
              self._is_running = False    # another shadow flag

  Invariant violated: **No parallel lifecycle**.

**Putting heavy business logic inside lifecycle transition hooks**

  Lifecycle transition hooks run synchronously in the ROS 2 executor. Long-running
  initialization (network calls, file I/O, expensive computation) inside ``_on_configure``
  or ``_on_activate`` blocks the entire executor spin loop, making the node unresponsive to
  all callbacks during that period.

  Move expensive work to a background thread or service call initiated from within the hook,
  and signal completion asynchronously if needed.

  Invariant upheld: **configure**, **activate** — hooks must return promptly.

**Calling ``_release_resources`` manually inside ``_on_cleanup``**

  The framework calls ``_release_resources`` automatically after ``_on_cleanup`` returns,
  regardless of the hook's return value (Rule D). Calling it inside the hook causes a
  double-release, which may destroy already-destroyed handles.

  .. code-block:: python

      # WRONG: double release
      def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
          self._release_resources()   # framework will call this again automatically
          return TransitionCallbackReturn.SUCCESS

  Invariant violated: **cleanup** (``_release_resources`` is called automatically).

.. _patterns:on_message-exceptions:

**Letting exceptions propagate from ``on_message``**

  Exceptions raised inside ``on_message`` are caught by the framework's
  ``_on_message_wrapper`` and logged at ``ERROR`` level, but the message is silently
  dropped and processing continues. Raising is therefore not a reliable error-signaling
  channel — the node stays active, the error is logged, and the next message arrives
  normally. Do not rely on raising to stop the component or trigger a state change.

  If an error inside ``on_message`` should stop the component, use a flag and gate
  future messages explicitly, or arrange for the node to transition out of the active
  state through another mechanism.

  .. code-block:: python

      # WRONG: relying on raise to propagate the error
      def on_message(self, msg: Float64) -> None:
          if msg.data < 0:
              raise ValueError(f"unexpected negative value: {msg.data}")
          self._process(msg)

      # CORRECT: handle the error locally and decide whether to continue
      def on_message(self, msg: Float64) -> None:
          if msg.data < 0:
              self.node.get_logger().warning(f"[{self.name}] dropping negative value: {msg.data}")
              return
          self._process(msg)

  Rule reference: **Rule C** in :doc:`architecture` (inbound exceptions are logged and
  dropped; they never propagate to the executor).

**Destroying a borrowed ``callback_group`` from inside a component**

  The ``callback_group`` passed to a component is borrowed (see
  :ref:`patterns:borrow-only-contract`). Destroying it, reassigning it, or treating it as
  component-owned state breaks the contract: other components or node-level callbacks may
  still hold the same reference, and the application has no way to know the group has
  been invalidated.

  .. code-block:: python

      # WRONG: a component must not invalidate a borrowed handle
      def _release_resources(self) -> None:
          self._callback_group = None  # the application still owns this reference
          super()._release_resources()

  Invariant violated: **borrow-only contract** — the component never owns the lifetime of
  injected handles.
