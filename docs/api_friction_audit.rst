:orphan:

API Friction Audit
==================

This page records the ergonomics audit required by
the Adoption & Hardening Roadmap (``docs/planning/adoption_hardening.rst`` §2). The goal is to count the steps a developer
must take to produce a useful component, identify any steps that exist only for
library bookkeeping, and designate a canonical "shortest path" example.

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
   with named arguments ``name`` and ``topic_name``; ``qos_profile`` remains
   optional (default: ``10``). ``msg_type`` is optional when the subclass is
   parameterized with a concrete generic argument.
3. Call ``self.publish(msg)`` from any callback or override.

**Total: 3 steps.**  No override is mandatory.

``LifecyclePublisherComponent`` + ``LifecycleTimerComponent`` (timer-driven)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Additional steps beyond the publish-on-demand case:

4. Import ``LifecycleTimerComponent``.
5. Subclass ``LifecycleTimerComponent``; pass the publisher instance at construction.
6. Implement ``on_tick()``: call the publisher's emit method or ``publish(msg)``.

**Total: 6 steps.**  No ``_on_activate``, ``_on_deactivate``, ``create_timer``, or
``destroy_timer`` call required.  Both components are gated by the library
automatically.  See ``examples/minimal_publisher.py`` for the canonical form.

.. note::

   Before ``LifecycleTimerComponent`` was used as a sibling component, timer-driven
   publication required overriding ``_on_activate`` and ``_on_deactivate`` with manual
   ``create_timer`` / ``destroy_timer`` calls — 7 steps total.  That path remains valid
  for resources without a library equivalent but should not be used for timers.

Minimal ``LifecycleSubscriberComponent``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Import ``LifecycleSubscriberComponent`` and the ROS message type.
2. Subclass ``LifecycleSubscriberComponent[MsgT]``; implement ``__init__``
   with named arguments ``name`` and ``topic_name``; ``qos_profile`` remains
   optional (default: ``10``). ``msg_type`` is optional when the subclass is
   parameterized with a concrete generic argument.
3. Implement ``on_message(self, msg: MsgT) -> None``.

**Total: 3 steps.**  ``on_message`` is the only mandatory user override.

Composing two components under a ``LifecycleComponentNode``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After both components are defined:

1. Subclass ``LifecycleComponentNode``.
2. In ``__init__``: call ``super().__init__(node_name)``.
3. Call ``self.add_component(comp_a)`` and ``self.add_component(comp_b)``.

**Total: 3 steps.**  No library-only overhead.

---

Friction candidates
-------------------

One potential friction item was identified during the audit.

``msg_type`` parameter is redundant with the generic argument
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before PR `#4 <https://github.com/apajon/lifecore_ros2/pull/4>`_, every
``TopicComponent`` subclass required the message type to be stated twice: once
as the generic parameter ``[String]`` and once as the constructor argument
``msg_type=String``.

.. code-block:: python

    class EchoSub(LifecycleSubscriberComponent[String]):  # String stated here …
        def __init__(self) -> None:
            super().__init__(
                name="echo",
                topic_name="/chatter",
                msg_type=String,           # … and again here
                qos_profile=10,
            )

The duplication came from Python's runtime type erasure: the library had to
recover the concrete generic argument at ``__init__`` time before handing the
resolved type to ``rclpy``.

**Initial decision (2026-04-24):** the current duplication is a Python
limitation, not a library design choice.  Making ``msg_type`` optional
(via ``__orig_bases__`` introspection) is feasible but was deferred to a
dedicated investigation.  See issue
`#1 <https://github.com/apajon/lifecore_ros2/issues/1>`_.

