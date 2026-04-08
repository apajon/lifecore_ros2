---
name: "lifecore | Feature Framing"
description: "Use when framing a new ROS 2 Jazzy lifecycle feature before implementation, to clarify behavior, transitions, touched modules, tests, examples, and validation scope."
argument-hint: "Describe the feature idea, expected lifecycle behavior, constraints, and success criteria."
agent: "Orchestrator | ROS 2 Feature Delivery"
---
Create a structured implementation brief for the requested lifecycle feature.

Context:
- Repository: lifecore_ros2 (ROS 2 Jazzy, Python, lifecycle-driven components)
- Goal: remove ambiguity before coding and delegation

Your task:
1. Rewrite the request into a precise feature goal.
2. Extract expected lifecycle behavior by transition:
   - configure
   - activate
   - deactivate
   - cleanup
   - shutdown
   - error
3. Identify modules likely impacted (core, components, examples, tests, docs) and why.
4. Define acceptance criteria that are testable and behavior-focused.
5. Propose the minimal validation plan (`uv run ruff check .`, `uv run pyright`, `uv run pytest`) scoped to touched areas.
6. List explicit non-goals to prevent scope creep.

If information is missing, ask targeted clarification questions before finalizing.

Output format:
- Feature goal
- Lifecycle behavior contract
- Impacted modules
- Acceptance criteria
- Validation plan
- Non-goals
- Clarifications needed
