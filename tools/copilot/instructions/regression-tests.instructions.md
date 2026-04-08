---
name: "Regression Test Style"
description: "Use when writing or reviewing pytest regression tests for lifecore_ros2 lifecycle transitions, activation gating, resource cleanup, and component behavior."
applyTo: "tests/**/*.py"
---
# Regression Test Style

## Naming
- Test files for regressions: `test_regression_<phase>_<behavior>.py` or add a `TestRegression<Behavior>` class inside an existing test module.
- Test function names: `test_<phase>_<behavior>_<condition>`, e.g. `test_activate_gating_callback_not_called_while_inactive`.
- Lifecycle phases in names must use exact repository terms: `configure`, `activate`, `deactivate`, `cleanup`, `shutdown`, `error`.

## Regression Identification
- Every regression test must include a one-line comment or docstring stating:
  - what was broken (observed behavior before fix)
  - what is now expected (restored behavior)
- Example:
  ```python
  def test_activate_gating_callback_not_called_while_inactive(node):
      # Regression: callback was invoked while component was inactive.
      # Expected: no processing before activate().
  ```

## Activation Gating Assertions
- Always assert the negative case first (before activate), then the positive case (after activate):
  ```python
  assert not callback_called   # before activate
  node.trigger_activate(state)
  assert callback_called        # after activate
  ```
- Never rely on implicit ordering or side effects to prove gating.

## Resource Cleanup
- Isolation. Each test that verifies cleanup must be independent and must not reuse a node fixture that already transitioned.
- Node destruction. Always destroy the node in teardown (fixture yields then calls `node.destroy_node()`).

## Instrumented Components
- Use a `RecordingComponent` pattern (see `tests/test_lifecycle.py`) for hook call verification.
- Use a `fail_on` parameter to inject controlled failures when testing error propagation.
- Do not use `unittest.mock.MagicMock` for lifecycle hook verification; prefer explicit instrumented subclasses.

## Test Structure
- Separate reproduction cases from guard cases:
  - `test_<behavior>_reproduces_regression` — proves the bug existed (may be skipped once fixed, or kept as a guard).
  - `test_<behavior>_guard` — proves the fix holds and guards against future regressions.
- Group related cases inside a `TestRegression<Behavior>` class.

## Fixtures
- Prefer module-scoped fixtures only when component state is read-only across all tests in the class.
- Prefer function-scoped fixtures (default) for any test that mutates lifecycle state.
- Fixture teardown must always call `node.destroy_node()`.

## Scope
- Keep regression tests focused on one boundary: transition, gating, cleanup, or API contract.
- Do not add convenience assertions that go beyond the regression scope — keep the minimal proof.
