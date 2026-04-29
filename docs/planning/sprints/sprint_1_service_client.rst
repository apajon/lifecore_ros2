Sprint 1 — Service server and Service client components
========================================================

.. note:: **Status: DELIVERED** — All implementation, tests, examples, and
   quality gates completed. See *Advancements* section below for a full
   delivery log.

**Objectif.** Complete ROS 2 primitive support: introduce a shared abstract
``ServiceComponent`` base (mirroring ``TopicComponent``) and add concrete
``LifecycleServiceServerComponent`` and ``LifecycleServiceClientComponent``
with full lifecycle gating.

**Livrable.** "lifecore supports all ROS 2 communication primitives with
consistent activation semantics, behind a uniform two-layer
(base + concrete) component design."

.. note::

   **Naming.** We do **not** use ``ServiceComponent``/``ClientComponent`` as
   user-facing concrete classes. The pair is asymmetric and ambiguous
   (``ClientComponent`` reads as "a generic client", not "a ROS service
   client"). Instead, we follow the existing topic pattern:

   - Abstract base: ``ServiceComponent[SrvT]`` — analogous to
     ``TopicComponent[MsgT]``. Holds shared state (service name, srv type,
     QoS, callback group). No ROS object, no lifecycle hooks.
   - Concrete server: ``LifecycleServiceServerComponent[SrvT]`` —
     analogous to ``LifecyclePublisherComponent``.
   - Concrete client: ``LifecycleServiceClientComponent[SrvT]`` —
     analogous to ``LifecycleSubscriberComponent``.

   This keeps naming symmetric, intent-explicit, and aligned with the
   framework convention ``Lifecycle<Capability>Component`` for concrete
   managed entities (see ``.github/instructions/naming-conventions``).

---

Content
-------

ServiceComponent (abstract base)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Abstract base class, mirrors ``TopicComponent``.
- Generic: ``ServiceComponent[SrvT]``.
- Owns:

  - service name
  - ``srv_type`` (resolved via ``_resolve_iface_type`` with
    ``interface_kind="srv_type"``)
  - QoS profile (defaulting to ROS 2 service QoS)
  - borrowed callback group (lifetime owned by caller)

- Does **not** own:

  - the ROS service or client object — those belong to concrete subclasses
  - any ``_on_*`` lifecycle hook implementation

- Not intended to be subclassed directly outside the framework. Application
  code subclasses ``LifecycleServiceServerComponent`` or
  ``LifecycleServiceClientComponent``.

LifecycleServiceServerComponent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Concrete subclass of ``ServiceComponent``.
- Generic: ``LifecycleServiceServerComponent[SrvT]``.
- Lifecycle:

  - ``_on_configure``: create ROS service, register internal dispatcher
    that routes requests to ``on_service_request`` only when active.
  - ``_on_activate``: enable request handling.
  - ``_on_deactivate``: reject new requests with the documented
    inactive-response policy (see Risks §1); in-flight handlers run to
    completion.
  - ``_on_cleanup``: destroy the service, release the reference.
  - ``_on_shutdown``: ensure cleanup is performed if not already done.
  - ``_on_error``: best-effort cleanup, surface diagnostic.

- Activation gating: requests received while inactive log a warning and
  return the default-constructed ``Response`` (with a diagnostic field
  populated if the message defines one). See Risks §1.
- Handler hook: ``on_service_request(request: RequestT) -> ResponseT``
  (abstract).

LifecycleServiceClientComponent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Concrete subclass of ``ServiceComponent``.
- Generic: ``LifecycleServiceClientComponent[SrvT]``.
- Lifecycle:

  - ``_on_configure``: create ROS client (no calls issued yet).
  - ``_on_activate``: enable ``call()`` and ``call_async()``.
  - ``_on_deactivate``: new ``call()`` raises ``ComponentNotActiveError``;
    previously-issued futures are **not** cancelled (documented).
  - ``_on_cleanup``: destroy the client.
  - ``_on_shutdown``: ensure cleanup.
  - ``_on_error``: best-effort cleanup.

- Activation gating: ``call()`` and ``call_async()`` raise
  ``ComponentNotActiveError`` when not active.
- Call methods:

  - ``call(request: RequestT, timeout_service: float | None = None, timeout_call: float | None = None) -> ResponseT``
  - ``call_async(request: RequestT, timeout_service: float | None = None) -> Future``

    - ``timeout_service``: if set, calls ``wait_for_service(timeout_sec=...)``
      before issuing the call; raises ``TimeoutError`` if unavailable.
    - ``timeout_call``: forwarded as ``timeout_sec`` to the underlying
      ``rclpy`` client (``call()`` only).

- ``wait_for_service(timeout)`` is available **only when ACTIVE**; calling
  it from any other state raises ``ComponentNotActiveError``.

TopicComponent behaviors
^^^^^^^^^^^^^^^^^^^^^^^^

Verify that existing ``LifecyclePublisherComponent`` and
``LifecycleSubscriberComponent`` apply the same activation gating rules.
No breaking changes; this sprint verifies consistency between the four
primitives (publisher, subscriber, service-server, service-client).

---

Tests to write
--------------

ServiceComponent (base) unit tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [x] ``srv_type`` inference from generic parameter
  (``LifecycleServiceServerComponent[Empty]`` → ``Empty`` resolved).
- [x] Explicit ``srv_type`` argument honored and validated against the
  generic parameter when both are supplied.
- [x] ``TypeError`` when ``srv_type`` cannot be resolved.

LifecycleServiceServerComponent unit tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [x] Service created in ``_on_configure``, destroyed in ``_on_cleanup``.
- [x] Request rejected (inactive response) when component is INACTIVE.
- [x] Request handled by ``on_service_request`` when component is ACTIVE.
- [x] Lifecycle: ``configure`` → ``activate`` → ``deactivate`` → ``cleanup``.
- [x] Double activate is idempotent (per adoption hardening §5 rule).
- [x] Exception raised in ``on_service_request`` does not leave the
  component in an inconsistent state; the service remains bound.

LifecycleServiceClientComponent unit tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [x] Client created in ``_on_configure``, destroyed in ``_on_cleanup``.
- [x] ``call()`` raises ``ComponentNotActiveError`` when not active.
- [x] ``call()`` succeeds when active.
- [x] ``call_async()`` raises (or returns failed future) when not active.
- [x] Lifecycle: ``configure`` → ``activate`` → ``call`` → ``deactivate``
  → calls blocked.
- [x] ``call(timeout_call=...)`` respects the timeout (forwarded to rclpy).
- [x] ``call(timeout_service=...)`` waits for service; raises
  ``TimeoutError`` when unavailable within the window.
- [x] ``call_async(timeout_service=...)`` raises ``TimeoutError`` when
  service unavailable.
- [x] In-flight futures are not cancelled on deactivate (documented
  contract).

Integration tests
^^^^^^^^^^^^^^^^^

- [x] ``LifecycleServiceServerComponent`` +
  ``LifecycleServiceClientComponent`` co-located in the same node perform
  a full request/response cycle.
- [x] Inactive server → client receives inactive-response.
- [x] Client deactivated → ``call()`` raises.
- [x] Activation-gating consistency test across all four primitives
  (publisher, subscriber, service-server, service-client).

---

Risks and mitigation
--------------------

**Risk 1: Server callback execution and inactive-response shape**

- **Problem**: A request arriving while INACTIVE must be handled
  deterministically. Returning the default-constructed ``Response``
  silently looks like success.
- **Decision**: the framework applies a single inactive-response policy:

  - Log a warning identifying the component, service name, and current
    lifecycle state.
  - Return the default-constructed ``Response``. If the response message
    defines a diagnostic-style field (e.g. ``success``, ``message``), the
    framework populates it to flag the inactive state; otherwise the
    default response is returned as-is.
  - In-flight handlers triggered before deactivation run to completion;
    deactivation does not cancel them. Documented in the docstring.

**Risk 2: Async client calls leak state**

- **Problem**: ``call_async()`` returns a future; if the component
  deactivates, the future may dangle.
- **Mitigation**:

  - This sprint either ships ``call_async()`` with the explicit contract
    "futures are not cancelled on deactivate; the application owns them",
    or defers it entirely. Default position: ship with the explicit
    contract; revisit in Sprint 2.

**Risk 3: Client timeout vs activation state**

- **Problem**: A long service call straddles a deactivation transition.
- **Mitigation**:

  - The client-side timeout passed to ``call()`` is independent of
    component state.
  - Already-issued calls are not cancelled by ``_on_deactivate``.
  - New calls issued after deactivate raise ``ComponentNotActiveError``.

**Risk 4: Inconsistency with publisher/subscriber gating**

- **Problem**: Publisher gates on publication; subscriber gates on
  message handling. Service-server and service-client must match.
- **Mitigation**:

  - Service-server: gate incoming requests (inactive-response when
    inactive).
  - Service-client: gate outgoing calls (raise when inactive).
  - Add a regression test that asserts the four primitives behave
    consistently.

**Risk 5: Naming drift**

- **Problem**: Earlier drafts used ``ClientComponent``, which is ambiguous
  (reads as "any client") and asymmetric with ``ServiceComponent``
  (which here doubles as both abstract base and "server" in casual
  reading).
- **Mitigation**:

  - Reserve ``ServiceComponent`` for the abstract base (mirrors
    ``TopicComponent``).
  - Use ``LifecycleServiceServerComponent`` and
    ``LifecycleServiceClientComponent`` for the concrete classes.
  - Naming is enforced by ``.github/instructions/naming-conventions``.

---

Dependencies
------------

- Requires: ``LifecycleComponent`` base (shipped).
- Requires: ``TopicComponent`` two-layer pattern (shipped) — used as the
  blueprint for ``ServiceComponent``.
- Requires: ``_resolve_iface_type`` (shipped) — used with
  ``interface_kind="srv_type"``.
- Requires: ``when_active`` decorator (shipped) — used for callback
  gating.
- Requires: Error handling work (Sprint 2) — retroactively hardens error
  semantics.
- Requires: Testing fixtures (Sprint 3) — shared utilities for testing
  this sprint.

---

Scope boundaries
----------------

**In-scope for this sprint:**

- Abstract ``ServiceComponent[SrvT]`` base (mirrors ``TopicComponent``).
- Concrete ``LifecycleServiceServerComponent[SrvT]``.
- Concrete ``LifecycleServiceClientComponent[SrvT]``.
- Single request/response semantics.
- Lifecycle integration and activation gating.
- Inactive-response policy (server) and ``ComponentNotActiveError``
  (client).

**Out-of-scope:**

- Async request handlers on the server (deferred).
- Service pooling or multiplexing.
- Framework-level timeout policies (timeout remains a parameter to
  ``call()``).
- Action components (different semantics, separate sprint).
- Parameter components (separate sprint).
- Cancelling in-flight ``call_async()`` futures on deactivate.

---

Success signal
--------------

- [x] ``from lifecore_ros2 import ServiceComponent,
  LifecycleServiceServerComponent, LifecycleServiceClientComponent``
  works.
- [x] All tests pass (unit + integration): 42 service-related tests,
  248 total, all green.
- [x] Activation gating is enforced and tested across all four
  primitives.
- [x] Ruff, Pyright, Pytest all green
  (``uv run ruff check .`` / ``uv run pyright`` / ``uv run pytest``).
- [x] Examples: ``examples/minimal_service_server.py`` and
  ``examples/minimal_service_client.py``.
- [x] Design note: none required (primitives only).
- [x] Docstrings complete (Google style, Napoleon-ready).

---

Example hooks
-------------

Server minimal implementation::

   class MinimalServiceServer(LifecycleServiceServerComponent[std_srvs.srv.Empty]):
       def on_service_request(
           self,
           request: std_srvs.srv.Empty.Request,
       ) -> std_srvs.srv.Empty.Response:
           # Called by the framework only when the component is ACTIVE.
           return std_srvs.srv.Empty.Response()

Client minimal implementation::

   class MinimalServiceClient(LifecycleServiceClientComponent[std_srvs.srv.Empty]):
       def trigger(self) -> std_srvs.srv.Empty.Response:
           # Raises ComponentNotActiveError if not ACTIVE.
           return self.call(std_srvs.srv.Empty.Request(), timeout_service=1.0)

---

Advancements
------------

All deliverables completed in one session on 2026-04-28.

Implementation
^^^^^^^^^^^^^^

- ``src/lifecore_ros2/components/service_component.py`` — ``ServiceComponent[SrvT]``
  abstract base; mirrors ``TopicComponent``; no ROS objects, no lifecycle hooks.
- ``src/lifecore_ros2/components/lifecycle_service_server_component.py`` —
  ``LifecycleServiceServerComponent[SrvT]``; creates service in
  ``_on_configure``; inactive requests annotate ``success``/``message``
  fields if present, return default response otherwise.
- ``src/lifecore_ros2/components/lifecycle_service_client_component.py`` —
  ``LifecycleServiceClientComponent[SrvT]``; ``call()`` and ``call_async()``
  gated by ``@when_active``; ``timeout_service`` and ``timeout_call``
  parameters added.
- ``src/lifecore_ros2/components/__init__.py`` and
  ``src/lifecore_ros2/__init__.py`` — all three names exported in ``__all__``.

Examples
^^^^^^^^

- ``examples/minimal_service_server.py`` — ``TriggerServer`` node;
  demonstrates configure/activate via ``ros2 lifecycle set``.
- ``examples/minimal_service_client.py`` — instantiates
  ``LifecycleServiceClientComponent[Trigger]`` directly; calls with
  ``timeout_service=2.0``.

Tests
^^^^^

Test suite split into focused files backed by shared stubs:

- ``tests/_service_stubs.py`` — ``_TriggerServer``, ``_TriggerClient``,
  ``_EmptyServer``, ``_CrashingServer``, ``_GatedPublisher``,
  ``_GatedSubscriber``, ``DUMMY_STATE``, ``node`` and
  ``mock_svc_factories`` fixtures (loaded via ``pytest_plugins``).
- ``tests/test_service_server.py`` — 12 tests: server lifecycle
  (Sections B) and activation gating (Section C).
- ``tests/test_service_client.py`` — 17 tests: client lifecycle
  (Section D), activation gating (Section E), and timeout parameters
  (Section E2).
- ``tests/test_service_components.py`` — 13 tests: ``srv_type``
  inference (Section A), integration (Section F), and four-primitive
  gating consistency (Section G).

Similarly, topic-component tests were split in the same session:

- ``tests/_topic_stubs.py``, ``tests/test_publisher_component.py``,
  ``tests/test_subscriber_component.py``, ``tests/test_timer_component.py``
  (``tests/test_components.py`` retains transversal QoS/callback-group
  tests only).

Quality gates
^^^^^^^^^^^^^

- Ruff lint: ✓ 0 errors
- Ruff format: ✓ all files formatted
- Pyright: ✓ 0 errors
- Pytest: ✓ 248/248 passed