Investigation outcome (2026-04-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Verdict: IMPLEMENT** as a transverse utility usable by
``ServiceComponent`` (shipped) and future ``ActionComponent`` as well as
today's topic components.

Evidence: the POC ``scripts/investigate_iface_type_inference.py`` exercised
nine scenarios on CPython 3.12 against the exact PEP 695 generic shape used
by ``TopicComponent[MsgT]``.  All nine matched the oracle:

.. list-table::
   :header-rows: 1
   :widths: 6 60 34

   * - #
     - Scenario
     - Oracle
   * - 1
     - Direct subclass parameterized as ``Sub(Base[MsgT])``
     - infer ``MsgT``
   * - 2
     - Indirect subclass without re-parameterization (resolution via MRO)
     - infer ``MsgT``
   * - 3
     - Multi-level concrete chain ``Leaf < Mid < Base[MsgT]``
     - infer ``MsgT``
   * - 4
     - Unparameterized subclass and no explicit argument
     - ``TypeError`` at ``__init__``
   * - 5
     - Ancestor forwards an unresolved ``TypeVar``
     - ``TypeError`` at ``__init__`` (no false positive)
   * - 6
     - Generic and explicit argument disagree
     - ``TypeError`` at ``__init__`` (no silent surprise)
   * - 7
     - Generic and explicit argument agree
     - resolved to that type
   * - 8
     - Explicit only, generic unparameterized (fallback)
     - resolved to the explicit type
   * - 9
     - ``__orig_bases__`` under ``from __future__ import annotations``
     - contains real type objects, not strings

Result on Python 3.12.3: ``failures: 0/9``.

Decisions locked
~~~~~~~~~~~~~~~~

These apply uniformly to ``msg_type``, ``srv_type``, and ``action_type``
across current and future components.

.. rubric:: ADR — R-IfaceTypeInference

**Decision.** Any component parameterized over a ROS interface type accepts
that type either via the generic parameter of the class
(``Component[InterfaceT]``) or via an explicit constructor argument.  The
two sources are reconciled by a single transverse utility.  When neither is
available, or when both are available and disagree, the library raises a
typed boundary exception at ``__init__`` time.

**Rationale.** Avoids the "stated twice" friction documented above without
adding magic: explicit argument remains supported, generic parameterization
becomes sufficient, and divergence is surfaced loudly instead of silently.

**Consequences.**

- A single resolver lives at ``src/lifecore_ros2/core/_iface_type.py`` —
  transverse, reused by ``ServiceComponent`` (shipped) and reusable by
  ``ActionComponent`` when introduced (see ``TODO.md §2``).  Placing it in
  ``core/`` rather than ``components/`` is deliberate: the rule is not
  topic-specific.
- Boundary failure is a typed exception
  ``_InterfaceTypeNotResolvedError(LifecoreError, TypeError)`` — internal
  (Rule A: typed boundary errors), prefixed with ``_``, and **not**
  re-exported from ``lifecore_ros2``.  Subclassing ``TypeError`` keeps
  user-facing tracebacks idiomatic.
- Conflict policy is **error**, never "explicit wins".  Silent disagreement
  is forbidden.
- Failure happens **at** ``__init__``.  No component can ever reach
  ``_on_configure`` with an unresolved interface type, which keeps the
  Rule A / Rule B split intact (boundary errors stay outside lifecycle
  hooks).
- Pedagogical examples under ``examples/`` keep ``msg_type=…`` explicit;
  the generic-only short form is documented in ``docs/patterns.rst`` only.

**Implementation landed.** The rule is enforced directly in
``TopicComponent.__init__`` through the transverse resolver in
``src/lifecore_ros2/core/_iface_type.py``.

Status
~~~~~~

- Investigation: closed.
- Implementation: shipped in PR
  `#4 <https://github.com/apajon/lifecore_ros2/pull/4>`_
  for issue `#1 <https://github.com/apajon/lifecore_ros2/issues/1>`_.
- Tracker: Adoption & Hardening §2 is closed and ``docs/patterns.rst``
  documents the generic-only form.

No other library-bookkeeping-only steps were found.  All remaining steps
either carry clear functional justification or belong to application logic
(timer management, message construction).

---

Canonical shortest-path example
--------------------------------

**Designated example:** ``examples/minimal_subscriber.py``

Rationale: the subscriber requires only a three-step setup (import, subclass +
``__init__``, ``on_message``) and imposes zero timer lifecycle overhead.  It
demonstrates activation gating — the primary differentiator of the library —
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
  application logic, not library overhead.
- Subscriber path (3 steps): minimal.  ``on_message`` is the sole mandatory
  override.
- Composition path (3 steps): straightforward.
- One friction item shipped: ``msg_type`` no longer needs to be duplicated when
  the component class is parameterized with a concrete generic argument.
- Canonical shortest path: ``examples/minimal_subscriber.py`` — 24 lines for
  component + node definition.
