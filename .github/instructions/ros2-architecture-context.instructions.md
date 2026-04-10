---
name: "ROS 2 Architecture Context"
description: "Use when making architectural decisions, modifying lifecycle transitions, adding components, reviewing core design, or touching files in src/lifecore_ros2/core/ or src/lifecore_ros2/components/. Enforces two-layer architecture, native lifecycle semantics, mempalace-with-fallback context gathering, and validation gates."
applyTo: src/lifecore_ros2/**/*.py, examples/**/*.py, tests/**/*.py
---
# ROS 2 Architecture Context

## Context Gathering — Priority Order

Collect architecture context in this order. Stop at the first source that succeeds:

1. **mempalace** (if tools are available in the current session):
   - Wing `lifecore_ros2`: project-specific architecture decisions, component contracts, orchestration patterns.
   - Wing `ROS2`: shared general ROS 2 knowledge (lifecycle, topics, ros_control, MoveIt, nav2, tf2, etc.).
   - Query both wings via `mcp_mempalace_mempalace_search` or `mcp_mempalace_mempalace_kg_query`.
2. **`docs/architecture.rst`**: read the file for layer descriptions and lifecycle design rules.
3. **`README.md`**, section *Design Principles* or *Architecture*: read for high-level intent.
4. **Workspace search**: search for `lifecycle`, `managed entity`, `topic component`, `ComposedLifecycleNode`, `LifecycleComponent` to reconstruct context from code.

## Robustness Rules

- If mempalace tools are unavailable or return errors, continue silently with local sources. Never fail or block a task because an external tool is missing.
- Never block a task solely because a preferred context source is unreachable.
- Prefer small, incremental, reviewable changes. Do not perform large refactors unless explicitly requested.

## Architecture Guardrails

These rules are mandatory for any change touching lifecycle or component code:

1. **Preserve native ROS 2 lifecycle semantics.** Do not override, bypass, or reinterpret the standard lifecycle state machine from `rclpy`.
2. **No hidden parallel state machines.** Components must not introduce internal states that diverge from or shadow the node lifecycle.
3. **Two-layer architecture.** Maintain the separation between:
   - `core/` — lifecycle primitives (`ComposedLifecycleNode`, `LifecycleComponent`, managed entity registration).
   - `components/` — topic-oriented components (publishers, subscribers) built on the core.
4. **Topic component lifecycle pattern:**
   - **Configure** — create ROS publishers/subscriptions.
   - **Activate** — gate message processing and publication on activation state.
   - **Cleanup** — release ROS resources.
5. **Keep `LifecycleComponent` minimal.** It is a managed entity with explicit hooks. Do not add implicit behavior.

## Validation

After any change that touches lifecycle or component code:

- Run lint: `uv run ruff check .`
- Run type-check: `uv run pyright`
- Run tests: `uv run pytest`
- Verify no implicit lifecycle logic was introduced (no hidden state, no silent transition side effects).

## Architecture Knowledge Persistence

After any significant architecture decision (new rule, new pattern, contract change, component addition), persist it in mempalace if tools are available:

- **Project-specific decisions** (lifecore_ros2 patterns, component contracts, orchestration rules): store in wing `lifecore_ros2`.
- **General ROS 2 knowledge** (lifecycle semantics, ros_control patterns, MoveIt conventions, etc.): store in wing `ROS2`.
- Use `mcp_mempalace_mempalace_add_drawer` with the appropriate wing and a room matching the topic.
- Before adding, use `mcp_mempalace_mempalace_check_duplicate` to avoid redundant entries.
- If mempalace tools are unavailable, skip silently. Do not block the task.

## Response Format

Use this structured format only when the change involves lifecycle logic, state transitions, component architecture, algorithmic behavior, or symbol renames. Skip it for typo fixes, simple corrections, and cosmetic edits.

When applicable, structure the response as:

1. **Architecture decisions applied** — summarize which guardrails were relevant.
2. **Context source used** — state whether mempalace, `architecture.rst`, `README.md`, or workspace search provided the context.
3. **Lifecycle regression risks** — flag any transitions, hooks, or state changes that could regress existing behavior.
4. **Validations executed** — list which checks were run and their outcomes.
