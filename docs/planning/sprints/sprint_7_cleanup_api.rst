Sprint 7 - Cleanup and ownership API
====================================

**Objective.** Make resource ownership and cleanup behavior boringly clear
before concurrency, health, or watchdog behavior depend on it.

**Deliverable.** Components have consistent cleanup semantics, and docs explain
which resources are owned by the component versus borrowed from the application.

---

Scope
-----

Audit and refine cleanup behavior for:

- publisher components
- subscriber components
- timer components
- service server components
- service client components
- custom ``LifecycleComponent`` subclasses in examples

Clarify:

- resources created in configure are released in cleanup
- deactivation gates runtime behavior but does not necessarily destroy ROS resources
- borrowed resources such as callback groups remain application-owned
- shutdown is not the only release path a component should rely on

Decisions
---------

All decisions below are final for Sprint 7.

**Resource lifecycle contract:**

- Configure owns ROS resource creation.
- Cleanup, shutdown, and error own release of resources created by the component.
- Deactivate changes runtime behavior only; it does not destroy ROS resources.
- Borrowed resources remain borrowed and must not be destroyed or nulled by components.
- ``_release_resources()`` must be called after ``_on_*`` in cleanup/shutdown/error,
  even if ``_on_*`` returns FAILURE or ERROR.

**``_needs_cleanup`` reset policy (Q1):**

``_needs_cleanup`` must be reset to ``False`` after the release *attempt*, regardless of
whether ``_release_resources()`` succeeded or failed. The flag reflects whether the
framework should attempt a lifecycle cleanup, not whether the component is in a
perfectly clean memory state.

Preferred pattern::

    try:
        release_result = self._safe_release_resources()
    finally:
        self._needs_cleanup = False

Result aggregation rule:

- ``_on_cleanup`` failure/error + release success → transition failure/error
- ``_on_cleanup`` success + release error → transition error
- ``_on_cleanup`` error + release error → transition error

The current ``if release_result == SUCCESS: self._needs_cleanup = False`` pattern is
the behavior to fix.

**No new public API (Q2):**

No ``is_cleaned_up`` or similar property will be added. Ownership is documented via
``Owns:`` / ``Does not own:`` docstring sections on each component class. Internal
state is tested directly in unit tests (``_publisher is None``, etc.).

Public API contract stays:

- ``is_active``: runtime activation state.
- ``is_configured``: whether configure succeeded (not currently public; keep internal).
- No new accessors.

**Timer methods after cleanup (Q3):**

``start()``, ``stop()``, and ``reset()`` must raise ``ComponentNotConfiguredError``
explicitly when ``self._timer is None``, following the same convention as
``publish()``, ``call()``, and ``call_async()``::

    if self._timer is None:
        raise ComponentNotConfiguredError(
            f"Timer component '{self.name}' is not configured"
        )

**No shared helper utilities needed.** Guard pattern is ``if x is not None`` / explicit
raise; no abstraction layer is warranted for one-liners already consistent across types.

**Ownership documented in docstrings, not only in architecture docs.** ``Owns:`` and
``Does not own:`` sections are the authoritative per-component record.

---

Final contract table
--------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Point
     - Decision
   * - Resources created
     - In ``configure()``
   * - Resources released
     - In ``cleanup()``, ``shutdown()``, ``error()``
   * - ``deactivate()``
     - Gates runtime only; destroys nothing
   * - Callback group
     - Borrowed; never destroyed or nulled by the component
   * - Idempotence
     - ``_release_resources()`` is safe on double call
   * - ``_needs_cleanup``
     - Reset to ``False`` after release attempt, not only on success
   * - New public state
     - None
   * - Timer methods after cleanup
     - Raise ``ComponentNotConfiguredError`` explicitly

---

Validation
----------

- [ ] ``on_cleanup`` resets ``_needs_cleanup = False`` even when ``_release_resources()`` returns ERROR.
- [ ] ``on_shutdown`` and ``on_error`` apply the same ``_needs_cleanup`` reset policy.
- [ ] Cleanup releases owned ROS handles for each component type.
- [ ] Deactivate gates behavior without destroying resources.
- [ ] Cleanup is idempotent (double call raises no exception).
- [ ] Borrowed callback groups are not nulled or destroyed by components.
- [ ] ``Timer.start()`` / ``stop()`` / ``reset()`` raise ``ComponentNotConfiguredError`` after cleanup.
- [ ] ``Owns:`` / ``Does not own:`` docstring sections are present on all five component types.

Required tests (minimum)
-------------------------

For each component type (publisher, subscriber, timer, service server, service client):

- ``test_cleanup_releases_owned_resource``
- ``test_cleanup_is_idempotent``
- ``test_deactivate_does_not_destroy_resource``
- ``test_cleanup_preserves_borrowed_callback_group``
- ``test_shutdown_releases_owned_resource``
- ``test_error_releases_owned_resource``

Timer-specific:

- ``test_timer_start_after_cleanup_raises_component_not_configured``
- ``test_timer_stop_after_cleanup_raises_component_not_configured``
- ``test_timer_reset_after_cleanup_raises_component_not_configured``

Custom example ``LifecycleComponent`` subclasses: one smoke test or doc example is
sufficient; no heavy battery unless the example owns external resources.

---

Success signal
--------------

- [ ] A user can answer "who owns this resource?" from the component docstring alone.
- [ ] Concurrency and health planning can assume cleanup behavior is explicit and tested.
- [ ] No component leaves ``_needs_cleanup = True`` after a cleanup/shutdown/error transition.
