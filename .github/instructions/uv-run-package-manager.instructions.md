---
name: "UV Run Command Policy"
description: "Use when proposing, generating, or executing Python package, build, lint, type-check, test, or tooling commands in lifecore_ros2. Enforce uv run usage and never use pip directly."
---
# UV Run Command Policy

- Always use `uv run` to execute Python tools and project commands.
- Never run `python` or `python3` directly for project commands. Use `uv run python ...` instead.
- Never use `pip` directly (`pip`, `pip3`, or `python -m pip`) in commands or examples.
- Never use `python -m pip`; use `uv` package workflows instead.
- When a package operation is needed, prefer `uv` workflows and keep commands consistent with project tooling.
- Keep command examples aligned with repository conventions:
  - `uv run ruff format .`
  - `uv run ruff check .`
  - `uv run pyright`
  - `uv run pytest`
  - `uv run python -m build`
- If a command from external docs uses `python`, `python3`, or `pip`, translate it to an equivalent `uv run` / `uv` command before suggesting it.
