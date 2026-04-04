Examples
========

Overview
--------

The repository currently contains a small set of examples intended to validate the core architecture rather than provide a full application template.

Minimal Composed Node
---------------------

examples/minimal_node.py defines a small lifecycle-aware node based on ComposedLifecycleNode.

It demonstrates:

- attaching a LifecycleComponent to a composed node
- relying on the native lifecycle callback flow
- keeping component lifecycle hooks explicit and minimal

Minimal Subscriber Component
----------------------------

examples/minimal_subscriber.py defines a SubscriberComponent subclass attached to a composed node.

It demonstrates:

- declaring a topic-oriented component
- handling incoming messages through on_message
- using the lifecycle-aware component model instead of embedding subscriber logic directly into the node

Reading Examples Safely
-----------------------

These examples should be read as architecture demonstrations, not as production-ready launch patterns.
When extending them, preserve the repository lifecycle rules:

- create ROS resources during configure
- gate runtime behavior with activation state
- release ROS resources during cleanup
