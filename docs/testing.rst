Testing Utilities
=================

``lifecore_ros2.testing`` provides reusable helpers for tests that need to
exercise lifecycle behavior without re-declaring the same components and states
in every file.

The package is intentionally small: it uses the framework's public lifecycle
APIs, concrete ROS 2 interface types, and pytest-compatible fixtures. It does
not add a second lifecycle model or a general mocking framework.

What It Provides
----------------

Use the root package for the public testing surface:

.. code-block:: python

   from lifecore_ros2.testing import (
       DUMMY_STATE,
       FakeComponent,
       FakePublisherComponent,
       activate_component,
       assert_transition_order,
       lifecycle_node_fixture,
   )

The package contains four groups of helpers.

**Lifecycle fakes**
  ``FakeComponent`` records lifecycle hook calls, stores the state passed to
  each hook, and can return a controlled failure or raise from a selected hook.
  ``FailingComponent`` is the shortcut for exception-path tests: by default it
  raises from the selected hook and lets the framework hook guard map that to
  ``TransitionCallbackReturn.ERROR``.

**Topic, timer, service, and client fakes**
  ``FakePublisherComponent``, ``FakeSubscriberComponent``, ``FakeTimerComponent``,
  ``FakeServiceComponent``, and ``FakeClientComponent`` use concrete ROS 2
  types: ``std_msgs.msg.String`` and ``std_srvs.srv.Trigger``. They preserve the
  same activation gating expectations as the framework components while avoiding
  repeated ROS resource boilerplate in tests.

**Fixtures and assertions**
  ``lifecycle_node_fixture`` creates and destroys a ``LifecycleComponentNode``.
  ``node_with_components`` returns a ``NodeWithComponents`` value whose ``node``
  field is preloaded with one standard fake of each supported kind.
  Assertions cover component contract state, hook order, and activation gating.

**Helpers for common flows**
  ``activate_component`` runs configure then activate for one registered
  component. ``deactivate_component`` runs deactivate then cleanup. Log helpers
  capture Python logger output, and concurrency helpers support simple threaded
  transition probes.

Minimal Lifecycle Test
----------------------

To use the packaged fixtures in a pytest suite, register the fixture module in
the suite's ``conftest.py``:

.. code-block:: python

    pytest_plugins = ["lifecore_ros2.testing.fixtures"]

Then use the fixtures directly in tests.

.. code-block:: python

   from lifecore_ros2.testing import FakeComponent, activate_component, assert_transition_order


   def test_component_activation(lifecycle_node_fixture):
       component = FakeComponent("camera")
       lifecycle_node_fixture.add_component(component)

       activate_component(lifecycle_node_fixture, "camera")

       assert_transition_order(component, ["configure", "activate"])

Testing Activation Gating
-------------------------

The built-in fakes are useful when a test only needs to verify the framework's
activation boundary, not the details of a real ROS transport handle.

.. code-block:: python

   from lifecore_ros2.testing import FakePublisherComponent, assert_activation_gated


   def test_publisher_is_activation_gated():
       assert_activation_gated(FakePublisherComponent())

Failure Paths
-------------

Use ``fail_at_hook`` when the test needs a hook to return
``TransitionCallbackReturn.FAILURE``. Use ``FailingComponent`` when the test
needs the framework hook guard to convert an exception into
``TransitionCallbackReturn.ERROR``.

.. code-block:: python

   from rclpy.lifecycle import TransitionCallbackReturn

   from lifecore_ros2.testing import DUMMY_STATE, FakeComponent, FailingComponent


   def test_configure_failure_return():
       component = FakeComponent(fail_at_hook="configure")

       assert component.on_configure(DUMMY_STATE) == TransitionCallbackReturn.FAILURE


   def test_configure_exception_is_guarded():
       component = FailingComponent(fail_at_hook="configure", exception=RuntimeError("boom"))

       assert component.on_configure(DUMMY_STATE) == TransitionCallbackReturn.ERROR

When To Keep Local Test Doubles
-------------------------------

Use these utilities for generic lifecycle behavior: hook order, activation
state, failure propagation, registration checks, and common pub/sub/service
gating assertions.

Keep local test doubles when a test verifies a specialized contract that the
standard fakes deliberately bypass, such as calls to ``create_publisher``,
``destroy_publisher``, callback group forwarding, QoS values, or custom resource
rollback behavior.

Reference
---------

The generated API reference for each testing submodule is available in
:doc:`api/testing`.
