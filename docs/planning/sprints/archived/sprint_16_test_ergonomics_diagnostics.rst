Sprint 16 - Test ergonomics and diagnostics polish
==================================================

Status:
  Completed

Branch:
  sprint/16-test-ergonomics

Track:
  Core + DX / Testing / Diagnostics

Priority:
  P1/P3 - adoption leverage and API hardening

**Objective.** Make lifecycle behavior easier to test and diagnose without
expanding the core conceptual model.

Decisions
---------

- Lifecycle helpers stay private in ``tests/helpers/lifecycle.py``.
- Improve assertion messages first, not production exceptions.
- Do not add a new exception hierarchy.
- Do not add generalized transition history.
- Add a minimal ``FakeLifecycleComponent`` covering success, failure,
  exceptions, and hook order.
- Modify core code only if a test demonstrates a concrete diagnostic gap.
- Add minimal documentation only if the helpers become a contributor
  convention.

Possible scope
--------------

- Add lifecycle test fixtures.
- Add reusable fake components.
- Add helpers for activation/deactivation assertions.
- Improve assertion-level transition diagnostics.
- Improve lifecycle-state assertions.
- Keep production diagnostic changes conditional on a concrete failing test.

Non-goals
---------

- No large new abstraction.
- No recovery framework.
- No hidden transition automation.
- No new exception hierarchy.
- No generalized transition history.
- No public testing helper API unless explicitly promoted later.

Acceptance criteria
-------------------

- [x] Component lifecycle tests are simpler to write.
- [x] Failures are easier to read.
- [x] ``FakeLifecycleComponent`` covers success, failure, exception, and hook
  order scenarios.
- [x] The core remains minimal.
- [x] No heavy abstraction is introduced.

Implementation notes
--------------------

- Added private lifecycle helpers in ``tests/helpers/lifecycle.py``.
- Updated core lifecycle tests to use assertion helpers with component,
  transition, hook-order, and contract-state diagnostics.
- Added focused tests for helper success, failure, exception, hook order, and
  assertion messages.
- Did not change production exceptions, core lifecycle behavior, or public
  testing exports.

Validation
----------

- ``uv run ruff check tests/helpers/lifecycle.py tests/helpers/__init__.py tests/core/test_lifecycle.py tests/testing/test_private_lifecycle_helpers.py``
- ``uv run pytest tests/core/test_lifecycle.py tests/testing/test_private_lifecycle_helpers.py``

Archive note
------------

Move this sprint to ``docs/planning/sprints/archived/`` after review and any
release-note decision.
