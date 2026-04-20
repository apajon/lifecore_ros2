Examples
========

Overview
--------

The repository currently contains a small set of examples intended to validate the core architecture rather than provide a full application template.

Minimal Composed Node
---------------------

examples/minimal_node.py defines a small lifecycle-aware node based on LifecycleComponentNode.

It demonstrates:

- attaching a LifecycleComponent to a composed node
- relying on the native lifecycle callback flow
- keeping component lifecycle hooks explicit and minimal

Minimal Subscriber Component
----------------------------

examples/minimal_subscriber.py defines a LifecycleSubscriberComponent subclass attached to a managed node.

It demonstrates:

- declaring a topic-oriented component
- handling incoming messages through on_message
- using the lifecycle-aware component model instead of embedding subscriber logic directly into the node

Minimal Publisher Component
---------------------------

examples/minimal_publisher.py defines a LifecyclePublisherComponent subclass attached to a managed node.

It demonstrates:

- creating a periodic publisher on a topic using a timer
- gating publication with activation state
- releasing the timer and publisher during deactivate and cleanup

Telemetry Publisher
-------------------

examples/telemetry_publisher.py defines a ``LifecyclePublisherComponent`` subclass with all four
lifecycle hooks overridden.

It demonstrates:

- the split between configure-time resource acquisition and activate-time sampling behavior
- a timer created on activate and destroyed on deactivate (runtime resource vs ROS resource)
- that deactivate suspends behavior without releasing the sensor handle, while cleanup does
- how ``@when_active`` gating on ``publish()`` makes explicit activation guards unnecessary in ``_emit``

Composed Pipeline
-----------------

examples/composed_pipeline.py composes three sibling components inside one ``LifecycleComponentNode``:
a ``SineSource`` publisher, a ``MovingAverageRelay``, and a ``LoggingSink`` subscriber.  All three
transition together via the standard ROS 2 lifecycle.

It demonstrates what the minimal and telemetry examples cannot show individually:

- composition as the unit of value: no single component delivers the observable pipeline behavior;
  the value only appears when all three activate together
- ``MovingAverageRelay`` extends ``LifecycleComponent`` directly, owning both a raw ROS subscription
  and a raw ROS publisher; this makes explicit what the pre-built topic components do internally and
  shows that any pair of ROS resources belongs together in one component
- activation gating across a multi-hop pipeline: while inactive, no data flows even though both
  topics remain visible in ``ros2 topic list``
- buffer reset on deactivate: the relay clears its moving-average window so that reactivation
  always starts from a known empty state rather than from stale samples

Observability Format
--------------------

Every example module docstring contains an ``Expected output`` section (or ``Expected output per
transition`` for multi-component examples) that follows a consistent format.  Reading it before
running an example tells you exactly what to expect:

- ``[before configure]`` — baseline state before any lifecycle transition: which topics are absent,
  which node info is visible.
- ``[configure]`` — log lines emitted on configure plus the resulting ``ros2 topic list`` state and
  initial data-flow gate.
- ``[activate]`` / ``[while active]`` — log lines on activate and the periodic output while the node
  is running.  Silent transitions are stated explicitly as ``(no component log — by design)``.
- ``[deactivate]`` — what stops, what is retained (topics still visible; handles kept), and whether
  any drops are silent.
- ``[cleanup]`` — final log lines and which topics disappear from ``ros2 topic list``.
- ``[shutdown]`` — terminal teardown note.

The ``[before configure]`` and cleanup disappearance entries answer the four ``TODO 5.4``
sub-questions directly: what to observe in logs, what happens before activation, what happens after
deactivation, and what disappears after cleanup.

Reading Examples Safely
-----------------------

These examples should be read as architecture demonstrations, not as production-ready launch patterns.
When extending them, preserve the repository lifecycle rules:

- create ROS resources during configure
- gate runtime behavior with activation state
- release ROS resources during cleanup
