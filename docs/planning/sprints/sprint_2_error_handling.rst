Sprint 2 — Solid error handling
================================

**Objectif.** Define and enforce error propagation rules; guarantee no zombie states on partial failure.

**Livrable.** "Error semantics are explicit and lifecycle is always coherent on failure."

---

Content
-------

Error propagation rules
^^^^^^^^^^^^^^^^^^^^^^^

Define and document:

- What happens when ``_on_configure`` fails in one component?
  - Do siblings already configured stay in that state, or rollback?
  - What is the node's final state? (CONFIGURED or UNCONFIGURED?)
- What happens when ``_on_activate`` fails?
  - Do already-activated siblings stay active?
  - Can the node be partially active?
- Error hooks: when is ``_on_error`` called vs ``_on_cleanup``?
- Can a component skip ``_on_cleanup`` if ``_on_configure`` failed?

Rollback semantics
^^^^^^^^^^^^^^^^^^

- On partial failure during ``configure`` or ``activate``:
  - Option A: **Rollback all** — restore previously-configured siblings to UNCONFIGURED
  - Option B: **All-or-nothing** — if one component fails, entire node transition fails, no partial state
  - Option C: **Partial allowed** — siblings stay configured; node state reflects which succeeded
- Decision: **Pick one, document it, enforce it**

Retry and idempotence
^^^^^^^^^^^^^^^^^^^^^

- Is ``_on_configure`` safe to call multiple times?
- Is ``_on_activate`` idempotent?
- Document contract: "hooks are called exactly once per transition, not retried on transient failure"

Protected hook invocation
^^^^^^^^^^^^^^^^^^^^^^^^^

- Wrap all ``_on_*`` hook calls in try/catch
- On exception:
  - Log with component name, hook type, exception message
  - Return ``FAILURE`` (or raise if enforced)
  - Do not leak exception to application
- State coherence: component must be in a valid state after hook failure (no half-allocated resources)

Resource cleanup on failure
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- If ``_on_configure`` fails partway through resource allocation, ``_release_resources`` must clean what was allocated
- Document contract: "if ``_on_configure`` raises, ``_release_resources`` will be called to clean partial allocation"

---

Tests to write
--------------

Configure failure tests
^^^^^^^^^^^^^^^^^^^^^^^

- [x] One component fails in ``_on_configure`` → node returns FAILURE
- [x] Siblings already configured → state depends on rollback decision (A/B/C)
- [x] After failure, node can retry configure (idempotence test)
- [x] Resources allocated before failure → cleaned by ``_release_resources`` on cleanup

Activate failure tests
^^^^^^^^^^^^^^^^^^^^^^^

- [x] One component fails in ``_on_activate`` → node returns FAILURE
- [x] Already-activated siblings → state depends on rollback decision
- [x] Node is not in ACTIVE state after failure
- [x] Partial activation → can retry or deactivate+cleanup

Partial failure scenarios
^^^^^^^^^^^^^^^^^^^^^^^^^

- [x] Three components: C1 OK, C2 fails, C3 never reached. Final state coherent.
- [x] Resource cleanup: C2 fails after allocating some resources; ``_release_resources`` called
- [x] Exception in ``_on_configure`` → caught, logged, not leaked to application

Error hook tests
^^^^^^^^^^^^^^^^

- [x] ``_on_error`` called when transition enters ERROR state (implementation-dependent)
- [x] ``_on_cleanup`` called on shutdown even if ``_on_configure`` failed
- [x] No double-cleanup: if ``_on_error`` already released resources, ``_on_cleanup`` should be safe (idempotent)

Logging tests
^^^^^^^^^^^^^

- [x] Failure logs include: component name, hook type, error message
- [x] Rollback (if implemented) logs component restoration
- [x] Example log output in test docstring

---

Risks and mitigation
--------------------

**Risk 1: Zombie state after failure**

- **Problem**: If rollback is not enforced, partially-active components leak visible state.
- **Mitigation**:
  - Enforce one of rollback options (A/B/C) in code, not just documentation
  - Test every scenario
  - Document the chosen contract clearly

**Risk 2: Resource leak on failure**

- **Problem**: ``_on_configure`` fails after allocating resource X; ``_release_resources`` not called or incomplete.
- **Mitigation**:
  - Framework calls ``_release_resources`` on failure (before returning)
  - Test explicitly: allocate in ``_on_configure``, raise exception, verify ``_release_resources`` called

**Risk 3: Retry infinite loop**

- **Problem**: If a hook is not idempotent, retrying configure could cause issues.
- **Mitigation**:
  - Document: "hooks are called exactly once per transition; application is responsible for making them idempotent if needed"
  - Do not auto-retry in framework

**Risk 4: Exception leak to application**

- **Problem**: Unhandled exception in hook bubbles up to user code.
- **Mitigation**:
  - All hook invocations wrapped in try/catch
  - Return ``FAILURE`` or raise a typed ``LifecycleHookError`` (framework-controlled exception)
  - Test that user code never sees raw hook exception

---

Dependencies
------------

- Requires: ``LifecycleComponent`` base (shipped)
- Requires: Error handling from Sprint 1 (service/client error responses)
- Requires: Testing fixtures (Sprint 3) for easy failure scenario setup

---

Scope boundaries
----------------

**In-scope:**

- Error propagation rules (pick A/B/C, document, enforce)
- Rollback on partial failure (if chosen)
- Protected hook invocation (try/catch)
- Logging (component name, hook, error)
- Resource cleanup guarantees
- Idempotence contract

**Out-of-scope:**

- User-defined error recovery policies (e.g., "on failure, do X") — deferred to lifecycle policies (Sprint 6)
- Automatic retry with backoff — application responsibility
- Compensation transactions (complex orchestration) — out of scope

---

Success signal
--------------

- [ ] Error propagation rules written and documented in ``docs/architecture.rst``
- [ ] Rollback option chosen and enforced in code
- [ ] All error scenarios have tests (unit + integration)
- [ ] Resource cleanup is guaranteed (test with ``Mock`` if needed)
- [ ] Logs are actionable and include component context
- [ ] Ruff, Pyright, Pytest all green
- [ ] Design note: error handling contract (if future-proofing needed)

---

Related design notes
--------------------

- :doc:`../design_notes/error_handling_contract` — future reference for advanced policies
