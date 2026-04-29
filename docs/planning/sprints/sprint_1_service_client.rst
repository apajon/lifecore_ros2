Sprint 1 — Service and Client components
===========================================

**Objectif.** Complete ROS 2 primitive support: add ``ServiceComponent`` and ``ClientComponent`` with full lifecycle gating.

**Livrable.** "lifecore supports all ROS 2 communication primitives with consistent activation semantics."

---

Content
-------

ServiceComponent
^^^^^^^^^^^^^^^^

- Abstract base class (like ``LifecycleSubscriberComponent``)
- Generic: ``ServiceComponent[SrvType]`` (or ``ServiceComponent`` without generics if not param-inferred)
- Lifecycle:

  - ``_on_configure``: create ROS service (service stub, callback registration)
  - ``_on_activate``: make service available for calls
  - ``_on_deactivate``: reject new calls (pending calls complete or timeout)
  - ``_on_cleanup``: destroy service
- Activation gating: all callback execution blocked if not active (return error response)
- Handler hook: ``on_service_request(request: RequestType) -> ResponseType`` (abstract)

ClientComponent
^^^^^^^^^^^^^^^

- Abstract base class (like ``LifecycleSubscriberComponent``)
- Generic: ``ClientComponent[SrvType]``
- Lifecycle:

  - ``_on_configure``: create ROS client (client object only, no calls yet)
  - ``_on_activate``: enable ``call()`` and ``call_async()``
  - ``_on_deactivate``: block new calls
  - ``_on_cleanup``: destroy client
- Activation gating: ``call()`` raises ``ComponentNotActiveError`` if not active
- Call methods: ``call(request: RequestType, timeout: Optional[float] = None) -> ResponseType``
- Optional async: ``call_async(request: RequestType) -> Future``

TopicComponent behaviors
^^^^^^^^^^^^^^^^^^^^^^^^

Verify that existing ``LifecyclePublisherComponent`` and ``LifecycleSubscriberComponent`` apply the same activation gating rules. No breaking changes; this sprint verifies consistency.

---

Tests to write
--------------

ServiceComponent unit tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- [ ] Service created in ``_on_configure``, destroyed in ``_on_cleanup``
- [ ] Service callback rejected if not active (component in INACTIVE state)
- [ ] Service callback accepted if active (component in ACTIVE state)
- [ ] Service transitions: ``configure`` → ``activate`` → ``deactivate`` → ``cleanup``
- [ ] Double activate → idempotent or error (per adoption hardening §5 rule)
- [ ] Error in ``on_service_request`` → exception handling (component state, service remains bound)

ClientComponent unit tests
^^^^^^^^^^^^^^^^^^^^^^^^^^

- [ ] Client created in ``_on_configure``, destroyed in ``_on_cleanup``
- [ ] ``call()`` blocked if not active → raises ``ComponentNotActiveError``
- [ ] ``call()`` succeeds if active
- [ ] ``call_async()`` blocked if not active → returns failed Future or raises
- [ ] Lifecycle: ``configure`` → ``activate`` → ``call`` → ``deactivate`` → blocked calls
- [ ] Timeout handling: ``call(timeout=1.0)`` respects timeout
- [ ] Error in service handler → client receives error response (not exception leak)

Integration tests
^^^^^^^^^^^^^^^^^

- [ ] ServiceComponent + ClientComponent in same node
- [ ] Client calls service in same node (request/response cycle)
- [ ] Service inactive → client gets error response or timeout
- [ ] Multiple services in same node (distinct names, independent lifecycle)
- [ ] Multiple clients calling same service concurrently

---

Risks and mitigation
--------------------

**Risk 1: Callback execution during deactivate**

- **Problem**: Service/client callbacks might be executing when deactivate is called.
- **Mitigation**:
  - New calls blocked immediately on deactivate
  - Pending calls allowed to complete (with timeout guard if needed)
  - Document in docstring: "deactivate does not cancel in-flight requests"

**Risk 2: Async service calls leak state**

- **Problem**: ``call_async()`` on client returns Future; if component deactivates, Future might dangle.
- **Mitigation**:
  - Deprecate ``call_async()`` from this sprint or accept it with clear contract
  - If included: track all pending Futures, cancel them on deactivate
  - Document: "Futures returned by ``call_async()`` are not cancelled on deactivate; application must manage"

**Risk 3: Service response timeout vs activation state**

- **Problem**: Client calls service, service is slow, client deactivates. What happens?
- **Mitigation**:
  - Client-side timeout is independent of component state
  - If timeout expires, ``call()`` raises ``TimeoutError``
  - If component deactivates, ``call()`` is blocked (but already-issued calls are NOT cancelled)

**Risk 4: Inconsistency with publisher/subscriber activation gating**

- **Problem**: Publisher gates on message publication; subscriber gates on message handling. Service/client should be consistent.
- **Mitigation**:
  - Service: gate on incoming *requests* (return error response if inactive)
  - Client: gate on outgoing *calls* (raise if inactive)
  - Match existing TopicComponent semantics
  - Add test that verifies all four components (pub, sub, svc, cli) behave consistently

---

Dependencies
------------

- Requires: ``LifecycleComponent`` base (shipped)
- Requires: ``when_active`` decorator (shipped) — used for callback gating
- Requires: Error handling (Sprint 2) — retroactively hardens error semantics
- Requires: Testing fixtures (Sprint 3) — utilities for testing this sprint

---

Scope boundaries
----------------

**In-scope for this sprint:**

- Basic ``ServiceComponent`` and ``ClientComponent``
- Single request/response semantics
- Lifecycle integration
- Activation gating
- Error responses (not exceptions to application)

**Out-of-scope:**

- Async handlers (deferred; blocked API shape not yet decided)
- Service pooling or multiplexing
- Timeout policies at framework level (timeout is parameter to ``call()``)
- Action components (different semantic, separate sprint)
- Parameter components (separate sprint)

---

Success signal
--------------

- [ ] ``from lifecore_ros2 import ServiceComponent, ClientComponent`` works
- [ ] All tests pass (unit + integration)
- [ ] Activation gating is enforced and tested
- [ ] Ruff, Pyright, Pytest all green
- [ ] Example: ``examples/minimal_service.py`` and ``examples/minimal_client.py`` (or combined)
- [ ] Design note: none required (primitives only)
- [ ] Docstrings complete (Google style, Napoleon-ready)

---

Example hook
------------

ServiceComponent minimal implementation::

   class MinimalServiceComponent(ServiceComponent[std_srvs.srv.Empty]):
       def _on_configure(self) -> LifecycleNodeTransitionCallbackReturn:
           self._service = self.node.create_service(
               std_srvs.srv.Empty,
               "my_service",
               self._handle_request
           )
           return TransitionCallbackReturn.SUCCESS

       def on_service_request(self, request):
           # This is called by the framework only if component is active
           return std_srvs.srv.Empty.Response()

       def _on_cleanup(self) -> LifecycleNodeTransitionCallbackReturn:
           self.node.destroy_service(self._service)
           self._service = None
           return TransitionCallbackReturn.SUCCESS
