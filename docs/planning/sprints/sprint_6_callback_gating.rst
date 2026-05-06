Sprint 6 - Unified callback gating
==================================

**Objective.** Extract activation-gating logic into a shared, reusable utility.
Remove duplication across publisher, subscriber, service, client, and timer
components.

**Deliverable.** Activation gating is consistent everywhere; no duplicate logic.

---

Decisions locked (planning complete)
-------------------------------------

**Architecture:**

- New module ``lifecore_ros2/core/activation_gating.py`` holds the shared
  primitive::

      def require_active(is_active: bool, *, component_name: str) -> None:
          """Raise RuntimeError if not active."""

- ``LifecycleComponent.require_active()`` is a convenience façade that calls
  the primitive with ``self._is_active`` and ``self._name``.  No logic of its
  own.
- ``@when_active`` default-raise path is refactored to call the primitive
  instead of its own inline raise.  Drop paths (``when_not_active=None`` and
  ``when_not_active=callable``) are unchanged.
- ``LifecycleServiceServerComponent._on_request_wrapper`` replaces its
  ``if not self._is_active:`` guard with
  ``try: self.require_active() / except RuntimeError:``.  Warning log and
  annotated default response are preserved exactly.
- No raw ``if not self._is_active:`` check remains in any component file
  outside ``LifecycleComponent`` internals.
- ``is_active`` remains the existing property.  No ``is_active()`` method added.
- Node-level "fully active" terminology stays out of scope.

**Inactive policy per site (preserved exactly):**

+--------------------------------------------------+----------------------------------+
| Site                                             | Inactive policy                  |
+==================================================+==================================+
| ``publish``                                      | ``RuntimeError``                 |
+--------------------------------------------------+----------------------------------+
| ``call`` / ``call_async`` / ``wait_for_service`` | ``RuntimeError``                 |
+--------------------------------------------------+----------------------------------+
| ``_on_message_wrapper``                          | silent drop + debug log          |
+--------------------------------------------------+----------------------------------+
| ``_on_timer_wrapper``                            | silent drop + debug log          |
+--------------------------------------------------+----------------------------------+
| ``_on_request_wrapper``                          | warning log + default response   |
+--------------------------------------------------+----------------------------------+

Components covered
------------------

All five gating sites delegate to the shared primitive:

- ``LifecyclePublisherComponent`` publish path
- ``LifecycleSubscriberComponent`` message callback
- ``LifecycleServiceServerComponent`` request callback
- ``LifecycleServiceClientComponent`` call / call_async / wait_for_service
- ``LifecycleTimerComponent`` tick callback

---

Validation
----------

- [x] ``require_active(False, component_name="x")`` raises ``RuntimeError("Component 'x' is not active")``.
- [x] ``require_active(True, component_name="x")`` returns ``None``.
- [x] ``LifecycleComponent.require_active()`` delegates to the primitive without added logic.
- [x] ``@when_active`` default-raise path produces the same error message as before.
- [x] No raw ``if not self._is_active:`` check remains in component files.
- [x] Service-server inactive behavior (warning log + annotated default response) is preserved.
- [x] Gated callbacks (subscriber, timer) silently drop when inactive.
- [x] Existing tests pass without semantic changes.

---

Risks and mitigation
--------------------

**Risk: behavior-preserving refactor changes semantics.** Keep old behavior as
the golden standard and compare component-by-component.

**Risk: overgeneralized gating hides component-specific behavior.** Keep the
shared utility small; component-specific inactive behavior stays in the
component.

---

Dependencies
------------

- Requires: publisher, subscriber, timer, service, and client component surfaces.
- Requires: error handling rules from Sprint 2.
- Requires: testing support from Sprint 3.

---

Scope boundaries
----------------

In scope:

- ``core/activation_gating.py`` with the ``require_active`` primitive
- ``LifecycleComponent.require_active()`` façade
- ``@when_active`` default-raise path refactored to the primitive
- ``LifecycleServiceServerComponent._on_request_wrapper`` refactored to
  ``try/except RuntimeError`` on ``self.require_active()``
- behavior-preserving unit and regression tests

Out of scope:

- node-level "fully active" terminology
- ``is_active()`` method (``is_active`` remains a property)
- new gating modes or conditional application-specific gating
- changes to ``when_not_active=None`` / ``when_not_active=callable`` paths
- example updates (public lifecycle semantics unchanged)
- performance work unless a regression is measured

---

Success signal
--------------

- [x] ``require_active()``, ``@when_active``, and the service-server inactive
  handler all rely on the same shared activation check.
- [x] Each component preserves its existing inactive policy.
- [x] No raw ``if not self._is_active:`` remains outside ``LifecycleComponent``
  internals.
- [x] Ruff, Pyright, and pytest are green.
