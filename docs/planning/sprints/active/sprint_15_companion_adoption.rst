Sprint 15 - Companion adoption examples
=======================================

Status:
  Completed

Branch:
  sprint/15-companion-adoption

Track:
  Companion / Adoption

Priority:
  P1

Goal:
  Strengthen proof of value with concrete, readable, testable examples.

Scope
-----

- Audit the companion repository when available in the workspace.
- Identify the strongest lifecycle comparison example.
- Strengthen the comparative lifecycle example.
- Cover active publication, inactive publication blocking, activation gating,
  deactivation gating, cleanup, and expected errors in runtime tests.
- Explain why ``lifecore_ros2`` helps compared with manual ``rclpy`` lifecycle
  code.
- Add links from ``README.md`` and ``ROADMAP.md`` when the example is ready.

Non-goals
---------

- No new core abstraction just to make an example shorter.
- No dependency-heavy showcase unless the scenario requires it.

Acceptance criteria
-------------------

- [x] A new user can understand the value by reading and running one example.
- [x] The example does not require knowing the full internal architecture.
- [x] The example demonstrates less boilerplate, cleaner transitions, clearer
  errors, safer activation/deactivation, and deterministic cleanup.

Delivered
---------

- Companion README and lifecycle comparison README now frame inactive runtime
  misuse as lifecycle gating behavior: configured-but-inactive or deactivated
  nodes drop incoming samples, block timer-driven status publication, and keep
  running without introducing a new exception policy.
- The companion comparison also clarifies that ``on_message`` and ``on_tick``
  remain explicit public application hooks while framework-managed lifecycle
  gates decide when those hooks run.
- Companion runtime tests cover active publication, inactive publication
  blocking, activation gating, deactivation gating, cleanup, and inactive
  runtime misuse.
- Core README and ROADMAP keep short links to the companion comparison instead
  of duplicating the walkthrough.

Validation
----------

From ``lifecore_ros2_examples`` on 2026-05-13:

.. code-block:: bash

  uv run ruff check .
  uv run pyright
  uv run pytest

Result: passed, with ``9 passed`` from pytest.
