# Copilot Instructions for lifecore_ros2

## Project Scope

- Framework: composable lifecycle framework for ROS 2 nodes.
- Maturity: early development; favor small, incremental, reviewable changes.
- Language/runtime: Python 3.12+.
- Packaging: `src/` layout with setuptools and setuptools-scm.

## Behavioral Guidelines

Transverse rules to reduce common LLM coding mistakes. Bias toward caution over
speed; for trivial tasks, use judgment. These merge with the more specific
sections below and with `.instructions.md` files.

### Think before coding

- State assumptions explicitly; if uncertain, ask before implementing.
- When multiple interpretations exist, present them — do not pick silently.
- If a simpler approach exists, say so and push back when warranted.
- If something is unclear, stop and name what is confusing.

### Simplicity first

- Write the minimum code that solves the stated problem; nothing speculative.
- No features, abstractions, configurability, or error handling for scenarios
  that were not requested or cannot happen.
- If the result feels overcomplicated for a senior reviewer, rewrite smaller.

### Surgical changes

- Every changed line must trace directly to the user's request.
- Do not "improve" adjacent code, comments, or formatting; match existing style
  even if you would write it differently.
- Remove only imports/variables/functions that *your* changes orphaned. Do not
  delete pre-existing dead code unless asked — mention it instead.

### Goal-driven execution

- Translate tasks into verifiable success criteria before coding
  (e.g. "fix the bug" → "write a failing test that reproduces it, then make it
  pass"; "refactor X" → "tests pass before and after").
- For multi-step work, state a brief plan with a verification step per item,
  and use `manage_todo_list` when tracking adds value.
- Loop until the stated criteria are met; do not declare done on weak signals.
  Strong success criteria enable independent iteration; weak ones
  ("make it work") force re-clarification.

### Accountability

Codex reviews your output. Write code and explanations that hold up under a
second pair of eyes: traceable changes, stated assumptions, verified criteria.
These guidelines are working when diffs contain fewer unnecessary changes,
fewer rewrites due to overcomplication, and clarifying questions arrive
*before* implementation rather than after mistakes.

## Environment Assumptions

- ROS 2 (`rclpy`) is required at runtime and is expected to come from the system ROS installation.
- Do not add `rclpy` as a normal PyPI dependency in `pyproject.toml`.

## Preferred Commands

- Package manager: `uv` (never use `pip` directly)
- Format: `ruff format .`
- Lint: `ruff check .`
- Type-check: `pyright`
- Tests: `pytest`
- Build package: `python -m build`
- Pre-commit all hooks: `pre-commit run --all-files`

Use these commands for validation after changes that touch code or configuration.

## CI Cost Controls

- Prefer docs validation on pull requests and manual dispatch instead of every push.
- Keep docs workflow changes path-scoped to documentation-related files.
- Favor local docs build (`uv run --group docs python -m sphinx -b html docs docs/_build/html`) before pushing.

## Code Conventions

- Keep line length at 119 and formatting compatible with Ruff config.
- Use double quotes.
- Preserve strict typing and public type annotations.
- Keep lifecycle behavior explicit and minimal; avoid hidden state machines.
- Avoid broad architectural refactors unless explicitly requested.

## Engineering Principles

- Write code for humans first; optimize readability and maintainability over terseness.
- Prefer clarity over cleverness.
- Keep functions small and focused on one responsibility.
- Name things with intent; avoid vague or overloaded names.
- Avoid duplication where it improves maintainability, but do not force abstraction too early.
- Follow this order of priorities: make it work -> make it right -> make it fast.
- Comments should explain why a decision exists, not restate what the code does.
- Delete dead code aggressively instead of leaving unused branches or legacy leftovers.
- Keep configuration out of code when values vary by environment or deployment.

## Reliability and Operations

- Log what matters for diagnosis and operations; avoid noisy or redundant logging.
- Build features with observability in mind (actionable logs, measurable behavior, debuggable flows).
- Keep dependencies minimal and up to date; prefer fewer, well-maintained libraries.

## Architecture Map

- Core lifecycle primitives: `src/lifecore_ros2/core/`
- Topic-oriented components: `src/lifecore_ros2/components/`
- Public package exports: `src/lifecore_ros2/__init__.py`
- Examples: `examples/`
- Roadmap and validation checklist: `TODO.md`

## Naming Conventions

- `LifecycleComponent` is the core managed-entity abstraction. Do not rename it to `LifecycleCoreComponent`, `LifecycleAbstractComponent`, or similar variants.
- `LifecycleComponentNode` is the framework base node. Do not use `ComposedLifecycleNode`, `ComponentLifecycleNode`, or compound variants.
- Application nodes must use business/domain names: `class CameraNode(LifecycleComponentNode)`, not `class LifecycleCameraNode`.
- Framework-provided components follow the pattern `Lifecycle<Capability>Component` (e.g. `LifecyclePublisherComponent`).
- See `.github/instructions/naming-conventions.instructions.md` for the full rule set.

## Lifecycle Design Rules

- `LifecycleComponentNode` owns and drives registered `LifecycleComponent` instances as managed entities.
- `LifecycleComponent` subclasses should keep `_on_*` hooks focused and deterministic.
- For topic components:
  - create ROS pub/sub resources in `_on_configure`
  - gate message processing/publication with activation state
  - release resources in `_on_cleanup`

## Known Repository Gotchas

- `src/lifecore_ros2/_version.py` is generated by setuptools-scm; avoid manual edits unless required for a specific packaging task.
- There are currently few/no tests; when adding behavior, prefer adding focused pytest tests when feasible.

## Editing Guidelines for Agents

- Prefer narrow edits over sweeping rewrites.
- Preserve public imports and `__all__` compatibility unless change is requested.
- If changing lifecycle semantics, update or add an example in `examples/` that demonstrates the behavior.
- Link to existing docs/files instead of duplicating large explanations in code comments.

## Useful References

- Project overview: `README.md`
- Implementation checklist: `TODO.md`
- Release automation: `.github/workflows/release.yml`
- Tooling and package config: `pyproject.toml`, `.pre-commit-config.yaml`
