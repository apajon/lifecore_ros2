Sprint 16 - Test ergonomics and diagnostics polish
==================================================

**Track.** Core + DX / Testing / Diagnostics.

**Branch.** ``sprint/16-test-ergonomics``.

**Priority.** P1/P3 - adoption leverage and API hardening.

**Objective.** Make lifecycle behavior easier to test and diagnose without
expanding the core conceptual model.

Possible scope
--------------

- Add lifecycle test fixtures.
- Add reusable fake components.
- Add helpers for activation/deactivation assertions.
- Improve transition diagnostics.
- Improve lifecycle-state assertions.
- Add bounded transition history only if a concrete test or watchdog use case
  needs it.
- Improve error messages without creating a new exception hierarchy unless the
  existing typed exceptions are insufficient.

Non-goals
---------

- No large new abstraction.
- No recovery framework.
- No hidden transition automation.

Acceptance criteria
-------------------

- [ ] Component lifecycle tests are simpler to write.
- [ ] Failures are easier to read.
- [ ] The core remains minimal.
- [ ] No heavy abstraction is introduced.
