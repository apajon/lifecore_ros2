:orphan:

API Friction Audit
==================

This page records the ergonomics audit required by
``TODO_adoption_hardening.md §2``.  The goal is to count the steps a developer
must take to produce a useful component, identify any steps that exist only for
framework bookkeeping, and designate a canonical "shortest path" example.

Audit date: 2026-04-24.

---

Step counts
-----------

The steps below correspond to a blank file: nothing imported, no base classes
available.  Optional overrides are marked ``(optional)``.

Minimal ``LifecyclePublisherComponent`` (publish-on-demand)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Import ``LifecyclePublisherComponent`` and the ROS message type.
2. Subclass ``LifecyclePublisherComponent[MsgT]``; implement ``__init__``
   with four named arguments: ``name``, ``topic_name``, ``msg_type``,
   ``qos_profile`` (default: ``10``).
3. Call ``self.publish(msg)`` from any callback or override.

**Total: 3 steps.**  No override is mandatory.

Minimal ``LifecyclePublisherComponent`` (timer-driven publication)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Additional steps beyond the publish-on-demand case:

4. Declare ``self._timer: Timer | None = None`` in ``__init__``.
5. Override ``_on_activate``: call ``self.node.create_timer(...)``; store ref.
6. Override ``_on_deactivate``: cancel and destroy the timer.
7. Implement the timer callback; build the message and call ``self.publish(msg)``.

**Total: 7 steps.**  Steps 4–7 are application logic (timer lifecycle), not
framework bookkeeping.  No mandatory framework-only step was identified.

Minimal ``LifecycleSubscriberComponent``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Import ``LifecycleSubscriberComponent`` and the ROS message type.
2. Subclass ``LifecycleSubscriberComponent[MsgT]``; implement ``__init__``
   with four named arguments: ``name``, ``topic_name``, ``msg_type``,
   ``qos_profile`` (default: ``10``).
3. Implement ``on_message(self, msg: MsgT) -> None``.

**Total: 3 steps.**  ``on_message`` is the only mandatory user override.

Composing two components under a ``LifecycleComponentNode``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After both components are defined:

1. Subclass ``LifecycleComponentNode``.
2. In ``__init__``: call ``super().__init__(node_name)``.
3. Call ``self.add_component(comp_a)`` and ``self.add_component(comp_b)``.

**Total: 3 steps.**  No framework-only overhead.

---

Friction candidates
-------------------

One potential friction item was identified during the audit.

``msg_type`` parameter is redundant with the generic argument
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every ``TopicComponent`` subclass requires the message type to be stated
twice: once as the generic parameter ``[String]`` and once as the constructor
argument ``msg_type=String``.

.. code-block:: python

    class EchoSub(LifecycleSubscriberComponent[String]):  # String stated here …
        def __init__(self) -> None:
            super().__init__(
                name="echo",
                topic_name="/chatter",
                msg_type=String,           # … and again here
                qos_profile=10,
            )

The duplication is a consequence of Python's runtime type erasure: generic
parameters are not available via ``type(self)`` at ``__init__`` time, so
``msg_type`` must be supplied explicitly for ``rclpy`` to create the
publisher or subscription.

**Decision recorded here:** the current duplication is a Python limitation,
not a framework design choice.  Making ``msg_type`` optional (via
``__orig_bases__`` introspection) is feasible but fragile and out of scope
for the ``0.x`` series.  A GitHub issue has been opened to track the
investigation (see ``TODO_adoption_hardening.md``).

No other framework-bookkeeping-only steps were found.  All remaining steps
either carry clear functional justification or belong to application logic
(timer management, message construction).

---

Canonical shortest-path example
--------------------------------

**Designated example:** ``examples/minimal_subscriber.py``

Rationale: the subscriber requires only a three-step setup (import, subclass +
``__init__``, ``on_message``) and imposes zero timer lifecycle overhead.  It
demonstrates activation gating — the primary differentiator of the framework —
without incidental complexity.

**Regression snapshot (2026-04-24):**

.. list-table::
   :header-rows: 1
   :widths: 40 20

   * - Scope
     - Line count
   * - Total file (including module docstring)
     - 90
   * - Code only (lines 36–90, excluding module docstring)
     - 55
   * - Component + node definition (lines 43–66)
     - 24

Any PR that grows the ``Component + node definition`` scope beyond **24 lines**
without explicit justification should be treated as a regression in API
ergonomics.

The example fits on one screen and does not require the reader to know any
``_on_*`` hook beyond ``on_message``.

---

Conclusions
-----------

- Publisher path (3 steps / 7 with timer): clean.  Timer management is
  application logic, not framework overhead.
- Subscriber path (3 steps): minimal.  ``on_message`` is the sole mandatory
  override.
- Composition path (3 steps): straightforward.
- One friction item noted: ``msg_type`` duplication (Python limitation;
  tracked as issue, deferred).
- Canonical shortest path: ``examples/minimal_subscriber.py`` — 24 lines for
  component + node definition.
