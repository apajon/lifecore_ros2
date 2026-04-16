---
name: "Code Clarity and Review Heuristics"
description: "Use when writing, refactoring, or reviewing Python code quality in lifecore_ros2. Enforce clarity-first design, focused functions, intentional naming, and dead-code removal."
applyTo: "src/**/*.py, tests/**/*.py, examples/**/*.py"
---
# Code Clarity and Review Heuristics

- Write code for humans first. Prefer readability and maintainability over terse or clever constructs.
- Prefer clarity over cleverness in control flow, naming, and abstractions.
- Keep functions small and focused on one responsibility.
- Name things with intent. Use domain language and avoid vague names.
- Avoid duplication when it improves maintainability, but do not force abstractions too early.
- Follow this order of priorities: make it work -> make it right -> make it fast.
- Comments should explain why a decision exists, not restate what the code does.
- Delete dead code aggressively instead of keeping unused branches or legacy leftovers.

## Review Triggers

- Function does multiple unrelated tasks.
- Name does not communicate intent or lifecycle role.
- Repeated logic appears in multiple files.
- Comment describes mechanics instead of rationale.
- Unreachable, unused, or obsolete code remains after a change.
