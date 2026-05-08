Recommended Patterns and Anti-Patterns
=======================================

This page documents concrete patterns and anti-patterns for extending lifecore_ros2.
Each entry references the lifecycle invariant it upholds or violates (defined in :doc:`architecture`).

Recommended Patterns
--------------------

**Allocate resources during configure, not in the constructor**

  Allocate resources inside ``_on_configure``, not in ``__init__``.
  This keeps the component's constructor free of runtime dependencies and aligns with the
  **configure** invariant: resources exist if and only if a successful configure has run.

  For standard ROS resources, prefer the dedicated library components over raw
  ``create_*`` calls: ``LifecyclePublisherComponent``, ``LifecycleSubscriberComponent``,
  ``LifecycleTimerComponent``, ``LifecycleServiceServerComponent``, and
  ``LifecycleServiceClientComponent`` each encapsulate the configure / cleanup plumbing
  automatically.  Reserve the ``_on_configure`` override for resources without a library
  equivalent — for example, a hardware handle or a custom sensor connection.

  .. code-block:: python

      class SensorPublisher(LifecyclePublisherComponent[BatteryState]):
          def _on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
              result = super()._on_configure(state)  # creates the ROS publisher
              if result != TransitionCallbackReturn.SUCCESS:
                  return result
              # Acquire a custom resource not covered by a library component.
              self._sensor = open_sensor_connection(self._port)
              return TransitionCallbackReturn.SUCCESS

          def _release_resources(self) -> None:
              if self._sensor is not None:
                  self._sensor.close()
                  self._sensor = None
              super()._release_resources()  # destroys the ROS publisher

  Invariant upheld: **configure** (allocate in configure) and **cleanup** (release in
  ``_release_resources``, called automatically).

  .. seealso::

     :doc:`architecture` — Member Convention table for the ``super()._on_configure`` call
     contract on ``LifecyclePublisherComponent``.

**Prefer library activation-gating primitives**

  Any component-level operation or callback boundary that depends on activation must use the
  library gating primitives rather than an ad hoc state check.

  - Use ``@when_active`` when the inactive policy is one of the library defaults:
    raise for outbound operations, or silent drop for inbound middleware-driven callbacks.
  - Use ``self.require_active()`` when the component needs a custom inactive policy but should
    still rely on the same shared activation check.
  - Keep ``self.is_active`` for broader application branching when needed; do not use it as a
    replacement for library gating at component callback boundaries.

  .. code-block:: python

      def _on_request_wrapper(self, request, response):
          try:
              self.require_active()
          except RuntimeError:
              response.success = False
              response.message = "component inactive"
              return response
          return self.on_service_request(request, response)

  ``LifecycleTimerComponent.on_tick()`` and ``LifecycleSubscriberComponent.on_message()`` are
  already invoked behind library-owned wrappers, so subclasses do not need to re-check the
  activation state inside those extension points.

  Invariant upheld: **Activation gating**.

**Prefer the generic-only form for concrete topic and service components**

  When a concrete component class already parameterizes
  ``LifecyclePublisherComponent[MsgT]``,
  ``LifecycleSubscriberComponent[MsgT]``,
  ``LifecycleServiceServerComponent[SrvT]``, or
  ``LifecycleServiceClientComponent[SrvT]``, omit the corresponding
  ``msg_type=...`` / ``srv_type=...`` keyword in the constructor call. The
  library infers the ROS interface type from the generic argument at
  ``__init__`` time, through the same transverse resolver for both topic and
  service components.

  .. code-block:: python

    class EchoSub(LifecycleSubscriberComponent[String]):
      def __init__(self) -> None:
        super().__init__(
          name="echo",
          topic_name="/chatter",
        )

      def on_message(self, msg: String) -> None:
        self.node.get_logger().info(msg.data)

  Keep the explicit ``msg_type=...`` / ``srv_type=...`` form only when the subclass is not
  parameterized or when the type is supplied dynamically. If both the generic
  argument and the explicit keyword are provided, they must agree or ``__init__`` raises
  ``TypeError``.

  Invariant upheld: **configure** boundary correctness starts at construction time;
  no component reaches lifecycle hooks with an unresolved interface type.

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
    deactivate / cleanup / shutdown / error all see the same reference.
    ``cleanup``, ``shutdown``, and ``error`` release the ROS publisher or
    subscription that referenced the group; they never touch the group itself.

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

  Invariant upheld: **cleanup / shutdown / error** — components release only what they
  allocated; borrowed handles outlive the component instance.

**Use ``get_or_create_callback_group`` to let the node own groups**

  When a component needs a dedicated callback group but the application prefers to
  keep group lifetime on the node rather than manage it separately,
  ``LifecycleComponentNode.get_or_create_callback_group`` is the idiomatic alternative
  to manual group construction. The method is keyed by component name and is idempotent:
  multiple calls with the same name and compatible type return the same instance.

  .. code-block:: python

      class CameraNode(LifecycleComponentNode):
          def __init__(self) -> None:
              super().__init__("camera")
              # Node owns the group; component borrows it via the helper.
              cb_group = self.get_or_create_callback_group("image_sub")
              self.add_component(
                  LifecycleSubscriberComponent(
                      name="image_sub",
                      topic_name="/image_raw",
                      msg_type=Image,
                      callback_group=cb_group,
                  )
              )

  Passing ``None`` as ``group_type`` (the default) creates a
  ``MutuallyExclusiveCallbackGroup``. Pass ``ReentrantCallbackGroup`` explicitly when
  intra-component parallelism is intentional. Requesting a different type for an already
  registered name raises ``TypeError``.

  The borrow contract still applies: the component stores the reference and forwards it
  to ROS resource creation; it never creates, reassigns, or destroys the group.

  Invariant upheld: **borrow-only contract** — groups owned by the node outlive their
  components and are not destroyed during cleanup or shutdown.

Anti-Patterns
-------------

**Allocating ROS resources in ``__init__``**

  Creating publishers or subscriptions in the constructor bypasses the lifecycle
  contract entirely. The resource exists before configure, persists through cleanup,
  and cannot be released by the library.

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
  The library's ``_is_active`` flag is the only lifecycle-adjacent state a component should
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

  The library calls ``_release_resources`` automatically after ``_on_cleanup`` returns,
  regardless of the hook's return value (Rule D). Calling it inside the hook causes a
  double-release, which may destroy already-destroyed handles.

  .. code-block:: python

      # WRONG: double release
      def _on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
          self._release_resources()   # library will call this again automatically
          return TransitionCallbackReturn.SUCCESS

  Invariant violated: **cleanup** (``_release_resources`` is called automatically).

.. _patterns:on_message-exceptions:

**Letting exceptions propagate from ``on_message``**

  Exceptions raised inside ``on_message`` are caught by the library's
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
